"""
HR Data Sync
Daily sync from Google Sheets (source of truth) to PostgreSQL.
Handles TRUNCATE+INSERT with email preservation.

Sanitized version — no real employee data or company details.
"""

import os
import logging
from typing import Optional

import gspread
import pandas as pd
from supabase import create_client

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def connect_sheets():
    creds = os.environ["GOOGLE_CREDENTIALS"]
    return gspread.service_account_from_dict(creds)


def connect_db():
    return create_client(os.environ["DATABASE_URL"], os.environ["DATABASE_KEY"])


def extract_employees(gc) -> pd.DataFrame:
    """Extract employee data from the HR spreadsheet."""
    sh = gc.open_by_key(os.environ["HR_SPREADSHEET_ID"])
    ws = sh.worksheet("Employees")

    raw = ws.get_all_values()
    if len(raw) < 2:
        raise ValueError("HR spreadsheet has no data rows")

    headers = raw[0]
    data = raw[1:]
    df = pd.DataFrame(data, columns=headers)

    expected = ["Name", "Role", "Department", "Level", "Salary", "Start Date", "Status"]
    actual = list(df.columns[:len(expected)])
    if actual != expected:
        raise ValueError(f"Header mismatch! Expected {expected}, got {actual}")

    return df


def transform_employees(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and normalize employee data."""
    # Normalize status
    df["Status"] = df["Status"].str.strip().str.lower()
    df["Status"] = df["Status"].map({
        "ativo": "active",
        "active": "active",
        "desligado": "terminated",
        "terminated": "terminated",
    }).fillna("unknown")

    # Parse dates (DD/MM/YYYY -> YYYY-MM-DD)
    for col in ["Start Date", "End Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], format="%d/%m/%Y", errors="coerce")

    # Parse salary (R$ 5.000,00 -> 5000.00)
    if "Salary" in df.columns:
        df["Salary"] = (
            df["Salary"]
            .str.replace("R$", "", regex=False)
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
            .str.strip()
            .astype(float, errors="ignore")
        )

    # Normalize department names
    df["Department"] = df["Department"].str.strip().str.title()

    return df


def preserve_emails(db) -> dict[str, Optional[str]]:
    """Save existing emails before TRUNCATE.
    Emails are assigned during onboarding and don't exist in the source sheet.
    """
    result = db.table("employees").select("name, email").execute()
    return {row["name"]: row.get("email") for row in result.data}


def load_employees(db, df: pd.DataFrame, email_map: dict):
    """TRUNCATE + INSERT with email restoration."""

    # TRUNCATE (fresh start)
    db.rpc("truncate_employees").execute()
    logger.info("Truncated employees table")

    # Restore emails and build records
    records = []
    for _, row in df.iterrows():
        record = {
            "name": row["Name"],
            "role": row["Role"],
            "department": row["Department"],
            "level": row.get("Level", ""),
            "salary": row.get("Salary"),
            "start_date": row["Start Date"].strftime("%Y-%m-%d") if pd.notna(row["Start Date"]) else None,
            "end_date": row.get("End Date", pd.NaT),
            "status": row["Status"],
            "email": email_map.get(row["Name"]),
        }

        if pd.notna(record.get("end_date")):
            record["end_date"] = record["end_date"].strftime("%Y-%m-%d")
        else:
            record["end_date"] = None

        # Suspend email for terminated employees
        if record["status"] == "terminated" and record["email"]:
            record["email_suspended"] = True

        records.append(record)

    # Batch insert
    batch_size = 50
    for i in range(0, len(records), batch_size):
        batch = records[i : i + batch_size]
        db.table("employees").insert(batch).execute()

    logger.info(f"Loaded {len(records)} employees")

    # Summary
    active = sum(1 for r in records if r["status"] == "active")
    terminated = sum(1 for r in records if r["status"] == "terminated")
    logger.info(f"  Active: {active} | Terminated: {terminated}")


def sync_departments(db, df: pd.DataFrame):
    """Sync department list from employee data."""
    departments = df["Department"].unique().tolist()

    for dept in departments:
        db.table("departments").upsert(
            {"name": dept}, on_conflict="name"
        ).execute()

    logger.info(f"Synced {len(departments)} departments")


def run_hr_sync():
    logger.info("Starting HR data sync...")

    gc = connect_sheets()
    db = connect_db()

    # Extract
    raw_df = extract_employees(gc)
    logger.info(f"Extracted {len(raw_df)} rows from HR spreadsheet")

    # Transform
    df = transform_employees(raw_df)

    # Preserve emails before TRUNCATE
    email_map = preserve_emails(db)
    logger.info(f"Preserved {len(email_map)} email mappings")

    # Load
    sync_departments(db, df)
    load_employees(db, df, email_map)

    logger.info("HR sync complete.")


if __name__ == "__main__":
    run_hr_sync()
