"""
Multi-Platform Payment Reconciliation Engine
Matches transactions across payment platforms, detects duplicates,
reconciles currencies, and generates discrepancy reports.

Sanitized version — no real platform names, credentials, or financial data.
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime

import pandas as pd

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

AMOUNT_TOLERANCE = 0.50  # USD — accounts for FX rounding
FX_DISCREPANCY_THRESHOLD = 2.0  # percent


@dataclass
class ReconciliationResult:
    matched: set = field(default_factory=set)
    in_db_only: set = field(default_factory=set)
    in_platform_only: set = field(default_factory=set)
    amount_mismatches: list = field(default_factory=list)
    duplicate_refunds: list = field(default_factory=list)
    fx_discrepancies: list = field(default_factory=list)


def normalize_order_id(raw_id: str) -> str:
    """Normalize order IDs across platforms (trim, uppercase, strip prefixes)."""
    if not raw_id:
        return ""
    clean = str(raw_id).strip().upper()
    for prefix in ["ORD-", "ORDER-", "#"]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
    return clean


def reconcile_orders(
    orders_db: pd.DataFrame,
    platform_reports: dict[str, pd.DataFrame],
) -> ReconciliationResult:
    """
    Cross-reference orders between the database and all platform reports.

    Relationship: 1 order_id -> N events (sale, upsell, rebill, refund, chargeback)
    """
    result = ReconciliationResult()

    # Build unified order map from all platforms
    all_orders = {}
    for platform_name, df in platform_reports.items():
        for _, row in df.iterrows():
            oid = normalize_order_id(row["order_id"])
            if not oid:
                continue
            if oid not in all_orders:
                all_orders[oid] = []
            all_orders[oid].append({
                "platform": platform_name,
                "type": row.get("event_type", "sale"),
                "amount_usd": float(row.get("amount_usd", 0)),
                "date": row.get("date"),
            })

    # Match against database
    db_order_ids = set(orders_db["order_id"].apply(normalize_order_id).unique())
    platform_order_ids = set(all_orders.keys())

    result.matched = db_order_ids & platform_order_ids
    result.in_db_only = db_order_ids - platform_order_ids
    result.in_platform_only = platform_order_ids - db_order_ids

    # Amount reconciliation for matched orders
    for oid in result.matched:
        db_rows = orders_db[orders_db["order_id"].apply(normalize_order_id) == oid]
        db_amount = db_rows["amount_usd"].sum()

        platform_amount = sum(
            e["amount_usd"] for e in all_orders[oid]
            if e["type"] == "sale"
        )

        diff = abs(db_amount - platform_amount)
        if diff > AMOUNT_TOLERANCE:
            result.amount_mismatches.append({
                "order_id": oid,
                "db_amount": round(db_amount, 2),
                "platform_amount": round(platform_amount, 2),
                "diff": round(diff, 2),
            })

    # Refund deduplication
    seen_refunds = set()
    for oid, events in all_orders.items():
        refunds = [e for e in events if e["type"] in ("refund", "chargeback")]
        for refund in refunds:
            key = (oid, refund["type"], str(refund["date"]), refund["amount_usd"])
            if key in seen_refunds:
                result.duplicate_refunds.append({
                    "order_id": oid,
                    "platform": refund["platform"],
                    "type": refund["type"],
                    "amount_usd": refund["amount_usd"],
                })
            else:
                seen_refunds.add(key)

    return result


def reconcile_currency(
    orders: pd.DataFrame,
    exchange_rates: pd.DataFrame,
) -> pd.DataFrame:
    """
    Compare platform-reported BRL amounts vs. official PTAX conversion.
    Flags discrepancies above the threshold.
    """
    merged = orders.merge(
        exchange_rates[["date", "ptax_sell"]],
        on="date",
        how="left",
    )

    merged["expected_brl"] = merged["amount_usd"] * merged["ptax_sell"]

    merged["fx_diff_pct"] = (
        (merged["reported_brl"] - merged["expected_brl"]).abs()
        / merged["expected_brl"].replace(0, float("nan"))
        * 100
    )

    merged["fx_alert"] = merged["fx_diff_pct"] > FX_DISCREPANCY_THRESHOLD

    flagged = merged[merged["fx_alert"]].copy()
    if len(flagged) > 0:
        logger.warning(
            f"FX discrepancies: {len(flagged)} transactions "
            f"(>{FX_DISCREPANCY_THRESHOLD}% diff from PTAX)"
        )

    return merged


def generate_report(result: ReconciliationResult, month: str) -> str:
    """Generate a text reconciliation report."""
    total_db = len(result.matched) + len(result.in_db_only)
    total_platform = len(result.matched) + len(result.in_platform_only)
    match_rate = len(result.matched) / max(total_db, 1) * 100

    mismatch_total = sum(m["diff"] for m in result.amount_mismatches)
    dup_total = sum(d["amount_usd"] for d in result.duplicate_refunds)
    db_only_total = len(result.in_db_only)
    platform_only_total = len(result.in_platform_only)

    report = f"""
{'=' * 50}
 RECONCILIATION REPORT - {month}
{'=' * 50}

SUMMARY
  Total orders (DB):        {total_db:,}
  Total orders (platforms): {total_platform:,}
  Matched:                  {len(result.matched):,}
  Match rate:               {match_rate:.1f}%

DISCREPANCIES
  In DB only:               {db_only_total:,} orders
  In platforms only:        {platform_only_total:,} orders
  Amount mismatches:        {len(result.amount_mismatches):,} (total diff: ${mismatch_total:,.2f})

DUPLICATES
  Duplicate refunds caught: {len(result.duplicate_refunds)} (${dup_total:,.2f})

STATUS: {'OK' if match_rate > 98 else 'REVIEW NEEDED' if match_rate > 95 else 'ALERT'}
{'=' * 50}
"""
    return report


def run_reconciliation(db_connection, platform_connections: dict, month: str):
    """Main reconciliation orchestrator."""
    logger.info(f"Starting reconciliation for {month}...")

    # Extract data
    orders_db = pd.DataFrame(
        db_connection.table("orders")
        .select("order_id, amount_usd, date")
        .gte("date", f"{month}-01")
        .lt("date", f"{month}-31")
        .execute()
        .data
    )

    platform_reports = {}
    for name, conn in platform_connections.items():
        df = conn.get_orders(month)
        platform_reports[name] = df
        logger.info(f"  {name}: {len(df)} orders")

    # Reconcile
    result = reconcile_orders(orders_db, platform_reports)

    # Generate report
    report = generate_report(result, month)
    logger.info(report)

    return result
