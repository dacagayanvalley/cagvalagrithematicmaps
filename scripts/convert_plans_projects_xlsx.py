import csv
import json
import re
import shutil
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path


NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

SUMMARY_FIELDS = [
    "province",
    "municipality",
    "plans_projects_2025_count",
    "plans_projects_2025_budget",
    "plans_projects_2026_count",
    "plans_projects_2026_budget",
    "plans_projects_2027_count",
    "plans_projects_2027_budget",
    "plans_projects_total_count",
    "plans_projects_total_budget",
    "plans_projects_2027_physical_target",
    "plans_rice_2027_budget",
    "plans_corn_2027_budget",
    "plans_hvc_2027_budget",
    "plans_fmr_2027_count",
    "plans_fmr_2027_budget",
    "plans_fmr_2027_length_km",
    "plans_irrigation_2027_count",
    "plans_irrigation_2027_budget",
    "plans_2027_programs",
    "plans_source_files",
]

DETAIL_FIELDS = [
    "source_file",
    "sheet",
    "province",
    "district",
    "municipality",
    "year",
    "program",
    "activity",
    "unit",
    "physical_target",
    "budget",
    "length_km",
    "allocation_method",
    "source_note",
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
    text = clean_text(value)
    if not text or text in {"-", "#REF!", "#DIV/0!"}:
        return 0.0
    text = text.replace(",", "")
    text = re.sub(r"[^\d.\-]", "", text)
    if text in {"", "-", "."}:
        return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def format_number(value):
    return f"{value:.2f}"


def normalize_key(value):
    text = unicodedata.normalize("NFKD", clean_text(value))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.upper()
    text = text.replace("CITY OF ILAGAN", "ILAGAN CITY")
    text = text.replace("CITY OF CAUAYAN", "CAUAYAN CITY")
    text = text.replace("CITY OF SANTIAGO", "SANTIAGO CITY")
    text = text.replace("STA.", "SANTA")
    text = text.replace("STA ", "SANTA ")
    text = text.replace("(CAPITAL)", "")
    return re.sub(r"[^A-Z0-9]", "", text)


def normalize_district_code(value, province=""):
    text = normalize_key(value)
    province_key = normalize_key(province)
    if not text:
        return ""
    if "LONE" in text or text == province_key:
        return "LONE"
    roman = re.search(r"\b(I|II|III|IV|V|VI)\b", clean_text(value).upper())
    if roman:
        return {"I": "1", "II": "2", "III": "3", "IV": "4", "V": "5", "VI": "6"}[roman.group(1)]
    ordinal = re.search(r"(\d+)(ST|ND|RD|TH)?", text)
    if ordinal:
        return ordinal.group(1)
    return text


def district_lookup_key(province, district):
    return (normalize_key(province), normalize_district_code(district, province))


def read_shared_strings(archive):
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []
    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    values = []
    for item in root.findall("a:si", NS):
        values.append("".join((text.text or "") for text in item.findall(".//a:t", NS)))
    return values


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


def load_municipalities(path):
    municipalities = {}
    by_province = defaultdict(dict)
    by_district = defaultdict(dict)
    with Path(path).open(newline="", encoding="utf-8-sig") as file:
        for row in csv.DictReader(file):
            province = clean_text(row.get("province"))
            municipality = clean_text(row.get("municipality"))
            if not province or not municipality:
                continue
            key = normalize_key(municipality)
            district = clean_text(row.get("district"))
            municipalities[key] = {"province": province, "municipality": municipality}
            by_province[normalize_key(province)][key] = municipality
            by_district[district_lookup_key(province, district)][key] = municipality

    aliases = {
        "STAANA": "SANTAANA",
        "STAANACAGAYAN": "SANTAANA",
        "STA.TERESITA": "SANTATERESITA",
        "STATERESITA": "SANTATERESITA",
        "LALLO": "LALLO",
        "ILAGAN": "ILAGANCITY",
        "CITYOFILAGAN": "ILAGANCITY",
        "TUGUEGARAO": "TUGUEGARAOCITY",
        "CITYOFTUGUEGARAO": "TUGUEGARAOCITY",
        "CAUAYAN": "CAUAYANCITY",
        "CITYOFCAUAYAN": "CAUAYANCITY",
        "SANTIAGO": "SANTIAGOCITY",
        "CITYOFSANTIAGO": "SANTIAGOCITY",
    }
    return municipalities, by_province, by_district, aliases


def match_direct_municipality(value, province_key, by_province, aliases):
    key = normalize_key(value)
    key = aliases.get(key, key)
    if key in by_province.get(province_key, {}):
        return key
    return None


def find_municipalities(text, province_key, by_province, aliases):
    normalized = normalize_key(text)
    if not normalized:
        return []

    found = []
    province_muns = by_province.get(province_key, {})
    for key in province_muns:
        if key and key in normalized:
            found.append(key)

    for alias, canonical in aliases.items():
        if alias in normalized and canonical in province_muns:
            found.append(canonical)

    return sorted(set(found), key=lambda key: len(key), reverse=True)


def workbook_province(filename, rows):
    text = filename.upper()
    if "BATANES" in text:
        return "Batanes"
    if "CAGAYAN" in text:
        return "Cagayan"
    if "ISABELA" in text:
        return "Isabela"
    if "NUEVA" in text:
        return "Nueva Vizcaya"
    if "QUIRINO" in text:
        return "Quirino"
    for row in rows[:12]:
        joined = " ".join(row).upper()
        match = re.search(r"PROVINCE:\s*([A-Z ]+)", joined)
        if match:
            return clean_text(match.group(1)).title()
    return ""


def workbook_district(rows):
    for row in rows[:12]:
        joined = " ".join(row)
        match = re.search(r"DISTRICT:\s*([A-Za-z0-9IVX ]+)", joined, flags=re.I)
        if match:
            return clean_text(match.group(1))
    return ""


def classify_program(sheet_name, rows):
    haystack = " ".join([sheet_name] + [" ".join(row[:4]) for row in rows[:6]]).upper()
    if "RICE" in haystack:
        return "Rice Program"
    if "CORN" in haystack:
        return "Corn Program"
    if "HIGH VALUE" in haystack or "HVCD" in haystack:
        return "High Value Crops"
    if "FARM-TO-MARKET" in haystack or re.search(r"\bFMR\b", haystack):
        return "Farm-to-Market Roads"
    if "PRDP" in haystack or "PHILIPPINE RURAL" in haystack:
        return "PRDP"
    if "4K" in haystack or "KABUHAYAN" in haystack:
        return "4Ks"
    if "SOIL HEALTH" in haystack or "NSHP" in haystack:
        return "National Soil Health"
    if "MCRA" in haystack:
        return "MCRA"
    return clean_text(sheet_name) or "Other Program"


def is_infra_program(program, activity):
    text = f"{program} {activity}".upper()
    return any(term in text for term in ["FMR", "FARM-TO-MARKET", "ROAD", "PRDP"])


def is_irrigation_program(activity):
    text = activity.upper()
    return any(term in text for term in ["IRRIGATION", "PUMP", "SOLAR-POWERED", "CANAL", "DIVERSION DAM"])


def is_dedicated_hvcdp_file(path):
    name = normalize_key(Path(path).stem)
    return "FY2027HVCDP" in name or name == "HVCDP2027"


def sheet_2027_columns(rows):
    header_rows = rows[5:15]
    start = None
    end = None

    for row in header_rows:
        for idx, value in enumerate(row):
            if "FY 2027" in clean_text(value).upper():
                start = idx if start is None else min(start, idx)

    if start is None:
        return None

    for row in header_rows:
        for idx, value in enumerate(row):
            text = clean_text(value).upper()
            if idx > start and ("REMARK" in text or re.search(r"\bFY\s*20(2[89]|3\d)\b", text)):
                end = idx if end is None else min(end, idx)

    if end is None:
        end = start + 8

    physical_cols = []
    budget_cols = []
    for row in header_rows:
        for idx in range(start, min(end, len(row))):
            text = clean_text(row[idx]).upper()
            if "PHYSICAL" in text:
                physical_cols.append(idx)
            if "BUDGET" in text:
                budget_cols.append(idx)

    if not physical_cols and not budget_cols:
        physical_cols = list(range(start, end, 2))
        budget_cols = list(range(start + 1, end, 2))

    return {
        "physical_cols": sorted(set(physical_cols)),
        "budget_cols": sorted(set(budget_cols)),
    }


def value_from_columns(cells, cols):
    if not cols:
        return 0.0
    total_col = cols[-1]
    total_value = to_number(cells[total_col]) if total_col < len(cells) else 0.0
    if total_value:
        return total_value
    tier_cols = cols[:-1] or cols
    return sum(to_number(cells[col]) for col in tier_cols if col < len(cells))


def fy2027_values(cells, columns):
    if columns:
        physical = value_from_columns(cells, columns["physical_cols"])
        budget = value_from_columns(cells, columns["budget_cols"])
        if physical or budget:
            return physical, budget

    physical = to_number(cells[10]) or to_number(cells[6]) + to_number(cells[8])
    budget = to_number(cells[11]) or to_number(cells[7]) + to_number(cells[9])
    if not physical and not budget:
        physical = to_number(cells[6]) or to_number(cells[8])
        budget = to_number(cells[7]) or to_number(cells[9])
    return physical, budget


def all_municipalities_marker(text):
    normalized = normalize_key(text)
    return "ALLMUNICIPAL" in normalized or "ALLMUNICIP" in normalized


def province_from_sheet_name(sheet_name):
    key = normalize_key(sheet_name)
    provinces = {
        "BATANES": "Batanes",
        "CAGAYAN": "Cagayan",
        "ISABELA": "Isabela",
        "NUEVAVIZCAYA": "Nueva Vizcaya",
        "QUIRINO": "Quirino",
    }
    return provinces.get(key, "")


def hvcdp_district_blocks(rows, province, by_district):
    header = rows[4] + [""] * 64 if len(rows) > 4 else []
    blocks = []
    district_blocks = []

    for start in range(3, min(len(header), 64), 6):
        label = clean_text(header[start])
        label_key = normalize_key(label)
        if not label or label_key in {"PROVINCEWIDE", "REGIONWIDE"} or label_key.startswith("PROVINCE") and label_key != "PROVINCE":
            continue

        if label_key == "PROVINCE":
            district = "LONE"
        else:
            district = label.replace("DISTRICT", "").strip() or label

        total_budget = sum(to_number((row + [""] * 64)[start + 5]) for row in rows[9:])
        if total_budget <= 0:
            continue

        block = {
            "start": start,
            "label": label,
            "district": district,
            "targets": sorted(by_district.get(district_lookup_key(province, district), {})),
        }
        blocks.append(block)
        if label_key != "PROVINCE":
            district_blocks.append(block)

    return district_blocks or blocks[:1]


def is_hvcdp_detail_row(activity, unit):
    key = normalize_key(activity)
    if not key:
        return False
    skip_exact = {
        "OPERATIONS",
        "TECHNICALANDSUPPORTSEVICESPROGRAM",
        "TECHNICALANDSUPPORTSERVICESPROGRAM",
        "PRODUCTIONSUPPORTSERVICESSUBPROGRAM",
        "OUTCOMEINDICATORS",
        "OUTPUTINDICATORS",
        "INPUTINDICATORS",
        "RESEARCHANDDEVELOPMENTSUBPROGRAM",
        "AGRICULTURALMACHINERYEQUIPMENTFACILITESANDINFRASTRUCTUREPROGRAM",
        "AGRICULTURALMACHINERYEQUIPMENTANDFACILITIESSUPPORTSERVICESSUBPROGRAM",
        "IRRIGATIONNETWORKSERVICESSUBPROGRAM",
        "GRANDTOTAL",
    }
    skip_contains = [
        "DISTRIBUTION",
        "ESTABLISHMENT",
        "SUPPORTSERVICES",
        "ACTIVITIES",
        "BENEFICIARIESRATING",
        "DELIVERIESOF",
        "LGUSASSISTED",
    ]
    if key in skip_exact:
        return False
    if not clean_text(unit):
        return key.startswith("CONDUCT") or key.startswith("OTHERPROFESSIONALSERVICES")
    if not clean_text(unit) and any(term in key for term in skip_contains):
        return False
    return True


def is_hvcdp_context_heading(activity, unit):
    key = normalize_key(activity)
    if clean_text(unit) or not key:
        return False
    skip = {
        "OPERATIONS",
        "TECHNICALANDSUPPORTSEVICESPROGRAM",
        "TECHNICALANDSUPPORTSERVICESPROGRAM",
        "PRODUCTIONSUPPORTSERVICESSUBPROGRAM",
        "OUTCOMEINDICATORS",
        "OUTPUTINDICATORS",
        "INPUTINDICATORS",
        "GRANDTOTAL",
    }
    return key not in skip


def contextual_hvcdp_activity(activity, context):
    key = normalize_key(activity)
    generic = {
        "PROCURED",
        "PRODUCED",
        "DISTRIBUTED",
        "AREAPLANTED",
        "BENEFICIARIES",
        "SERVICEAREA",
        "NEW",
        "CONTINUING",
    }
    if context and key in generic:
        return f"{context} - {activity}"
    return activity


def is_hvcdp_aggregate_generic_detail(activity, context):
    activity_key = normalize_key(activity)
    context_key = normalize_key(context)
    generic = {
        "PROCURED",
        "PRODUCED",
        "DISTRIBUTED",
        "AREAPLANTED",
        "BENEFICIARIES",
        "SERVICEAREA",
    }
    aggregate_context = [
        "DISTRIBUTION",
        "ESTABLISHMENT",
        "SUPPORTSERVICES",
        "ACTIVITIES",
        "SUBPROGRAM",
    ]
    return activity_key in generic and any(term in context_key for term in aggregate_context)


def extract_dedicated_hvcdp_rows(path, sheets, by_district):
    details = []
    for sheet_name, rows in sheets:
        province = province_from_sheet_name(sheet_name)
        if not province:
            continue

        for block in hvcdp_district_blocks(rows, province, by_district):
            targets = block["targets"]
            if not targets:
                continue
            start = block["start"]
            district = block["district"]
            context = ""

            for row in rows[9:]:
                cells = row + [""] * 64
                activity = clean_text(cells[0])
                unit = clean_text(cells[1])
                if is_hvcdp_context_heading(activity, unit):
                    context = activity
                if not is_hvcdp_detail_row(activity, unit):
                    continue

                physical = to_number(cells[start])
                budget = to_number(cells[start + 5])
                if not physical and not budget:
                    continue
                if is_hvcdp_aggregate_generic_detail(activity, context):
                    continue

                divisor = len(targets)
                display_activity = contextual_hvcdp_activity(activity, context)
                for key in targets:
                    details.append({
                        "source_file": path.name,
                        "sheet": sheet_name,
                        "province": province,
                        "district": district,
                        "municipality": by_district[district_lookup_key(province, district)][key],
                        "year": 2027,
                        "program": "High Value Crops",
                        "activity": display_activity,
                        "unit": unit,
                        "physical_target": format_number(physical / divisor) if physical else "",
                        "budget": format_number(budget / divisor) if budget else "0.00",
                        "length_km": "",
                        "allocation_method": "district column municipalities split",
                        "source_note": f"{sheet_name} {block['label']} FY 2027 HVCDP district column",
                    })
    return details


def summarize_rows(files, municipal_csv):
    _, by_province, by_district, aliases = load_municipalities(municipal_csv)
    details = []
    unmatched = []
    has_dedicated_hvcdp = any(is_dedicated_hvcdp_file(path) for path in files)

    for path in files:
        sheets = read_workbook(path)
        if is_dedicated_hvcdp_file(path):
            details.extend(extract_dedicated_hvcdp_rows(path, sheets, by_district))
            continue

        province = ""
        province_key = ""
        for sheet_name, rows in sheets:
            if not province:
                province = workbook_province(path.name, rows)
                province_key = normalize_key(province)
            district = workbook_district(rows)
            program = classify_program(sheet_name, rows)
            if has_dedicated_hvcdp and program == "High Value Crops":
                continue
            columns_2027 = sheet_2027_columns(rows)
            current_year = None

            for row in rows:
                cells = row + [""] * (24 - len(row))
                joined = " ".join(cells).upper()
                if "FY 2025" in joined or "CY 2025" in joined:
                    current_year = 2025
                if "FY 2026" in joined:
                    current_year = 2026
                if "FY 2027" in joined:
                    current_year = 2027

                direct_key = match_direct_municipality(cells[0], province_key, by_province, aliases)
                if direct_key and not any(term in joined for term in ["TOTAL", "SUBTOTAL", "GRAND TOTAL"]):
                    municipality = by_province[province_key][direct_key]
                    amount = to_number(cells[4]) or to_number(cells[5]) or max(to_number(cell) for cell in cells[1:8])
                    length = to_number(cells[3])
                    details.append({
                        "source_file": path.name,
                        "sheet": sheet_name,
                        "province": province,
                        "district": district,
                        "municipality": municipality,
                        "year": current_year or 2027,
                        "program": program,
                        "activity": cells[2] or cells[0],
                        "unit": cells[1],
                        "physical_target": "",
                        "budget": format_number(amount),
                        "length_km": format_number(length) if length else "",
                        "allocation_method": "direct municipality row",
                        "source_note": cells[2] or cells[1],
                    })
                    continue

                if len(cells) < 12 or not cells[0] or any(term in joined for term in ["GRAND TOTAL", "PREPARED BY", "CONCURRED BY"]):
                    continue

                remarks = " ".join(cells[12:])
                targets = find_municipalities(remarks, province_key, by_province, aliases)
                is_all_district_municipalities = program == "High Value Crops" and all_municipalities_marker(remarks)
                if is_all_district_municipalities:
                    targets = sorted(by_district.get(district_lookup_key(province, district), {}))
                if not targets:
                    continue

                activity = cells[0]
                if activity.upper().startswith(("I.", "II.", "III.", "A.", "B.")):
                    continue

                physical_2027, budget_2027 = fy2027_values(cells, columns_2027)

                divisor = len(targets) or 1
                for key in targets:
                    municipality = by_province[province_key].get(key) or by_district[district_lookup_key(province, district)].get(key)
                    details.append({
                        "source_file": path.name,
                        "sheet": sheet_name,
                        "province": province,
                        "district": district,
                        "municipality": municipality,
                        "year": 2027,
                        "program": program,
                        "activity": activity,
                        "unit": cells[1],
                        "physical_target": format_number(physical_2027 / divisor) if physical_2027 else "",
                        "budget": format_number(budget_2027 / divisor) if budget_2027 else "0.00",
                        "length_km": "",
                        "allocation_method": "all district municipalities split" if is_all_district_municipalities else "remarks municipality split",
                        "source_note": remarks,
                    })

                for token in re.split(r"[,;\n]| and ", remarks, flags=re.I):
                    token = clean_text(token)
                    if all_municipalities_marker(token):
                        continue
                    if token and not find_municipalities(token, province_key, by_province, aliases):
                        if re.search(r"[A-Za-z]{4,}", token):
                            unmatched.append({
                                "source_file": path.name,
                                "sheet": sheet_name,
                                "province": province,
                                "text": token,
                            })

    return details, unmatched


def aggregate(details):
    summary = defaultdict(lambda: {
        "plans_projects_2025_count": 0,
        "plans_projects_2025_budget": 0.0,
        "plans_projects_2026_count": 0,
        "plans_projects_2026_budget": 0.0,
        "plans_projects_2027_count": 0,
        "plans_projects_2027_budget": 0.0,
        "plans_projects_2027_physical_target": 0.0,
        "plans_rice_2027_budget": 0.0,
        "plans_corn_2027_budget": 0.0,
        "plans_hvc_2027_budget": 0.0,
        "plans_fmr_2027_count": 0,
        "plans_fmr_2027_budget": 0.0,
        "plans_fmr_2027_length_km": 0.0,
        "plans_irrigation_2027_count": 0,
        "plans_irrigation_2027_budget": 0.0,
        "programs": set(),
        "sources": set(),
    })

    for row in details:
        if not row["municipality"]:
            continue
        key = (row["province"], row["municipality"])
        bucket = summary[key]
        year = int(row["year"] or 0)
        budget = to_number(row["budget"])
        physical = to_number(row["physical_target"])
        length = to_number(row["length_km"])
        program = row["program"]
        activity = row["activity"]

        if year in {2025, 2026, 2027}:
            bucket[f"plans_projects_{year}_count"] += 1
            bucket[f"plans_projects_{year}_budget"] += budget
        if year == 2027:
            bucket["plans_projects_2027_physical_target"] += physical
            bucket["programs"].add(program)
            if program == "Rice Program":
                bucket["plans_rice_2027_budget"] += budget
            if program == "Corn Program":
                bucket["plans_corn_2027_budget"] += budget
            if program == "High Value Crops":
                bucket["plans_hvc_2027_budget"] += budget
            if is_infra_program(program, activity):
                bucket["plans_fmr_2027_count"] += 1
                bucket["plans_fmr_2027_budget"] += budget
                bucket["plans_fmr_2027_length_km"] += length
            if is_irrigation_program(activity):
                bucket["plans_irrigation_2027_count"] += 1
                bucket["plans_irrigation_2027_budget"] += budget
        bucket["sources"].add(row["source_file"])

    rows = []
    for (province, municipality), data in sorted(summary.items()):
        total_count = data["plans_projects_2025_count"] + data["plans_projects_2026_count"] + data["plans_projects_2027_count"]
        total_budget = data["plans_projects_2025_budget"] + data["plans_projects_2026_budget"] + data["plans_projects_2027_budget"]
        output = {
            "province": province,
            "municipality": municipality,
            "plans_projects_total_count": total_count,
            "plans_projects_total_budget": format_number(total_budget),
            "plans_2027_programs": " | ".join(sorted(data["programs"])),
            "plans_source_files": " | ".join(sorted(data["sources"])),
        }
        for field in SUMMARY_FIELDS:
            if field in {"province", "municipality", "plans_projects_total_count", "plans_projects_total_budget", "plans_2027_programs", "plans_source_files"}:
                continue
            value = data.get(field, 0)
            output[field] = str(value) if "count" in field else format_number(value)
        rows.append(output)
    return rows


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_metadata(path, source_dir, source_files, summary_count, detail_count):
    generated_at = datetime.now().astimezone().isoformat(timespec="seconds")
    files = []
    latest_mtime = None
    for source in source_files:
        stat = source.stat()
        modified = datetime.fromtimestamp(stat.st_mtime).astimezone()
        latest_mtime = max(latest_mtime, modified) if latest_mtime else modified
        files.append({
            "name": source.name,
            "size_bytes": stat.st_size,
            "local_modified_at": modified.isoformat(timespec="seconds"),
        })

    metadata = {
        "dataset_name": "DA Region 02 Plans and Projects 2025-2027",
        "source": "Google Drive planning workbooks",
        "source_folder_url": "https://drive.google.com/drive/folders/1mOY40xTSz2KGzj4mLOAkhIEptkKnlVr9?usp=sharing",
        "generated_at": generated_at,
        "latest_source_file_modified_at": latest_mtime.isoformat(timespec="seconds") if latest_mtime else generated_at,
        "source_file_count": len(source_files),
        "summary_rows": summary_count,
        "detail_rows": detail_count,
        "source_directory": str(source_dir),
        "source_files": files,
    }

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def safe_version_id(value):
    text = clean_text(value)
    text = text.replace(":", "").replace("+", "-").replace("\\", "-").replace("/", "-")
    return re.sub(r"[^0-9A-Za-zT._-]", "-", text)


def relative_posix(path):
    return path.as_posix()


def write_version_snapshot(output, detail_output, metadata_output, unmatched_output, metadata):
    version_root = Path("data/plans_versions")
    version_id = safe_version_id(metadata.get("generated_at")) or datetime.now().strftime("%Y%m%dT%H%M%S")
    version_dir = version_root / version_id
    version_dir.mkdir(parents=True, exist_ok=True)

    snapshot_files = {
        "summary_url": version_dir / output.name,
        "detail_url": version_dir / detail_output.name,
        "metadata_url": version_dir / metadata_output.name,
        "unmatched_url": version_dir / unmatched_output.name,
    }

    shutil.copy2(output, snapshot_files["summary_url"])
    shutil.copy2(detail_output, snapshot_files["detail_url"])
    shutil.copy2(metadata_output, snapshot_files["metadata_url"])
    if unmatched_output.exists():
        shutil.copy2(unmatched_output, snapshot_files["unmatched_url"])

    manifest_path = version_root / "manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            manifest = {}
    else:
        manifest = {}

    versions = [
        item for item in manifest.get("versions", [])
        if item.get("id") != version_id
    ]
    versions.append({
        "id": version_id,
        "label": metadata.get("generated_at", version_id),
        "generated_at": metadata.get("generated_at"),
        "latest_source_file_modified_at": metadata.get("latest_source_file_modified_at"),
        "source_file_count": metadata.get("source_file_count", 0),
        "summary_rows": metadata.get("summary_rows", 0),
        "detail_rows": metadata.get("detail_rows", 0),
        "summary_url": relative_posix(snapshot_files["summary_url"]),
        "detail_url": relative_posix(snapshot_files["detail_url"]),
        "metadata_url": relative_posix(snapshot_files["metadata_url"]),
        "unmatched_url": relative_posix(snapshot_files["unmatched_url"]),
    })
    versions.sort(key=lambda item: item.get("generated_at") or item.get("id") or "", reverse=True)

    manifest = {
        "latest_version_id": versions[0]["id"] if versions else version_id,
        "versions": versions,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main():
    source_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data/plans_raw")
    output = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("data/plans_projects_2025_2027.csv")
    detail_output = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("data/plans_projects_2025_2027_details.csv")
    municipal_csv = Path(sys.argv[4]) if len(sys.argv) > 4 else Path("data/municipal_data.csv")
    metadata_output = Path("data/plans_projects_metadata.json")
    unmatched_output = Path("data/plans_projects_unmatched_terms.csv")

    files = sorted(source_dir.glob("*.xlsx"))
    if not files:
        print(f"No .xlsx files found in {source_dir}")
        return 1

    details, unmatched = summarize_rows(files, municipal_csv)
    summary = aggregate(details)
    write_csv(output, summary, SUMMARY_FIELDS)
    write_csv(detail_output, details, DETAIL_FIELDS)
    write_csv(unmatched_output, unmatched, ["source_file", "sheet", "province", "text"])
    metadata = write_metadata(metadata_output, source_dir, files, len(summary), len(details))
    write_version_snapshot(output, detail_output, metadata_output, unmatched_output, metadata)

    print(f"Wrote {len(summary)} municipal planning rows to {output}")
    print(f"Wrote {len(details)} extracted planning detail rows to {detail_output}")
    print(f"Wrote planning metadata to {metadata_output}")
    print(f"Wrote {len(unmatched)} unmatched terms to {unmatched_output}")
    print("Archived this refresh in data/plans_versions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
