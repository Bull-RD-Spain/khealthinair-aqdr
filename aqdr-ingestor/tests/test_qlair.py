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

"""Tests for the QlairSensor class and its methods"""

import os
import sys
from datetime import datetime

import pytest
from influxdb_client import Point

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from modules.qlair_sensor import QlairSensor


class TestQlairSensor:
    """Tests for the InbiotSensor class and its methods"""

    @pytest.fixture
    def sensor_device(self):
        """Returns a qlairSensor instance with its description"""
        device = {
            "sensor_id": "35a9c0825cda4c72974ad52c31602639",
            "provider": "MH",
            "apikey": "0f18620e4724794c411388653cb94c09997fa",
            "pilot": "ES",
            "scenario": "HOM",
            "sub_scenario": "HOM01",
            "area": 1,
            "outdoor_apikey": "0f18620e4724794c411388653cb94c09997fa",
            "building": 91,
            "inclusion_time": datetime(2023, 12, 1, 14, 0, 0),
        }
        return QlairSensor(**device)

    @pytest.fixture
    def ind_record_example(self):
        """Returns a (raw) indoor record example from qlair API"""
        return {
            "pmtwoaqi": 0.0,
            "eventdatetime": 1696496539.0,
            "chemisense": {
                "total_aqi": 14,
                "productivity_score": 90.61192805000006,
                "covid": 100.0,
                "voc_ppb": 111.0,
                "comfort_score": 95.86190000000012,
                "cotwo": 447.0,
                "h": 57.0,
                "voc": 4.324999999999999,
                "total_aqi_hundred": 97.11666666666667,
                "ventilation_score": 31.333333333333336,
                "air_cost": 610.0,
                "asthma_score": 100.0,
                "pmtwo": 1.0,
                "mold_score": 100.0,
                "t": 22.0,
                "pmone": 0.6,
                "pmten": 2.0,
                "sensedtimedate": 1696496539.0,
                "Total_AQI": 14,
            },
            "mac": "511f867529b344718c0aeb449e72e1fc",
            "pmtenaqi": 0.0,
        }

    @pytest.fixture
    def historic_ind_record_example(self):
        """Returns a (raw) indoor historic record example from qlair API"""

        # List of dictionary records (from oldest to most recent)
        return [
            {
                "pmtwoaqi": 0.0,
                "eventdatetime": 1685577772.0,
                "chemisense": {
                    "total_aqi": 25,
                    "productivity_score": 89.73843700000003,
                    "covid": 78.57142857142857,
                    "voc_ppb": 3.0,
                    "comfort_score": 90.00530000000008,
                    "cotwo": 409.0,
                    "h": 42.0,
                    "voc": 0.0,
                    "total_aqi_hundred": 95.0,
                    "ventilation_score": 6.000000000000005,
                    "air_cost": 667.0,
                    "asthma_score": 100.0,
                    "pmtwo": 6.0,
                    "mold_score": 100.0,
                    "t": 21.0,
                    "pmone": 3.5999999999999996,
                    "pmten": 6.0,
                    "sensedtimedate": 1685577772.0,
                    "Total_AQI": 25,
                },
                "mac": "a8a371311f184c778df0fd34d0d86e61",
                "pmtenaqi": 0.0,
            },
            {
                "pmtwoaqi": 0.0,
                "eventdatetime": 1685578071.0,
                "chemisense": {
                    "total_aqi": 25,
                    "productivity_score": 89.65036600000003,
                    "covid": 78.57142857142857,
                    "voc_ppb": 16.0,
                    "comfort_score": 90.00530000000008,
                    "cotwo": 412.0,
                    "h": 42.0,
                    "voc": 0.0,
                    "total_aqi_hundred": 95.0,
                    "ventilation_score": 7.9999999999999964,
                    "air_cost": 672.0,
                    "asthma_score": 100.0,
                    "pmtwo": 6.0,
                    "mold_score": 100.0,
                    "t": 21.0,
                    "pmone": 3.5999999999999996,
                    "pmten": 6.0,
                    "sensedtimedate": 1685578071.0,
                    "Total_AQI": 25,
                },
                "mac": "a8a371311f184c778df0fd34d0d86e61",
                "pmtenaqi": 0.0,
            },
        ]

    @pytest.fixture
    def out_record_example(self):
        """Returns a (raw) out record example from qlair API
        Note that .0 will be removed and subsceneraio"""
        return {
            "aqi": {"category": "Good", "type": "airnow", "value": 35.0},
            "eventdatetime": 1682422399.0,
            "facilityname": "03",
            "pollutants": {
                "Total_AQI": 35,
                "co": 0.38,
                "h": 67.0,
                "no2": 7.39,
                "o3": 26.86,
                "pm10": 22.09,
                "pm25": 15.5,
                "pmten": 22.09,
                "pmtwo": 6.066,
                "so2": 0.45,
                "t": 12.0,
                "total_aqi": 35,
            },
            "sensedtimedate": 1682422399,  # int transformation removing .0
            "weather": {"h": 67.0, "t": 12.0},
        }

    @pytest.fixture
    def historic_out_record_example(self):
        """Returns a (raw) outdoor historic record example from qlair API"""

        # List of dictionary records (from oldest to most recent)
        return [
            {
                "aqi": {"category": "Good", "type": "airnow", "value": 35.0},
                "eventdatetime": 1682422399.0,
                "facilityname": "03",
                "pollutants": {
                    "Total_AQI": 35,
                    "co": 0.38,
                    "h": 67.0,
                    "no2": 7.39,
                    "o3": 26.86,
                    "pm10": 22.09,
                    "pm25": 15.5,
                    "pmten": 22.09,
                    "pmtwo": 6.066,
                    "so2": 0.45,
                    "t": 12.0,
                    "total_aqi": 35,
                },
                "sensedtimedate": 1682422399.0,
                "weather": {"h": 67.0, "t": 12.0},
            },
            {
                "aqi": {"category": "Good", "type": "airnow", "value": 35.0},
                "eventdatetime": 1682425699.0,
                "facilityname": "03",
                "pollutants": {
                    "Total_AQI": 35,
                    "co": 2.0,
                    "h": 87.0,
                    "no2": 7.0,
                    "o3": 35.0,
                    "pm10": 6.835,
                    "pm25": 3.801,
                    "pmten": 6.835,
                    "pmtwo": 3.801,
                    "so2": 2.0,
                    "t": 10.0,
                    "total_aqi": 35,
                },
                "sensedtimedate": 1702299500,  # int transformation removing .0
                "weather": {"h": 87, "t": 10.0},
            },
        ]

    def test_ind_transform(
        self, sensor_device: QlairSensor, ind_record_example
    ):
        """Test the transformation of a single indoor record from
        qlair API to InfluxDB datapoint"""
        expected_dp = self.ind_build_datapoint(
            sensor_device,
            sensor_device.ind_record_build(ind_record_example),
            int(ind_record_example["chemisense"]["sensedtimedate"]),
        )
        assert (
            sensor_device.ind_transform(
                ind_record_example, measurement="CONTINUOUS_MONITORING_"
            ).__dict__
            == expected_dp.__dict__
        )

    def test_ind_transform_hist(
        self, sensor_device: QlairSensor, historic_ind_record_example
    ):
        """Test the transformation of a list of indoor historic records into a
        list of Point objects"""
        expected_dps = [
            Point.from_dict(
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
                    "fields": {
                        "temperature": 21.0,
                        "humidity": 42.0,
                        "co2": 409.0,
                        "tvocs": 3.0,
                        "pm1": 3.6,
                        "pm10": 6.0,
                        "pm25": 6.0,
                        "formaldehyde": None,
                    },
                    "time": 1685577772,
                },
                write_precision="s",
            ),
            Point.from_dict(
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
                    "fields": {
                        "temperature": 21.0,
                        "humidity": 42.0,
                        "co2": 412.0,
                        "tvocs": 16.0,
                        "pm1": 3.6,
                        "pm10": 6.0,
                        "pm25": 6.0,
                        "formaldehyde": None,
                    },
                    "time": 1685578071,
                },
                write_precision="s",
            ),
        ]

        # Check length equality of lists
        assert len(
            sensor_device.ind_transform_hist(
                historic_ind_record_example,
                measurement="CONTINUOUS_MONITORING_",
            )
        ) == len(expected_dps)
        # Check all elements in list have same attributes
        assert all(
            [
                actual.__dict__ == expected.__dict__
                for actual, expected in zip(
                    sensor_device.ind_transform_hist(
                        historic_ind_record_example,
                        measurement="CONTINUOUS_MONITORING_",
                    ),
                    expected_dps,
                )
            ]
        )

    def test_ind_build_record(
        self, sensor_device: QlairSensor, ind_record_example
    ):
        """Test the transformation of a single indoor record into a dictionary
        record"""
        expected_record = {
            "temperature": ind_record_example["chemisense"]["t"],
            "humidity": ind_record_example["chemisense"]["h"],
            "co2": ind_record_example["chemisense"]["cotwo"],
            "tvocs": ind_record_example["chemisense"]["voc_ppb"],
            "pm1": ind_record_example["chemisense"]["pmone"],
            "pm10": ind_record_example["chemisense"]["pmten"],
            "pm25": ind_record_example["chemisense"]["pmtwo"],  # REVIEW !!
            "formaldehyde": None,
        }
        assert (
            sensor_device.ind_record_build(ind_record_example)
            == expected_record
        )

    def test_out_transform_to_dp(
        self, sensor_device: QlairSensor, out_record_example
    ):
        """Test the transformation of a single outdoor record from Outdoor API"""
        expected_dp = self.out_build_datapoint(
            sensor_device,
            sensor_device.out_record_build(sensor_device, out_record_example),
            int(out_record_example["sensedtimedate"]),
        )
        assert (
            QlairSensor.out_transform_to_dp(
                sensor_device,
                sensor_device.out_record_build(
                    sensor_device, out_record_example
                ),
                out_record_example["sensedtimedate"],
                measurement="CONTINUOUS_MONITORING_",
            ).__dict__
            == expected_dp.__dict__
        )

    def test_out_transform_to_dp_hist(
        self, sensor_device: QlairSensor, historic_out_record_example
    ):
        """Test the transformation of a list of outdoor historic records
        from qlair API to InfluxDB datapoints"""

        expected_dps = [
            self.out_build_datapoint(
                sensor_device,
                sensor_device.out_record_build(
                    sensor_device, historic_out_record_example[0]
                ),
                int(historic_out_record_example[0]["sensedtimedate"]),
            ),
            self.out_build_datapoint(
                sensor_device,
                sensor_device.out_record_build(
                    sensor_device, historic_out_record_example[1]
                ),
                int(historic_out_record_example[1]["sensedtimedate"]),
            ),
        ]

        # Check length equality of lists
        assert len(
            sensor_device.out_transform_to_dp_hist(
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
                    sensor_device.out_transform_to_dp_hist(
                        sensor_device,
                        historic_out_record_example,
                        measurement="CONTINUOUS_MONITORING_",
                    ),
                    expected_dps,
                )
            ]
        )

    def test_out_record_build(
        self, sensor_device: QlairSensor, out_record_example
    ):
        """Test the transformation of a single outdoor record from qlair API to
        InfluxDB record format"""
        expected_record = {
            "out_temperature": out_record_example["pollutants"]["t"],
            "out_humidity": out_record_example["pollutants"]["h"],
            "out_o3": out_record_example["pollutants"]["o3"],
            "out_pm25": out_record_example["pollutants"]["pm25"],
            "out_pm10": out_record_example["pollutants"]["pmten"],
            "out_co": out_record_example["pollutants"]["co"],
            "out_no2": out_record_example["pollutants"]["no2"],
            "out_so2": out_record_example["pollutants"]["so2"],
        }

        assert (
            sensor_device.out_record_build(sensor_device, out_record_example)
            == expected_record
        )

    def ind_build_datapoint(
        self, sensor_device: QlairSensor, record, timestamp
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

    def out_build_datapoint(
        self, sensor_device: QlairSensor, record, timestamp
    ):
        """Returns a (InfluxDB) datapoint from a record and timestamp"""
        return Point.from_dict(
            {
                "measurement": "CONTINUOUS_MONITORING_",
                "tags": {
                    "AQ": "OAQ",
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
