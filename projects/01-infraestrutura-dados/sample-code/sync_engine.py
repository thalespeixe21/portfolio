"""
Financial Data Sync Engine
Automated ETL pipeline that syncs data from multiple sources
into a centralized PostgreSQL database.

This is a sanitized version — credentials, company names, and
platform-specific details have been removed.
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Optional

import gspread
import pandas as pd
import requests
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DB_URL = os.environ["DATABASE_URL"]
DB_KEY = os.environ["DATABASE_KEY"]
SHEETS_CREDS = os.environ["GOOGLE_CREDENTIALS"]

CENTRAL_BANK_API = "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"


# --- Currency Conversion ---

def fetch_ptax_rate(date: str) -> Optional[float]:
    """Fetch official PTAX sell rate (USD->BRL) from Central Bank of Brazil."""
    formatted = datetime.strptime(date, "%Y-%m-%d").strftime("%m-%d-%Y")
    url = f"{CENTRAL_BANK_API}/CotacaoDolarDia(dataCotacao=@d)"
    params = {"@d": f"'{formatted}'", "$format": "json"}

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json().get("value", [])

    if not data:
        return None  # Weekend/holiday — caller falls back to last available

    return data[-1]["cotacaoVenda"]


def get_exchange_rate(date: str, fallback_days: int = 5) -> float:
    """Get PTAX rate, falling back to previous business days if needed."""
    target = datetime.strptime(date, "%Y-%m-%d")

    for offset in range(fallback_days + 1):
        check_date = (target - timedelta(days=offset)).strftime("%Y-%m-%d")
        rate = fetch_ptax_rate(check_date)
        if rate:
            if offset > 0:
                logger.info(f"FX rate for {date}: using {check_date} (offset -{offset}d)")
            return rate

    raise ValueError(f"No PTAX rate found within {fallback_days} days of {date}")


# --- Deduplication ---

DEDUP_STRATEGIES = {
    "orders": {
        "key": ["order_id"],
        "method": "drop_duplicates",
        "keep": "last",
    },
    "refunds": {
        "key": ["order_id", "event_type", "date", "amount_usd"],
        "method": "drop_duplicates",
        "keep": "last",
    },
    "ad_campaigns": {
        "key": ["date", "campaign_name"],
        "method": "aggregate",
        "agg_cols": {"spend": "sum", "impressions": "sum", "clicks": "sum", "conversions": "sum"},
    },
    "video_analytics": {
        "key": ["account", "date", "video_id"],
        "method": "aggregate",
        "agg_cols": {"plays": "sum", "unique_plays": "sum", "button_clicks": "sum"},
    },
}


def deduplicate(df: pd.DataFrame, source: str) -> pd.DataFrame:
    """Apply source-specific deduplication strategy."""
    strategy = DEDUP_STRATEGIES.get(source)
    if not strategy:
        logger.warning(f"No dedup strategy for '{source}', returning as-is")
        return df

    before = len(df)

    if strategy["method"] == "drop_duplicates":
        df = df.drop_duplicates(subset=strategy["key"], keep=strategy["keep"])
    elif strategy["method"] == "aggregate":
        df = df.groupby(strategy["key"], as_index=False).agg(strategy["agg_cols"])

    after = len(df)
    if before != after:
        logger.info(f"Dedup [{source}]: {before} -> {after} rows ({before - after} removed)")

    return df


# --- Data Extraction ---

def extract_from_sheets(spreadsheet_id: str, sheet_name: str) -> pd.DataFrame:
    """Extract data from Google Sheets using column-index mapping."""
    gc = gspread.service_account_from_dict(SHEETS_CREDS)
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet(sheet_name)

    # IMPORTANT: use get_all_values(), NOT get_all_records()
    # get_all_records() breaks on duplicate headers or empty columns
    raw = ws.get_all_values()

    if len(raw) < 2:
        logger.warning(f"Sheet '{sheet_name}' has no data rows")
        return pd.DataFrame()

    headers = raw[0]
    data = raw[1:]

    return pd.DataFrame(data, columns=headers)


def validate_headers(df: pd.DataFrame, expected: list[str], source: str) -> bool:
    """Validate that source headers match expected schema.
    Column-index mapping breaks silently if source adds/removes columns.
    """
    actual = list(df.columns)
    if actual[:len(expected)] != expected:
        logger.error(
            f"Header mismatch in '{source}'!\n"
            f"  Expected: {expected[:5]}...\n"
            f"  Got:      {actual[:5]}..."
        )
        return False
    return True


# --- Data Loading ---

def load_to_database(df: pd.DataFrame, table: str, conflict_key: Optional[str] = None):
    """Load DataFrame into Supabase/PostgreSQL with batch upsert."""
    supabase = create_client(DB_URL, DB_KEY)

    records = df.to_dict("records")

    # Batch in chunks of 500 to avoid payload limits
    batch_size = 500
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]

        if conflict_key:
            supabase.table(table).upsert(batch, on_conflict=conflict_key).execute()
        else:
            supabase.table(table).insert(batch).execute()

        logger.info(f"Loaded batch {i // batch_size + 1} ({len(batch)} rows) into '{table}'")


# --- Validation & Alerts ---

def validate_data(df: pd.DataFrame, source: str) -> list[str]:
    """Run validation checks and return list of alerts."""
    alerts = []

    # Check for zero BRL amounts when USD is non-zero (broken FX conversion)
    if "amount_brl" in df.columns and "amount_usd" in df.columns:
        broken_fx = df[(df["amount_usd"] > 0) & (df["amount_brl"] == 0)]
        if len(broken_fx) > 0:
            alerts.append(f"CRITICAL [{source}]: {len(broken_fx)} rows with USD > 0 but BRL = 0")

    # Check for future dates
    if "date" in df.columns:
        today = datetime.now().strftime("%Y-%m-%d")
        future = df[df["date"] > today]
        if len(future) > 0:
            alerts.append(f"WARNING [{source}]: {len(future)} rows with future dates")

    # Check for null order_ids
    if "order_id" in df.columns:
        nulls = df["order_id"].isna().sum()
        if nulls > 0:
            alerts.append(f"WARNING [{source}]: {nulls} rows with null order_id")

    return alerts


# --- Main Sync ---

def run_sync():
    """Main sync orchestrator."""
    logger.info("=" * 60)
    logger.info("Starting financial data sync")
    logger.info("=" * 60)

    all_alerts = []

    # 1. Sync exchange rates
    logger.info("[1/4] Syncing exchange rates...")
    today = datetime.now()
    rates = []
    for i in range(7):
        date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
        try:
            rate = get_exchange_rate(date)
            rates.append({"date": date, "ptax_sell": rate})
        except ValueError:
            logger.warning(f"Could not get rate for {date}")

    if rates:
        rates_df = pd.DataFrame(rates)
        load_to_database(rates_df, "exchange_rates", conflict_key="date")

    # 2. Sync daily financial data
    logger.info("[2/4] Syncing daily financial data...")
    finance_df = extract_from_sheets("SPREADSHEET_ID", "daily_data")
    if not finance_df.empty:
        finance_df = deduplicate(finance_df, "orders")
        alerts = validate_data(finance_df, "daily_finance")
        all_alerts.extend(alerts)
        load_to_database(finance_df, "daily_finance", conflict_key="date")

    # 3. Sync ad campaigns
    logger.info("[3/4] Syncing ad campaign data...")
    ads_df = extract_from_sheets("SPREADSHEET_ID", "campaigns")
    if not ads_df.empty:
        ads_df = deduplicate(ads_df, "ad_campaigns")
        load_to_database(ads_df, "ad_campaigns", conflict_key="date,campaign_name")

    # 4. Sync video analytics
    logger.info("[4/4] Syncing video analytics...")
    video_df = extract_from_sheets("SPREADSHEET_ID", "video_data")
    if not video_df.empty:
        video_df = deduplicate(video_df, "video_analytics")
        load_to_database(video_df, "video_analytics", conflict_key="account,date,video_id")

    # Report alerts
    if all_alerts:
        logger.warning(f"\n{'=' * 40}\n{len(all_alerts)} ALERTS:\n")
        for alert in all_alerts:
            logger.warning(f"  {alert}")
    else:
        logger.info("All validations passed.")

    logger.info("Sync complete.")


if __name__ == "__main__":
    run_sync()
