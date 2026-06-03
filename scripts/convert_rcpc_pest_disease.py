import csv
import json
import math
import re
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "rcpc_raw"
OUT_DETAIL = ROOT / "data" / "rcpc_pest_disease_incidence.csv"
OUT_SUMMARY = ROOT / "data" / "rcpc_municipal_summary.csv"
OUT_METADATA = ROOT / "data" / "rcpc_pest_disease_metadata.json"

SOURCES = [
    ("rice", "rice_pest_diseases_2015_2026.csv"),
    ("corn", "corn_pest_disease_incidence_2015_2026.csv"),
    ("hvc", "hvc_pest_disease_incidence_2015_2026.csv"),
    ("cassava", "cassava_pest_disease_incidence_2015_2026.csv"),
]

MONTHS = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

DETAIL_FIELDS = [
    "incident_id",
    "source_file",
    "source_commodity_group",
    "season",
    "series_code",
    "month",
    "month_num",
    "year_raw",
    "year_start",
    "year_end",
    "region",
    "province",
    "municipality",
    "barangay",
    "latitude",
    "longitude",
    "coordinate_quality",
    "crop_affected",
    "commodity_group",
    "date_planted",
    "total_area_planted_ha",
    "variety",
    "growth_stage",
    "pest_observed",
    "pest_family",
    "monitored_validated_ha",
    "total_area_affected_ha",
    "percent_infestation",
    "severity",
    "insects_per_hill",
    "total_area_treated_ha",
    "total_area_untreated_ha",
    "treatment_gap_ha",
    "action_taken",
    "remarks",
    "date_reported",
    "affected_farmers",
    "risk_score",
    "risk_class",
]

SUMMARY_FIELDS = [
    "province",
    "municipality",
    "rcpc_incident_records",
    "rcpc_incident_points",
    "rcpc_commodities",
    "rcpc_top_commodity",
    "rcpc_top_pest_family",
    "rcpc_latest_year",
    "rcpc_latest_report_date",
    "rcpc_total_planted_area_ha",
    "rcpc_monitored_area_ha",
    "rcpc_affected_area_ha",
    "rcpc_treated_area_ha",
    "rcpc_untreated_area_ha",
    "rcpc_treatment_gap_ha",
    "rcpc_affected_farmers",
    "rcpc_avg_infestation_pct",
    "rcpc_max_infestation_pct",
    "rcpc_avg_severity",
    "rcpc_high_severity_records",
    "rcpc_recent_records",
    "rcpc_recent_affected_area_ha",
    "rcpc_recent_affected_farmers",
    "rcpc_recent_treatment_gap_ha",
    "rcpc_rice_affected_area_ha",
    "rcpc_corn_affected_area_ha",
    "rcpc_hvc_affected_area_ha",
    "rcpc_cassava_affected_area_ha",
    "rcpc_rice_records",
    "rcpc_corn_records",
    "rcpc_hvc_records",
    "rcpc_cassava_records",
    "rcpc_pest_pressure_score",
    "rcpc_surveillance_priority_score",
    "rcpc_response_gap_score",
    "rcpc_risk_class",
]


def header_key(value):
    return re.sub(r"\s+", " ", (value or "").replace("\n", " ")).strip().lower()


def get(row, wanted):
    wanted = wanted.lower()
    for key, value in row.items():
        if header_key(key) == wanted:
            return (value or "").strip()
    for key, value in row.items():
        if wanted in header_key(key):
            return (value or "").strip()
    return ""


def clean_text(value):
    value = re.sub(r"\s+", " ", str(value or "")).strip()
    return "" if value in {"_", "-", "--"} else value


def proper_name(value):
    value = clean_text(value)
    if not value:
        return ""
    fixes = {
        "ii": "II",
        "sta ana": "Sta. Ana",
        "sta. ana": "Sta. Ana",
        "sta fe": "Sta. Fe",
        "sto nino": "Sto. Nino",
        "sto. nino": "Sto. Nino",
        "city of ilagan": "City of Ilagan",
        "ilagan": "City of Ilagan",
        "ilagan city": "City of Ilagan",
        "cauayan  city": "Cauayan City",
        "cauayan city": "Cauayan City",
        "dupax del sur": "Dupax del Sur",
    }
    norm = re.sub(r"\s+", " ", value.lower()).strip()
    if norm in fixes:
        return fixes[norm]
    return " ".join(part[:1].upper() + part[1:].lower() for part in value.split())


def parse_number(value):
    value = clean_text(value)
    if not value:
        return None
    value = value.replace("######", "").replace(",", "").replace("%", "")
    value = re.sub(r"(?<=\d)\s+(?=\d)", "", value)
    match = re.search(r"-?\d+(?:\.\d+)?", value)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def parse_years(value):
    years = [int(y) for y in re.findall(r"(?:19|20)\d{2}", value or "")]
    if not years:
        return "", ""
    return min(years), max(years)


def month_num(value):
    value = clean_text(value).lower()
    for name, num in MONTHS.items():
        if name in value:
            return num
    return ""


def valid_coord(lat, lng):
    if lat is None or lng is None:
        return False
    return 15 <= lat <= 21 and 120 <= lng <= 123.5


def commodity_group(source_group, crop):
    crop_norm = clean_text(crop).lower()
    if "rice" in crop_norm or crop_norm == "":
        return "rice" if source_group == "rice" else source_group
    if "corn" in crop_norm:
        return "corn"
    if "cassava" in crop_norm:
        return "cassava"
    return source_group if source_group in {"hvc", "cassava"} else crop_norm


def pest_family(value):
    text = clean_text(value).lower()
    if not text:
        return ""
    groups = [
        ("Fall Armyworm", ["faw", "fall army"]),
        ("Rodents", ["rodent", "rat"]),
        ("Plant Hopper", ["bph", "cph", "hopper"]),
        ("Leaf Folder/Miner", ["leaffolder", "leaf folder", "leaf miner", "case worm"]),
        ("Stem/Shoot/Fruit Borer", ["stem borer", "shoot", "fruit borer", "top borer", "pod borer", "bark borer"]),
        ("Bacterial Leaf Blight", ["blb", "bacterial leaf blight", "kresek"]),
        ("Blast/Blight/Spot", ["blast", "blight", "brown spot", "leaf spot", "northern corn leaf blight", "banded sheath"]),
        ("Cassava Phytoplasma/Mosaic", ["cpd", "phytoplasma", "mosaic"]),
        ("Fruit Fly", ["fruit fly"]),
        ("Gummosis", ["gummosis"]),
        ("Aphids/Scale/Mealybug", ["aphid", "scale", "mealy"]),
        ("Cutworm/Armyworm", ["cutworm", "armyworm"]),
        ("Disease - Fungal/Bacterial", ["sigatoka", "rust", "rot", "wilt", "anthracnose", "antrachnose", "gummosis"]),
    ]
    for label, needles in groups:
        if any(needle in text for needle in needles):
            return label
    return clean_text(value).title()


def risk_class(score):
    if score >= 75:
        return "Critical"
    if score >= 55:
        return "High"
    if score >= 35:
        return "Moderate"
    if score > 0:
        return "Watchlist"
    return "Data Insufficient"


def compute_record_score(row):
    affected = parse_number(row["total_area_affected_ha"]) or 0
    infestation = parse_number(row["percent_infestation"]) or 0
    severity = parse_number(row["severity"]) or 0
    farmers = parse_number(row["affected_farmers"]) or 0
    untreated = parse_number(row["total_area_untreated_ha"])
    gap = parse_number(row["treatment_gap_ha"]) or (untreated or 0)
    score = (
        min(35, affected / 8)
        + min(25, infestation / 4)
        + min(15, severity * 1.7)
        + min(15, farmers / 4)
        + min(10, gap / 5)
    )
    return min(100, score)


def normalize_record(raw, source_group, source_file, idx):
    year_raw = clean_text(get(raw, "year"))
    year_start, year_end = parse_years(year_raw)
    lat = parse_number(get(raw, "lattitude") or get(raw, "latitude"))
    lng = parse_number(get(raw, "longitude"))
    coord_ok = valid_coord(lat, lng)

    total_area_planted = parse_number(get(raw, "total area planted"))
    monitored = parse_number(get(raw, "monitored/validated"))
    affected = parse_number(get(raw, "total area affected"))
    treated = parse_number(get(raw, "total area treated"))
    untreated = parse_number(get(raw, "total area untreated"))
    if untreated is None and affected is not None and treated is not None:
        untreated = max(0, affected - treated)
    treatment_gap = untreated if untreated is not None else ""

    row = {
        "incident_id": f"RCPC-{source_group.upper()}-{idx:05d}",
        "source_file": source_file,
        "source_commodity_group": source_group,
        "season": clean_text(get(raw, "season")),
        "series_code": clean_text(get(raw, "series code")),
        "month": clean_text(get(raw, "month")),
        "month_num": month_num(get(raw, "month")),
        "year_raw": year_raw,
        "year_start": year_start,
        "year_end": year_end,
        "region": clean_text(get(raw, "region")).upper(),
        "province": proper_name(get(raw, "province")),
        "municipality": proper_name(get(raw, "municipality")),
        "barangay": proper_name(get(raw, "barangay")),
        "latitude": lat if coord_ok else "",
        "longitude": lng if coord_ok else "",
        "coordinate_quality": "valid" if coord_ok else "invalid_or_missing",
        "crop_affected": proper_name(get(raw, "crop affected")) or source_group.title(),
        "commodity_group": "",
        "date_planted": clean_text(get(raw, "date planted")),
        "total_area_planted_ha": total_area_planted if total_area_planted is not None else "",
        "variety": clean_text(get(raw, "variety")),
        "growth_stage": clean_text(get(raw, "growth stage")),
        "pest_observed": clean_text(get(raw, "pest observed")),
        "pest_family": "",
        "monitored_validated_ha": monitored if monitored is not None else "",
        "total_area_affected_ha": affected if affected is not None else "",
        "percent_infestation": parse_number(get(raw, "percent infestation")) or "",
        "severity": parse_number(get(raw, "severity")) or "",
        "insects_per_hill": clean_text(get(raw, "no. of insects")),
        "total_area_treated_ha": treated if treated is not None else "",
        "total_area_untreated_ha": untreated if untreated is not None else "",
        "treatment_gap_ha": treatment_gap,
        "action_taken": clean_text(get(raw, "action taken")),
        "remarks": clean_text(get(raw, "remarks")),
        "date_reported": clean_text(get(raw, "date reported")),
        "affected_farmers": parse_number(get(raw, "no. of affected farmer")) or "",
    }
    row["commodity_group"] = commodity_group(source_group, row["crop_affected"])
    row["pest_family"] = pest_family(row["pest_observed"])
    score = compute_record_score(row)
    row["risk_score"] = round(score, 1)
    row["risk_class"] = risk_class(score)
    return row


def fmt(value, digits=2):
    if value is None or value == "":
        return ""
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if math.isfinite(value):
            return f"{value:.{digits}f}".rstrip("0").rstrip(".")
        return ""
    return value


def build_summary(records):
    groups = defaultdict(list)
    for row in records:
        if row["province"] and row["municipality"]:
            groups[(row["province"], row["municipality"])].append(row)

    summaries = []
    for (province, municipality), rows in sorted(groups.items()):
        records = len(rows)
        points = sum(1 for r in rows if r["coordinate_quality"] == "valid")
        affected = sum(parse_number(r["total_area_affected_ha"]) or 0 for r in rows)
        monitored = sum(parse_number(r["monitored_validated_ha"]) or 0 for r in rows)
        planted = sum(parse_number(r["total_area_planted_ha"]) or 0 for r in rows)
        treated = sum(parse_number(r["total_area_treated_ha"]) or 0 for r in rows)
        untreated = sum(parse_number(r["total_area_untreated_ha"]) or 0 for r in rows)
        gap = sum(parse_number(r["treatment_gap_ha"]) or 0 for r in rows)
        farmers = sum(parse_number(r["affected_farmers"]) or 0 for r in rows)
        infestations = [parse_number(r["percent_infestation"]) for r in rows if parse_number(r["percent_infestation"]) is not None]
        severities = [parse_number(r["severity"]) for r in rows if parse_number(r["severity"]) is not None]
        latest = max((parse_number(r["year_end"]) or parse_number(r["year_start"]) or 0) for r in rows)
        recent_rows = [r for r in rows if (parse_number(r["year_end"]) or parse_number(r["year_start"]) or 0) >= max(0, latest - 1)]
        commodities = Counter(r["commodity_group"] for r in rows if r["commodity_group"])
        pests = Counter(r["pest_family"] for r in rows if r["pest_family"])

        commodity_area = defaultdict(float)
        commodity_records = defaultdict(int)
        for r in rows:
            grp = r["commodity_group"]
            commodity_area[grp] += parse_number(r["total_area_affected_ha"]) or 0
            commodity_records[grp] += 1

        avg_infestation = sum(infestations) / len(infestations) if infestations else 0
        avg_severity = sum(severities) / len(severities) if severities else 0
        recent_area = sum(parse_number(r["total_area_affected_ha"]) or 0 for r in recent_rows)
        recent_farmers = sum(parse_number(r["affected_farmers"]) or 0 for r in recent_rows)
        recent_gap = sum(parse_number(r["treatment_gap_ha"]) or 0 for r in recent_rows)

        pressure = min(100, min(35, affected / 50) + min(20, records / 10) + min(20, avg_infestation / 2) + min(15, avg_severity * 1.7) + min(10, recent_area / 25))
        surveillance = min(100, pressure * 0.45 + min(30, recent_area / 10) + min(15, recent_farmers / 8) + min(10, len(pests) * 1.5))
        response_gap = min(100, min(50, gap / 20) + min(25, untreated / max(affected, 1) * 25) + min(25, recent_gap / 10))

        summaries.append({
            "province": province,
            "municipality": municipality,
            "rcpc_incident_records": records,
            "rcpc_incident_points": points,
            "rcpc_commodities": "; ".join(k for k, _ in commodities.most_common()),
            "rcpc_top_commodity": commodities.most_common(1)[0][0] if commodities else "",
            "rcpc_top_pest_family": pests.most_common(1)[0][0] if pests else "",
            "rcpc_latest_year": int(latest) if latest else "",
            "rcpc_latest_report_date": "",
            "rcpc_total_planted_area_ha": planted,
            "rcpc_monitored_area_ha": monitored,
            "rcpc_affected_area_ha": affected,
            "rcpc_treated_area_ha": treated,
            "rcpc_untreated_area_ha": untreated,
            "rcpc_treatment_gap_ha": gap,
            "rcpc_affected_farmers": farmers,
            "rcpc_avg_infestation_pct": avg_infestation,
            "rcpc_max_infestation_pct": max(infestations) if infestations else 0,
            "rcpc_avg_severity": avg_severity,
            "rcpc_high_severity_records": sum(1 for r in rows if (parse_number(r["severity"]) or 0) >= 7 or (parse_number(r["percent_infestation"]) or 0) >= 50),
            "rcpc_recent_records": len(recent_rows),
            "rcpc_recent_affected_area_ha": recent_area,
            "rcpc_recent_affected_farmers": recent_farmers,
            "rcpc_recent_treatment_gap_ha": recent_gap,
            "rcpc_rice_affected_area_ha": commodity_area["rice"],
            "rcpc_corn_affected_area_ha": commodity_area["corn"],
            "rcpc_hvc_affected_area_ha": commodity_area["hvc"],
            "rcpc_cassava_affected_area_ha": commodity_area["cassava"],
            "rcpc_rice_records": commodity_records["rice"],
            "rcpc_corn_records": commodity_records["corn"],
            "rcpc_hvc_records": commodity_records["hvc"],
            "rcpc_cassava_records": commodity_records["cassava"],
            "rcpc_pest_pressure_score": pressure,
            "rcpc_surveillance_priority_score": surveillance,
            "rcpc_response_gap_score": response_gap,
            "rcpc_risk_class": risk_class(max(pressure, surveillance, response_gap)),
        })
    return summaries


def write_csv(path, rows, fields):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: fmt(row.get(field, "")) for field in fields})


def main():
    records = []
    source_stats = {}
    for source_group, filename in SOURCES:
        path = RAW_DIR / filename
        with path.open(newline="", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.DictReader(f)
            count = 0
            for raw in reader:
                if not any(clean_text(v) for v in raw.values()):
                    continue
                count += 1
                records.append(normalize_record(raw, source_group, filename, count))
        source_stats[filename] = {"commodity_group": source_group, "records": count}

    summaries = build_summary(records)
    write_csv(OUT_DETAIL, records, DETAIL_FIELDS)
    write_csv(OUT_SUMMARY, summaries, SUMMARY_FIELDS)

    metadata = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source": "Regional Crop Protection Center, DA-RFO2 shared CSV folder",
        "source_files": source_stats,
        "detail_file": OUT_DETAIL.name,
        "summary_file": OUT_SUMMARY.name,
        "records": len(records),
        "municipalities": len(summaries),
        "columns_considered": DETAIL_FIELDS,
        "notes": [
            "Raw source headers with embedded newlines were normalized to stable snake_case fields.",
            "Rows with invalid or out-of-region coordinates remain in the detail CSV but are not counted as valid incident points.",
            "Year ranges such as 2023-2024 are represented as year_start and year_end.",
            "Risk scores are screening indicators for planning and field validation, not official loss or damage assessments.",
        ],
    }
    OUT_METADATA.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(json.dumps({"records": len(records), "municipalities": len(summaries), "outputs": [str(OUT_DETAIL), str(OUT_SUMMARY), str(OUT_METADATA)]}, indent=2))


if __name__ == "__main__":
    main()
