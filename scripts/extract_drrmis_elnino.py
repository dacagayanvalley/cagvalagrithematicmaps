#!/usr/bin/env python3
"""Extract province-level historical El Nino damage data from DA-DRRMO DRRMIS.

The public Looker Studio dashboard links to a Google Sheets/XLSX source. This
script reads the workbook, keeps Cagayan Valley provinces, and writes app-ready
CSV summaries. Values are province-level context; they should not be treated as
municipal raw observations.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import tempfile
import urllib.request
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


SHEET_ID = "1KYuowXvOCPYeNQMTayd88RWJ4HrxsjFT78Kjz0GlYlo"
SOURCE_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit?usp=sharing"
XLSX_EXPORT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=xlsx"
DASHBOARD_URL = "https://datastudio.google.com/reporting/5adf7ccf-22ae-45aa-a423-2ed6c8bbfecc/page/uW9wF"
RAW_DATA_LINK = "https://bit.ly/DADRRMSELNINODATA"
REGION_2_PROVINCES = {"BATANES", "CAGAYAN", "ISABELA", "NUEVA VIZCAYA", "QUIRINO"}

NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

DETAIL_FIELDS = [
    "episode",
    "episode_date",
    "year",
    "region",
    "province",
    "calamity",
    "drrmis_total_farmers_affected",
    "drrmis_total_area_affected_ha",
    "drrmis_total_production_loss_mt",
    "drrmis_total_value_loss_php",
    "drrmis_rice_farmers_affected",
    "drrmis_rice_area_affected_ha",
    "drrmis_rice_production_loss_mt",
    "drrmis_rice_value_loss_php",
    "drrmis_corn_farmers_affected",
    "drrmis_corn_area_affected_ha",
    "drrmis_corn_production_loss_mt",
    "drrmis_corn_value_loss_php",
    "drrmis_hvcc_farmers_affected",
    "drrmis_hvcc_area_affected_ha",
    "drrmis_hvcc_production_loss_mt",
    "drrmis_hvcc_value_loss_php",
    "drrmis_fisheries_value_loss_php",
    "drrmis_livestock_value_loss_php",
    "drrmis_infra_equipment_value_loss_php",
    "drrmis_source_url",
]

SUMMARY_FIELDS = [
    "province",
    "drrmis_region",
    "drrmis_elnino_source_level",
    "drrmis_elnino_episode_count",
    "drrmis_elnino_first_year",
    "drrmis_elnino_latest_year",
    "drrmis_elnino_total_farmers_affected",
    "drrmis_elnino_total_area_affected_ha",
    "drrmis_elnino_total_production_loss_mt",
    "drrmis_elnino_total_value_loss_php",
    "drrmis_elnino_rice_area_affected_ha",
    "drrmis_elnino_rice_value_loss_php",
    "drrmis_elnino_corn_area_affected_ha",
    "drrmis_elnino_corn_value_loss_php",
    "drrmis_elnino_hvcc_area_affected_ha",
    "drrmis_elnino_hvcc_value_loss_php",
    "drrmis_elnino_fisheries_value_loss_php",
    "drrmis_elnino_livestock_value_loss_php",
    "drrmis_elnino_infra_equipment_value_loss_php",
    "drrmis_elnino_latest_total_value_loss_php",
    "drrmis_elnino_latest_area_affected_ha",
    "drrmis_elnino_latest_farmers_affected",
    "drrmis_elnino_historical_impact_score",
    "drrmis_elnino_historical_impact_class",
    "drrmis_elnino_context_note",
    "drrmis_elnino_source_url",
]


def column_index(cell_ref: str) -> int:
    match = re.match(r"([A-Z]+)", cell_ref or "")
    if not match:
        return 0
    value = 0
    for char in match.group(1):
        value = value * 26 + ord(char) - 64
    return value - 1


def clean_header(value: object) -> str:
    text = clean_text(value)
    text = re.sub(r"\s+", "_", text).strip("_")
    return text


def clean_text(value: object) -> str:
    if value is None:
        return ""
    text = str(value).replace("\u00a0", " ")
    return re.sub(r"\s+", " ", text).strip()


def as_number(value: object) -> float:
    text = clean_text(value).replace(",", "")
    if not text:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def fmt_number(value: float, digits: int = 2) -> str:
    rounded = round(float(value or 0), digits)
    if abs(rounded - round(rounded)) < 10 ** -digits:
        return str(int(round(rounded)))
    return f"{rounded:.{digits}f}".rstrip("0").rstrip(".")


def read_shared_strings(archive: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return ["".join((node.text or "") for node in item.findall(".//a:t", NS)) for item in root.findall("a:si", NS)]


def read_cell(cell: ET.Element, shared_strings: list[str]) -> str:
    value = cell.find("a:v", NS)
    if value is None:
        inline = cell.find("a:is", NS)
        if inline is None:
            return ""
        return "".join((node.text or "") for node in inline.findall(".//a:t", NS))
    text = value.text or ""
    if cell.attrib.get("t") == "s" and text:
        return shared_strings[int(text)]
    return text


def workbook_sheets(path: Path) -> dict[str, list[list[str]]]:
    with zipfile.ZipFile(path) as archive:
        shared_strings = read_shared_strings(archive)
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rel_root = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rels = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rel_root.findall("rel:Relationship", NS)}
        sheets = {}
        for sheet in workbook.findall("a:sheets/a:sheet", NS):
            name = sheet.attrib["name"]
            rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = "xl/" + rels[rel_id].lstrip("/")
            root = ET.fromstring(archive.read(target))
            rows = []
            for row in root.findall("a:sheetData/a:row", NS):
                values = []
                for cell in row.findall("a:c", NS):
                    index = column_index(cell.attrib.get("r", "A1"))
                    if index >= len(values):
                        values.extend([""] * (index - len(values) + 1))
                    values[index] = read_cell(cell, shared_strings)
                rows.append(values)
            sheets[name] = rows
        return sheets


def download_source() -> Path:
    target = Path(tempfile.gettempdir()) / "drrmis_elnino_historical.xlsx"
    headers = {"User-Agent": "Mozilla/5.0 AgriSight-DRRMIS-Fetcher/1.0"}
    request = urllib.request.Request(XLSX_EXPORT_URL, headers=headers)
    with urllib.request.urlopen(request, timeout=90) as response:
        target.write_bytes(response.read())
    return target


def find_header(rows: list[list[str]]) -> int:
    for index, row in enumerate(rows):
        values = {clean_text(value) for value in row}
        if {"EPISODE", "REGION", "PROVINCE", "TOTAL_NoF"}.issubset(values):
            return index
    raise ValueError("Could not find Data sheet header row.")


def make_unique(headers: list[str]) -> list[str]:
    seen = {}
    output = []
    for header in headers:
        header = header or "Unnamed"
        seen[header] = seen.get(header, 0) + 1
        output.append(header if seen[header] == 1 else f"{header}_{seen[header]}")
    return output


def detail_from_raw(raw: dict[str, str]) -> dict[str, str]:
    return {
        "episode": clean_text(raw.get("EPISODE")),
        "episode_date": clean_text(raw.get("Date")),
        "year": fmt_number(as_number(raw.get("YEAR")), 0),
        "region": clean_text(raw.get("REGION")),
        "province": clean_text(raw.get("PROVINCE")),
        "calamity": clean_text(raw.get("CALAMITY")),
        "drrmis_total_farmers_affected": fmt_number(as_number(raw.get("TOTAL_NoF")), 0),
        "drrmis_total_area_affected_ha": fmt_number(as_number(raw.get("TOTAL_AA_Tot"))),
        "drrmis_total_production_loss_mt": fmt_number(as_number(raw.get("TOTAL_PL_Vol"))),
        "drrmis_total_value_loss_php": fmt_number(as_number(raw.get("TOTAL_PL_Val"))),
        "drrmis_rice_farmers_affected": fmt_number(as_number(raw.get("RICE_NoF")), 0),
        "drrmis_rice_area_affected_ha": fmt_number(as_number(raw.get("RICE_AA_Tot"))),
        "drrmis_rice_production_loss_mt": fmt_number(as_number(raw.get("RICE_PL_Vol"))),
        "drrmis_rice_value_loss_php": fmt_number(as_number(raw.get("RICE_PL_Val"))),
        "drrmis_corn_farmers_affected": fmt_number(as_number(raw.get("CORN_NoF")), 0),
        "drrmis_corn_area_affected_ha": fmt_number(as_number(raw.get("CORN_AA_Tot"))),
        "drrmis_corn_production_loss_mt": fmt_number(as_number(raw.get("CORN_PL_Vol"))),
        "drrmis_corn_value_loss_php": fmt_number(as_number(raw.get("CORN_PL_Val"))),
        "drrmis_hvcc_farmers_affected": fmt_number(as_number(raw.get("HVCC_NoF")), 0),
        "drrmis_hvcc_area_affected_ha": fmt_number(as_number(raw.get("HVCC_AA_Tot"))),
        "drrmis_hvcc_production_loss_mt": fmt_number(as_number(raw.get("HVCC_PL_Vol"))),
        "drrmis_hvcc_value_loss_php": fmt_number(as_number(raw.get("HVCC_PL_Val"))),
        "drrmis_fisheries_value_loss_php": fmt_number(as_number(raw.get("FISH_PL_Val"))),
        "drrmis_livestock_value_loss_php": fmt_number(as_number(raw.get("LIVE_PL_Val"))),
        "drrmis_infra_equipment_value_loss_php": fmt_number(
            as_number(raw.get("IRRIG_PL_Val")) +
            as_number(raw.get("INFRA_PL_Val")) +
            as_number(raw.get("EQP_PL_Val")) +
            as_number(raw.get("INFEQP_PL_Val"))
        ),
        "drrmis_source_url": SOURCE_URL,
    }


def read_detail_rows(path: Path) -> tuple[list[dict[str, str]], list[dict[str, str]], list[str]]:
    sheets = workbook_sheets(path)
    rows = sheets.get("Data")
    if not rows:
        raise ValueError("Workbook has no Data sheet.")
    header_index = find_header(rows)
    headers = make_unique([clean_header(value) for value in rows[header_index]])
    details = []
    mismatches = []
    for row in rows[header_index + 1:]:
        raw = {headers[index]: row[index] if index < len(row) else "" for index in range(len(headers))}
        if not raw.get("EPISODE") or not raw.get("REGION") or not raw.get("PROVINCE"):
            continue
        region = clean_text(raw.get("REGION"))
        province = clean_text(raw.get("PROVINCE"))
        if region == "RFO II" and province.upper() not in REGION_2_PROVINCES:
            mismatches.append({
                "source_sheet": "Data",
                "region": region,
                "province": province,
                "issue": "RFO II row is outside current AgriSight Cagayan Valley province list and was excluded.",
            })
        if region != "RFO II" or province.upper() not in REGION_2_PROVINCES:
            continue
        details.append(detail_from_raw(raw))
    return details, mismatches, list(sheets.keys())


def impact_class(score: float) -> str:
    if score >= 75:
        return "Very High Historical Impact"
    if score >= 55:
        return "High Historical Impact"
    if score >= 35:
        return "Moderate Historical Impact"
    if score > 0:
        return "Lower Historical Impact"
    return "No Extracted Historical Impact"


def summarize(details: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in details:
        grouped[row["province"]].append(row)

    raw_summaries = []
    for province, rows in grouped.items():
        years = [int(as_number(row["year"])) for row in rows if as_number(row["year"])]
        latest_year = max(years) if years else 0
        latest_rows = [row for row in rows if int(as_number(row["year"])) == latest_year]
        latest_value = sum(as_number(row["drrmis_total_value_loss_php"]) for row in latest_rows)
        latest_area = sum(as_number(row["drrmis_total_area_affected_ha"]) for row in latest_rows)
        latest_farmers = sum(as_number(row["drrmis_total_farmers_affected"]) for row in latest_rows)
        raw_summaries.append({
            "province": province,
            "drrmis_region": "RFO II",
            "drrmis_elnino_source_level": "Province",
            "drrmis_elnino_episode_count": len({row["episode"] for row in rows if row["episode"]}),
            "drrmis_elnino_first_year": min(years) if years else "",
            "drrmis_elnino_latest_year": latest_year or "",
            "drrmis_elnino_total_farmers_affected": sum(as_number(row["drrmis_total_farmers_affected"]) for row in rows),
            "drrmis_elnino_total_area_affected_ha": sum(as_number(row["drrmis_total_area_affected_ha"]) for row in rows),
            "drrmis_elnino_total_production_loss_mt": sum(as_number(row["drrmis_total_production_loss_mt"]) for row in rows),
            "drrmis_elnino_total_value_loss_php": sum(as_number(row["drrmis_total_value_loss_php"]) for row in rows),
            "drrmis_elnino_rice_area_affected_ha": sum(as_number(row["drrmis_rice_area_affected_ha"]) for row in rows),
            "drrmis_elnino_rice_value_loss_php": sum(as_number(row["drrmis_rice_value_loss_php"]) for row in rows),
            "drrmis_elnino_corn_area_affected_ha": sum(as_number(row["drrmis_corn_area_affected_ha"]) for row in rows),
            "drrmis_elnino_corn_value_loss_php": sum(as_number(row["drrmis_corn_value_loss_php"]) for row in rows),
            "drrmis_elnino_hvcc_area_affected_ha": sum(as_number(row["drrmis_hvcc_area_affected_ha"]) for row in rows),
            "drrmis_elnino_hvcc_value_loss_php": sum(as_number(row["drrmis_hvcc_value_loss_php"]) for row in rows),
            "drrmis_elnino_fisheries_value_loss_php": sum(as_number(row["drrmis_fisheries_value_loss_php"]) for row in rows),
            "drrmis_elnino_livestock_value_loss_php": sum(as_number(row["drrmis_livestock_value_loss_php"]) for row in rows),
            "drrmis_elnino_infra_equipment_value_loss_php": sum(as_number(row["drrmis_infra_equipment_value_loss_php"]) for row in rows),
            "drrmis_elnino_latest_total_value_loss_php": latest_value,
            "drrmis_elnino_latest_area_affected_ha": latest_area,
            "drrmis_elnino_latest_farmers_affected": latest_farmers,
        })

    max_value = max((row["drrmis_elnino_total_value_loss_php"] for row in raw_summaries), default=0) or 1
    max_area = max((row["drrmis_elnino_total_area_affected_ha"] for row in raw_summaries), default=0) or 1
    max_farmers = max((row["drrmis_elnino_total_farmers_affected"] for row in raw_summaries), default=0) or 1
    max_latest = max((row["drrmis_elnino_latest_total_value_loss_php"] for row in raw_summaries), default=0) or 1

    output = []
    for row in raw_summaries:
        crop_value = row["drrmis_elnino_rice_value_loss_php"] + row["drrmis_elnino_corn_value_loss_php"] + row["drrmis_elnino_hvcc_value_loss_php"]
        crop_share = crop_value / row["drrmis_elnino_total_value_loss_php"] if row["drrmis_elnino_total_value_loss_php"] else 0
        score = (
            min(1, row["drrmis_elnino_episode_count"] / 8) * 25 +
            min(1, row["drrmis_elnino_total_value_loss_php"] / max_value) * 25 +
            min(1, row["drrmis_elnino_total_area_affected_ha"] / max_area) * 20 +
            min(1, row["drrmis_elnino_total_farmers_affected"] / max_farmers) * 15 +
            min(1, row["drrmis_elnino_latest_total_value_loss_php"] / max_latest) * 10 +
            min(1, crop_share) * 5
        )
        formatted = {}
        for field in SUMMARY_FIELDS:
            value = row.get(field, "")
            if isinstance(value, float):
                formatted[field] = fmt_number(value)
            else:
                formatted[field] = str(value)
        formatted["drrmis_elnino_historical_impact_score"] = fmt_number(score, 1)
        formatted["drrmis_elnino_historical_impact_class"] = impact_class(score)
        formatted["drrmis_elnino_context_note"] = (
            "Province-level historical DRRMIS El Nino damage/loss context. "
            "Values are repeated to municipalities for screening only and are not municipal raw totals."
        )
        formatted["drrmis_elnino_source_url"] = SOURCE_URL
        output.append(formatted)

    return sorted(output, key=lambda item: item["province"])


def write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract DA-DRRMO DRRMIS El Nino historical damage data.")
    parser.add_argument("--source", type=Path, help="Optional local XLSX file. If omitted, downloads the public workbook.")
    parser.add_argument("--out-dir", type=Path, default=Path("data"))
    args = parser.parse_args()

    source = args.source or download_source()
    details, mismatches, sheet_names = read_detail_rows(source)
    summary = summarize(details)

    write_csv(args.out_dir / "drrmis_elnino_province_year.csv", details, DETAIL_FIELDS)
    write_csv(args.out_dir / "drrmis_elnino_province_summary.csv", summary, SUMMARY_FIELDS)
    write_csv(args.out_dir / "drrmis_elnino_mismatches.csv", mismatches, ["source_sheet", "region", "province", "issue"])

    metadata = {
        "source": "DA National Disaster Risk Reduction and Management Office DRRMIS dashboard",
        "dashboard_url": DASHBOARD_URL,
        "raw_data_link": RAW_DATA_LINK,
        "source_url": SOURCE_URL,
        "source_sheet_id": SHEET_ID,
        "source_file": str(source),
        "fetched_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "workbook_sheets": sheet_names,
        "province_year_rows": len(details),
        "province_summary_rows": len(summary),
        "mismatch_rows": len(mismatches),
        "notes": [
            "Notes tab says province reporting can be incomplete in earlier reports, especially infrastructure reports.",
            "Notes tab says animal pests and diseases such as ASF and AI are excluded.",
            "Notes tab says farmer/fisherfolk affected counts are available from 2019 to present.",
            "Values are province-level historical context, not municipal raw observations.",
        ],
    }
    (args.out_dir / "drrmis_elnino_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    print(f"Wrote {len(details)} province-year rows")
    print(f"Wrote {len(summary)} province summaries")
    print(f"Wrote {len(mismatches)} mismatch rows")


if __name__ == "__main__":
    main()
