import argparse
import csv
import json
import math
import re
import sys
import urllib.request
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path


API_BASE = "https://nsid.bswm.da.gov.ph:8000/api"
NSID_DATA_URL = f"{API_BASE}/msl-rst/nsidData"
SOURCE_APP_URL = "https://nsid.bswm.da.gov.ph:5173/"

REGION_02_PROVINCES = {
    "Batanes",
    "Cagayan",
    "Isabela",
    "Nueva Vizcaya",
    "Quirino",
}

SAMPLE_FIELDS = [
    "province",
    "municipality",
    "barangay",
    "latitude",
    "longitude",
    "laboratory_code",
    "batch_code",
    "date_received",
    "date_released",
    "soil_ph",
    "soil_ph_class",
    "organic_matter_class",
    "phosphorus_class",
    "potassium_class",
]

SUMMARY_FIELDS = [
    "province",
    "municipality",
    "bswm_sample_count",
    "bswm_coordinate_count",
    "bswm_complete_test_result_count",
    "bswm_latest_release_date",
    "bswm_avg_ph",
    "bswm_min_ph",
    "bswm_max_ph",
    "bswm_acidic_sample_count",
    "bswm_acidic_sample_pct",
    "bswm_low_om_count",
    "bswm_low_om_pct",
    "bswm_low_p_count",
    "bswm_low_p_pct",
    "bswm_low_k_count",
    "bswm_low_k_pct",
    "bswm_multiple_low_npk_count",
    "bswm_multiple_low_npk_pct",
    "bswm_fertilizer_constraint_score",
    "bswm_coverage_confidence_score",
    "bswm_has_fertmap_coverage",
]


def clean_text(value):
    return str(value or "").strip()


def lower(value):
    return clean_text(value).lower()


def as_float(value):
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def fmt_number(value, digits=2):
    if value is None:
        return ""
    if isinstance(value, float) and (math.isnan(value) or math.isinf(value)):
        return ""
    text = f"{value:.{digits}f}"
    return text.rstrip("0").rstrip(".")


def pct(part, total):
    return (part / total * 100) if total else 0


def parse_date(value):
    text = clean_text(value)
    if not text:
        return None
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def classify_ph(ph):
    if ph is None:
        return ""
    if ph < 5.5:
        return "Strongly Acidic"
    if ph < 6.5:
        return "Acidic"
    if ph <= 7.5:
        return "Near Neutral"
    return "Alkaline"


def fetch_json(url):
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "AgriSight data refresh/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=90) as response:
        return json.loads(response.read().decode("utf-8"))


def load_payload(source):
    if source:
        with open(source, "r", encoding="utf-8") as handle:
            return json.load(handle)
    return fetch_json(NSID_DATA_URL)


def normalize_sample(row):
    ph = as_float(row.get("soil_chem_ph") if row.get("soil_chem_ph") not in (None, "") else row.get("rst_ph"))
    return {
        "province": clean_text(row.get("province")),
        "municipality": clean_text(row.get("municipality")),
        "barangay": clean_text(row.get("barangay")),
        "latitude": clean_text(row.get("latitude")),
        "longitude": clean_text(row.get("longitude")),
        "laboratory_code": clean_text(row.get("laboratory_code")),
        "batch_code": clean_text(row.get("batch_code")),
        "date_received": clean_text(row.get("date_received")),
        "date_released": clean_text(row.get("date_released")),
        "soil_ph": fmt_number(ph),
        "soil_ph_class": classify_ph(ph),
        "organic_matter_class": clean_text(row.get("om")),
        "phosphorus_class": clean_text(row.get("p")),
        "potassium_class": clean_text(row.get("k")),
        "_ph_value": ph,
    }


def summarize(samples):
    grouped = defaultdict(list)
    for row in samples:
        grouped[(row["province"], row["municipality"])].append(row)

    summaries = []
    for (province, municipality), rows in sorted(grouped.items()):
        sample_count = len(rows)
        coordinates = {
            (row["latitude"], row["longitude"])
            for row in rows
            if row["latitude"] and row["longitude"]
        }
        ph_values = [row["_ph_value"] for row in rows if row["_ph_value"] is not None]
        acidic = sum(1 for value in ph_values if value < 6.5)
        low_om = sum(1 for row in rows if lower(row["organic_matter_class"]) == "low")
        low_p = sum(1 for row in rows if lower(row["phosphorus_class"]) == "low")
        low_k = sum(1 for row in rows if lower(row["potassium_class"]) == "low")
        complete = sum(
            1
            for row in rows
            if row["_ph_value"] is not None
            and row["organic_matter_class"]
            and row["phosphorus_class"]
            and row["potassium_class"]
        )
        multiple_low = sum(
            1
            for row in rows
            if (
                (1 if lower(row["organic_matter_class"]) == "low" else 0)
                + (1 if lower(row["phosphorus_class"]) == "low" else 0)
                + (1 if lower(row["potassium_class"]) == "low" else 0)
            )
            >= 2
        )
        release_dates = [parse_date(row["date_released"]) for row in rows]
        release_dates = [value for value in release_dates if value]

        acidic_pct = pct(acidic, len(ph_values))
        low_om_pct = pct(low_om, sample_count)
        low_p_pct = pct(low_p, sample_count)
        low_k_pct = pct(low_k, sample_count)
        multiple_low_pct = pct(multiple_low, sample_count)
        coverage_confidence = min(100, len(coordinates) * 7 + sample_count * 0.75)
        fertilizer_score = (
            acidic_pct * 0.25
            + low_om_pct * 0.20
            + low_p_pct * 0.20
            + low_k_pct * 0.20
            + multiple_low_pct * 0.15
        )

        summaries.append({
            "province": province,
            "municipality": municipality,
            "bswm_sample_count": str(sample_count),
            "bswm_coordinate_count": str(len(coordinates)),
            "bswm_complete_test_result_count": str(complete),
            "bswm_latest_release_date": max(release_dates).isoformat() if release_dates else "",
            "bswm_avg_ph": fmt_number(sum(ph_values) / len(ph_values) if ph_values else None),
            "bswm_min_ph": fmt_number(min(ph_values) if ph_values else None),
            "bswm_max_ph": fmt_number(max(ph_values) if ph_values else None),
            "bswm_acidic_sample_count": str(acidic),
            "bswm_acidic_sample_pct": fmt_number(acidic_pct),
            "bswm_low_om_count": str(low_om),
            "bswm_low_om_pct": fmt_number(low_om_pct),
            "bswm_low_p_count": str(low_p),
            "bswm_low_p_pct": fmt_number(low_p_pct),
            "bswm_low_k_count": str(low_k),
            "bswm_low_k_pct": fmt_number(low_k_pct),
            "bswm_multiple_low_npk_count": str(multiple_low),
            "bswm_multiple_low_npk_pct": fmt_number(multiple_low_pct),
            "bswm_fertilizer_constraint_score": fmt_number(fertilizer_score),
            "bswm_coverage_confidence_score": fmt_number(coverage_confidence),
            "bswm_has_fertmap_coverage": "Yes",
        })
    return summaries


def write_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description="Fetch and summarize public DA-BSWM FertMap soil-test data for AgriSight.")
    parser.add_argument("--source", help="Optional local JSON payload from /api/msl-rst/nsidData")
    parser.add_argument("--out-dir", default="data", help="Output directory for CSV/metadata files")
    args = parser.parse_args()

    payload = load_payload(args.source)
    raw_rows = payload.get("data", payload) if isinstance(payload, dict) else payload
    if not isinstance(raw_rows, list):
        raise SystemExit("FertMap payload does not contain a data array.")

    samples = [
        normalize_sample(row)
        for row in raw_rows
        if clean_text(row.get("province")) in REGION_02_PROVINCES
    ]
    samples = [row for row in samples if row["municipality"]]
    summaries = summarize(samples)

    sample_rows = [{key: row.get(key, "") for key in SAMPLE_FIELDS} for row in samples]
    out_dir = Path(args.out_dir)
    write_csv(out_dir / "bswm_fertmap_soil_samples.csv", SAMPLE_FIELDS, sample_rows)
    write_csv(out_dir / "bswm_fertmap_municipal_summary.csv", SUMMARY_FIELDS, summaries)

    coverage_by_province = defaultdict(lambda: {"samples": 0, "municipalities": set()})
    for row in samples:
        coverage_by_province[row["province"]]["samples"] += 1
        coverage_by_province[row["province"]]["municipalities"].add(row["municipality"])

    metadata = {
        "generated_at": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_app_url": SOURCE_APP_URL,
        "source_api_url": NSID_DATA_URL,
        "source_payload": str(args.source or NSID_DATA_URL),
        "notes": [
            "Public DA-BSWM FertMap point/lab-sample data summarized to municipality for AgriSight screening.",
            "Existing soil_* indicators remain attributed to DA-RFO2 Integrated Soils Laboratory.",
            "bswm_low_om fields use FertMap organic matter classification as the public N-related proxy displayed by the FertMap interface.",
            "Batanes is retained as Region 02 context but had no public FertMap rows in the source payload at generation time.",
        ],
        "raw_rows_total": len(raw_rows),
        "region_02_sample_rows": len(samples),
        "municipal_summary_rows": len(summaries),
        "coverage_by_province": {
            province: {
                "samples": item["samples"],
                "municipalities": len(item["municipalities"]),
            }
            for province, item in sorted(coverage_by_province.items())
        },
        "outputs": [
            "data/bswm_fertmap_soil_samples.csv",
            "data/bswm_fertmap_municipal_summary.csv",
        ],
    }
    with open(out_dir / "bswm_fertmap_metadata.json", "w", encoding="utf-8") as handle:
        json.dump(metadata, handle, indent=2)
        handle.write("\n")

    print(f"Wrote {len(samples)} BSWM FertMap sample rows.")
    print(f"Wrote {len(summaries)} BSWM FertMap municipal summaries.")


if __name__ == "__main__":
    main()
