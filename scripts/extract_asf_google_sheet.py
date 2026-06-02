#!/usr/bin/env python3
"""Build sanitized ASF summaries from the shared laboratory-results sheet.

The source sheet contains farmer names and farm/slaughterhouse identifiers.
This script deliberately does not write those fields. Outputs are aggregated
by municipality and barangay for app overlays and scenario scoring.
"""

from __future__ import annotations

import argparse
import csv
import re
import urllib.request
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path


SHEET_ID = "1q1zvS-IsurvlSFlFBiT-S72VBzp8DysNPEd49zHHjXE"
SHEET_CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv"

MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}

SAMPLE_GROUPS = {
    "whole_blood": (8, 9, 10),
    "organ": (13, 14, 15),
    "environmental_swab": (17, 18, 19),
    "fecal_swab": (21, 22, 23),
    "meat_products": (25, 26, 27),
}


@dataclass
class Summary:
    province: str = ""
    municipality: str = ""
    barangay: str = ""
    records: int = 0
    sample_total: float = 0
    positive_total: float = 0
    negative_total: float = 0
    report_dates: list[date] = field(default_factory=list)
    tested_barangays: set[str] = field(default_factory=set)
    affected_barangays: set[str] = field(default_factory=set)
    group_samples: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    group_positive: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    group_negative: dict[str, float] = field(default_factory=lambda: defaultdict(float))


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", (value or "").strip())


def to_number(value: str) -> float:
    text = clean_text(value).replace(",", "")
    if text == "":
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def parse_report_date(value: str) -> date | None:
    text = clean_text(value).replace(".", "")
    match = re.match(r"^([A-Za-z]+)\s+(\d{1,2}),?\s+(\d{4})$", text)
    if not match:
        return None
    month_text, day_text, year_text = match.groups()
    month = MONTHS.get(month_text.lower())
    if not month:
        return None
    try:
        return date(int(year_text), month, int(day_text))
    except ValueError:
        return None


def format_num(value: float, digits: int = 0) -> str:
    if abs(value - round(value)) < 1e-9:
        return str(int(round(value)))
    return f"{value:.{digits}f}".rstrip("0").rstrip(".")


def status_for(summary: Summary) -> str:
    if summary.positive_total > 0:
        return "Affected"
    if summary.sample_total > 0:
        return "At-risk"
    return "Clear"


def risk_score(summary: Summary) -> float:
    if summary.sample_total <= 0:
        return 0.0
    positive_rate = summary.positive_total / summary.sample_total if summary.sample_total else 0
    score = (
        min(1, summary.positive_total / 25) * 35
        + min(1, positive_rate) * 35
        + min(1, len(summary.affected_barangays) / 10) * 20
        + min(1, summary.sample_total / 100) * 10
    )
    if summary.positive_total <= 0:
        score = min(20, 5 + min(1, summary.sample_total / 100) * 10)
    return round(min(100, score), 1)


def update_summary(summary: Summary, row: list[str]) -> None:
    province = clean_text(row[1] if len(row) > 1 else "")
    municipality = clean_text(row[2] if len(row) > 2 else "")
    barangay = clean_text(row[3] if len(row) > 3 else "")
    if not province or not municipality:
        return

    summary.province = province
    summary.municipality = municipality
    if barangay:
        summary.barangay = barangay
    summary.records += 1

    report_date = parse_report_date(row[0] if row else "")
    if report_date:
        summary.report_dates.append(report_date)

    row_samples = 0.0
    row_positive = 0.0
    row_negative = 0.0
    for group, (sample_idx, pos_idx, neg_idx) in SAMPLE_GROUPS.items():
        samples = to_number(row[sample_idx] if len(row) > sample_idx else "")
        positive = to_number(row[pos_idx] if len(row) > pos_idx else "")
        negative = to_number(row[neg_idx] if len(row) > neg_idx else "")
        summary.group_samples[group] += samples
        summary.group_positive[group] += positive
        summary.group_negative[group] += negative
        row_samples += samples
        row_positive += positive
        row_negative += negative

    summary.sample_total += row_samples
    summary.positive_total += row_positive
    summary.negative_total += row_negative
    if barangay and row_samples > 0:
        summary.tested_barangays.add(barangay)
    if barangay and row_positive > 0:
        summary.affected_barangays.add(barangay)


def read_source(path: Path | None) -> list[list[str]]:
    if path:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            return list(csv.reader(handle))

    with urllib.request.urlopen(SHEET_CSV_URL, timeout=60) as response:
      text = response.read().decode("utf-8-sig")
    return list(csv.reader(text.splitlines()))


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def summary_row(summary: Summary, include_barangay: bool) -> dict[str, str]:
    dates = sorted(summary.report_dates)
    row = {
        "province": summary.province,
        "municipality": summary.municipality,
        "asf_lab_records": format_num(summary.records),
        "asf_sample_total": format_num(summary.sample_total),
        "asf_positive_total": format_num(summary.positive_total),
        "asf_negative_total": format_num(summary.negative_total),
        "asf_positive_rate_pct": f"{(summary.positive_total / summary.sample_total * 100):.2f}" if summary.sample_total else "0",
        "asf_tested_barangays": format_num(len(summary.tested_barangays)),
        "asf_affected_barangays": format_num(len(summary.affected_barangays)),
        "asf_first_report_date": dates[0].isoformat() if dates else "",
        "asf_latest_report_date": dates[-1].isoformat() if dates else "",
        "asf_status": status_for(summary),
        "asf_risk_score": f"{risk_score(summary):.1f}",
        "asf_source_note": "Sanitized aggregate from ASF laboratory-results Google Sheet; farmer names and farm identifiers excluded.",
    }
    if include_barangay:
        row["barangay"] = summary.barangay
    for group in SAMPLE_GROUPS:
        prefix = f"asf_{group}"
        row[f"{prefix}_samples"] = format_num(summary.group_samples[group])
        row[f"{prefix}_positive"] = format_num(summary.group_positive[group])
        row[f"{prefix}_negative"] = format_num(summary.group_negative[group])
    return row


def build_outputs(rows: list[list[str]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    municipal: dict[tuple[str, str], Summary] = defaultdict(Summary)
    barangay: dict[tuple[str, str, str], Summary] = defaultdict(Summary)

    for raw in rows[2:]:
        if len(raw) < 4:
            continue
        province = clean_text(raw[1])
        municipality = clean_text(raw[2])
        brgy = clean_text(raw[3])
        if not province or not municipality:
            continue
        update_summary(municipal[(province.lower(), municipality.lower())], raw)
        if brgy:
            update_summary(barangay[(province.lower(), municipality.lower(), brgy.lower())], raw)

    municipal_rows = [summary_row(value, include_barangay=False) for value in municipal.values()]
    barangay_rows = [summary_row(value, include_barangay=True) for value in barangay.values()]
    municipal_rows.sort(key=lambda row: (row["province"], row["municipality"]))
    barangay_rows.sort(key=lambda row: (row["province"], row["municipality"], row["barangay"]))
    return municipal_rows, barangay_rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract sanitized ASF summaries from Google Sheet CSV.")
    parser.add_argument("--source", type=Path, help="Optional local CSV export to use instead of downloading.")
    parser.add_argument("--out-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    rows = read_source(args.source)
    municipal_rows, barangay_rows = build_outputs(rows)

    base_fields = [
        "province",
        "municipality",
        "asf_lab_records",
        "asf_sample_total",
        "asf_positive_total",
        "asf_negative_total",
        "asf_positive_rate_pct",
        "asf_tested_barangays",
        "asf_affected_barangays",
        "asf_first_report_date",
        "asf_latest_report_date",
        "asf_status",
        "asf_risk_score",
        "asf_source_note",
    ]
    sample_fields = []
    for group in SAMPLE_GROUPS:
        sample_fields.extend([
            f"asf_{group}_samples",
            f"asf_{group}_positive",
            f"asf_{group}_negative",
        ])

    write_csv(args.out_dir / "asf_municipal_summary.csv", municipal_rows, base_fields + sample_fields)
    write_csv(args.out_dir / "asf_barangay_summary.csv", barangay_rows, ["province", "municipality", "barangay"] + base_fields[2:] + sample_fields)

    print(f"Wrote {len(municipal_rows)} municipal ASF summaries")
    print(f"Wrote {len(barangay_rows)} barangay ASF summaries")
    print("PII fields excluded: first name, last name, extension, farm/slaughterhouse/agency")


if __name__ == "__main__":
    main()
