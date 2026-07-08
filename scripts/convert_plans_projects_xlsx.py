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
    "commodity",
    "office_function",
    "tier_1",
    "tier_2",
    "result_level",
    "pap_type",
    "prexc_program",
    "prexc_subprogram",
    "indicator_id",
    "indicator_level_1",
    "indicator_level_2",
    "indicator_level_3",
    "indicator_specify_type",
    "indicator_match_basis",
    "result_chain",
    "data_structure_note",
    "activity",
    "activity_context",
    "original_activity",
    "unit",
    "physical_target",
    "budget",
    "original_physical_target",
    "original_budget",
    "target_count",
    "target_scope",
    "length_km",
    "allocation_method",
    "source_row",
    "source_note",
]

ALL_PROGRAMS_FILE_KEY = "ALLPROGRAMS2027"
PRESERVE_LEGACY_2027_PROGRAMS = {
    "Farm-to-Market Roads",
    "4Ks",
    "PRDP",
    "SAAD",
    "National Soil Health",
    "HALAL",
}

PROGRAM_BY_SHEET = {
    "IES": "Rice Program",
    "SCRCSEEDSYSTEMHIGHIMPACT": "Research and Development (R4)",
    "RICE": "Rice Program",
    "CORN": "Corn Program",
    "HVCDP": "High Value Crops",
    "HVCDPEXPORT": "High Value Crops",
    "HVCDPCOFFEE": "High Value Crops",
    "LIVESTOCK": "LIVESTOCK",
    "OAP": "OAP",
    "NUPAP": "NUPAP",
    "4KS": "4Ks",
    "SAAD": "SAAD",
    "MCRA": "MCRA",
    "F2C2": "F2C2",
}

COMMODITY_BY_SHEET = {
    "IES": "Rice Seed System",
    "SCRCSEEDSYSTEMHIGHIMPACT": "Rice and Vegetable Seed System",
    "RICE": "Rice",
    "CORN": "Corn",
    "HVCDP": "Legumes, Spices, Vegetable, Bamboo",
    "HVCDPEXPORT": "Ube, Dragon Fruit, Okra, Banana",
    "HVCDPCOFFEE": "Coffee",
    "LIVESTOCK": "Livestock",
    "OAP": "Organic Agriculture",
    "NUPAP": "Urban and Peri-Urban Agriculture",
    "4KS": "4Ks",
    "SAAD": "SAAD",
    "MCRA": "MCRA",
    "F2C2": "F2C2",
}

FUNCTION_ALIASES = {
    "PSS": ("Technical Support Services", "Production Support Services"),
    "PRODUCTIONSUPPORTSERVICES": ("Technical Support Services", "Production Support Services"),
    "PRODUCTIONSUPPORTSERVICESSUBPROGRAM": ("Technical Support Services", "Production Support Services"),
    "ESETS": ("Technical Support Services", "Extension Support, Education and Training Services"),
    "EXTENSIONSUPPORTEDUCATIONANDTRAINING": ("Technical Support Services", "Extension Support, Education and Training Services"),
    "EXTENSIONSUPPORTEDUCATIONANDTRAININGSERVICES": ("Technical Support Services", "Extension Support, Education and Training Services"),
    "MARKETDEVELOPMENTSERVICES": ("Other Functions", "Market Development Services"),
    "MARKETLINKAGEANDFACILITATION": ("Other Functions", "Market Development Services"),
    "R4": ("Other Functions", "Research and Development (R4)"),
    "RESEARCHANDDEVELOPMENT": ("Other Functions", "Research and Development (R4)"),
    "AMEFS": ("Other Functions", "AMEFIP"),
    "AMEFIP": ("Other Functions", "AMEFIP"),
    "INS": ("Other Functions", "AMEFIP"),
    "IRRIGATIONNETWORKSERVICES": ("Other Functions", "AMEFIP"),
    "REGULATORYSERVICES": ("Other Functions", "Regulatory Services"),
}

REFERENCE_RESULT_CHAIN = {
    "outcomes": "Long/medium-term and sector outcomes are tracked through PDP, NAFMIP, AFMP, commodity roadmaps, and program/project logframes.",
    "outputs": "Operational results are immediate program/project outputs reported against GAA, OPIF/PREXC, and program commitments.",
    "pap": "Programs group projects and activities; projects are time-bound schemes, while activities deliver specific outputs supporting a program or project.",
    "indicators": "Performance indicators measure quantity, quality, timeliness, or cost and are grouped by PREXC Program, PREXC Sub-Program, and PI Level 1-3.",
}

PROGRAM_INDICATOR_SHEETS = {
    "Rice Program": "NRP",
    "Corn Program": "NCP",
    "High Value Crops": "HVCDP",
    "LIVESTOCK": "NLP",
    "OAP": "NOAP",
    "NUPAP": "NUPAP",
    "HALAL": "HALAL",
}

INDICATOR_RULES = [
    {"keywords": ["SEED", "SEEDLING", "PLANTING MATERIAL"], "unit_keywords": ["KG", "BAG", "PACK", "SACHET", "NUMBER", "PIECE"], "indicator_id": "", "level_1": "Seeds and planting materials distributed", "level_2": "Seeds/seedlings/planting materials distributed", "level_3": "Seeds and planting materials distributed"},
    {"keywords": ["FERTILIZER", "SOIL AMELIORANT", "BIOFERTILIZER", "COMPOST"], "unit_keywords": ["KG", "BAG", "LITER", "GALLON", "SACK"], "indicator_id": "PSS046", "level_1": "Agri-chemicals distributed", "level_2": "Agri-chemicals distributed Solid", "level_3": "Agri-chemicals distributed_kg"},
    {"keywords": ["PESTICIDE", "INSECTICIDE", "FUNGICIDE", "HERBICIDE", "CHEMICAL", "PHEROMONE"], "unit_keywords": ["LITER", "GALLON", "KG", "PACK", "PIECE"], "indicator_id": "PSS047", "level_1": "Agri-chemicals distributed", "level_2": "Agri-chemicals distributed Liquid/Solid", "level_3": "Agri-chemicals distributed by unit"},
    {"keywords": ["ANIMAL", "CATTLE", "CARABAO", "GOAT", "SHEEP", "SWINE", "CHICKEN", "DUCK", "BEE"], "unit_keywords": ["HEAD", "NUMBER"], "indicator_id": "PSS002", "level_1": "Animals distributed", "level_2": "Livestock/poultry distributed", "level_3": "Animals distributed by type"},
    {"keywords": ["MACHIN", "EQUIPMENT", "FACILITY", "GREENHOUSE", "POSTHARVEST", "POST-HARVEST", "PROCESSING"], "unit_keywords": ["UNIT", "SET", "NUMBER"], "indicator_id": "", "level_1": "Production and postharvest facilities provided", "level_2": "Facilities, machinery, and equipment provided", "level_3": "Facilities/machinery/equipment provided"},
    {"keywords": ["TRAINING", "CAPACITY", "SCHOOL", "FARMER FIELD", "CONDUCT OF"], "unit_keywords": ["BATCH", "NUMBER", "PERSON", "PARTICIPANT"], "indicator_id": "", "level_1": "Training and extension services provided", "level_2": "Training/learning events conducted", "level_3": "Participants or events served"},
    {"keywords": ["FMR", "FARM-TO-MARKET", "ROAD", "CONCRETING", "BRIDGE"], "unit_keywords": ["KM", "KILOMETER", "METER"], "indicator_id": "", "level_1": "Infrastructure projects completed", "level_2": "Farm-to-market roads constructed/rehabilitated", "level_3": "FMR length or project count"},
    {"keywords": ["IRRIGATION", "PUMP", "CANAL", "DIVERSION DAM", "SWIP", "SOLAR-POWERED"], "unit_keywords": ["UNIT", "HA", "KM", "NUMBER"], "indicator_id": "", "level_1": "Irrigation support provided", "level_2": "Irrigation facilities constructed/rehabilitated", "level_3": "Irrigation facility, area, or length"},
    {"keywords": ["MARKET", "LINKAGE", "PROMOTION", "TRADE FAIR", "KADIWA"], "unit_keywords": ["NUMBER", "EVENT", "GROUP"], "indicator_id": "", "level_1": "Market development services provided", "level_2": "Market linkage and promotion services provided", "level_3": "Market events/linkages/beneficiaries served"},
    {"keywords": ["RESEARCH", "STUDY", "TECHNOLOGY", "DEMO", "VALIDATION"], "unit_keywords": ["NUMBER", "PROJECT", "STUDY"], "indicator_id": "", "level_1": "Research and development services provided", "level_2": "Studies, technologies, and demonstrations conducted", "level_3": "R4 outputs completed"},
    {"keywords": ["SOIL", "MAP", "FERTILITY", "SAMPLE", "ANALYSIS"], "unit_keywords": ["NUMBER", "SAMPLE", "MAP", "HA"], "indicator_id": "", "level_1": "Soil health and fertility services provided", "level_2": "Soil tests/maps/interventions provided", "level_3": "Soil health outputs delivered"},
    {"keywords": ["MONITORING", "EVALUATION", "REPORT", "ASSESSMENT"], "unit_keywords": ["REPORT", "NUMBER", "STUDY"], "indicator_id": "", "level_1": "Monitoring and evaluation reports disseminated", "level_2": "Monitoring/evaluation studies or reports completed", "level_3": "M&E output completed"},
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
        "REYNAMERCEDES": "REINAMERCEDES",
        "TUMAINI": "TUMAUINI",
        "PEAABLANCA": "PEABLANCA",
        "PENABLANCA": "PEABLANCA",
        "NAGUILLAN": "NAGUILIAN",
        "STONINO": "SANTONIOFAIRE",
        "SANTONINO": "SANTONIOFAIRE",
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


def is_all_programs_file(path):
    return ALL_PROGRAMS_FILE_KEY in normalize_key(Path(path).stem)


def preserve_legacy_2027_program(program):
    return clean_text(program) in PRESERVE_LEGACY_2027_PROGRAMS


def default_detail_fields(row):
    defaults = {
        "commodity": "",
        "office_function": "",
        "tier_1": "",
        "tier_2": "",
        "activity_context": "",
        "original_activity": row.get("activity", ""),
        "original_physical_target": row.get("physical_target", ""),
        "original_budget": row.get("budget", ""),
        "target_count": "1",
        "target_scope": row.get("municipality", ""),
        "source_row": "",
        "source_note": "",
    }
    for key, value in defaults.items():
        row.setdefault(key, value)
    return row


def all_programs_sheet_key(sheet_name):
    return normalize_key(sheet_name)


def all_programs_sheet_program(sheet_name):
    key = all_programs_sheet_key(sheet_name)
    return PROGRAM_BY_SHEET.get(key, clean_text(sheet_name) or "Other Program")


def all_programs_sheet_commodity(sheet_name, rows):
    key = all_programs_sheet_key(sheet_name)
    for row in rows[:8]:
        text = " ".join(clean_text(cell) for cell in row[:4])
        match = re.search(r"COMMODITY:\s*(.+)", text, flags=re.I)
        if match:
            commodity = clean_text(match.group(1))
            if commodity:
                return commodity
    return COMMODITY_BY_SHEET.get(key, all_programs_sheet_program(sheet_name))


def normalize_all_programs_function(value, fallback=None):
    key = normalize_key(value)
    if key in FUNCTION_ALIASES:
        return FUNCTION_ALIASES[key]
    if fallback:
        return fallback
    return ("Technical Support Services", "Production Support Services")


def infer_prexc(row):
    text = normalize_key(" ".join([
        row.get("activity", ""),
        row.get("activity_context", ""),
        row.get("program", ""),
        row.get("source_note", ""),
    ]))
    tier_1 = clean_text(row.get("tier_1"))
    tier_2 = clean_text(row.get("tier_2") or row.get("office_function"))

    if not tier_1 or not tier_2:
        if any(term in text for term in ["TRAINING", "CAPACITY", "SCHOOL", "LEARNING"]):
            tier_1, tier_2 = "Technical Support Services", "Extension Support, Education and Training Services"
        elif any(term in text for term in ["MARKET", "LINKAGE", "PROMOTION", "KADIWA"]):
            tier_1, tier_2 = "Other Functions", "Market Development Services"
        elif any(term in text for term in ["RESEARCH", "STUDY", "TECHNOLOGY", "DEMO"]):
            tier_1, tier_2 = "Other Functions", "Research and Development (R4)"
        elif any(term in text for term in ["REGULATORY", "CERTIFICATION", "INSPECTION", "QUARANTINE"]):
            tier_1, tier_2 = "Other Functions", "Regulatory Services"
        elif any(term in text for term in ["FMR", "FARMTOMARKET", "ROAD", "IRRIGATION", "SWIP", "PUMP"]):
            tier_1, tier_2 = "Other Functions", "AMEFIP"
        else:
            tier_1, tier_2 = "Technical Support Services", "Production Support Services"

    return tier_1, tier_2


def infer_pap_type(row):
    program = clean_text(row.get("program"))
    activity = normalize_key(row.get("activity"))
    text = normalize_key(" ".join([program, row.get("activity", ""), row.get("source_note", "")]))
    if any(term in text for term in ["FMR", "FARMTOMARKET", "CONCRETING", "BRIDGE", "IRRIGATION", "SWIP", "DIVERSIONDAM", "PRDP"]):
        return "Project"
    if activity and any(term in activity for term in ["DISTRIBUT", "TRAINING", "CONDUCT", "PROCURE", "PROVID", "ESTABLISH", "MONITOR", "ASSESS"]):
        return "Activity"
    if program:
        return "Program"
    return "Activity"


def infer_result_level(row):
    text = normalize_key(" ".join([row.get("activity", ""), row.get("source_note", "")]))
    if any(term in text for term in ["OUTCOME", "IMPACT", "EVALUATIONSTUDY"]):
        return "Program/project outcome"
    return "Operational output"


def indicator_text(row):
    return normalize_key(" ".join([
        row.get("activity", ""),
        row.get("activity_context", ""),
        row.get("original_activity", ""),
        row.get("source_note", ""),
        row.get("unit", ""),
        row.get("commodity", ""),
    ]))


def match_indicator(row):
    text = indicator_text(row)
    unit_text = normalize_key(row.get("unit"))
    best = None
    best_score = 0
    best_hits = []
    for rule in INDICATOR_RULES:
        hits = [term for term in rule["keywords"] if normalize_key(term) in text]
        unit_hits = [term for term in rule.get("unit_keywords", []) if normalize_key(term) in unit_text]
        score = len(hits) * 2 + len(unit_hits)
        if score > best_score:
            best = rule
            best_score = score
            best_hits = hits + unit_hits
    if best:
        return {
            "indicator_id": best["indicator_id"],
            "indicator_level_1": best["level_1"],
            "indicator_level_2": best["level_2"],
            "indicator_level_3": best["level_3"],
            "indicator_match_basis": "Matched activity/unit terms: " + ", ".join(sorted(set(best_hits))),
        }

    activity = clean_text(row.get("activity") or row.get("source_note"))
    unit = clean_text(row.get("unit"))
    fallback = activity or clean_text(row.get("program")) or "Unclassified output"
    return {
        "indicator_id": "",
        "indicator_level_1": fallback,
        "indicator_level_2": fallback,
        "indicator_level_3": f"{fallback}_{unit}" if unit else fallback,
        "indicator_match_basis": "No direct indicator keyword match; grouped by extracted activity and unit.",
    }


def enrich_detail_row(row):
    row = default_detail_fields(row)
    tier_1, tier_2 = infer_prexc(row)
    row["tier_1"] = row.get("tier_1") or tier_1
    row["tier_2"] = row.get("tier_2") or tier_2
    row["office_function"] = row.get("office_function") or row["tier_2"]
    row["prexc_program"] = row.get("prexc_program") or row["tier_1"]
    row["prexc_subprogram"] = row.get("prexc_subprogram") or row["tier_2"]
    row["pap_type"] = row.get("pap_type") or infer_pap_type(row)
    row["result_level"] = row.get("result_level") or infer_result_level(row)

    match = match_indicator(row)
    for key, value in match.items():
        row[key] = row.get(key) or value
    row["indicator_specify_type"] = row.get("indicator_specify_type") or PROGRAM_INDICATOR_SHEETS.get(row.get("program"), "")
    row["result_chain"] = row.get("result_chain") or "Outcome framework -> PREXC/OPIF program -> PAP -> operational output -> performance indicator"
    row["data_structure_note"] = row.get("data_structure_note") or "Grouped using OPIF/PREXC guidance and the relevant-indicators workbook fields: PREXC Program, PREXC Sub-Program, PI Level 1, PI Level 2, PI Level 3, Unit."
    return row

def is_all_programs_heading(row):
    activity = clean_text((row + [""])[0])
    joined = normalize_key(" ".join(row[:4]))
    if not activity:
        return False
    if activity.startswith("Column "):
        return False
    if joined in FUNCTION_ALIASES:
        return True
    if to_number((row + [""] * 5)[4]) and not clean_text((row + [""] * 7)[6]):
        return True
    return False


def province_district_from_text(value, default_province=""):
    text = clean_text(value)
    key = normalize_key(text)
    provinces = {
        "BATANES": "Batanes",
        "CAGAYAN": "Cagayan",
        "ISABELA": "Isabela",
        "NUEVAVIZCAYA": "Nueva Vizcaya",
        "QUIRINO": "Quirino",
    }

    province = default_province
    for province_key, province_name in provinces.items():
        if province_key in key:
            province = province_name
            break

    district = ""
    district_match = re.search(r"(?:DISTRICT|D)\s*[- ]*(LONE|I{1,3}|IV|V?I|\d+)", text, flags=re.I)
    if not district_match:
        district_match = re.search(r"(\d+)(?:ST|ND|RD|TH)?\s+DISTRICT", text, flags=re.I)
    if district_match:
        district = district_match.group(1)
    elif province in {"Batanes", "Nueva Vizcaya", "Quirino"}:
        district = "LONE"
    elif "LONE" in key:
        district = "LONE"

    return province, normalize_district_code(district, province) or district


def split_location_terms(text):
    cleaned = clean_text(text)
    cleaned = re.sub(r"\b(Cagayan|Isabela|Nueva Vizcaya|Quirino|Batanes)\b", "", cleaned, flags=re.I)
    cleaned = cleaned.replace("/", ",")
    cleaned = cleaned.replace("&", ",")
    cleaned = re.sub(r"\band\b", ",", cleaned, flags=re.I)
    return [clean_text(token) for token in re.split(r"[,;]", cleaned) if clean_text(token)]


def all_program_targets(location, province, district, by_province, by_district, aliases):
    province_key = normalize_key(province)
    location_key = normalize_key(location)
    district_key = district_lookup_key(province, district)

    if location_key in {"REGION", "REGIONAL"}:
        location_key = "REGIONWIDE"

    if "REGIONWIDE" in location_key:
        targets = []
        for mun_map in by_province.values():
            targets.extend(mun_map.values())
        return sorted(set(targets))

    if "PROVINCEWIDE" in location_key or "ALLMUNICIPAL" in location_key or location_key == province_key:
        targets = by_province.get(province_key, {})
        if "EXCEPTCITY" in location_key:
            return sorted(value for key, value in targets.items() if "CITY" not in key)
        return sorted(set(targets.values()))

    if "DISTRICTWIDE" in location_key:
        district_targets = by_district.get(district_key, {})
        if district_targets:
            return sorted(set(district_targets.values()))
        return sorted(set(by_province.get(province_key, {}).values()))

    targets = []
    for token in split_location_terms(location):
        token_key = match_direct_municipality(token, province_key, by_province, aliases)
        if token_key:
            targets.append(by_province[province_key][token_key])
            continue
        found = find_municipalities(token, province_key, by_province, aliases)
        targets.extend(by_province[province_key][key] for key in found if key in by_province[province_key])

    if not targets:
        for key in find_municipalities(location, province_key, by_province, aliases):
            targets.append(by_province[province_key][key])

    return sorted(set(targets))


def contextual_activity(activity, context):
    activity = clean_text(activity)
    context = clean_text(context)
    if context and normalize_key(activity) in {"SEEDS", "LIQUIDFERTIZER", "LIQUIDFERTILIZER", "FERTILIZER"}:
        return f"{context} - {activity}"
    return activity


def extract_all_programs_rows(path, sheets, by_province, by_district, aliases):
    details = []
    unmatched = []

    for sheet_name, rows in sheets:
        program = all_programs_sheet_program(sheet_name)
        commodity = all_programs_sheet_commodity(sheet_name, rows)
        has_district_column = any(
            "PROVINCE AND DISTRICT" in clean_text(cell).upper()
            for row in rows[:10]
            for cell in row
        )
        district_idx = 2 if has_district_column else None
        physical_idx = 3 if has_district_column else 2
        budget_idx = 4 if has_district_column else 3
        location_idx = 6 if has_district_column else 5
        readiness_idx = 7 if has_district_column else 6
        kra_idx = 8 if has_district_column else 7
        alignment_idx = 13 if has_district_column else 12
        current_activity = ""
        current_description = ""
        current_context = ""
        current_function = normalize_all_programs_function("")

        for source_row, row in enumerate(rows[8:], start=9):
            cells = row + [""] * 14
            activity_cell = clean_text(cells[0])
            if not activity_cell or activity_cell.startswith("Column "):
                continue
            if activity_cell.startswith("(") and activity_cell.endswith(")"):
                continue

            if is_all_programs_heading(cells):
                maybe_function = normalize_all_programs_function(activity_cell, None)
                if normalize_key(activity_cell) in FUNCTION_ALIASES:
                    current_function = maybe_function
                else:
                    current_context = activity_cell
                continue

            district_text = clean_text(cells[district_idx]) if district_idx is not None else ""
            location = clean_text(cells[location_idx])
            budget = to_number(cells[budget_idx])
            physical = to_number(cells[physical_idx])
            if not district_text and not location and budget:
                current_context = activity_cell
                continue
            if not budget and not physical and not location:
                continue

            if activity_cell:
                current_activity = contextual_activity(activity_cell, current_context)
                current_description = clean_text(cells[1])
            activity = current_activity or contextual_activity(activity_cell, current_context)
            if not activity:
                continue

            province, district = province_district_from_text(district_text)
            if not province:
                province, district = province_district_from_text(location)
            if not province:
                unmatched.append({
                    "source_file": path.name,
                    "sheet": sheet_name,
                    "province": "",
                    "text": district_text or location or activity,
                })
                continue

            targets = all_program_targets(location, province, district, by_province, by_district, aliases)
            if not targets:
                unmatched.append({
                    "source_file": path.name,
                    "sheet": sheet_name,
                    "province": province,
                    "text": location or district_text or activity,
                })
                continue

            divisor = len(targets) or 1
            tier_1, tier_2 = current_function
            source_bits = [
                current_description,
                clean_text(cells[readiness_idx]),
                clean_text(cells[kra_idx]),
                clean_text(cells[alignment_idx]),
            ]
            source_note = " | ".join(bit for bit in source_bits if bit)
            for municipality in targets:
                details.append({
                    "source_file": path.name,
                    "sheet": sheet_name,
                    "province": province,
                    "district": district,
                    "municipality": municipality,
                    "year": 2027,
                    "program": program,
                    "commodity": commodity,
                    "office_function": tier_2,
                    "tier_1": tier_1,
                    "tier_2": tier_2,
                    "activity": activity,
                    "activity_context": current_context,
                    "original_activity": activity_cell,
                    "unit": cells[physical_idx],
                    "physical_target": format_number(physical / divisor) if physical else "",
                    "budget": format_number(budget / divisor) if budget else "0.00",
                    "original_physical_target": format_number(physical) if physical else "",
                    "original_budget": format_number(budget) if budget else "0.00",
                    "target_count": str(divisor),
                    "target_scope": location or district_text,
                    "length_km": "",
                    "allocation_method": "ALL PROGRAMS 2027 municipality split",
                    "source_row": str(source_row),
                    "source_note": source_note,
                })

    return details, unmatched


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


GULAYAN_PRIORITY = [
    "ALICIA",
    "BAGGAO",
    "SANMARIANO",
    "CABATUAN",
    "CORDON",
    "SANISIDRO",
    "LASAM",
    "GATTARAN",
    "SANTAMARIA",
    "ROXAS",
    "KAYAPA",
    "ECHAGUE",
    "RAMON",
    "ARITAO",
    "BAMBANG",
    "REINAMERCEDES",
]

GULAYAN_EXCLUDED = {
    "TUGUEGARAOCITY",
    "ILAGANCITY",
    "CAUAYANCITY",
    "SANTIAGOCITY",
}


def selected_hvcdp_targets(activity, targets, physical, group_count):
    activity_key = normalize_key(activity)
    if activity_key == "GULAYANSABAYAN":
        candidates = [key for key in targets if key not in GULAYAN_EXCLUDED]
        target_count = int(round(group_count or physical or len(candidates)))
        priority = [key for key in GULAYAN_PRIORITY if key in candidates]
        remainder = [key for key in candidates if key not in priority]
        return (priority + remainder)[:target_count]

    target_count = int(round(group_count)) if group_count and group_count <= len(targets) else 0
    if target_count > 0:
        return targets[:target_count]
    return targets


def per_target_physical(activity, physical, target_count):
    if target_count <= 0:
        return 0
    if normalize_key(activity) == "GULAYANSABAYAN":
        return 1.0
    return physical / target_count if physical else 0


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

            for source_row, row in enumerate(rows[9:], start=10):
                cells = row + [""] * 64
                activity = clean_text(cells[0])
                unit = clean_text(cells[1])
                if is_hvcdp_context_heading(activity, unit):
                    context = activity
                if not is_hvcdp_detail_row(activity, unit):
                    continue

                physical = to_number(cells[start])
                group_count = to_number(cells[start + 1])
                budget = to_number(cells[start + 5])
                if not physical and not budget:
                    continue
                if is_hvcdp_aggregate_generic_detail(activity, context):
                    continue

                selected_targets = selected_hvcdp_targets(activity, targets, physical, group_count)
                if not selected_targets:
                    continue
                divisor = len(selected_targets)
                physical_per_target = per_target_physical(activity, physical, divisor)
                display_activity = contextual_hvcdp_activity(activity, context)
                for key in selected_targets:
                    details.append({
                        "source_file": path.name,
                        "sheet": sheet_name,
                        "province": province,
                        "district": district,
                        "municipality": by_district[district_lookup_key(province, district)][key],
                        "year": 2027,
                        "program": "High Value Crops",
                        "activity": display_activity,
                        "activity_context": context,
                        "original_activity": activity,
                        "unit": unit,
                        "physical_target": format_number(physical_per_target) if physical_per_target else "",
                        "budget": format_number(budget / divisor) if budget else "0.00",
                        "original_physical_target": format_number(physical) if physical else "",
                        "original_budget": format_number(budget) if budget else "0.00",
                        "target_count": str(divisor),
                        "target_scope": block["label"],
                        "length_km": "",
                        "allocation_method": "district column municipalities split",
                        "source_row": str(source_row),
                        "source_note": f"{sheet_name} {block['label']} FY 2027 HVCDP district column",
                    })
    return details


def summarize_rows(files, municipal_csv):
    _, by_province, by_district, aliases = load_municipalities(municipal_csv)
    details = []
    unmatched = []
    has_dedicated_hvcdp = any(is_dedicated_hvcdp_file(path) for path in files)
    all_programs_files = [path for path in files if is_all_programs_file(path)]
    has_all_programs_2027 = bool(all_programs_files)

    for path in all_programs_files:
        all_details, all_unmatched = extract_all_programs_rows(
            path,
            read_workbook(path),
            by_province,
            by_district,
            aliases,
        )
        details.extend(all_details)
        unmatched.extend(all_unmatched)

    for path in files:
        if is_all_programs_file(path):
            continue
        sheets = read_workbook(path)
        if is_dedicated_hvcdp_file(path):
            if has_all_programs_2027:
                continue
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

            for source_row, row in enumerate(rows, start=1):
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
                    row_year = current_year or 2027
                    if has_all_programs_2027 and row_year == 2027 and not preserve_legacy_2027_program(program):
                        continue
                    municipality = by_province[province_key][direct_key]
                    amount = to_number(cells[4]) or to_number(cells[5]) or max(to_number(cell) for cell in cells[1:8])
                    length = to_number(cells[3])
                    details.append({
                        "source_file": path.name,
                        "sheet": sheet_name,
                        "province": province,
                        "district": district,
                        "municipality": municipality,
                        "year": row_year,
                        "program": program,
                        "activity": cells[2] or cells[0],
                        "activity_context": sheet_name,
                        "original_activity": cells[0],
                        "unit": cells[1],
                        "physical_target": "",
                        "budget": format_number(amount),
                        "original_physical_target": "",
                        "original_budget": format_number(amount),
                        "target_count": "1",
                        "target_scope": municipality,
                        "length_km": format_number(length) if length else "",
                        "allocation_method": "direct municipality row",
                        "source_row": str(source_row),
                        "source_note": cells[2] or cells[1],
                    })
                    continue

                if len(cells) < 12 or not cells[0] or any(term in joined for term in ["GRAND TOTAL", "PREPARED BY", "CONCURRED BY"]):
                    continue
                if has_all_programs_2027 and not preserve_legacy_2027_program(program):
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
                        "activity_context": sheet_name,
                        "original_activity": cells[0],
                        "unit": cells[1],
                        "physical_target": format_number(physical_2027 / divisor) if physical_2027 else "",
                        "budget": format_number(budget_2027 / divisor) if budget_2027 else "0.00",
                        "original_physical_target": format_number(physical_2027) if physical_2027 else "",
                        "original_budget": format_number(budget_2027) if budget_2027 else "0.00",
                        "target_count": str(divisor),
                        "target_scope": "All district municipalities" if is_all_district_municipalities else remarks,
                        "length_km": "",
                        "allocation_method": "all district municipalities split" if is_all_district_municipalities else "remarks municipality split",
                        "source_row": str(source_row),
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

    return [enrich_detail_row(row) for row in details], unmatched


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


