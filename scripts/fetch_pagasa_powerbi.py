import argparse
import csv
import json
import re
import time
import urllib.request
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path


REPORT_URL = "https://app.powerbi.com/view?r=eyJrIjoiOTJkN2U4MjUtYWE1Ny00NzA4LWExMzctMDBiYjQ2NjZiZWVjIiwidCI6ImJkMDNhNzM1LTJhYTMtNGNjYS05NzIyLTJhZTQ5MjlhYjNlYyIsImMiOjEwfQ%3D%3D&pageName=adfba30c52355c5b1631"
RESOURCE_KEY = "92d7e825-aa57-4708-a137-00bb4666beec"
TENANT_ID = "bd03a735-2aa3-4cca-9722-2ae4929ab3ec"
MODEL_ID = 2912241
API_URI = "https://wabi-south-east-asia-c-primary-api.analysis.windows.net"

STATIONS = ["Aparri", "Tuguegarao", "Casiguran", "Calayan", "Basco", "Itbayat"]
YEAR_MIN = 1991
YEAR_MAX = 2020

MONTH_ORDER = {
    "JANUARY": 1,
    "JAN": 1,
    "FEBRUARY": 2,
    "FEB": 2,
    "MARCH": 3,
    "MAR": 3,
    "APRIL": 4,
    "APR": 4,
    "MAY": 5,
    "JUNE": 6,
    "JUN": 6,
    "JULY": 7,
    "JUL": 7,
    "AUGUST": 8,
    "AUG": 8,
    "SEPTEMBER": 9,
    "SEP": 9,
    "OCTOBER": 10,
    "OCT": 10,
    "NOVEMBER": 11,
    "NOV": 11,
    "DECEMBER": 12,
    "DEC": 12,
}

MONTH_FIELDS = [
    "station",
    "province",
    "latitude",
    "longitude",
    "year",
    "month_number",
    "month",
    "climatological_season",
    "philippine_season",
    "annual_rainfall_mm",
    "rainfall_mm",
    "date",
    "source_url",
]

SEASON_FIELDS = [
    "station",
    "province",
    "latitude",
    "longitude",
    "year",
    "season_type",
    "season",
    "months",
    "rainfall_mm",
    "available_months",
    "source_url",
]

POWERBI_EXTRACT_FIELDS = [
    "province",
    "municipality",
    "pagasa_powerbi_rainfall_mm",
    "pagasa_powerbi_rainfall_anomaly_pct",
    "pagasa_powerbi_drought_class",
    "pagasa_powerbi_dry_spell_probability_pct",
    "pagasa_powerbi_heat_stress_days",
    "pagasa_powerbi_agri_risk_score",
    "pagasa_powerbi_valid_from",
    "pagasa_powerbi_valid_to",
    "pagasa_powerbi_source_url",
    "pagasa_powerbi_notes",
]


def clean_text(value):
    text = "" if value is None else str(value)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    return "" if text.lower() == "null" else text


def as_float(value):
    text = clean_text(value).replace(",", "")
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def as_int(value):
    number = as_float(value)
    return None if number is None else int(round(number))


def fmt_number(value, digits=2):
    number = as_float(value)
    if number is None:
        return ""
    rounded = round(number, digits)
    if abs(rounded - int(rounded)) < 10 ** -digits:
        return str(int(rounded))
    return f"{rounded:.{digits}f}".rstrip("0").rstrip(".")


def format_powerbi_date(value):
    text = clean_text(value)
    if not text:
        return ""
    if re.match(r"^\d{4}-\d{2}-\d{2}", text):
        return text[:10]
    number = as_float(text)
    if number is None:
        return text
    try:
        return datetime.fromtimestamp(number / 1000, tz=timezone.utc).date().isoformat()
    except (OSError, OverflowError, ValueError):
        return text


def make_request(url, method="GET", body=None, timeout=90):
    headers = {
        "Accept": "application/json",
        "ActivityId": str(uuid.uuid4()),
        "RequestId": str(uuid.uuid4()),
        "X-PowerBI-ResourceKey": RESOURCE_KEY,
        "User-Agent": "Mozilla/5.0 AgriSight-PAGASA-Fetcher/1.0",
    }
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read().decode("utf-8-sig")
        return json.loads(raw)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, separators=(",", ":"))
        handle.write("\n")


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fields})


def column_select(source, entity, property_name, native_name):
    return {
        "Column": {
            "Expression": {"SourceRef": {"Source": source}},
            "Property": property_name,
        },
        "Name": f"{entity}.{property_name}",
        "NativeReferenceName": native_name,
    }


def station_payload(station):
    source = station[0].lower()
    selects = [
        column_select(source, station, "Station", "station"),
        column_select(source, station, "Year", "year"),
        column_select(source, station, "Annual", "annual_rainfall_mm"),
        column_select(source, station, "Month", "month"),
        column_select(source, station, "Rainfall (mm)", "rainfall_mm"),
        column_select(source, station, "Date", "date"),
    ]
    return make_payload(station, source, selects, 1000)


def station_list_payload():
    entity = "02 Station List"
    source = "s"
    selects = [
        column_select(source, entity, "Station", "station"),
        column_select(source, entity, "Province", "province"),
        column_select(source, entity, "Latitude", "latitude"),
        column_select(source, entity, "Longitude", "longitude"),
        column_select(source, entity, "Climate Type", "climate_type"),
    ]
    return make_payload(entity, source, selects, 1000)


def make_payload(entity, source, selects, count):
    return {
        "version": "1.0.0",
        "queries": [
            {
                "Query": {
                    "Commands": [
                        {
                            "SemanticQueryDataShapeCommand": {
                                "Query": {
                                    "Version": 2,
                                    "From": [{"Name": source, "Entity": entity, "Type": 0}],
                                    "Select": selects,
                                },
                                "Binding": {
                                    "Primary": {"Groupings": [{"Projections": list(range(len(selects)))}]},
                                    "DataReduction": {
                                        "DataVolume": 4,
                                        "Primary": {"Top": {"Count": count}},
                                    },
                                    "Version": 1,
                                },
                                "ExecutionMetricsKind": 1,
                            }
                        }
                    ]
                }
            }
        ],
        "cancelQueries": [],
        "modelId": MODEL_ID,
    }


def payload_select_names(payload):
    command = payload["queries"][0]["Query"]["Commands"][0]["SemanticQueryDataShapeCommand"]
    return [item.get("NativeReferenceName") or item.get("Name") for item in command["Query"]["Select"]]


def find_data_member(node):
    if isinstance(node, list):
        if node and isinstance(node[0], dict) and "S" in node[0]:
            return node
        for item in node:
            found = find_data_member(item)
            if found is not None:
                return found
    elif isinstance(node, dict):
        for value in node.values():
            found = find_data_member(value)
            if found is not None:
                return found
    return None


def find_value_dicts(node):
    if isinstance(node, dict):
        if "ValueDicts" in node:
            return node["ValueDicts"]
        for value in node.values():
            found = find_value_dicts(value)
            if found is not None:
                return found
    elif isinstance(node, list):
        for item in node:
            found = find_value_dicts(item)
            if found is not None:
                return found
    return None


def decode_powerbi_result(result, column_names):
    data = result["results"][0]["result"]["data"]
    rows = find_data_member(data["dsr"])
    value_dicts = find_value_dicts(data["dsr"]) or {}
    if not rows:
        return []

    schema = rows[0]["S"]
    previous = [None] * len(schema)
    decoded = []

    for raw_row in rows:
        values = raw_row.get("C", [])
        value_index = 0
        repeat_mask = int(raw_row.get("R", 0) or 0)
        null_mask = int(raw_row.get("\u00d8", raw_row.get("Ã˜", 0)) or 0)
        current = []

        for index, spec in enumerate(schema):
            if repeat_mask & (1 << index):
                value = previous[index]
            elif null_mask & (1 << index):
                value = None
            else:
                value = values[value_index] if value_index < len(values) else None
                value_index += 1

            dict_name = spec.get("DN")
            if dict_name and value is not None:
                dictionary = value_dicts.get(dict_name, [])
                try:
                    value = dictionary[int(value)]
                except (ValueError, TypeError, IndexError):
                    pass

            current.append(value)

        previous = current
        decoded.append(
            {
                (column_names[i] if i < len(column_names) else schema[i].get("N", f"col_{i}")): clean_text(value)
                for i, value in enumerate(current)
            }
        )

    return decoded


def month_number(month):
    return MONTH_ORDER.get(clean_text(month).upper())


def climatological_season(month_no):
    if month_no in {12, 1, 2}:
        return "DJF"
    if month_no in {3, 4, 5}:
        return "MAM"
    if month_no in {6, 7, 8}:
        return "JJA"
    if month_no in {9, 10, 11}:
        return "SON"
    return ""


def philippine_season(month_no):
    if month_no in {11, 12, 1, 2, 3, 4}:
        return "Dry Season"
    if month_no in {5, 6, 7, 8, 9, 10}:
        return "Wet Season"
    return ""


def season_months(season_type, season):
    if season_type == "climatological":
        return {
            "DJF": "Dec-Jan-Feb",
            "MAM": "Mar-Apr-May",
            "JJA": "Jun-Jul-Aug",
            "SON": "Sep-Oct-Nov",
        }.get(season, "")
    return {
        "Dry Season": "Nov-Dec-Jan-Feb-Mar-Apr",
        "Wet Season": "May-Jun-Jul-Aug-Sep-Oct",
    }.get(season, "")


def build_month_rows(raw_rows, station_meta):
    rows = []
    for raw in raw_rows:
        year = as_int(raw.get("year"))
        month_no = month_number(raw.get("month"))
        if year is None or month_no is None:
          continue
        if year < YEAR_MIN or year > YEAR_MAX:
          continue

        station = clean_text(raw.get("station")) or clean_text(raw.get("Station"))
        meta = station_meta.get(station.upper(), {})
        rows.append(
            {
                "station": station,
                "province": meta.get("province", ""),
                "latitude": meta.get("latitude", ""),
                "longitude": meta.get("longitude", ""),
                "year": str(year),
                "month_number": str(month_no),
                "month": clean_text(raw.get("month")),
                "climatological_season": climatological_season(month_no),
                "philippine_season": philippine_season(month_no),
                "annual_rainfall_mm": fmt_number(raw.get("annual_rainfall_mm") or raw.get("annual_category"), 2),
                "rainfall_mm": fmt_number(raw.get("rainfall_mm"), 2),
                "date": format_powerbi_date(raw.get("date")),
                "source_url": REPORT_URL,
            }
        )
    return rows


def build_season_rows(month_rows):
    buckets = defaultdict(lambda: {"rainfall": 0.0, "count": 0, "meta": None})
    for row in month_rows:
        rain = as_float(row.get("rainfall_mm"))
        if rain is None:
            continue
        for season_type, season in [
            ("climatological", row.get("climatological_season")),
            ("philippine", row.get("philippine_season")),
        ]:
            key = (row["station"], row["year"], season_type, season)
            buckets[key]["rainfall"] += rain
            buckets[key]["count"] += 1
            buckets[key]["meta"] = row

    rows = []
    for (station, year, season_type, season), bucket in sorted(buckets.items()):
        meta = bucket["meta"] or {}
        rows.append(
            {
                "station": station,
                "province": meta.get("province", ""),
                "latitude": meta.get("latitude", ""),
                "longitude": meta.get("longitude", ""),
                "year": year,
                "season_type": season_type,
                "season": season,
                "months": season_months(season_type, season),
                "rainfall_mm": fmt_number(bucket["rainfall"], 2),
                "available_months": str(bucket["count"]),
                "source_url": REPORT_URL,
            }
        )
    return rows


def build_powerbi_extract(month_rows):
    grouped = defaultdict(list)
    for row in month_rows:
        grouped[(row["province"], row["station"])].append(row)

    output = []
    for (province, station), rows in sorted(grouped.items()):
        rainfall_values = [as_float(row["rainfall_mm"]) for row in rows]
        rainfall_values = [value for value in rainfall_values if value is not None]
        annual_values = defaultdict(float)
        for row in rows:
            annual_values[row["year"]] += as_float(row["rainfall_mm"]) or 0.0
        mean_monthly = sum(rainfall_values) / len(rainfall_values) if rainfall_values else 0
        mean_annual = sum(annual_values.values()) / len(annual_values) if annual_values else 0
        risk = min(100, max(0, (1 - min(1, mean_annual / 2500)) * 50))
        output.append(
            {
                "province": province,
                "municipality": station,
                "pagasa_powerbi_rainfall_mm": fmt_number(mean_monthly, 2),
                "pagasa_powerbi_rainfall_anomaly_pct": "0",
                "pagasa_powerbi_drought_class": "",
                "pagasa_powerbi_dry_spell_probability_pct": "0",
                "pagasa_powerbi_heat_stress_days": "0",
                "pagasa_powerbi_agri_risk_score": fmt_number(risk, 1),
                "pagasa_powerbi_valid_from": f"{YEAR_MIN}-01",
                "pagasa_powerbi_valid_to": f"{YEAR_MAX}-12",
                "pagasa_powerbi_source_url": REPORT_URL,
                "pagasa_powerbi_notes": "1991-2020 station monthly normal extracted from PAGASA Power BI rainfall tables; anomaly/drought/heat fields require advisory-specific refresh.",
            }
        )
    return output


def fetch_metadata(root):
    write_json(root / "modelsAndExploration.json", make_request(f"{API_URI}/public/reports/{RESOURCE_KEY}/modelsAndExploration?preferReadOnlySession=true"))
    write_json(root / "conceptualschema.json", make_request(f"{API_URI}/public/reports/{RESOURCE_KEY}/conceptualschema"))


def fetch_query(root, name, payload):
    query_dir = root / "query_payloads"
    raw_dir = root / "query_results_raw"
    write_json(query_dir / f"{name}.json", payload)
    result = make_request(f"{API_URI}/public/reports/querydata?synchronous=true", method="POST", body=payload)
    write_json(raw_dir / f"{name}.json", result)
    return decode_powerbi_result(result, payload_select_names(payload))


def write_readme(root, month_count, season_count):
    lines = [
        "# Power BI PAGASA Extraction",
        "",
        f"Source resource key: {RESOURCE_KEY}",
        f"Tenant ID: {TENANT_ID}",
        "Report/model: PAGASA EASi Tool public Power BI report",
        f"FetchedAtUtc: {datetime.now(timezone.utc).isoformat(timespec='seconds')}",
        f"Stations: {', '.join(STATIONS)}",
        f"Period: {YEAR_MIN}-{YEAR_MAX}",
        "",
        f"Extracted {month_count} station-month rows and {season_count} station-season rows.",
        "",
        "App-ready outputs:",
        "",
        "- `data/pagasa_station_monthly_1991_2020.csv`",
        "- `data/pagasa_station_seasonal_1991_2020.csv`",
        "- `data/pagasa_powerbi_climate_extract.csv`",
        "",
        "Refresh command:",
        "",
        "```powershell",
        "python scripts\\fetch_pagasa_powerbi.py",
        "```",
    ]
    (root / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Refresh PAGASA station climate normals from the public Power BI report.")
    parser.add_argument("--skip-fetch", action="store_true", help="Rebuild CSVs from existing raw query JSON only.")
    parser.add_argument("--root", default=".", help="Repository root. Defaults to current directory.")
    args = parser.parse_args()

    repo = Path(args.root).resolve()
    powerbi_root = repo / "data" / "powerbi_pagasa"
    powerbi_root.mkdir(parents=True, exist_ok=True)

    if not args.skip_fetch:
        fetch_metadata(powerbi_root)

    if args.skip_fetch:
        station_list = decode_powerbi_result(
            read_json(powerbi_root / "query_results_raw" / "station_list.json"),
            payload_select_names(read_json(powerbi_root / "query_payloads" / "station_list.json")),
        )
    else:
        station_list = fetch_query(powerbi_root, "station_list", station_list_payload())
        time.sleep(0.25)

    station_meta = {
        clean_text(row.get("station")).upper(): {
            "province": clean_text(row.get("province")),
            "latitude": clean_text(row.get("latitude")),
            "longitude": clean_text(row.get("longitude")),
        }
        for row in station_list
    }

    month_rows = []
    for station in STATIONS:
        if args.skip_fetch:
            raw_rows = decode_powerbi_result(
                read_json(powerbi_root / "query_results_raw" / f"{station}.json"),
                payload_select_names(read_json(powerbi_root / "query_payloads" / f"{station}.json")),
            )
        else:
            print(f"Fetching {station} ...")
            raw_rows = fetch_query(powerbi_root, station, station_payload(station))
            time.sleep(0.25)
        month_rows.extend(build_month_rows(raw_rows, station_meta))

    month_rows.sort(key=lambda row: (row["station"], int(row["year"]), int(row["month_number"])))
    season_rows = build_season_rows(month_rows)
    powerbi_extract = build_powerbi_extract(month_rows)

    write_csv(powerbi_root / "cleaned_csv" / "pagasa_station_monthly_1991_2020.csv", month_rows, MONTH_FIELDS)
    write_csv(powerbi_root / "cleaned_csv" / "pagasa_station_seasonal_1991_2020.csv", season_rows, SEASON_FIELDS)
    write_csv(repo / "data" / "pagasa_station_monthly_1991_2020.csv", month_rows, MONTH_FIELDS)
    write_csv(repo / "data" / "pagasa_station_seasonal_1991_2020.csv", season_rows, SEASON_FIELDS)
    write_csv(repo / "data" / "pagasa_powerbi_climate_extract.csv", powerbi_extract, POWERBI_EXTRACT_FIELDS)
    write_readme(powerbi_root, len(month_rows), len(season_rows))

    print(f"Wrote {len(month_rows)} station-month rows.")
    print(f"Wrote {len(season_rows)} station-season rows.")


if __name__ == "__main__":
    main()
