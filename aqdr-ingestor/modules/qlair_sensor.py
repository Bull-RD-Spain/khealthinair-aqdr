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
Module for qlairSensor class.
"""

import calendar
import json
import logging
from datetime import datetime, timedelta

import requests
from fastapi import HTTPException
from influxdb_client import Point
from modules.config import Config
from modules.exceptions import RetrievalError, TransformError
from modules.oaq_cache import OAQCache
from modules.sensor import Sensor

REQUEST_TIMEOUT = 60
endpoint_url = Config.QLAIR_API_URL


class QlairSensor(Sensor):
    """A qlair Sensor is a single device for continous monitoring that
    comes mann-hummel as partner in the context of K-HEALTHinAIR project.
    For specific info, please see `https://api.v2.i-qlair.eu/docs`.
    """

    # Indoor Linkage w/ Data Model
    ind_linkage = {
        "temperature": "t",
        "humidity": "h",
        "co2": "cotwo",
        "tvocs": "voc_ppb",
        "pm1": "pmone",
        "pm10": "pmten",
        "pm25": "pmtwo",  # REVIEW is considered equivalent !!!!
    }

    def ind_extract(self):
        """Extract step of ETL Indoor [qlair].

        Returns
        -------
            result (dict): raw record response from API.
        """

        try:
            # logging.info(
            #  "(IAQ) sensorId [%s/%s]: request last-measurements [qlair]",
            #  self.provider,
            #  self.sensor_id[:5] + "...",
            # )
            res = requests.get(
                endpoint_url + "/open/indoor_air_quality",
                headers={"x-api-key": self.apikey},
                params={"mac": self.sensor_id},
                timeout=REQUEST_TIMEOUT,
            )
            if res.status_code != 200:
                # 400: start parameter is later than the end parameter.
                # 404: building_id parameter no associated known building.
                # 422: Other validation errors
                # 500: Internal Server Error:
                #  probably indicates the reponse size was too large;
                # try again with a start and end closer together.
                # 2 week ranges should be good to use
                raise RetrievalError(
                    f"(IAQ) sensorId [{self.provider}/{self.sensor_id[:5]}..."
                    + f"]: could not request data [qlair]: {res.status_code} -"
                    + f" {res.reason}."
                )

            result = json.loads(res.content)

            if "Not Found" in result.values():
                logging.error(
                    "sensorId [%s/%s]: Not Found",
                    self.provider,
                    self.sensor_id[:5] + "...",
                )
            elif "No Access" in result.values():
                logging.error(
                    "sensorId [%s/%s]: No Access",
                    self.provider,
                    self.sensor_id[:5] + "...",
                )
            return result

        except Exception as error:
            raise RetrievalError(
                f"(IAQ) sensorId [{self.provider}/{self.sensor_id[:5]}...]: "
                + f"could not request data [qlair]: {error}."
            ) from error

    def ind_extract_hist(self, init_ts: int):
        """Extract step of ETL Indoor (qlair, Historic).

        Parameters
        ----------
            init_ts (int): timestamp to get data from.
        Returns
        -------
            result (list of dicts): list of filtered historical records.
        """

        try:
            hist_records = []
            periods = self.get_needed_dt_range(
                aq_tag="IAQ", init_ts=init_ts, max_days=15
            )

            index = 0
            for period in periods:
                index += 1
                # Make one GET request per small period
                logging.info(
                    "(IAQ) sensorId [%s/%s]: request %d/%d "
                    + "from %s(%d) to %s(%d)",
                    self.provider,
                    self.sensor_id[:5] + "...",
                    index,
                    len(periods),
                    period[0].strftime("%d-%m-%Y %H:%M:%S"),
                    calendar.timegm(period[0].timetuple()),
                    period[1].strftime("%d-%m-%Y %H:%M:%S"),
                    calendar.timegm(period[1].timetuple()),
                )

                res = requests.get(
                    endpoint_url + "/open/indoor_air_quality",
                    headers={"x-api-key": self.apikey},
                    params={
                        "mac": self.sensor_id,
                        "start": calendar.timegm(period[0].timetuple()),
                        "end": calendar.timegm(period[1].timetuple()),
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                result = json.loads(res.content)

                if result == [] or result == {}:
                    logging.warning(
                        "(IAQ) sensorId [%s/%s]: No data from %s(%d) "
                        + "to %s(%d)",
                        self.provider,
                        self.sensor_id[:5] + "...",
                        period[0].strftime("%d-%m-%Y %H:%M:%S"),
                        calendar.timegm(period[0].timetuple()),
                        period[1].strftime("%d-%m-%Y %H:%M:%S"),
                        calendar.timegm(period[1].timetuple()),
                    )

                elif ("detail" in result) and (
                    result["detail"].startswith("Not Found")
                ):
                    logging.debug(
                        "(IAQ) sensorId [%s/%s]: Not Found from %s(%d) "
                        + "to %s(%d)",
                        self.provider,
                        self.sensor_id[:5] + "...",
                        period[0].strftime("%d-%m-%Y %H:%M:%S"),
                        calendar.timegm(period[0].timetuple()),
                        period[1].strftime("%d-%m-%Y %H:%M:%S"),
                        calendar.timegm(period[1].timetuple()),
                    )
                    continue
                elif ("detail" in result) and (
                    result["detail"].startswith("No Access")
                ):
                    logging.debug(
                        "(IAQ) sensorId [%s/%s]: No Access from %s(%d) "
                        + "to %s(%d)",
                        self.provider,
                        self.sensor_id[:5] + "...",
                        period[0].strftime("%d-%m-%Y %H:%M:%S"),
                        calendar.timegm(period[0].timetuple()),
                        period[1].strftime("%d-%m-%Y %H:%M:%S"),
                        calendar.timegm(period[1].timetuple()),
                    )
                    continue
                else:
                    # logging.debug(
                    #    "(IAQ) sensorId [%s/%s]: Appending [%s] records for ",
                    #    len(result),
                    #    self.provider,
                    #    self.sensor_id[:5] + "...",
                    # )
                    for record in result:
                        hist_records.append(record)

            return hist_records

        except Exception as error:
            raise RetrievalError(
                f"(IAQ) sensorId [{self.provider}/{self.sensor_id[:5]}...]"
                + f"could not request data [qlair]: {error}."
            ) from error

    def ind_transform(self, response: dict, measurement: str):
        """Transform step of ETL Indoor [qlair].

        Parameters
        ----------
            response (dict): raw record response from API from Extract Step.
            measurement (str): name of InfluxDB measurement to add datapoint.
        Returns
        -------
            datapoint: influxdb_client.Point for Load Step.
        """

        try:
            ind_record = self.ind_record_build(response)
            ind_record_ts = int(response["chemisense"]["sensedtimedate"])

            # Record to datapoint
            dp = {
                "measurement": measurement,
                "tags": {
                    "AQ": "IAQ",
                    "id_pilot": self.pilot,
                    "scenario": self.scenario,
                    "sub_scenario": self.sub_scenario,
                    "area": self.sub_scenario + str(self.area).zfill(3),
                    "sensor_id": self.sensor_id,
                },
                "fields": ind_record,
                "time": ind_record_ts,
            }

            datapoint = Point.from_dict(dp, write_precision="s")
            return datapoint

        except Exception as error:
            raise TransformError(
                f"(IAQ) sensorId [{self.provider}/{self.sensor_id[:5]}...]: "
                + "could not transform data."
            ) from error

    def ind_transform_hist(self, hist_records: list[dict], measurement: str):
        """Transform step of ETL Indoor (qlair, Historic).

        Parameters
        ----------
            hist_records (list of dicts): historical record response from
            Extract Step.
            measurement (str): name of InfluxDB measurement to add datapoint.
        Returns
        -------
            hist_datapoints: list of influxdb_client.Points for Load Step.
        """

        try:
            hist_datapoints = []

            for record in hist_records:
                datapoint = self.ind_transform(record, measurement)
                hist_datapoints.append(datapoint)

            logging.debug(
                "(IAQ) sensorId [%s/%s]: %s total historic records [qlair]",
                self.provider,
                self.sensor_id[:5] + "...",
                len(hist_datapoints),
            )

            return hist_datapoints

        except Exception as error:
            raise TransformError(
                f"(IAQ) sensorId [{self.provider}/{self.sensor_id[:5]}...]: "
                + "could not transform data."
            ) from error

    def ind_record_build(self, response: dict):
        """Builds ind_record according to Data Model.

        Parameters
        ----------
            response (dict): raw record response from API from Extract Step.
        Returns
        -------
            record (dict): complete record based on Data Model.
        """
        record = self.ind_model.copy()
        pollutants = response["chemisense"]

        try:
            for pollutant in pollutants.keys():
                if pollutant in self.ind_linkage.values():
                    p_key = list(
                        filter(
                            lambda x, p=pollutant: self.ind_linkage[x] == p,
                            self.ind_linkage,
                        )
                    )[0]
                    p_value = pollutants[pollutant]
                    if p_value is not None:
                        record[p_key] = float(f"{p_value:.2f}")
                    else:
                        # logging.warning(
                        #    "(IAQ) sensorId [%s/%s]: No Value for [%s] for
                        #    p_key,
                        #    self.provider,
                        #    self.sensor_id[:5] + "...",
                        # )
                        continue
                else:
                    continue
        except TypeError as error:
            raise TransformError(
                f"(IAQ) sensorId [{self.provider}/{self.sensor_id[:5]}...]: "
                + "could not transform data."
            ) from error

        return record

    @staticmethod
    def out_extract(sensor: Sensor):
        """Extract step of ETL Outdoor.

        https://api.v2.i-qlair.eu/docs#/Partner/Partner-get_outdoor_air_quality

        Parameters
        ----------
            sensor (Sensor): sensor object.
        Returns
        -------
            result (dict): raw record response from API.
        """

        try:
            # logging.debug(
            #     "(OAQ) sensorId [%s/%s]/building_id [%d] : requesting [qlair]",
            #     sensor.provider,
            #     sensor.sensor_id[:5] + "...",
            #     sensor.building,
            # )
            res = requests.get(
                endpoint_url + "/open/outdoor_air_quality",
                headers={"x-api-key": sensor.outdoor_apikey},
                params={"building_id": sensor.building},
                timeout=REQUEST_TIMEOUT,
            )

            if res.status_code != 200:
                # 400: start parameter is later than the end parameter.
                # 404: building_id parameter no associated known building.
                # 422: Other validation errors
                # 500: Internal Server Error:
                #  probably indicates the reponse size was too large
                if (
                    b'{"detail":"Building not found Error: building_id'
                    in res.content
                ):
                    raise RetrievalError("building_id not found")
                raise RetrievalError(f"{res.status_code}-{res.reason} [qlair]")

            result = json.loads(res.content)
            return result

        except Exception as error:
            raise RetrievalError(
                f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}...]"
                + f"/building_id [{sensor.building}]: "
                + f"could not request data [qlair]: {error}"
            ) from error

    @staticmethod
    def out_extract_hist(sensor: Sensor, init_ts: int):
        """Extract step of ETL Outdoor.
        https://api.v2.i-qlair.eu/docs#/Partner/Partner-get_outdoor_air_quality
        It returns 24 historical records per day, at the hours!
        so is ideal for storing in cache and use it if set period to 60W!

        Parameters
        ----------
            init_ts (int): timestamp to get data from.
        Returns
        -------
            result (list of dicts): list of filtered hourly historical records.
        """

        try:
            hist_records = []
            periods = sensor.get_needed_dt_range(
                aq_tag="OAQ", init_ts=init_ts, max_days=30
            )

            index = 0
            for period in periods:
                index += 1
                # Make one GET request per small period
                logging.debug(
                    "(OAQ) sensorId [%s/%s]/building_id [%d]: request "
                    + "%d/%d from %s(%d) to %s(%d) [qlair]",
                    sensor.provider,
                    sensor.sensor_id[:5] + "...",
                    sensor.building,
                    index,
                    len(periods),
                    period[0].strftime("%d-%m-%Y %H:%M:%S"),
                    calendar.timegm(period[0].timetuple()),
                    period[1].strftime("%d-%m-%Y %H:%M:%S"),
                    calendar.timegm(period[1].timetuple()),
                )
                res = requests.get(
                    endpoint_url + "/open/outdoor_air_quality",
                    headers={"x-api-key": sensor.outdoor_apikey},
                    params={
                        "building_id": sensor.building,
                        "start": calendar.timegm(period[0].timetuple()),
                        "end": calendar.timegm(period[1].timetuple()),
                    },
                    timeout=REQUEST_TIMEOUT,
                )

                if res.status_code != 200:
                    # 400: start parameter is later than the end parameter.
                    # 404: building_id parameter no associated known building.
                    # 422: Other validation errors
                    # 500: Internal Server Error:
                    #  probably indicates the reponse size was too large
                    if (
                        b'{"detail":"Building not found Error: building_id'
                        in res.content
                    ):
                        logging.error(
                            "(OAQ) building_id [%d]: building_id not found [qlair]",
                            sensor.building,
                        )
                        break  # Abort for this specific sensor
                    logging.error(
                        "(OAQ) building_id [%d]: %s-%s [qlair]",
                        sensor.building,
                        res.status_code,
                        res.reason,
                    )
                    continue  # Abort for this specific period

                else:
                    result = json.loads(res.content)

                    if not isinstance(result, list) and (
                        "Not Found" in result.values()
                        or "No Access" in result.values()
                    ):
                        logging.error(
                            "(OAQ) Not Found / No Access for building_id [%d]",
                            sensor.building,
                        )
                        continue
                    elif result == []:
                        logging.warning(
                            "(OAQ) sensorId [%s/%s]/building_id [%d]: "
                            + "NO data using such building_id "
                            + "from %s(%d) to %s(%d).",
                            sensor.provider,
                            sensor.sensor_id[:5] + "...",
                            sensor.building,
                            period[0].strftime("%d-%m-%Y %H:%M:%S"),
                            calendar.timegm(period[0].timetuple()),
                            period[1].strftime("%d-%m-%Y %H:%M:%S"),
                            calendar.timegm(period[1].timetuple()),
                        )
                        continue
                    else:
                        logging.info(
                            "(OAQ) sensorId [%s/%s]/building_id [%d]: "
                            + "got data from %s(%d) to %s(%d): %d records.",
                            sensor.provider,
                            sensor.sensor_id[:5] + "...",
                            sensor.building,
                            period[0].strftime("%d-%m-%Y %H:%M:%S"),
                            calendar.timegm(period[0].timetuple()),
                            period[1].strftime("%d-%m-%Y %H:%M:%S"),
                            calendar.timegm(period[1].timetuple()),
                            len(result),
                        )
                        for record in result:
                            hist_records.append(record)

            # Discard redundant records
            result = QlairSensor._keep_just_onthehour(hist_records)

            return result

        except Exception as error:
            raise RetrievalError(
                f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}...]"
                + f"/building_id [{sensor.building}]: "
                + f"could not request data [qlair]: {error.args[0]}"
            ) from error

    @staticmethod
    def out_transform_to_dp(
        sensor: Sensor,
        out_record: dict,
        out_record_ts: int,
        measurement: str,
    ):
        """Transform step of ETL Outdoor.

        Parameters
        ----------
            out_record (dict): raw record already transformed from API
            response to the model.
            out_ts (float): the datetime stamp.
            measurement (str): name of InfluxDB measurement to add datapoint.
        Returns
        -------
            datapoint: influxdb_client.Point for Load Step.
        """
        try:
            # Record to datapoint
            dp = {
                "measurement": measurement,
                "tags": {
                    "AQ": "OAQ",
                    "id_pilot": sensor.pilot,
                    "scenario": sensor.scenario,
                    "sub_scenario": sensor.sub_scenario,
                    "area": sensor.sub_scenario + str(sensor.area).zfill(3),
                    "sensor_id": sensor.sensor_id,
                },
                "fields": out_record,
                "time": out_record_ts,
            }

            datapoint = Point.from_dict(dp, write_precision="s")

            if not OAQCache.exist_in_cache(
                "qlair", sensor.building, out_record_ts
            ):
                OAQCache.insert_oaq_in_cache(
                    "qlair", sensor.building, out_record_ts, datapoint._fields
                )

            return datapoint

        except Exception as error:
            raise TransformError(
                f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}"
                + "...]: could not transform data."
            ) from error

    @staticmethod
    def out_transform_to_dp_hist(
        sensor: Sensor, hist_response: list[dict], measurement: str
    ):
        """Transform step of ETL Outdoor (Historic).
        Static method since this will be used also for inBiot ones
        Parameters
        ----------
            hist_response (list of dicts): raw record response from API from
            Extract Step.
            measurement (str): name of InfluxDB measurement to add datapoint.
            out_cache (dict): cached datapoints of already-requested buildings
            in same batch iteration of the
            ETL pipeline.
        Returns
        -------
            hist_datapoints: list of influxdb_client.Points for Load Step.
        """

        try:
            # Treat each of the past records retrieved individually and
            # transform
            hist_datapoints = []

            for response in hist_response:
                out_record = QlairSensor.out_record_build(sensor, response)
                datapoint = QlairSensor.out_transform_to_dp(
                    sensor,
                    out_record,
                    int(response["sensedtimedate"]),
                    measurement,
                )
                hist_datapoints.append(datapoint)

            logging.debug(
                "(OAQ) sensorId [%s/%s]: %s total historic records [qlair]",
                sensor.provider,
                sensor.sensor_id[:5] + "...",
                len(hist_datapoints),
            )

            return hist_datapoints

        except Exception as error:
            raise TransformError(
                f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}"
                + "...]: could not transform data."
            ) from error

    @staticmethod
    def out_record_build(sensor: Sensor, response: dict):
        """Builds out_record according to Data Model.

        Parameters
        ----------
            response (dict): raw record response from API from Extract Step.
        Returns
        -------
            record (dict): complete record based on Data Model
        """

        # Outdoor Linkage w/ Data Model
        out_linkage = {
            "out_temperature": "t",  # Also under 'weather'
            "out_humidity": "h",  # Also under 'weather'
            "out_o3": "o3",
            "out_pm25": "pm25",
            "out_pm10": "pm10",
            "out_co": "co",
            "out_no2": "no2",
            "out_so2": "so2",
        }

        record = sensor.out_model.copy()
        if "pollutants" not in response:
            raise TransformError(
                f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}...]: "
                + "key 'pollutants' not found in response."
            )
        pollutants = response["pollutants"]

        for pollutant in pollutants.keys():
            try:
                if pollutant in out_linkage.values():
                    p_key = list(
                        filter(
                            lambda x, p=pollutant: out_linkage[x] == p,
                            out_linkage,
                        )
                    )[0]
                    p_value = pollutants[pollutant]
                    if p_value is not None:
                        # Here we can apply Conversion Factors between units
                        # https://api.v2.i-qlair.eu/docs#/Partner/Partner-get_outdoor_air_quality
                        # if p_key == "out_o3":
                        #    # Ozone (O3): ppb --> µg/m3 = x2.141
                        #    record[p_key] = float(f"{p_value* 2.141:.2f}")
                        # else:
                        record[p_key] = float(f"{p_value:.2f}")
                    else:
                        # logging.warning(
                        #    "(OAQ) sensorId [%s/%s]: No Value for [%s]",
                        #    p_key,
                        #    sensor.provider,
                        #    sensor.sensor_id[:5] + "...",
                        # )
                        continue
                else:
                    continue

            except TypeError as error:
                raise TransformError(
                    f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}"
                    + "...]: could not transform data."
                ) from error

        return record

    @staticmethod
    def _keep_just_onthehour(records: list):
        """Extract only one measurements and the closest to on the hour

        Parameters:
        records (list of records): List of records, having at least a
        'sensedtimedate' with a epoch timestamp formatted in seconds.

        Returns:
        list of dict: Filtered list of records.
        """

        if records == []:
            return []

        for record in records:
            record_datetime = datetime.fromtimestamp(record["sensedtimedate"])
            start_of_hour = record_datetime.replace(
                minute=0, second=0, microsecond=0
            )
            end_of_hour = start_of_hour + timedelta(hours=1)

            # Calculate the difference in minutes with nearest hour to the hour
            diff_start = (
                abs((record_datetime - start_of_hour).total_seconds()) / 60
            )
            diff_end = (
                abs((record_datetime - end_of_hour).total_seconds()) / 60
            )
            record["diff"] = min(diff_start, diff_end)

        # Group by hour to keep only one
        records.sort(key=lambda x: x["sensedtimedate"])  # Ensure order
        grouped_by_hour = {}
        for record in records:
            hour = datetime.fromtimestamp(record["sensedtimedate"]).strftime(
                "%Y-%m-%d %H"
            )
            if hour not in grouped_by_hour:
                grouped_by_hour[hour] = []
            grouped_by_hour[hour].append(record)

        # Find the closets measurement to the hour per group
        closest_to_hour = []
        for hour, group in grouped_by_hour.items():
            closest_record = min(group, key=lambda x: x["diff"])
            closest_to_hour.append(closest_record)

        # Delete 'diff' key added for the process
        for record in closest_to_hour:
            del record["diff"]

        return closest_to_hour

    @staticmethod
    def _check_sensor_existence_qlair(sensor_id: str, apikey: str):
        """Checks if sensor_id is being monitored in Qlair API."""
        res = requests.get(
            endpoint_url + "/open/indoor_air_quality",
            headers={"x-api-key": apikey},
            params={"mac": sensor_id},
            timeout=REQUEST_TIMEOUT,
        )
        if res.status_code == 200:
            return True
        else:
            if res.content == {"message": "system not found"}:  # 404
                reason = "sensor not found in qlair API"
            elif res.content == {
                "message": "There are no systems with that apikey"
            }:  # 404
                reason = "please check provider or apikey-ID matching"
            else:  # 403 qlair "No Access", unexpected, not considered here
                reason = "please check provider or apikey-ID matching"
            raise HTTPException(
                status_code=400,
                detail=f"Invalid SensorID [sensor_id]: {reason}.",
            )
