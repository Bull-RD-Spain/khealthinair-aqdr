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

"""Tests for the KunakSensor class and its methods"""

import os
import sys
from datetime import datetime

import pytest
from influxdb_client import Point

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from modules.kunak_sensor import KunakSensor
from modules.qlair_sensor import QlairSensor


class TestKunakSensor:
    """Tests for the KunakSensor class and its methods"""

    @pytest.fixture
    def sensor_device(self):
        """Returns a KunakSensor instance with its description"""
        device = {
            "sensor_id": "35a9c0825cda4c72974ad52c31602639",
            "provider": "MH",
            "apikey": "0f18620e4724794c411388653cb94c09997fa",
            "pilot": "ES",
            "scenario": "HOM",
            "sub_scenario": "HOM01",
            "area": 1,
            "outdoor_apikey": "0f18620e4724794c411388653cb94c09997fa",
            "building": 68,  # The importat part for Kunak data to be used
            "inclusion_time": datetime(2023, 12, 1, 14, 0, 0),
        }
        return QlairSensor(**device)  # Reference sensor is not Kunak but other

    @pytest.fixture
    def out_record_example(self):
        """Returns a (raw) out record example from qlair API

        Note that the endpoint /reads/fromGroupByTs uses a single 'ts',
        and the /reads/fromToGroupByTs uses 'startTs' and 'endTs'"""

        return {
            "ts": 1692000000000,  # Monday, 14 August 2023 8:00:00
            "PM1": {"value": "0.24", "validation": "T", "reason": "0"},
            "NO2 GCc": {"value": "14.76", "validation": "T", "reason": "0"},
            "PM10": {"value": "0.68", "validation": "T", "reason": "0"},
            "Pressure": {"value": "1025.58", "validation": "T", "reason": "0"},
            "Temp ext": {"value": "-4.61", "validation": "T", "reason": "0"},
            "Humidity ext": {
                "value": "86.26",
                "validation": "T",
                "reason": "0",
            },
            "VOCs GCc": {"value": "0.00", "validation": "T", "reason": "0"},
            "PM2.5": {"value": "0.61", "validation": "T", "reason": "0"},
        }

    @pytest.fixture
    def historic_out_record_example(self):
        """Returns a (raw) outdoor historic record example from qlair API"""

        # List of dictionary records (from oldest to most recent)
        return [
            {
                "ts": 1692000000000,  # Monday, 14 August 2023 8:00:00
                "PM1": {"value": "0.24", "validation": "T", "reason": "0"},
                "NO2 GCc": {
                    "value": "14.76",
                    "validation": "T",
                    "reason": "0",
                },
                "PM10": {"value": "0.68", "validation": "T", "reason": "0"},
                "Pressure": {
                    "value": "1025.58",
                    "validation": "T",
                    "reason": "0",
                },
                "Temp ext": {
                    "value": "-4.61",
                    "validation": "T",
                    "reason": "0",
                },
                "Humidity ext": {
                    "value": "86.26",
                    "validation": "T",
                    "reason": "0",
                },
                "VOCs GCc": {
                    "value": "0.00",
                    "validation": "T",
                    "reason": "0",
                },
                "PM2.5": {"value": "0.61", "validation": "T", "reason": "0"},
            },
            {
                "ts": 1692003600000,  # Monday, 14 August 2023 9:00:00
                "PM1": {"value": "0.20", "validation": "T", "reason": "0"},
                "VOCs GCc": {
                    "value": "0.00",
                    "validation": "T",
                    "reason": "0",
                },
                "Temp ext": {
                    "value": "-4.59",
                    "validation": "T",
                    "reason": "0",
                },
                "PM10": {"value": "0.50", "validation": "T", "reason": "0"},
                "NO2 GCc": {
                    "value": "14.91",
                    "validation": "T",
                    "reason": "0",
                },
                "Pressure": {
                    "value": "1025.52",
                    "validation": "T",
                    "reason": "0",
                },
                "Humidity ext": {
                    "value": "86.23",
                    "validation": "T",
                    "reason": "0",
                },
                "PM2.5": {"value": "0.46", "validation": "T", "reason": "0"},
            },
        ]

    def test_out_transform_to_dp(
        self, sensor_device: QlairSensor, out_record_example
    ):
        """Test the transformation of a single outdoor record from Outdoor API"""
        expected_dp = self.out_build_datapoint(
            sensor_device,
            KunakSensor.out_record_build(out_record_example),
            int(out_record_example["ts"]),
        )
        assert {
            k: v
            for k, v in KunakSensor.out_transform_to_dp(
                sensor_device,
                KunakSensor.out_record_build(out_record_example),
                out_record_example["ts"] / 1000,
                measurement="CONTINUOUS_MONITORING_",
            ).__dict__.items()
            if k != "_time"
        } == {k: v for k, v in expected_dp.__dict__.items() if k != "_time"}

    def test_out_transform_to_dp_hist(
        self, sensor_device: QlairSensor, historic_out_record_example
    ):
        """Test the transformation of a list of outdoor historic records
        from qlair API to InfluxDB datapoints"""

        expected_dps = [
            self.out_build_datapoint(
                sensor_device,
                KunakSensor.out_record_build(historic_out_record_example[0]),
                int(historic_out_record_example[0]["ts"] / 1000),
            ),
            self.out_build_datapoint(
                sensor_device,
                KunakSensor.out_record_build(historic_out_record_example[1]),
                int(historic_out_record_example[1]["ts"] / 1000),
            ),
        ]

        # Check length equality of lists
        assert len(
            KunakSensor.out_transform_to_dp_hist(
                sensor_device,
                historic_out_record_example,
                measurement="CONTINUOUS_MONITORING_",
            )
        ) == len(expected_dps)
        # Check all elements in list have same attributes
        assert all(
            [
                actual.__dict__ == expected.__dict__
                for actual, expected in zip(
                    KunakSensor.out_transform_to_dp_hist(
                        sensor_device,
                        historic_out_record_example,
                        measurement="CONTINUOUS_MONITORING_",
                    ),
                    expected_dps,
                )
                if "_time" not in actual.__dict__
            ]
        )

    def test_out_record_build(self, out_record_example):
        """Test the transformation of a single outdoor record from qlair API to
        InfluxDB record format"""
        expected_record = {
            "out_temperature": float(out_record_example["Temp ext"]["value"])
            or 0,
            "out_humidity": float(out_record_example["Humidity ext"]["value"])
            or 0,
            "out_pm25": float(out_record_example["PM2.5"]["value"]) or 0,
            "out_pm10": float(out_record_example["PM10"]["value"]) or 0,
            "out_no2": float(out_record_example["NO2 GCc"]["value"]) or 0,
            "out_pressure": float(out_record_example["Pressure"]["value"])
            or 0,
            "out_vocs": None,
        }

        assert (
            KunakSensor.out_record_build(out_record_example) == expected_record
        )

    def out_build_datapoint(
        self, sensor_device: QlairSensor, record, timestamp
    ):
        """Returns a (InfluxDB) datapoint from a record and timestamp"""
        return Point.from_dict(
            {
                "measurement": "CONTINUOUS_MONITORING_",
                "tags": {
                    "AQ": "OAQ_kunak",
                    "sensor_id": sensor_device.sensor_id,
                    "id_pilot": sensor_device.pilot,
                    "scenario": sensor_device.scenario,
                    "sub_scenario": sensor_device.sub_scenario,
                    "area": sensor_device.sub_scenario
                    + str(sensor_device.area).zfill(3),
                },
                "fields": record,
                "time": timestamp / 1000,
            },
            write_precision="s",
        )
