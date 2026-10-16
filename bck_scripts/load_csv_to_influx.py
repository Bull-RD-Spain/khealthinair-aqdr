# Copyright © 2021-2026 Bull SAS
# SPDX-License-Identifier: GPL-3.0-or-later
#
# This file is part of work done in the K-HEALTHinAIR EU funded project.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

# -*- coding: utf-8 -*-
"""
Load inBiot CSV historical data into InfluxDB.

Reads CSV files exported by inBiot (format: data_<scenario><area>.csv),
maps them to the correct sensor using the PostgreSQL sensors table export,
transforms IAQ columns to match the ingestor's InfluxDB data model,
and writes the points to InfluxDB.

Usage:
    1. Place all data_*.csv files in a folder (e.g. ./csv_data/)
    2. Place the PostgreSQL sensors table export as sensors_table.csv
    3. Set environment variables (or edit the CONFIG section below)
    4. Run: python load_csv_to_influx.py

Environment variables (or edit CONFIG below):
    INFLUXDB_URL                        e.g. http://localhost:8086
    DOCKER_INFLUXDB_INIT_ADMIN_TOKEN    InfluxDB admin token
    DOCKER_INFLUXDB_INIT_ORG            InfluxDB org
    DOCKER_INFLUXDB_INIT_BUCKET         e.g. AIR_QUALITY
"""

import csv
import glob
import os
import re
import sys
from datetime import datetime, timezone

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS

# ============================================================================
# CONFIG — edit these or set as environment variables
# ============================================================================
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN", "")
INFLUXDB_ORG = os.getenv("DOCKER_INFLUXDB_INIT_ORG", "")
INFLUXDB_BUCKET = os.getenv("DOCKER_INFLUXDB_INIT_BUCKET", "AIR_QUALITY")

CSV_DIR = os.getenv("CSV_DIR", "./csv_data")          # folder with data_*.csv
SENSORS_TABLE = os.getenv("SENSORS_TABLE", "./sensors_table.csv")  # pg export
MEASUREMENT = "CONTINUOUS_MONITORING_"
BATCH_SIZE = 5000   # points per write batch
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"  # set true to test

# ============================================================================
# CSV column -> InfluxDB field mapping (matching ingestor ind_linkage)
# ============================================================================
# CSV columns use ";" separator, latin1 encoding
# We map by column position (0-indexed) to avoid encoding issues in headers
#
#  Col 0: Date           (dd/mm/yyyy)
#  Col 1: Time           (HH:MM:SS)
#  Col 2: Ventilation Indicator   -- SKIP (not in data model)
#  Col 3: IAQ Indicator           -- SKIP
#  Col 4: Virus Index             -- SKIP
#  Col 5: thermalIndicator        -- SKIP
#  Col 6: Temperature (°C)        -> temperature
#  Col 7: Humidity (%)             -> humidity
#  Col 8: CO2 (ppm)               -> co2
#  Col 9: Formaldehyde (µg/m³)    -> formaldehyde
#  Col 10: TVOC (ppb)             -> tvocs
#  Col 11: PM 1.0 (µg/m³)         -> pm1
#  Col 12: PM 4.0 (µg/m³)         -- SKIP (not in data model)
#  Col 13: PM 10 (µg/m³)          -> pm10
#  Col 14: PM 2.5 (µg/m³)         -> pm25
#  Col 15-20: Weather/Outdoor     -- SKIP (different dates, not IAQ)

COL_MAPPING = {
    6:  "temperature",
    7:  "humidity",
    8:  "co2",
    9:  "formaldehyde",
    10: "tvocs",
    11: "pm1",
    13: "pm10",
    14: "pm25",
}


def load_sensors_table(path):
    """Load PostgreSQL sensors table export and build lookup by scenario+area.

    Returns dict: { "RES0411": { sensor_id, pilot, scenario, sub_scenario,
                                  area_tag, ... }, ... }
    """
    sensors = {}
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Clean possible quotes and whitespace
            sensor_id = row["sensor_id"].strip().strip('"')
            scenario_full = row["scenario"].strip()   # e.g. "RES01"
            area_num = row["area"].strip()             # e.g. "11"

            # Key matching filename pattern: data_RES0411.csv
            key = f"{scenario_full}{area_num}"

            # Tags exactly as the ingestor builds them
            scenario_tag = scenario_full[:3]           # "RES"
            sub_scenario_tag = scenario_full            # "RES01"
            area_tag = f"{scenario_full}{str(int(area_num)).zfill(3)}"  # "RES01011"
            pilot = row["pilot"].strip()                # "NO"

            sensors[key] = {
                "sensor_id": sensor_id,
                "pilot": pilot,
                "scenario": scenario_tag,
                "sub_scenario": sub_scenario_tag,
                "area": area_tag,
                "scenario_full": scenario_full,
                "area_num": area_num,
            }
    return sensors


def parse_csv_row_to_fields(cols):
    """Extract IAQ fields from a CSV row (list of column values).

    Returns (timestamp_utc, fields_dict) or (None, None) if row is invalid.
    """
    # Parse date + time -> UTC timestamp
    date_str = cols[0].strip()  # dd/mm/yyyy
    time_str = cols[1].strip()  # HH:MM:SS

    if not date_str or not time_str:
        return None, None

    try:
        # Support both date formats: dd/mm/yyyy and yyyy-mm-dd
        if "/" in date_str:
            dt = datetime.strptime(f"{date_str} {time_str}", "%d/%m/%Y %H:%M:%S")
        else:
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
        dt = dt.replace(tzinfo=timezone.utc)
        ts_epoch = int(dt.timestamp())
    except ValueError:
        return None, None

    # Extract fields
    fields = {}
    for col_idx, field_name in COL_MAPPING.items():
        if col_idx < len(cols) and cols[col_idx].strip():
            try:
                value = float(cols[col_idx].strip())
                fields[field_name] = round(value, 2)
            except ValueError:
                continue

    if not fields:
        return None, None

    return ts_epoch, fields


def build_point(ts_epoch, fields, sensor_info):
    """Build an InfluxDB Point matching the ingestor's format."""
    dp = {
        "measurement": MEASUREMENT,
        "tags": {
            "AQ": "IAQ",
            "id_pilot": sensor_info["pilot"],
            "scenario": sensor_info["scenario"],
            "sub_scenario": sensor_info["sub_scenario"],
            "area": sensor_info["area"],
            "sensor_id": sensor_info["sensor_id"],
        },
        "fields": fields,
        "time": ts_epoch,
    }
    return Point.from_dict(dp, write_precision="s")


def process_csv(csv_path, sensor_info, writer):
    """Process a single CSV file and write points to InfluxDB.

    Returns (points_written, first_date, last_date).
    """
    points = []
    first_ts = None
    last_ts = None
    skipped = 0

    # Read with latin1 encoding (inBiot exports use ISO-8859-1)
    with open(csv_path, "r", encoding="latin1") as f:
        reader = csv.reader(f, delimiter=";")
        header = next(reader)  # skip header

        for row_num, row in enumerate(reader, start=2):
            if len(row) < 15:
                skipped += 1
                continue

            ts_epoch, fields = parse_csv_row_to_fields(row)
            if ts_epoch is None:
                skipped += 1
                continue

            if first_ts is None or ts_epoch < first_ts:
                first_ts = ts_epoch
            if last_ts is None or ts_epoch > last_ts:
                last_ts = ts_epoch

            point = build_point(ts_epoch, fields, sensor_info)
            points.append(point)

            # Write in batches
            if len(points) >= BATCH_SIZE:
                if not DRY_RUN:
                    writer.write(
                        bucket=INFLUXDB_BUCKET,
                        org=INFLUXDB_ORG,
                        record=points,
                    )
                print(f"    ... wrote batch of {len(points)} points")
                points = []

    # Write remaining points
    if points:
        if not DRY_RUN:
            writer.write(
                bucket=INFLUXDB_BUCKET,
                org=INFLUXDB_ORG,
                record=points,
            )

    first_dt = datetime.fromtimestamp(first_ts, timezone.utc) if first_ts else None
    last_dt = datetime.fromtimestamp(last_ts, timezone.utc) if last_ts else None

    total = (row_num - 1) if 'row_num' in dir() else 0
    written = total - skipped

    return written, skipped, first_dt, last_dt


def main():
    print("=" * 70)
    print("inBiot CSV -> InfluxDB Loader")
    print("=" * 70)

    if DRY_RUN:
        print("*** DRY RUN MODE — no data will be written ***\n")

    # Load sensor mapping
    print(f"Loading sensors table from: {SENSORS_TABLE}")
    sensors = load_sensors_table(SENSORS_TABLE)
    print(f"  Found {len(sensors)} sensors\n")

    # Find CSV files
    csv_files = sorted(glob.glob(os.path.join(CSV_DIR, "data_*.csv")))
    if not csv_files:
        print(f"ERROR: No data_*.csv files found in {CSV_DIR}")
        sys.exit(1)
    print(f"Found {len(csv_files)} CSV files in {CSV_DIR}\n")

    # Connect to InfluxDB
    if not DRY_RUN:
        print(f"Connecting to InfluxDB at {INFLUXDB_URL}")
        client = InfluxDBClient(
            url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG
        )
        writer = client.write_api(write_options=SYNCHRONOUS)
        print("  Connected.\n")
    else:
        client = None
        writer = None

    # SQL statements for inclusion_time updates
    sql_updates = []

    # Process each CSV
    for csv_path in csv_files:
        filename = os.path.basename(csv_path)

        # Extract scenario+area from filename: data_RES0411.csv -> RES0411
        match = re.match(r"data_([A-Z]+\d+)\.csv", filename)
        if not match:
            print(f"SKIP {filename}: cannot parse scenario+area from name")
            continue

        raw_key = match.group(1)  # e.g. "RES01011"

        # Match against sensors table, trying multiple interpretations
        # Filenames may use zero-padded area (RES01011 = RES01 + 011)
        # while the sensors table key uses unpadded area (RES01 + 11 = RES0111)
        key = None
        if raw_key in sensors:
            key = raw_key
        else:
            # Try scenario (first 5 chars) + area (remaining, stripped of
            # leading zeros): RES01011 -> RES01 + 011 -> RES01 + 11 -> RES0111
            for scenario_len in [5, 4]:  # try RES01 (5) then RES0 (4)
                if len(raw_key) > scenario_len:
                    scenario_part = raw_key[:scenario_len]
                    area_part = raw_key[scenario_len:].lstrip("0") or "0"
                    candidate = scenario_part + area_part
                    if candidate in sensors:
                        key = candidate
                        break

        if key is None:
            print(f"SKIP {filename}: no sensor found for key '{raw_key}'")
            print(f"  Available keys: {sorted(sensors.keys())}")
            continue

        sensor_info = sensors[key]
        sid_short = sensor_info["sensor_id"][:8]

        print(f"Processing {filename}")
        print(f"  -> sensor_id: {sid_short}... "
              f"({sensor_info['sub_scenario']} area {sensor_info['area_num']})")

        try:
            written, skipped, first_dt, last_dt = process_csv(
                csv_path, sensor_info, writer
            )
        except Exception as e:
            print(f"  ERROR: {e}")
            continue

        print(f"  -> {written} points written, {skipped} skipped")
        if first_dt:
            print(f"  -> Date range: {first_dt:%Y-%m-%d %H:%M} to "
                  f"{last_dt:%Y-%m-%d %H:%M} UTC")

            # Generate SQL update for inclusion_time
            sql = (
                f"UPDATE {sensors_table_name()} "
                f"SET inclusion_time = '{first_dt:%Y-%m-%d %H:%M:%S}' "
                f"WHERE sensor_id = '{sensor_info['sensor_id']}';"
            )
            sql_updates.append((filename, sensor_info["sensor_id"][:8], sql))
        print()

    # Print SQL updates
    if sql_updates:
        print("=" * 70)
        print("SQL: UPDATE inclusion_time for each sensor")
        print("=" * 70)
        for fname, sid, sql in sql_updates:
            print(f"-- {fname} ({sid}...)")
            print(sql)
        print()

        # Also write to file
        sql_path = os.path.join(
            os.path.dirname(SENSORS_TABLE), "update_inclusion_time.sql"
        )
        with open(sql_path, "w") as f:
            f.write("-- Auto-generated: update inclusion_time based on CSV data\n")
            f.write(f"-- Generated: {datetime.now():%Y-%m-%d %H:%M:%S}\n\n")
            for fname, sid, sql in sql_updates:
                f.write(f"-- {fname} ({sid}...)\n{sql}\n\n")
        print(f"SQL file written to: {sql_path}")

    if not DRY_RUN and client:
        client.close()

    print("\nDone.")


def sensors_table_name():
    """Return the PostgreSQL table name. Adjust if needed."""
    return "sensors"


if __name__ == "__main__":
    main()
