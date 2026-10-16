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

""" Module for generic Sensor class."""

import logging
import time
from datetime import datetime, timedelta, timezone
from typing import Iterable, Union

import numpy as np
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from modules.config import Config
from modules.exceptions import IngestionError

REQUEST_TIMEOUT = 60


class Sensor:
    """A Sensor is a single device responsible for continuous monitoring in
    the context of K-HEALTHinAIR project.

    Description: an Indoor Data Model and Outdoor Data Model have been
    designed to fix an expected Data Model in the project, any sensor
    manufacturer will transform its own data model to this one.
    """

    # Data Model (Indoor)
    ind_model = {
        "temperature": None,  # Qlair + inBiot
        "humidity": None,  # Qlair + inBiot
        "co2": None,  # Qlair + inBiot
        "tvocs": None,  # Qlair + inBiot
        "pm1": None,  # Qlair + inBiot
        "pm10": None,  # Qlair + inBiot
        "pm25": None,  # Qlair + inBiot
        "formaldehyde": None,  # inBiot
    }
    # Data Model (Outdoor)
    out_model = {
        "out_temperature": None,  # Qlair + Kunak
        "out_humidity": None,  # Qlair + Kunak
        "out_pm25": None,  # Qlair + Kunak
        "out_pm10": None,  # Qlair + Kunak
        "out_no2": None,  # Qlair + Kunak
        "out_o3": None,  # Qlair
        "out_co": None,  # Qlair
        "out_so2": None,  # Qlair
    }

    def __init__(
        self,
        sensor_id: str,
        apikey: str,
        provider: str,
        pilot: str,
        scenario: str,
        sub_scenario: str,
        area: int,
        outdoor_apikey: str,
        building: int,  # Wanted to be moved to 26 characters
        inclusion_time: datetime,
    ):
        self.sensor_id = sensor_id
        self.apikey = apikey
        self.provider = provider
        self.pilot = pilot
        self.scenario = scenario
        self.sub_scenario = sub_scenario
        self.area = area  # str(area).zfill(3)
        self.outdoor_apikey = outdoor_apikey
        self.building = building
        self.inclusion_time = inclusion_time

    def load_datapoint(
        self,
        datapoint_s: Union[Point, Iterable["Point"]],
        influx_client: InfluxDBClient,
    ):
        """Load step of ETL (both Indoor & Outdoor, both Latest & Historical).
        Ingests datapoint (or list of datapoints) into AQDR-TS-DB through and
        InfluxDB Client. Performed per individual sensor for better
        reliability and independence.

        Parameters
        ----------
            datapoints: influxdb_client.Point
            (or list of influxdb_client.Points) from Transform Step.
            influx_client (InfluxDBClient): client for InfluxDB v2.
        """

        writer = influx_client.write_api(write_options=SYNCHRONOUS)

        try:
            # logging.debug(
            #     "      sensorId [%s/%s]: loading datapoint/s into "
            #     + "AQDR-TS-DB org/bucket [%s/%s]",
            #     self.sensor_id[:5] + "...",
            #     self.provider,
            #     influx_client.org,
            #     Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_BUCKET"],
            # )
            writer.write(
                bucket=Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_BUCKET"],
                org=influx_client.org,
                record=datapoint_s,
            )

        except Exception as error:
            raise IngestionError(
                f"sensorId [{self.provider}/{self.sensor_id[:5]}...]"
                + f"/building_id [{self.building}]: "
                + "could not ingest data. "
                + str(error)
            ) from error

    def overwrite_datapoint(self, cached_datapoint: Point):
        """Updates datapoint attributes to copy outdoor record from a sensor
        to another.
        This avoids together with out_cache to request several times the same
        OAQ record.

        Parameters
        ----------
            cached_datapoint: influxdb_client.Point from cache.
        Returns
        -------
            cached_datapoint: influxdb_client.Point updated with specific tags.
        """

        cached_datapoint.tag("id_pilot", self.pilot)
        cached_datapoint.tag("scenario", self.scenario)
        cached_datapoint.tag("sub_scenario", self.sub_scenario)
        cached_datapoint.tag("area", str(self.area).zfill(3))
        cached_datapoint.tag("sensor_id", self.sensor_id)
        return cached_datapoint

    def get_needed_dt_range(self, aq_tag: str, init_ts: int, max_days: int):
        """Extracts needed recovery sub-periods from total datetime range
        needed. Since APIs has limitations with high-range datetime requests,
        a maximum limit can be specified bu max_days to fit sub-periods for
        the requests.

        Parameters
        ----------
            aq_tag (str): {IAQ, OAQ} for logging purposes.
            init_ts (int): initial timestamp from which data has to be
            recovered, in seconds.
            max_days (int): max days for the period.
        Returns
        -------
            periods (list): list of sub-periods (p_init_date, p_end_date) to
            request.
        """
        api_days_limit = timedelta(days=max_days)

        last_dt = datetime.fromtimestamp(init_ts, timezone.utc)
        current_dt = datetime.fromtimestamp(time.time(), timezone.utc)
        needed_period = current_dt - last_dt

        num_subperiods = int(np.ceil(needed_period / api_days_limit))

        if num_subperiods > 0:
            logging.debug(
                "(%s) sensorId [%s/%s]: will recover %s batches "
                + "(of max %s days)",
                aq_tag,
                self.provider,
                self.sensor_id[:5] + "...",
                num_subperiods,
                max_days,
            )

        periods = []
        for n_period in range(num_subperiods):
            p_init_date = last_dt + api_days_limit * n_period
            p_init_date = p_init_date.combine(
                p_init_date, datetime.min.time()
            ).replace(tzinfo=timezone.utc)
            p_end_date = last_dt + api_days_limit * (n_period + 1)
            p_end_date = (
                p_end_date.combine(p_end_date, datetime.max.time())
                - timedelta(days=1)
            ).replace(tzinfo=timezone.utc)
            if p_end_date.date() > current_dt.date():
                p_end_date = current_dt  # qlair API does not accept future ts
            period = (p_init_date, p_end_date)
            periods.append(period)

        return periods
