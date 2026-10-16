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

""" Module for KunakSensor class.

The Kunak sensors is an outdoor air quality monitoring device that has
been installed in the University of Adger (Grimstad-NO) since outside air
quality data was not available from third-party services as in the rest of the
pilots, located in urban areas. (https://k-healthinair.eu/grimstad/)

The data obtained will be associated with all buildings in the pilot (68 to 72)
and for all the scenarios in the NO pilot
Outdoor parameters with Kunak measurement station:
NO2, VOC, PM1, PM2.5, PM10, temperature, humidity, and pressure

"""

import calendar
import json
import logging
import time
from datetime import datetime, timedelta, timezone

import requests
from influxdb_client import Point
from modules.config import Config
from modules.exceptions import RetrievalError, TransformError
from modules.oaq_cache import OAQCache
from modules.sensor import Sensor

REQUEST_TIMEOUT = 60
endpoint_url = Config.KUNAK_API_URL


class KunakSensor(Sensor):
    """A KunakSensor is a single device for continous monitoring that
    comes from Kunak in the context of K-HEALTHinAIR project.
    For specific info, please see
    `https://kunakair.com/doc/08.Manuals/html/Kunak_APIRest_UserManual_EN.html`.
    """

    # Data Model (Outdoor)
    out_model_kunak = {
        "out_temperature": None,
        "out_humidity": None,
        "out_pm25": None,
        "out_pm10": None,
        "out_no2": None,
        "out_pressure": None,
        "out_vocs": None,
    }

    current_time_ms = round(time.time() * 1000)

    @staticmethod
    def out_extract(sensor: Sensor):
        """Extract step of ETL Outdoor.

        Get reads from: Multiple elements (/reads/fromGroupByTs)
        It returns the reads within the period [ts, +∞)
         - sensors: Array with the sensors tag to get reads
         - ts: The minimum timestamp the returned reads must exceed.
           In milliseconds since January 1, 1970, 00:00:00 GMT
         - number (optional), reads to return. Min: 0, Max: 4000, Default: 1000
           'reads' means a value, if requesting 10 values per ts /10

        Parameters
        ----------
            sensor (Sensor): sensor object.
        Returns
        -------
            records (list of dicts): list of filtered historical records.
        """

        try:
            records = []
            init_date = (
                datetime.now(timezone.utc)
                - timedelta(minutes=(int(Config.OUTDOOR_PERIODICITY) + 1))
            ).replace(microsecond=0)
            init_ts = int(time.mktime(init_date.timetuple()))

            # Make one GET request per small period
            # logging.debug(
            #     "(OAQ) sensorId [%s/%s]/building_id [%d] : request "
            #     + "from %s(%d) [kunak]",
            #     sensor.provider,
            #     sensor.sensor_id[:5] + "...",
            #     sensor.building,
            #     init_date,
            #     calendar.timegm(init_date.timetuple()),
            # )
            res = requests.post(
                endpoint_url
                + "/rest/devices/"
                + Config.KUNAK_API_DEVICE
                + "/reads/fromGroupByTs",
                headers={
                    "Authorization": "Basic " + Config.KUNAK_API_BASIC_AUTH,
                    "Content-Type": "application/json",
                },
                data="{'sensors': "
                + "['Temp ext', 'Humidity ext', 'PM1', 'PM2.5', 'PM10', "
                + "'NO2 GCc', 'VOCs GCc', 'Pressure']"
                + ", 'ts': '"
                + str(init_ts * 1000)
                + "', 'number': 4000}",
                timeout=REQUEST_TIMEOUT,
            )

            if res.status_code != 200:
                # https://kunakair.com/doc/08.Manuals/html
                # /Kunak_APIRest_UserManual_EN.html#_Toc145079303
                logging.error(
                    "(OAQ) building_id [%d]: %s-%s [kunak]",
                    sensor.building,
                    res.status_code,
                    res.reason,
                )
                if res.status_code in [429, 402, 401]:
                    raise RetrievalError(
                        "(OAQ) Error status_code-reason: "
                        + f"{res.status_code}-{res.reason} [kunak]"
                    )

            else:
                result = json.loads(res.content)

                if not isinstance(result, list) and (
                    "Not Found" in result.values()
                    or "Invalid authentication" in result.values()
                    or "Server error" in result.values()
                ):
                    logging.error(
                        "(OAQ) Not Found, Invalid authentication or "
                        + "Server error for building_id [%d]",
                        sensor.building,
                    )
                elif result == [] or len(result) == 0:
                    logging.warning(
                        "(OAQ) sensorId [%s/%s]/building_id [%d]: "
                        + "NO data using such building_id "
                        + "from %s(%d).",
                        sensor.provider,
                        sensor.sensor_id[:5] + "...",
                        sensor.building,
                        calendar.timegm(init_date.timetuple()),
                        init_ts,
                    )
                else:
                    logging.debug(
                        "(OAQ) sensorId [%s/%s]/building_id [%d]: "
                        + "got data from %s(%d): %d records.",
                        sensor.provider,
                        sensor.sensor_id[:5] + "...",
                        sensor.building,
                        init_ts,
                        calendar.timegm(init_date.timetuple()),
                        len(result),
                    )
                    for record in result:
                        records.append(record)

            # Discard redundant records
            records = KunakSensor._keep_just_onthehour(records)

            return records

        except Exception as error:
            raise RetrievalError(
                f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}...]"
                + f"/building_id [{sensor.building}]: "
                + f"could not request data [kunak]: {error}."
            ) from error

    @staticmethod
    def out_extract_hist(sensor: Sensor, init_ts: int):
        """Extract step of ETL Outdoor.

        Get reads fromTo: Multiple elements (/reads/fromToGroupByTs)
        It returns the reads within the period [{starTs},{endTs}]
         - sensors: Array with the sensors tag to get reads
         - startTs: The minimum timestamp the returned reads must exceed.
           In milliseconds since January 1, 1970, 00:00:00 GMT
         - endTs: The minimum timestamp the returned reads must exceed.
           In milliseconds since January 1, 1970, 00:00:00 GMT
         - number (optional), reads to return. Min: 0, Max: 4000, Default: 1000
           'reads' means a value, if requesting 10 values per ts /10

        Parameters
        ----------
            sensor (Sensor): sensor object.
            init_ts (int): timestamp to get data from, in seconds.
        Returns
        -------
            result (list of dicts): list of filtered historical records.
        """

        try:
            hist_records = []

            # Check if is already in OAQ Cache
            init_ts = KunakSensor.get_previous_full_hour(init_ts)

            # Daily given ~288 reads day. Limit 4000/8=500 rec per request
            periods = sensor.get_needed_dt_range(
                aq_tag="OAQ",
                init_ts=init_ts,
                max_days=1,
            )

            index = 0
            for period in periods:
                index += 1
                # Make one GET request per small period
                logging.debug(
                    "(OAQ) sensorId [%s/%s]/building_id [%d]: "
                    + "request %d/%d from %s(%d) to %s(%d) [kunak]",
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

                res = requests.post(
                    endpoint_url
                    + "/rest/devices/"
                    + Config.KUNAK_API_DEVICE
                    + "/reads/fromToGroupByTs",
                    headers={
                        "Authorization": "Basic "
                        + Config.KUNAK_API_BASIC_AUTH,
                        "Content-Type": "application/json",
                    },
                    data="{'sensors': "
                    + "['Temp ext', 'Humidity ext', 'PM1', 'PM2.5', "
                    + "'PM10', 'NO2 GCc', 'VOCs GCc', 'Pressure']"
                    + ", 'startTs': '"
                    + str(calendar.timegm(period[0].timetuple()) * 1000)
                    + "', 'endTs': '"
                    + str(calendar.timegm(period[1].timetuple()) * 1000)
                    + "', 'number': 4000}",
                    timeout=REQUEST_TIMEOUT,
                )

                if res.status_code != 200:
                    # https://kunakair.com/doc/08.Manuals/html
                    # /Kunak_APIRest_UserManual_EN.html#_Toc145079303
                    logging.error(
                        "(OAQ) building_id [%d]: %s-%s [kunak]",
                        sensor.building,
                        res.status_code,
                        res.reason,
                    )
                    if res.status_code in [429, 402, 401]:
                        break  # Abort for this specific sensor,
                        # although it will fail for the following

                    continue  # Abort for this specific period

                else:
                    result = json.loads(res.content)

                    if not isinstance(result, list) and (
                        "Not Found" in result.values()
                        or "Invalid authentication" in result.values()
                        or "Server error" in result.values()
                    ):
                        logging.error(
                            "(OAQ) Not Found, Invalid authentication or "
                            + "Server error for building_id [%d]",
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
                        # logging.info(
                        #     "(OAQ) sensorId [%s/%s]/building_id [%d]: "
                        #     + "got data from %s(%d) to %s(%d): %s records.",
                        #     sensor.provider,
                        #     sensor.sensor_id[:5] + "...",
                        #     sensor.building,
                        #     period[0].strftime('%d-%m-%Y %H:%M'),
                        #     calendar.timegm(period[0].timetuple()),
                        #     period[1].strftime('%d-%m-%Y %H:%M'),
                        #     calendar.timegm(period[1].timetuple()),
                        #     len(result),
                        # )
                        for record in result:
                            hist_records.append(record)

            # Discard redundant records
            hist_records = KunakSensor._keep_just_onthehour(hist_records)

            return hist_records

        except Exception as error:
            raise RetrievalError(
                f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}...]"
                + f"/building_id [{sensor.building}]: "
                + f"could not request data [kunak]: {error}."
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
            sensor (Sensor): sensor object.
            out_record (dict): record to transform.
            out_record_ts (int): timestamp of the record, in seconds.
            measurement (str): name of InfluxDB measurement to add datapoint.
        Returns
        -------
            datapoint: influxdb_client.Point for Load Step.
        """
        try:
            dp = {
                "measurement": measurement,
                "tags": {
                    "AQ": "OAQ_kunak",
                    "sensor_id": sensor.sensor_id,
                    "id_pilot": sensor.pilot,
                    "scenario": sensor.scenario,
                    "sub_scenario": sensor.sub_scenario,
                    "area": sensor.sub_scenario + str(sensor.area).zfill(3),
                },
                "fields": out_record,
                "time": KunakSensor.get_previous_full_hour(int(out_record_ts)),
            }

            datapoint = Point.from_dict(dp, write_precision="s")

            if not OAQCache.exist_in_cache(
                "kunak", sensor.building, int(out_record_ts)
            ):
                OAQCache.insert_oaq_in_cache(
                    "kunak",
                    sensor.building,
                    int(out_record_ts),
                    datapoint._fields,
                )

            return datapoint

        except Exception as error:
            raise TransformError(
                f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}...]"
                + f": could not transform data. {error.args[0]}"
            ) from error

    @staticmethod
    def out_transform_to_dp_hist(
        sensor: Sensor, kunak_records: list[dict], measurement: str
    ):
        """Transform step of ETL Outdoor (Historic).
        Static method since this will be used also for inBiot ones
        Parameters
        ----------
            kunak_records (list of dicts): raw record response from API from
            Extract Step.
              Each Kunak response is a dict with the following keys:
              {
                'ts' = NNNNNNNNNNNNN   <13 digits milliseconds timestamp>
                'PM1'         = {'value':'N.NN','validation':'T','reason':'0'}
                'PM2.5'       = {'value':'N.NN','validation':'T','reason':'0'}
                'PM10'        = {'value':'N.NN','validation':'T','reason':'0'}
                'Temp ext'    = {'value':'N.NN','validation':'T','reason':'0'}
                'NO2 GCc'     = {'value':'N.NN','validation':'T','reason':'0'}
                'Humidity ext'= {'value':'N.NN','validation':'T','reason':'0'}
                'Pressure'    = {'value':'N.NN','validation':'T','reason':'0'}
                'VOCs GCc'    = {'value':'N.NN','validation':'T','reason':'0'}
              }
            measurement (str): name of InfluxDB measurement to add datapoint.
            out_cache (dict): cached datapoints of already-requested buildings
            in same batch iteration of the
            ETL pipeline.
        Returns
        -------
            hist_datapoints: list of influxdb_client.Points for Load Step.
        """

        try:
            # Treat each of the records retrieved individually and transform
            hist_datapoints = []

            for kunak_record in kunak_records:
                out_record = KunakSensor.out_record_build(kunak_record)
                datapoint = KunakSensor.out_transform_to_dp(
                    sensor,
                    out_record,
                    int(kunak_record["ts"]) / 1000,
                    measurement,
                )
                hist_datapoints.append(datapoint)

            logging.debug(
                "(OAQ) sensorId [%s/%s]: %s total historic records [kunak]",
                sensor.provider,
                sensor.sensor_id[:5] + "...",
                len(hist_datapoints),
            )

            return hist_datapoints

        except Exception as error:
            raise TransformError(
                f"(OAQ) sensorId [{sensor.provider}/{sensor.sensor_id[:5]}...]"
                + ": could not transform data."
            ) from error

    @staticmethod
    def out_record_build(kunak_record: dict):
        """Builds out_record according to Data Model.

        Parameters
        ----------
            kunak_record (dict): raw record response from API from Extract Step.
        Returns
        -------
            record (dict): complete record based on Data Model.
            {
                'out_temperature' = N.NN,
                'out_humidity'    = N.NN,
                'out_pm25'        = N.NN,
                'out_pm10'        = N.NN,
                'out_no2'         = N.NN,
                'out_vocs'        = N.NN,
                'out_pressure'    = N.NN
            }
        """

        # Outdoor Linkage w/ Data Model (Note SO2/CO not available in Kunak)
        out_linkage = {
            "out_temperature": "Temp ext",
            "out_humidity": "Humidity ext",
            "out_pm25": "PM2.5",
            "out_pm10": "PM10",
            "out_no2": "NO2 GCc",
            "out_vocs": "VOCs GCc",
            "out_pressure": "Pressure",
        }

        record = KunakSensor.out_model_kunak.copy()
        for poullant in kunak_record:
            if poullant in out_linkage.values():
                p_key = list(
                    filter(
                        lambda x, p=poullant: out_linkage[x] == p,
                        out_linkage,
                    )
                )[0]
                p_value = float(kunak_record[poullant]["value"])
                record[p_key] = float(f"{p_value:.2f}") if p_value else None
            else:
                continue

        return record

    @staticmethod
    def _keep_just_onthehour(kunak_records: list):
        """Extract only one measurements and the closest to on the hour

        Parameters:
        records (list of lists): List of lists, having at least a
        'sensedtimedate' with a epoch timestamp formatted in seconds.

        Returns:
        list of dict: Filtered list of records.
        """

        if kunak_records == []:
            return []

        try:
            for kunak_record in kunak_records:
                record_datetime = datetime.fromtimestamp(
                    int(kunak_record["ts"]) / 1000
                )
                start_of_hour = record_datetime.replace(
                    minute=0, second=0, microsecond=0
                )
                end_of_hour = start_of_hour + timedelta(hours=1)

                # Calculate the difference in minutes
                # with nearest hour to the hour
                diff_start = (
                    abs((record_datetime - start_of_hour).total_seconds()) / 60
                )
                diff_end = (
                    abs((record_datetime - end_of_hour).total_seconds()) / 60
                )
                kunak_record["diff"] = min(diff_start, diff_end)

            # Group by hour to keep only one
            kunak_records.sort(key=lambda x: x["ts"])  # Ensure order
            grouped_by_hour = {}
            for kunak_record in kunak_records:
                hour = datetime.fromtimestamp(
                    int(kunak_record["ts"]) / 1000
                ).strftime("%Y-%m-%d %H")
                if hour not in grouped_by_hour:
                    grouped_by_hour[hour] = []
                grouped_by_hour[hour].append(kunak_record)

            # Find the closets measurement to the hour per group
            closest_to_hour = []
            for hour, group in grouped_by_hour.items():
                closest_record = min(group, key=lambda x: x["diff"])
                closest_to_hour.append(closest_record)

            closest_to_hour.sort(key=lambda x: x["ts"])  # Ensure order
            # Delete 'diff' key added for the process
            for record in closest_to_hour:
                del record["diff"]
                ts_datetime = datetime.fromtimestamp(
                    int(record["ts"] / 1000), tz=timezone.utc
                )
                ts_datetime = ts_datetime.replace(
                    minute=0, second=0, microsecond=0
                )
                record["ts"] = int(ts_datetime.timestamp() * 1000)

            return closest_to_hour

        except Exception as error:
            raise TransformError(
                f"(OAQ) could not filter to _keep_just_onthehour: {error}."
            ) from error

    @staticmethod
    def get_previous_full_hour(ts_seconds):
        """Get the previous full hour timestamp from a given timestamp"""
        dt = datetime.fromtimestamp(ts_seconds)
        hour_point = dt.replace(minute=0, second=0, microsecond=0)
        # If timestamp is exactly on the hour, rest one
        if dt == hour_point:
            hour_point -= timedelta(hours=1)
        return int(hour_point.timestamp())
