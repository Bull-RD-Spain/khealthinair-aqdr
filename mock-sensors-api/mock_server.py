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



"""
K-HEALTHinAIR — Mock API Server for Inbiot, Qlair & Kunak
==========================================================
Single FastAPI server that simulates the three external sensor APIs.
Generates random but realistic air quality readings.

Configuration via environment variables:
  MOCK_NUM_READINGS   — number of readings per historic request (default: 24)
  MOCK_INTERVAL_MIN   — minutes between readings (default: 60)
  MOCK_PORT           — port to listen on (default: 8888)
"""

import os
import random
import time
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, Header, Query, Request
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="K-HEALTHinAIR Mock Sensor APIs")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
NUM_READINGS = int(os.getenv("MOCK_NUM_READINGS", "24"))
INTERVAL_MIN = int(os.getenv("MOCK_INTERVAL_MIN", "60"))

# ---------------------------------------------------------------------------
# Helpers — realistic random ranges
# ---------------------------------------------------------------------------
INDOOR_RANGES = {
    "temperature": (18.0, 28.0),
    "humidity": (30.0, 70.0),
    "co2": (350.0, 1200.0),
    "tvocs": (0.0, 500.0),
    "pm1": (0.0, 15.0),
    "pm10": (0.0, 50.0),
    "pm25": (0.0, 35.0),
    "formaldehyde": (0.0, 50.0),
}

OUTDOOR_RANGES = {
    "temperature": (-10.0, 35.0),
    "humidity": (20.0, 95.0),
    "pm1": (0.0, 10.0),
    "pm25": (0.0, 30.0),
    "pm10": (0.0, 60.0),
    "no2": (0.0, 80.0),
    "o3": (0.0, 120.0),
    "co": (0.0, 5.0),
    "so2": (0.0, 10.0),
    "vocs": (0.0, 5.0),
    "pressure": (990.0, 1035.0),
}


def _rv(lo: float, hi: float) -> float:
    return round(random.uniform(lo, hi), 2)


def _now_ms() -> int:
    return int(time.time() * 1000)


def _now_s() -> int:
    return int(time.time())


# ===================================================================
# INBIOT MOCK — https://docs.myinbiotpublicapi.com
# ===================================================================

def _inbiot_measurement(ts_ms: int) -> list:
    """Build systemData array for one timestamp."""
    types = [
        ("temperature", "CELSIUS"),
        ("humidity", "%"),
        ("co2", "ppm"),
        ("vocs", "ppb"),
        ("pm1", "µg/m³"),
        ("pm10", "µg/m³"),
        ("pm25", "µg/m³"),
        ("formaldehyde", "ppb"),
    ]
    system_data = []
    for idx, (t, unit) in enumerate(types):
        lo, hi = INDOOR_RANGES.get(t, (0, 100))
        system_data.append({
            "type": t,
            "_id": idx,
            "settings": {
                "lastMeasureDate": datetime.fromtimestamp(
                    ts_ms / 1000, tz=timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "measured": True,
                "rangeUnit": "h",
                "rangeValue": 24,
                "measurementUnit": unit,
            },
            "measurements": [{"value": _rv(lo, hi), "date": ts_ms}],
        })
    return system_data


def _inbiot_measurement_hist(num: int) -> list:
    """Build systemData array with multiple measurements per type."""
    now = _now_ms()
    types = [
        ("temperature", "CELSIUS"),
        ("humidity", "%"),
        ("co2", "ppm"),
        ("vocs", "ppb"),
        ("pm1", "µg/m³"),
        ("pm10", "µg/m³"),
        ("pm25", "µg/m³"),
        ("formaldehyde", "ppb"),
    ]
    system_data = []
    for idx, (t, unit) in enumerate(types):
        lo, hi = INDOOR_RANGES.get(t, (0, 100))
        measurements = []
        for i in range(num):
            ts = now - (i * INTERVAL_MIN * 60 * 1000)
            measurements.append({"value": _rv(lo, hi), "date": ts})
        system_data.append({
            "type": t,
            "_id": idx,
            "settings": {
                "lastMeasureDate": datetime.fromtimestamp(
                    now / 1000, tz=timezone.utc
                ).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "measured": True,
                "rangeUnit": "h",
                "rangeValue": 24,
                "measurementUnit": unit,
            },
            "measurements": measurements,
        })
    return system_data


@app.get("/last-measurements/{apikey}/{sensor_id}")
async def inbiot_last(apikey: str, sensor_id: str):
    """Inbiot: latest measurements for a sensor."""
    return {"systemData": _inbiot_measurement(_now_ms())}


@app.get("/measurements-by-time/{apikey}/{sensor_id}/{init_dt}/{end_dt}")
async def inbiot_hist(apikey: str, sensor_id: str, init_dt: str, end_dt: str):
    """Inbiot: historical measurements for a time range."""
    return {"systemData": _inbiot_measurement_hist(NUM_READINGS)}


# ===================================================================
# QLAIR MOCK — https://api.v2.i-qlair.eu/docs
# ===================================================================

def _qlair_indoor_record(ts_s: float) -> dict:
    """Build one indoor record."""
    return {
        "pmtwoaqi": 0.0,
        "eventdatetime": ts_s,
        "chemisense": {
            "total_aqi": random.randint(10, 80),
            "productivity_score": _rv(70, 100),
            "covid": _rv(50, 100),
            "voc_ppb": _rv(*INDOOR_RANGES["tvocs"]),
            "comfort_score": _rv(70, 100),
            "cotwo": _rv(*INDOOR_RANGES["co2"]),
            "h": _rv(*INDOOR_RANGES["humidity"]),
            "voc": _rv(0, 10),
            "total_aqi_hundred": _rv(80, 100),
            "ventilation_score": _rv(5, 60),
            "air_cost": _rv(400, 900),
            "asthma_score": _rv(80, 100),
            "pmtwo": _rv(*INDOOR_RANGES["pm25"]),
            "mold_score": _rv(80, 100),
            "t": _rv(*INDOOR_RANGES["temperature"]),
            "pmone": _rv(*INDOOR_RANGES["pm1"]),
            "pmten": _rv(*INDOOR_RANGES["pm10"]),
            "sensedtimedate": ts_s,
            "Total_AQI": random.randint(10, 80),
        },
        "mac": "mock_sensor_mac_address",
        "pmtenaqi": 0.0,
    }


def _qlair_outdoor_record(ts_s: float, building_id: int) -> dict:
    """Build one outdoor record."""
    return {
        "aqi": {
            "category": "Good",
            "type": "airnow",
            "value": float(random.randint(10, 80)),
        },
        "eventdatetime": ts_s,
        "facilityname": str(building_id),
        "pollutants": {
            "Total_AQI": random.randint(10, 80),
            "co": _rv(*OUTDOOR_RANGES["co"]),
            "h": _rv(*OUTDOOR_RANGES["humidity"]),
            "no2": _rv(*OUTDOOR_RANGES["no2"]),
            "o3": _rv(*OUTDOOR_RANGES["o3"]),
            "pm10": _rv(*OUTDOOR_RANGES["pm10"]),
            "pm25": _rv(*OUTDOOR_RANGES["pm25"]),
            "pmten": _rv(*OUTDOOR_RANGES["pm10"]),
            "pmtwo": _rv(*OUTDOOR_RANGES["pm25"]),
            "so2": _rv(*OUTDOOR_RANGES["so2"]),
            "t": _rv(*OUTDOOR_RANGES["temperature"]),
            "total_aqi": random.randint(10, 80),
        },
        "sensedtimedate": int(ts_s),
        "weather": {
            "h": _rv(*OUTDOOR_RANGES["humidity"]),
            "t": _rv(*OUTDOOR_RANGES["temperature"]),
        },
    }


@app.get("/open/indoor_air_quality")
async def qlair_indoor(
    mac: str = Query(None),
    start: Optional[int] = Query(None),
    end: Optional[int] = Query(None),
    x_api_key: Optional[str] = Header(None),
):
    """Qlair: indoor air quality — latest or historic."""
    if start and end:
        records = []
        ts = start
        while ts <= end:
            records.append(_qlair_indoor_record(float(ts)))
            ts += INTERVAL_MIN * 60
        return records
    return _qlair_indoor_record(float(_now_s()))


@app.get("/open/outdoor_air_quality")
async def qlair_outdoor(
    building_id: int = Query(91),
    start: Optional[int] = Query(None),
    end: Optional[int] = Query(None),
    x_api_key: Optional[str] = Header(None),
):
    """Qlair: outdoor air quality — latest or historic."""
    if start and end:
        records = []
        ts = start
        while ts <= end:
            records.append(_qlair_outdoor_record(float(ts), building_id))
            ts += INTERVAL_MIN * 60
        return records
    return _qlair_outdoor_record(float(_now_s()), building_id)


# ===================================================================
# KUNAK MOCK — https://kunakcloud.com/openAPIv0/v1
# ===================================================================

def _kunak_record(ts_ms: int) -> dict:
    """Build one Kunak outdoor record."""
    return {
        "ts": ts_ms,
        "PM1": {"value": str(_rv(*OUTDOOR_RANGES["pm1"])), "validation": "T", "reason": "0"},
        "PM2.5": {"value": str(_rv(*OUTDOOR_RANGES["pm25"])), "validation": "T", "reason": "0"},
        "PM10": {"value": str(_rv(*OUTDOOR_RANGES["pm10"])), "validation": "T", "reason": "0"},
        "Temp ext": {"value": str(_rv(*OUTDOOR_RANGES["temperature"])), "validation": "T", "reason": "0"},
        "Humidity ext": {"value": str(_rv(*OUTDOOR_RANGES["humidity"])), "validation": "T", "reason": "0"},
        "NO2 GCc": {"value": str(_rv(*OUTDOOR_RANGES["no2"])), "validation": "T", "reason": "0"},
        "VOCs GCc": {"value": str(_rv(*OUTDOOR_RANGES["vocs"])), "validation": "T", "reason": "0"},
        "Pressure": {"value": str(_rv(*OUTDOOR_RANGES["pressure"])), "validation": "T", "reason": "0"},
    }


@app.post("/rest/devices/{device_id}/reads/fromGroupByTs")
async def kunak_from(device_id: str, request: Request):
    """Kunak: reads from a timestamp onwards."""
    records = []
    now = _now_ms()
    for i in range(NUM_READINGS):
        ts = now - (i * INTERVAL_MIN * 60 * 1000)
        records.append(_kunak_record(ts))
    records.sort(key=lambda r: r["ts"])
    return records


@app.post("/rest/devices/{device_id}/reads/fromToGroupByTs")
async def kunak_from_to(device_id: str, request: Request):
    """Kunak: reads between two timestamps."""
    records = []
    now = _now_ms()
    for i in range(NUM_READINGS):
        ts = now - (i * INTERVAL_MIN * 60 * 1000)
        records.append(_kunak_record(ts))
    records.sort(key=lambda r: r["ts"])
    return records


# ===================================================================
# Health & info
# ===================================================================

@app.get("/health")
async def health():
    return {"status": "ok", "service": "mock-sensor-apis"}


@app.get("/")
async def root():
    return {
        "service": "K-HEALTHinAIR Mock Sensor APIs",
        "endpoints": {
            "inbiot": [
                "/last-measurements/{apikey}/{sensor_id}",
                "/measurements-by-time/{apikey}/{sensor_id}/{init}/{end}",
            ],
            "qlair": [
                "/open/indoor_air_quality?mac=...&start=...&end=...",
                "/open/outdoor_air_quality?building_id=...&start=...&end=...",
            ],
            "kunak": [
                "/rest/devices/{id}/reads/fromGroupByTs",
                "/rest/devices/{id}/reads/fromToGroupByTs",
            ],
        },
        "config": {
            "MOCK_NUM_READINGS": NUM_READINGS,
            "MOCK_INTERVAL_MIN": INTERVAL_MIN,
        },
    }


if __name__ == "__main__":
    port = int(os.getenv("MOCK_PORT", "8888"))
    uvicorn.run(app, host="0.0.0.0", port=port)
