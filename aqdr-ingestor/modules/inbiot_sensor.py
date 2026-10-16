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
Module for InbiotSensor class.

API Usage
There are several things that may be taken into account:

API Key is personal and non-transferable. You must be sure of storing it
properly to ensure security. If you have any problem contact support@inbiot.es.
Response format is JSON
Access to API is limited to 6 requests per hour, and this restriction applies
to each end-point and system individually.
The maximum time range per requested for historical data MAX_DAYS_REQUEST.
https://docs.myinbiotpublicapi.com/#section/API-Usage
"""

import calendar
import json
import logging
from datetime import datetime, timezone

import requests
from fastapi import HTTPException
from influxdb_client import Point
from modules.config import Config
from modules.exceptions import RetrievalError, TransformError
from modules.sensor import Sensor

REQUEST_TIMEOUT = 60
MAX_DAYS_REQUEST = 31
endpoint_url = Config.INBIOT_API_URL
inbiot_api_request_limit = int(Config.INBIOT_API_URL_REQUEST_LIMIT)


class InbiotSensor(Sensor):
    """An InbiotSensor is a single device for continous monitoring that comes
    from inBiot Monitoring, S.L. in the context of K-HEALTHinAIR project.
    For specific info, please see `https://en.inbiot.es/`.
    """

    # Indoor Linkage w/ Data Model
    ind_linkage = {
        "temperature": "temperature",
        "humidity": "humidity",
        "co2": "co2",
        "tvocs": "vocs",
        "pm1": "pm1",
        "pm10": "pm10",
        "pm25": "pm25",
        "formaldehyde": "formaldehyde",
    }

    def ind_extract(self):
        """Extract step of ETL Indoor (inBiot).

        Returns
        -------
            result (dict): raw record response from API.
        """
        result = []

        try:
            # Make one GET request per small period
            # logging.info(
            #  "(IAQ) sensorId [%s/%s]: requestst-measurements [inBiot]",
            #  self.provider,
            #  self.sensor_id[:5] + "...",
            # )
            res = requests.get(
                endpoint_url
                + "/last-measurements/"
                + self.apikey
                + "/"
                + self.sensor_id,
                timeout=REQUEST_TIMEOUT,
            )

            result = json.loads(res.content)
            if res.status_code == 200:
                return result
            # https://docs.myinbiotpublicapi.com/#section/Types-of-errors
            else:  # 403, 404, 429, 500
                match res.status_code:
                    case 403:
                        raise RetrievalError(
                            f"{res.status_code}:{res.reason} - "
                            "Authentication error when request sensorId "
                        )
                    case 404:
                        if result == json.loads(
                            '{"message": "measurements not found"}'
                        ):
                            raise RetrievalError(
                                f"{res.status_code}:{res.reason} - "
                                + "measurements not found"
                            )
                        if result == json.loads(
                            '{"message": "system not found"}'
                        ):
                            raise RetrievalError(
                                f"{res.status_code}:{res.reason}"
                            )
                        if result == json.loads(
                            '{"message": "There are no systems with that '
                            + 'apiKey"}'
                        ):
                            raise RetrievalError(
                                f"{res.status_code}:{res.reason} - "
                                + "There are no systems with that apikey"
                            )
                        if result == json.loads(
                            '{"message": "Please reduce the time range"}'
                        ):
                            raise RetrievalError(
                                f"{res.status_code}:{res.reason} - "
                                + "Please reduce the time range"
                            )
                        raise RetrievalError(f"{res.status_code}:{res.reason}")
                    case 429: # TODO check if we can already trust in codes
                        if result == {
                            "message": "You have reached the request limit "
                            + "per hour"
                        }:
                            raise RetrievalError(
                                f"{res.status_code}:Request limit reached"
                            )
                        raise RetrievalError(f"{res.status_code}:{res.reason}")
                    case 500 | 502 | 504:
                        raise RetrievalError(
                            f"{res.status_code}:{res.reason} - Server "
                            + "Exception"
                        )
                    case _:
                        raise RetrievalError(f"{res.status_code}:{res.reason}")

            return result

        except Exception as error:
            raise RetrievalError(
                f"(IAQ) sensorId [{self.provider}/{self.sensor_id[:5]}"
                + "...]: could not request data [inBiot]: "
                + str(error)
            ) from error

    def ind_extract_hist(self, init_ts: int):
        """Extract step of ETL Indoor (inBiot, Historic).

        Parameters
        ----------
            init_ts (int): timestamp to get data from.
        Returns
        -------
            result (dict): raw record response from API.
        """

        try:
            logging.debug(
                "(IAQ) sensorId [%s/%s]: "
                + "recovering historic data since %s(%d)",
                self.provider,
                self.sensor_id[:5] + "...",
                datetime.fromtimestamp(init_ts, timezone.utc).strftime(
                    "%d-%m-%Y %H:%M:%S"
                ),
                init_ts,
            )

            hist_records = []
            periods = self.get_needed_dt_range(
                aq_tag="IAQ", init_ts=init_ts, max_days=MAX_DAYS_REQUEST
            )

            if len(periods) > inbiot_api_request_limit:
                logging.error(
                    "(IAQ) sensorId [%s/%s]: The number of periods [%s] of "
                    + "max %s days required will reach, including 2 auxiliar, "
                    + "the limit of %s requests per hour/system/endpoint. "
                    + "Reducing it to %s in this iteration still will result "
                    + "in incomplete backfilling",
                    self.provider,
                    self.sensor_id[:5] + "...",
                    len(periods),
                    MAX_DAYS_REQUEST,
                    inbiot_api_request_limit,
                    inbiot_api_request_limit-2
                )
                # TODO: Note this is an incomplete backfilling but considered
                #       better than keeping insisting on the same periods
                if inbiot_api_request_limit != 0:
                    periods = periods[:inbiot_api_request_limit-2]
                else:
                    logging.error(
                        "(IAQ) sensorId [%s/%s]: inBiot API request limit is "
                        + "set to 0, so no limitation will be applied.",
                        self.provider,
                        self.sensor_id[:5] + "...",
                    )
                    return hist_records

            index = 0
            for period in periods:
                index += 1
                # Make one GET request per the supported small period
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
                    f"{endpoint_url}/measurements-by-time"
                    f"/{self.apikey}/{self.sensor_id}"
                    f"/{period[0].strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}"
                    f"/{period[1].strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3]}",
                    timeout=REQUEST_TIMEOUT,
                )

                result = json.loads(res.content)
                if res.status_code == 200:
                    if len(result["systemData"]) == 0:
                        logging.debug(
                            "(IAQ) sensorId [%s/%s]: no historic data "
                            + "available",
                            self.provider,
                            self.sensor_id[:5] + "...",
                        )
                        continue
                    # logging.debug(
                    #    "(IAQ) sensorId [%s/%s]: Appending [%s] records ",
                    #    len(result["systemData"]),
                    #    self.provider,
                    #    self.sensor_id[:5] + "...",
                    # )
                    for record in result["systemData"]:
                        hist_records.append(record)
                # https://docs.myinbiotpublicapi.com/#section/Types-of-errors
                else:  # 403, 404, 429, 500
                    match res.status_code:
                        case 403:
                            logging.debug(
                                "(IAQ) sensorId [%s/%s]: Authentication error "
                                + "request sensorId. %s:%s",
                                self.provider,
                                self.sensor_id[:5] + "...",
                                res.status_code,
                                res.reason,
                            )
                            break  # Skip periods for loop for the sensor
                        case 404:
                            # Skip sensor or just period depending on the error
                            if result == json.loads(
                                '{"message": "measurements not found"}'
                            ):
                                logging.warning(
                                    "(IAQ) sensorId [%s/%s]: measurements not "
                                    + "found. %s:%s",
                                    self.provider,
                                    self.sensor_id[:5] + "...",
                                    res.status_code,
                                    res.reason,
                                )
                                continue  # Try next period
                            if result == json.loads(
                                '{"message": "system not found"}'
                            ):
                                logging.debug(
                                    "(IAQ) sensorId [%s/%s]: System not found "
                                    + "with such apiKey/sensorId: %s:%s",
                                    self.provider,
                                    self.sensor_id[:5] + "...",
                                    res.status_code,
                                    res.reason,
                                )
                                break  # Skip periods for loop for thie sensor
                            if result == json.loads(
                                '{"message":'
                                + ' "There are no systems with that "apiKey"}'
                            ):
                                logging.debug(
                                    "(IAQ) sensorId [%s/%s]: There are no "
                                    + "systems with such apiKey/sensorId: "
                                    + "%s:%s",
                                    self.provider,
                                    self.sensor_id[:5] + "...",
                                    res.status_code,
                                    res.reason,
                                )
                                break  # Skip periods for loop for thie sensor
                            if result == json.loads(
                                '{"message": "Please reduce the time range"}'
                            ):
                                logging.debug(
                                    "(IAQ) sensorId [%s/%s]: Please reduce the"
                                    " time range request. %s:%s",
                                    self.provider,
                                    self.sensor_id[:5] + "...",
                                    res.status_code,
                                    res.reason,
                                )
                                break  # Skip periods for loop for the sensor
                            logging.debug(
                                "(IAQ) sensorId [%s/%s]: error. %s:%s",
                                self.provider,
                                self.sensor_id[:5] + "...",
                                res.status_code,
                                res.reason,
                            )
                            break  # Skip periods for loop for the sensor
                        case 429: # TODO check if we can already trust in codes
                            if result == {
                                "message": "You have reached the request "
                                + "limit per hour"
                            }:
                                logging.warning(
                                    "(IAQ) sensorId [%s/%s]: request limit "
                                    + "reached [inBiot]",
                                    self.provider,
                                    self.sensor_id[:5] + "...",
                                )
                                break  # Skip periods for loop for the sensor
                            logging.warning(
                                "(IAQ) sensorId [%s/%s]: error [inBiot]",
                                self.provider,
                                self.sensor_id[:5] + "...",
                            )
                            break  # Skip periods for loop for the sensor
                        case 500 | 502 | 504:
                            logging.warning(
                                "(IAQ) sensorId [%s/%s]: Server Exception: %s:"
                                + "%s [inBiot]",
                                self.provider,
                                self.sensor_id[:5] + "...",
                                res.status_code,
                                res.reason,
                            )
                            continue  # Try next period
                        case _:
                            logging.debug(
                                "(IAQ) sensorId [%s/%s]: could not request "
                                + "data [inBiot]: %s:%s",
                                self.provider,
                                self.sensor_id[:5] + "...",
                                res.status_code,
                                res.reason,
                            )
                            continue

            return hist_records

        except Exception as error:
            raise RetrievalError(
                f"(IAQ) sensorId [{self.provider}/{self.sensor_id[:5]}...]: "
                + "could not request data [inBiot]."
            ) from error

    def ind_transform(self, response: dict, measurement: str):
        """Transform step of ETL Indoor (inBiot).

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
            # date is common for all measurements in the record
            ind_record_ts = int(
                response["systemData"][0]["measurements"][0]["date"] / 1000
            )

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

    def ind_transform_hist(self, hist_records: dict, measurement: str):
        """Transform step of ETL Indoor (inBiot, Historic).

        Parameters
        ----------
            response (dict): historical records response from API from Extract
            Step.
            measurement (str): name of InfluxDB measurement to add datapoint.
        Returns
        -------
            hist_datapoints: list of influxdb_client.Points for Load Step.
        """

        try:
            hist_datapoints = []

            # Here, sorted by pollutant
            for pollutant in hist_records:
                p = pollutant["type"]
                p_records = pollutant["measurements"]

                if p in self.ind_linkage.values():
                    p_key = None
                    for key, value in self.ind_linkage.items():
                        if value == p:
                            p_key = key
                            break

                    # For each historic record, build a datapoint
                    for rec in p_records:
                        if rec["value"] is None:
                            # logging.warning(
                            #    "(IAQ) sensorId [%s/%s]: skip record with "
                            #    "'None' value: %s %s",
                            #    self.provider,
                            #    self.sensor_id[:5] + "...",
                            #    p_key, rec,
                            # )
                            # p_value = 0
                            continue  # skip rec/datapoint
                        p_value = rec["value"]
                        ind_record = {p_key: float(f"{p_value:.2f}")}
                        # outdoor/indoor detecion in portable sensors
                        if (
                            "outdoor" in rec
                            and rec["outdoor"] is not None
                            and rec["outdoor"] == "true"
                        ):
                            ind_record["outdoor"] = float(1)

                        ind_record_ts = int(rec["date"] / 1000)

                        # Transform each single record with own timestamp to
                        # datapoint
                        dp = {
                            "measurement": measurement,
                            "tags": {
                                "AQ": "IAQ",
                                "id_pilot": self.pilot,
                                "scenario": self.scenario,
                                "sub_scenario": self.sub_scenario,
                                "area": self.sub_scenario
                                + str(self.area).zfill(3),
                                "sensor_id": self.sensor_id,
                            },
                            "fields": ind_record,
                            "time": ind_record_ts,
                        }

                        datapoint = Point.from_dict(dp, write_precision="s")
                        hist_datapoints.append(datapoint)

            logging.debug(
                "(IAQ) sensorId [%s/%s]: %s total historic records [inBiot]",
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

    def ind_record_build(self, response):
        """Builds ind_record according to Data Model.

        Parameters
        ----------
            response (str): raw record response from API from Extract Step.
        Returns
        -------
            record (dict): complete record based on Data Model.
        """
        record = self.ind_model.copy()
        pollutants = response["systemData"]
        param = None

        try:
            for pollutant in pollutants:
                param = pollutant["type"]
                if param in self.ind_linkage.values():
                    param_key = list(
                        filter(
                            lambda x, param=param: self.ind_linkage[x]
                            == param,
                            self.ind_linkage,
                        )
                    )[0]
                    p_value = pollutant["measurements"][0]["value"]

                    if p_value is not None:
                        record[param_key] = float(f"{p_value:.2f}")
                        # outdoor/indoor detecion in portable sensors
                        if (
                            "outdoor" in pollutant["measurements"][0]
                            and pollutant["measurements"][0]["outdoor"]
                            is not None
                            and pollutant["measurements"][0]["outdoor"]
                            == "true"
                        ):
                            record["outdoor"] = float(1)

                    else:
                        # logging.warning(
                        #    "(IAQ) sensorId [%s/%s]: No Value for [%s] for "
                        #    + "date %s",
                        #    param_key,
                        #    self.provider,
                        #    self.sensor_id[:5] + "...",
                        #    pollutant["measurements"][0]["date"],
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
    def _check_sensor_existence_ib(sensor_id: str, apikey: str):
        """Checks if sensor_id is being monitored in inBiot API."""
        res = requests.get(
            endpoint_url + "/last-measurements/" + apikey + "/" + sensor_id,
            timeout=REQUEST_TIMEOUT,
        )
        if res.status_code == 200:
            return True
        else:  # https://docs.myinbiotpublicapi.com/#section/Types-of-errors
            if res.content == {"message": "system not found"}:  # 404
                reason = "System not found with this device ID"
            elif res.content == {
                "message": "There are no systems with that apikey"
            }:  # 404
                reason = "System not found with this API Key"
            elif res.content == {
                "message": "You have reached the request limit per hour"
            }:  # 429 # TODO check if we can already trust in codes
                reason = (
                    "please try again in a while (inBiot: max. req reached)"
                )
            else:
                reason = str(res.reason)
            raise HTTPException(
                status_code=400,
                detail=f"Invalid SensorID [{sensor_id}]: {reason}.",
            )
