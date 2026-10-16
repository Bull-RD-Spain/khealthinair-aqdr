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

"""Tests for the InbiotSensor class and its methods"""

import os
import sys
from datetime import datetime

import pytest
from influxdb_client import Point

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from modules.inbiot_sensor import InbiotSensor


class TestInbiotSensor:
    """Tests for the InbiotSensor class and its methods"""

    @pytest.fixture
    def sensor_device(self):
        """Returns a InbiotSensor instance with its description"""
        device = {
            "sensor_id": "ef6bffdd7801f52e64f75c4c784032323b88ca12",
            "provider": "IB",
            "apikey": "2436d94e-4359-11ee-b673",
            "pilot": "ES",
            "scenario": "HOM",
            "sub_scenario": "HOM01",
            "area": 1,
            "outdoor_apikey": "0f18620e4724794c411388653cb94c09997fa",
            "building": 66,
            "inclusion_time": datetime(2023, 12, 1, 14, 0, 0),
        }
        return InbiotSensor(**device)

    @pytest.fixture
    def ind_record_example(self):
        """Returns a (raw) indoor record example from inBiot API"""

        return {
            "systemData": [
                {
                    "type": "temperature",
                    "_id": 0,
                    "settings": {
                        "lastMeasureDate": "2023-12-11T14:02:22.128Z",
                        "measured": True,
                        "rangeUnit": "h",
                        "rangeValue": 24,
                        "measurementUnit": "CELSIUS",
                    },
                    "measurements": [{"value": 26.6, "date": 1702303342128}],
                },
                {
                    "type": "formaldehyde",
                    "_id": 3,
                    "settings": {
                        "lastMeasureDate": "2023-12-11T14:02:22.128Z",
                        "measured": True,
                        "rangeUnit": "h",
                        "rangeValue": 24,
                    },
                    "measurements": [{"value": 11, "date": 1702303342128}],
                },
                {
                    "type": "pm4",
                    "_id": 6,
                    "settings": {
                        "lastMeasureDate": "2023-12-11T14:02:22.128Z",
                        "measured": True,
                        "rangeUnit": "h",
                        "rangeValue": 24,
                    },
                    "measurements": [{"value": 2, "date": 1702303342128}],
                },
            ]
        }

    @pytest.fixture
    def historic_ind_record_example(self):
        """Returns a (raw) indoor historic record example from inBiot API"""

        # Dictionary of records with list of values per pollutant (from recent to oldest)
        return {
            "systemData": [
                {
                    "type": "temperature",
                    "_id": 0,
                    "settings": {
                        "lastMeasureDate": "2023-12-11T14:02:22.128Z",
                        "measured": True,
                        "rangeUnit": "h",
                        "rangeValue": 24,
                        "measurementUnit": "CELSIUS",
                    },
                    "measurements": [
                        {"value": 26.6, "date": 1702303342128},
                        {"value": 27.6, "date": 1702302745000},
                        {"value": 28.6, "date": 1702302145000},
                    ],
                },
                {
                    "type": "formaldehyde",
                    "_id": 3,
                    "settings": {
                        "lastMeasureDate": "2023-12-11T14:02:22.128Z",
                        "measured": True,
                        "rangeUnit": "h",
                        "rangeValue": 24,
                    },
                    "measurements": [
                        {"value": 11, "date": 1702303342128},
                        {"value": 12, "date": 1702302745000},
                        {"value": 13, "date": 1702302145000},
                    ],
                },
            ]
        }

    def test_ind_transform(
        self, sensor_device: InbiotSensor, ind_record_example
    ):
        """Test the transformation of a single indoor record from
        inBiot API to InfluxDB datapoint"""
        expected_dp = self.ind_build_datapoint(
            sensor_device,
            sensor_device.ind_record_build(ind_record_example),
            int(
                int(
                    ind_record_example["systemData"][0]["measurements"][0][
                        "date"
                    ]
                )
                / 1000
            ),
        )
        assert (
            sensor_device.ind_transform(
                ind_record_example, measurement="CONTINUOUS_MONITORING_"
            ).__dict__
            == expected_dp.__dict__
        )

    def test_ind_transform_hist(
        self, sensor_device: InbiotSensor, historic_ind_record_example
    ):
        """Test the transformation of a list of indoor historic records
        from inBiot API to InfluxDB datapoints"""

        expected_dps = [
            self.ind_build_datapoint(
                sensor_device,
                {"temperature": 26.6},
                timestamp=1702303342,
            ),
            self.ind_build_datapoint(
                sensor_device,
                {
                    "temperature": 27.6,
                },
                timestamp=1702302745,
            ),
            self.ind_build_datapoint(
                sensor_device,
                {
                    "temperature": 28.6,
                },
                timestamp=1702302145,
            ),
            self.ind_build_datapoint(
                sensor_device,
                {
                    "formaldehyde": 11,
                },
                timestamp=1702303342,
            ),
            self.ind_build_datapoint(
                sensor_device,
                {
                    "formaldehyde": 12,
                },
                timestamp=1702302745,
            ),
            self.ind_build_datapoint(
                sensor_device,
                {
                    "formaldehyde": 13,
                },
                timestamp=1702302145,
            ),
        ]

        # Check length equality of lists
        assert len(
            sensor_device.ind_transform_hist(
                historic_ind_record_example["systemData"],
                measurement="CONTINUOUS_MONITORING_",
            )
        ) == len(expected_dps)
        # Check all elements in list have same attributes
        assert all(
            [
                actual.__dict__ == expected.__dict__
                for actual, expected in zip(
                    sensor_device.ind_transform_hist(
                        historic_ind_record_example["systemData"],
                        measurement="CONTINUOUS_MONITORING_",
                    ),
                    expected_dps,
                )
            ]
        )

    def test_ind_record_build(
        self, sensor_device: InbiotSensor, ind_record_example
    ):
        """Test the transformation of a single indoor record from inBiot API to
        InfluxDB record format"""
        expected_record = {
            "temperature": 26.6,
            "humidity": None,
            "co2": None,
            "tvocs": None,
            "pm1": None,
            "pm10": None,
            "pm25": None,
            "formaldehyde": 11.0,
        }

        assert (
            sensor_device.ind_record_build(ind_record_example)
            == expected_record
        )

    def ind_build_datapoint(
        self, sensor_device: InbiotSensor, record, timestamp
    ):
        """Returns a (InfluxDB) datapoint from a record and timestamp"""
        return Point.from_dict(
            {
                "measurement": "CONTINUOUS_MONITORING_",
                "tags": {
                    "AQ": "IAQ",
                    "sensor_id": sensor_device.sensor_id,
                    "id_pilot": sensor_device.pilot,
                    "scenario": sensor_device.scenario,
                    "sub_scenario": sensor_device.sub_scenario,
                    "area": sensor_device.sub_scenario
                    + str(sensor_device.area).zfill(3),
                },
                "fields": record,
                "time": timestamp,
            },
            write_precision="s",
        )
