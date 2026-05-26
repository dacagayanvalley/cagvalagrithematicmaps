import csv
import json
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

SOURCE_HEADERS = [
    "Project Type",
    "Project Title",
    "Fund Source",
    "Source Agency",
    "Banner Program",
    "Year Funded",
    "Operating Unit",
    "Project Cost",
    "Beneficiary",
    "Quantity",
    "Province",
    "District",
    "Municipality",
    "Barangay",
]

SUMMARY_BASE_FIELDS = [
    "province",
    "district",
    "municipality",
    "abemis_total_projects",
    "abemis_total_cost",
    "abemis_total_quantity",
    "abemis_avg_cost_per_project",
    "abemis_latest_year",
    "abemis_dominant_project_type",
    "abemis_dominant_project_group",
    "abemis_banner_programs",
    "abemis_project_types",
]

BARANGAY_BASE_FIELDS = [
    "province",
    "district",
    "municipality",
    "barangay",
    "ADM4_PCODE",
    "ADM3_PCODE",
    "ADM2_PCODE",
    "abemis_total_projects",
    "abemis_total_cost",
    "abemis_total_quantity",
    "abemis_avg_cost_per_project",
    "abemis_latest_year",
    "abemis_dominant_project_type",
    "abemis_dominant_project_group",
    "abemis_banner_programs",
    "abemis_project_types",
]

DETAIL_FIELDS = [
    "project_id",
    "project_type",
    "project_type_key",
    "project_group",
    "project_group_key",
    "project_title",
    "fund_source",
    "source_agency",
    "banner_program",
    "year_funded",
    "operating_unit",
    "project_cost",
    "beneficiary",
    "quantity",
    "province",
    "district",
    "municipality",
    "barangay",
    "ADM4_PCODE",
    "ADM3_PCODE",
    "ADM2_PCODE",
    "match_status",
]

PROJECT_GROUPS = {
    "abemis_fmr": {
        "label": "Farm-to-Market Roads",
        "fields": ("abemis_fmr_projects", "abemis_fmr_cost"),
        "types": {"Farm-to-Market Road"},
    },
    "abemis_irrigation": {
        "label": "Irrigation and Water Systems",
        "fields": ("abemis_irrigation_projects", "abemis_irrigation_cost"),
        "types": {
            "Small Water Impounding Project",
            "Diversion Dam",
            "Solar-Powered Irrigation System",
            "Mobile Solar Power Irrigation Unit",
            "Solar-Powered Fertigation System (8)",
            "Spring Development",
            "Check Dam",
        },
    },
    "abemis_postharvest": {
        "label": "Postharvest and Processing",
        "fields": ("abemis_postharvest_projects", "abemis_postharvest_cost"),
        "types": {
            "Rice Processing Center",
            "Warehouse",
            "Multi-Purpose Drying Pavement",
            "Multi Crop Drying Pavement (MCDP)",
            "Multi-Commodity Drying Shed",
            "Palay Shed",
            "Cold Storage",
            "Packinghouse",
            "Coffee Processing Center",
            "Fertilizer Processing Center",
            "Grain Silo",
            "Village Type Corn Postharvest Processing Center (VTCPPC)",
        },
    },
    "abemis_protected_cultivation": {
        "label": "Protected Cultivation and Nurseries",
        "fields": ("abemis_protected_cultivation_projects", "abemis_protected_cultivation_cost"),
        "types": {
            "Greenhouse",
            "Rainshelter",
            "Mushroom Fruiting House",
            "Nursery Establishment",
            "Vermi-Composting Facilities",
        },
    },
    "abemis_food_garden": {
        "label": "Food Gardens",
        "fields": ("abemis_food_garden_projects", "abemis_food_garden_cost"),
        "types": {
            "School Garden",
            "Gulayan sa Barangay",
        },
    },
    "abemis_livestock": {
        "label": "Livestock Facilities",
        "fields": ("abemis_livestock_projects", "abemis_livestock_cost"),
        "types": {
            "Chicken Housing",
            "Rabbit Housing",
            "Swine Housing",
        },
    },
    "abemis_other": {
        "label": "Other ABEMIS Infrastructure",
        "fields": ("abemis_other_projects", "abemis_other_cost"),
        "types": set(),
    },
}

GROUP_FIELD_ORDER = [
    field
    for group in PROJECT_GROUPS.values()
    for field in group["fields"]
]


def column_index(cell_ref):
    letters = re.match(r"([A-Z]+)", cell_ref or "")
    if not letters:
        return 0
    value = 0
    for char in letters.group(1):
        value = value * 26 + ord(char) - 64
    return value - 1


def clean_text(value):
    return re.sub(r"\s+", " ", str(value or "").replace("\u00a0", " ")).strip()


def to_number(value):
    text = clean_text(value).replace(",", "")
    text = re.sub(r"[^\d.\-]", "", text)
    if text in {"", "-", "."}:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def format_number(value):
    return f"{float(value):.2f}"


def normalize_key(value):
    text = unicodedata.normalize("NFKD", clean_text(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.upper()
    replacements = {
        "CITY OF ILAGAN": "ILAGAN CITY",
        "CITY OF CAUAYAN": "CAUAYAN CITY",
        "CITY OF SANTIAGO": "SANTIAGO CITY",
        "TUGUEGARAO": "TUGUEGARAO CITY",
        "PE?ABLANCA": "PENABLANCA",
        "PEÑABLANCA": "PENABLANCA",
        "PEÃ±ABLANCA": "PENABLANCA",
        "STA.": "SANTA",
        "STA ": "SANTA ",
        "(CAPITAL)": "",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return re.sub(r"[^A-Z0-9]", "", text)


def slug_project_type(value):
    text = unicodedata.normalize("NFKD", clean_text(value)).encode("ascii", "ignore").decode("ascii")
    text = text.lower().replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return f"abemis_{text}_count" if text else "abemis_unknown_project_type_count"


def classify_project_group(project_type):
    project_type = clean_text(project_type)
    for group_key, group in PROJECT_GROUPS.items():
        if project_type in group["types"]:
            return group_key, group["label"]
    return "abemis_other", PROJECT_GROUPS["abemis_other"]["label"]


def read_shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    return [
        "".join((text.text or "") for text in item.findall(".//a:t", NS))
        for item in root.findall("a:si", NS)
    ]


def read_cell(cell, shared_strings):
    cell_type = cell.attrib.get("t")
    if cell_type == "inlineStr":
        return "".join((text.text or "") for text in cell.findall(".//a:t", NS))

    value = cell.find("a:v", NS)
    if value is None:
        return ""

    text = value.text or ""
    if cell_type == "s" and text:
        return shared_strings[int(text)]
    return text


def sheet_paths(archive):
    workbook = ET.fromstring(archive.read("xl/workbook.xml"))
    rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
    rel_targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall("rel:Relationship", NS)
    }

    sheets = []
    for sheet in workbook.findall("a:sheets/a:sheet", NS):
        name = sheet.attrib.get("name", "")
        rel_id = sheet.attrib.get(f"{{{NS['r']}}}id")
        target = rel_targets.get(rel_id, "")
        if target and not target.startswith("xl/"):
            target = "xl/" + target.lstrip("/")
        sheets.append((name, target))
    return sheets


def read_workbook(path):
    with zipfile.ZipFile(path) as archive:
        shared_strings = read_shared_strings(archive)
        sheets = []
        for name, sheet_path in sheet_paths(archive):
            if sheet_path not in archive.namelist():
                continue
            root = ET.fromstring(archive.read(sheet_path))
            rows = []
            for row in root.findall("a:sheetData/a:row", NS):
                values = []
                for cell in row.findall("a:c", NS):
                    idx = column_index(cell.attrib.get("r", "A1"))
                    if idx >= len(values):
                        values.extend([""] * (idx - len(values) + 1))
                    values[idx] = clean_text(read_cell(cell, shared_strings))
                rows.append(values)
            sheets.append((name, rows))
        return sheets


def load_municipal_lookup(path):
    lookup = {}
    by_province = defaultdict(dict)
    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            province = clean_text(row.get("province"))
            municipality = clean_text(row.get("municipality"))
            if not province or not municipality:
                continue
            province_key = normalize_key(province)
            municipality_key = normalize_key(municipality)
            canonical = {
                "province": province,
                "municipality": municipality,
                "district": clean_text(row.get("district")),
                "ADM3_PCODE": clean_text(row.get("ADM3_PCODE")),
                "ADM2_PCODE": clean_text(row.get("ADM2_PCODE")),
            }
            lookup[(province_key, municipality_key)] = canonical
            by_province[province_key][municipality_key] = canonical

    aliases = {
        "ILAGAN": "ILAGANCITY",
        "CITYOFILAGAN": "ILAGANCITY",
        "CAUAYAN": "CAUAYANCITY",
        "CITYOFCAUAYAN": "CAUAYANCITY",
        "SANTIAGO": "SANTIAGOCITY",
        "CITYOFSANTIAGO": "SANTIAGOCITY",
        "TUGUEGARAO": "TUGUEGARAOCITY",
        "CITYOFTUGUEGARAO": "TUGUEGARAOCITY",
        "PEABLANCA": "PENABLANCA",
        "PEABLANCA": "PENABLANCA",
        "SANTONINO": "SANTONIOFAIRE",
        "STONINO": "SANTONIOFAIRE",
        "LALLO": "LALLO",
        "DUPAXDELNORTE": "DUPAXDELNORTE",
        "DUPAXDELSUR": "DUPAXDELSUR",
        "REYNAMERCEDES": "REINAMERCEDES",
        "TUMAINI": "TUMAUINI",
        "NAGUILLAN": "NAGUILIAN",
    }
    return lookup, by_province, aliases


def canonical_municipality(province, municipality, lookup, by_province, aliases):
    province_key = normalize_key(province)
    municipality_key = aliases.get(normalize_key(municipality), normalize_key(municipality))
    direct = lookup.get((province_key, municipality_key))
    if direct:
        return direct

    province_rows = by_province.get(province_key, {})
    for key, row in province_rows.items():
        if key == municipality_key or key in municipality_key or municipality_key in key:
            return row

    return {
        "province": clean_text(province),
        "municipality": clean_text(municipality),
        "district": "",
        "ADM3_PCODE": "",
        "ADM2_PCODE": "",
    }


def load_barangay_lookup(path):
    if not Path(path).exists():
        return {}
    geojson = json.loads(Path(path).read_text(encoding="utf-8"))
    lookup = {}
    for feature in geojson.get("features", []):
        props = feature.get("properties", {})
        province = props.get("ADM2_EN") or props.get("province") or props.get("Province")
        municipality = props.get("ADM3_EN") or props.get("municipality") or props.get("Municipality")
        barangay = props.get("ADM4_EN") or props.get("barangay") or props.get("brgy_name")
        key = (normalize_key(province), normalize_key(municipality), normalize_key(barangay))
        lookup[key] = {
            "province": clean_text(province),
            "municipality": clean_text(municipality),
            "barangay": clean_text(barangay),
            "ADM4_PCODE": clean_text(props.get("ADM4_PCODE")),
            "ADM3_PCODE": clean_text(props.get("ADM3_PCODE")),
            "ADM2_PCODE": clean_text(props.get("ADM2_PCODE")),
        }
    return lookup


def canonical_barangay(row, barangay_lookup):
    key = (
        normalize_key(row["province"]),
        normalize_key(row["municipality"]),
        normalize_key(row["barangay"]),
    )
    direct = barangay_lookup.get(key)
    if direct:
        return direct, "barangay_matched"
    return {
        "barangay": row["barangay"],
        "ADM4_PCODE": "",
        "ADM3_PCODE": row["ADM3_PCODE"],
        "ADM2_PCODE": row["ADM2_PCODE"],
    }, "barangay_unmatched"


def extract_rows(source, municipal_csv, barangay_geojson):
    sheets = read_workbook(source)
    if not sheets:
        raise ValueError(f"No readable sheets found in {source}")

    rows = sheets[0][1]
    header = sheets[0][1][0] if False else sheets[0][1]
    sheet_name, sheet_rows = sheets[0]
    headers = [clean_text(value) for value in sheet_rows[0]]
    missing = [field for field in SOURCE_HEADERS if field not in headers]
    if missing:
        raise ValueError(f"Missing expected ABEMIS columns: {', '.join(missing)}")

    lookup, by_province, aliases = load_municipal_lookup(municipal_csv)
    barangay_lookup = load_barangay_lookup(barangay_geojson)
    details = []
    project_types = {}

    for index, values in enumerate(sheet_rows[1:], start=1):
        if not any(values):
            continue
        raw = {
            headers[i]: clean_text(values[i] if i < len(values) else "")
            for i in range(len(headers))
        }
        project_type = raw.get("Project Type", "")
        if not project_type:
            continue

        project_type_key = slug_project_type(project_type)
        project_group_key, project_group = classify_project_group(project_type)
        project_types[project_type_key] = project_type
        canonical = canonical_municipality(
            raw.get("Province", ""),
            raw.get("Municipality", ""),
            lookup,
            by_province,
            aliases,
        )
        normalized = {
            "project_id": f"ABEMIS{index:04d}",
            "project_type": project_type,
            "project_type_key": project_type_key,
            "project_group": project_group,
            "project_group_key": project_group_key,
            "project_title": raw.get("Project Title", ""),
            "fund_source": raw.get("Fund Source", ""),
            "source_agency": raw.get("Source Agency", ""),
            "banner_program": raw.get("Banner Program", ""),
            "year_funded": str(int(to_number(raw.get("Year Funded")))) if to_number(raw.get("Year Funded")) else "",
            "operating_unit": raw.get("Operating Unit", ""),
            "project_cost": format_number(to_number(raw.get("Project Cost"))),
            "beneficiary": raw.get("Beneficiary", ""),
            "quantity": format_number(to_number(raw.get("Quantity"))),
            "province": canonical["province"],
            "district": canonical["district"] or raw.get("District", ""),
            "municipality": canonical["municipality"],
            "barangay": raw.get("Barangay", ""),
            "ADM3_PCODE": canonical["ADM3_PCODE"],
            "ADM2_PCODE": canonical["ADM2_PCODE"],
            "source_sheet": sheet_name,
        }
        barangay, match_status = canonical_barangay(normalized, barangay_lookup)
        normalized["barangay"] = barangay["barangay"]
        normalized["ADM4_PCODE"] = barangay["ADM4_PCODE"]
        normalized["ADM3_PCODE"] = barangay["ADM3_PCODE"] or normalized["ADM3_PCODE"]
        normalized["ADM2_PCODE"] = barangay["ADM2_PCODE"] or normalized["ADM2_PCODE"]
        normalized["match_status"] = match_status
        details.append(normalized)

    return details, project_types


def add_to_bucket(bucket, row):
    bucket["abemis_total_projects"] += 1
    project_cost = to_number(row["project_cost"])
    bucket["abemis_total_cost"] += project_cost
    bucket["abemis_total_quantity"] += to_number(row["quantity"])
    year = int(row["year_funded"] or 0)
    if year:
        bucket["abemis_latest_year"] = max(bucket["abemis_latest_year"], year)
    bucket["project_type_counts"][row["project_type"]] += 1
    bucket["project_group_counts"][row["project_group"]] += 1
    bucket["banner_programs"].add(row["banner_program"])
    bucket["project_types"].add(row["project_type"])
    bucket[row["project_type_key"]] += 1
    group = PROJECT_GROUPS.get(row["project_group_key"], PROJECT_GROUPS["abemis_other"])
    project_count_field, project_cost_field = group["fields"]
    bucket[project_count_field] += 1
    bucket[project_cost_field] += project_cost


def finalize_bucket(base, bucket, project_type_fields):
    output = dict(base)
    output["abemis_total_projects"] = str(bucket["abemis_total_projects"])
    output["abemis_total_cost"] = format_number(bucket["abemis_total_cost"])
    output["abemis_total_quantity"] = format_number(bucket["abemis_total_quantity"])
    output["abemis_avg_cost_per_project"] = format_number(
        bucket["abemis_total_cost"] / bucket["abemis_total_projects"]
        if bucket["abemis_total_projects"] else 0
    )
    output["abemis_latest_year"] = str(bucket["abemis_latest_year"] or "")
    output["abemis_dominant_project_type"] = bucket["project_type_counts"].most_common(1)[0][0] if bucket["project_type_counts"] else ""
    output["abemis_dominant_project_group"] = bucket["project_group_counts"].most_common(1)[0][0] if bucket["project_group_counts"] else ""
    output["abemis_banner_programs"] = " | ".join(sorted(v for v in bucket["banner_programs"] if v))
    output["abemis_project_types"] = " | ".join(sorted(v for v in bucket["project_types"] if v))
    for field in GROUP_FIELD_ORDER:
        output[field] = format_number(bucket[field]) if field.endswith("_cost") else str(bucket[field])
    for field in project_type_fields:
        output[field] = str(bucket[field])
    return output


def summarize(details, project_type_fields):
    municipal = {}
    barangay = {}

    def new_bucket():
        return defaultdict(int, {
            "abemis_total_projects": 0,
            "abemis_total_cost": 0.0,
            "abemis_total_quantity": 0.0,
            "abemis_latest_year": 0,
            "project_type_counts": Counter(),
            "project_group_counts": Counter(),
            "banner_programs": set(),
            "project_types": set(),
        })

    for row in details:
        mun_key = (row["province"], row["municipality"])
        if mun_key not in municipal:
            municipal[mun_key] = {
                "base": {
                    "province": row["province"],
                    "district": row["district"],
                    "municipality": row["municipality"],
                },
                "bucket": new_bucket(),
            }
        add_to_bucket(municipal[mun_key]["bucket"], row)

        brgy_key = (row["province"], row["municipality"], row["barangay"])
        if brgy_key not in barangay:
            barangay[brgy_key] = {
                "base": {
                    "province": row["province"],
                    "district": row["district"],
                    "municipality": row["municipality"],
                    "barangay": row["barangay"],
                    "ADM4_PCODE": row["ADM4_PCODE"],
                    "ADM3_PCODE": row["ADM3_PCODE"],
                    "ADM2_PCODE": row["ADM2_PCODE"],
                },
                "bucket": new_bucket(),
            }
        add_to_bucket(barangay[brgy_key]["bucket"], row)

    municipal_rows = [
        finalize_bucket(item["base"], item["bucket"], project_type_fields)
        for item in municipal.values()
    ]
    barangay_rows = [
        finalize_bucket(item["base"], item["bucket"], project_type_fields)
        for item in barangay.values()
    ]
    municipal_rows.sort(key=lambda row: (row["province"], row["municipality"]))
    barangay_rows.sort(key=lambda row: (row["province"], row["municipality"], row["barangay"]))
    return municipal_rows, barangay_rows


def facility_rows(details):
    return [
        {
            "facility_id": row["project_id"],
            "facility_name": row["project_title"] or row["project_type"],
            "facility_type": row["project_group_key"].upper(),
            "province": row["province"],
            "district": row["district"],
            "municipality": row["municipality"],
            "barangay": row["barangay"],
            "latitude": "",
            "longitude": "",
            "status": row["banner_program"],
            "capacity": row["quantity"],
            "service_area_ha": "",
            "project_amount": row["project_cost"],
            "year_constructed": row["year_funded"],
            "farmer_beneficiaries": "",
            "banner_program": row["banner_program"],
            "remarks": f"Project Group: {row['project_group']} | Project Type: {row['project_type']} | Beneficiary: {row['beneficiary']}",
        }
        for row in details
    ]


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_metadata(path, source, details, project_types):
    stat = source.stat()
    metadata = {
        "dataset_name": "ABEMIS Infrastructure Inventory",
        "source": str(source),
        "as_of": "2026-03-30",
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source_file_size_bytes": stat.st_size,
        "source_file_modified_at": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds"),
        "project_rows": len(details),
        "project_type_count": len(project_types),
        "project_groups": [
            {
                "key": key,
                "label": group["label"],
                "project_count_field": group["fields"][0],
                "cost_field": group["fields"][1],
            }
            for key, group in PROJECT_GROUPS.items()
        ],
        "barangay_matched_rows": sum(1 for row in details if row["match_status"] == "barangay_matched"),
        "barangay_unmatched_rows": sum(1 for row in details if row["match_status"] != "barangay_matched"),
        "project_type_fields": [
            {"field": key, "label": label}
            for key, label in sorted(project_types.items(), key=lambda item: item[1])
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main():
    default_source = Path(r"C:\Users\Jeff Factora\Downloads\2026\PIP\ABEMIS_Infra_Inventory_as-of_Mar-30-2026.xlsx")
    source = Path(sys.argv[1]) if len(sys.argv) > 1 else default_source
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data")
    municipal_csv = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("data/municipal_data.csv")
    barangay_geojson = Path(sys.argv[4]) if len(sys.argv) > 4 else Path("data/barangay_boundaries.geojson")

    details, project_types = extract_rows(source, municipal_csv, barangay_geojson)
    project_type_fields = sorted(project_types)
    municipal_rows, barangay_rows = summarize(details, project_type_fields)
    facilities = facility_rows(details)

    write_csv(output_dir / "abemis_municipal_summary.csv", municipal_rows, SUMMARY_BASE_FIELDS + GROUP_FIELD_ORDER + project_type_fields)
    write_csv(output_dir / "abemis_barangay_summary.csv", barangay_rows, BARANGAY_BASE_FIELDS + GROUP_FIELD_ORDER + project_type_fields)
    write_csv(output_dir / "abemis_projects.csv", details, DETAIL_FIELDS)
    write_csv(output_dir / "abemis_facilities.csv", facilities, [
        "facility_id",
        "facility_name",
        "facility_type",
        "province",
        "district",
        "municipality",
        "barangay",
        "latitude",
        "longitude",
        "status",
        "capacity",
        "service_area_ha",
        "project_amount",
        "year_constructed",
        "farmer_beneficiaries",
        "banner_program",
        "remarks",
    ])
    metadata = write_metadata(output_dir / "abemis_metadata.json", source, details, project_types)

    print(f"Wrote {len(municipal_rows)} ABEMIS municipal summary rows")
    print(f"Wrote {len(barangay_rows)} ABEMIS barangay summary rows")
    print(f"Wrote {len(details)} ABEMIS project detail rows")
    print(f"Barangay matches: {metadata['barangay_matched_rows']} matched, {metadata['barangay_unmatched_rows']} unmatched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
