from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib import request

PROJECT_ROOT = "starter_project"
VALID_STATUSES = {"completed", "pending", "cancelled"}


def validate_orders_pseudocode(input_csv_path: str, output_json_path: str, webhook_url: str) -> dict:
    """
    Python-style pseudocode for the student solution.
    This file is intentionally close to real code, but still leaves implementation details open.
    """

    rows = read_csv_rows(input_csv_path)  # e.g. starter_project/data/orders_passed.csv

    missing_customer_ids = 0
    invalid_amounts = 0
    invalid_statuses = 0

    for row in rows:
        customer_id = row["customer_id"].strip()
        amount = row["amount"].strip()
        status = row["status"].strip()

        if not customer_id:
            missing_customer_ids += 1

        if not is_positive_number(amount):  # TODO: implement numeric check
            invalid_amounts += 1

        if status not in VALID_STATUSES:
            invalid_statuses += 1

    summary = {
        "row_count": len(rows),
        "missing_customer_ids": missing_customer_ids,
        "invalid_amounts": invalid_amounts,
        "invalid_statuses": invalid_statuses,
        "validation_status": "passed",
    }

    if missing_customer_ids or invalid_amounts or invalid_statuses:
        summary["validation_status"] = "failed"

    write_summary_json(output_json_path, summary)  # e.g. starter_project/output/validation_summary.json
    send_discord_message(webhook_url, summary)

    if summary["validation_status"] == "failed":
        raise ValueError("Validation failed. Stop the pipeline.")

    return summary


def read_csv_rows(input_csv_path: str) -> list[dict]:
    with Path(input_csv_path).open("r", encoding="utf-8", newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def is_positive_number(raw_amount: str) -> bool:
    try:
        return float(raw_amount) > 0
    except (TypeError, ValueError):
        return False


def write_summary_json(output_json_path: str, summary: dict) -> None:
    output_file = Path(output_json_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def send_discord_message(webhook_url: str, summary: dict) -> None:
    if not webhook_url:
        return

    message = (
        f"Sales Data Quality {summary['validation_status'].upper()}\n"
        f"Rows: {summary['row_count']}\n"
        f"Missing customer_id: {summary['missing_customer_ids']}\n"
        f"Invalid amounts: {summary['invalid_amounts']}\n"
        f"Invalid statuses: {summary['invalid_statuses']}"
    )
    payload = json.dumps({"content": message}).encode("utf-8")
    http_request = request.Request(
        webhook_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(http_request, timeout=15):
        pass
