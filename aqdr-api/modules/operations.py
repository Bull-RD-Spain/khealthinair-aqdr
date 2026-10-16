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
Module for Air Quality Data Repository Operations
(Extract processes of ETL Pipelines, query, ingest)

1. Functions to test POSTED sensor's description by validating latest record
available of the sensor
2. Back-up pipelines to be executed when POSTED sensor is validated and
registered in Sensors Database
"""

from datetime import datetime, timedelta
import json
import logging
import time
import numpy as np
import pandas as pd
import requests
from influxdb_client import Point, InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

from modules.config import Config

REQUEST_TIMEOUT = 60

###############################################################################
# ############################# BACK-UPS ETL PIPELINES ########################
###############################################################################


class RetrievalError(Exception):
    """There was an error on the AQ Retrieval process (Extract of ETL)."""

    def __init__(self, message):
        self.msg = message


class BackUpError(Exception):
    """There was an error on the back-up process of the sensor."""

    def __init__(self, message):
        self.msg = message


def indoor_backup_pipeline(
    influx_client: InfluxDBClient,
    sensor: pd.Series,
    last_ts: int,
):
    """
    Runs Indoor Back-Up Pipeline.

    Inputs:
        - influx_client: InfluxDBClient instance with url, token, org and bucket
        - sensor: pd.Series that contains all needed info of that sensor
        - last_ts: timestamp of the last indoor record stored for the sensor
    """

    if sensor.PROVIDER == "IB":
        response = extract_inbiot_historic(sensor, since_datetime=last_ts)
        try:
            # Which is the timestamp of its oldest indoor datapoint?
            first_historic_ts = int(
                response["systemData"][0]["measurements"][-1]["date"] / 1000
            )
        except IndexError:
            first_historic_ts = 1677628800  # 2023-03-01

        historic_datapoints = transform_inbiot_historic(
            sensor, historic_result=response
        )
        ingest_historic(influx_client, sensor, dps_list=historic_datapoints)

        logging.debug(
            "(IAQ) sensorId [%s]: back-up completed (%s) dps).",
            sensor.SENSOR_ID,
            len(historic_datapoints),
        )

        return first_historic_ts

    elif sensor.PROVIDER == "MH":
        response = extract_qlair_historic(sensor, since_datetime=last_ts)
        try:
            # Which is the timestamp of its oldest indoor datapoint?
            first_historic_ts = response[0]["chemisense"]["sensedtimedate"]
        except IndexError:
            first_historic_ts = 1677628800  # 2023-03-01

        historic_datapoints = transform_qlair_historic(
            sensor, historic_result=response
        )
        ingest_historic(influx_client, sensor, dps_list=historic_datapoints)
        logging.debug(
            "(IAQ) sensorId [%s]: back-up completed (%s)} dps).",
            sensor.SENSOR_ID,
            len(historic_datapoints),
        )

        return first_historic_ts


def outdoor_backup_pipeline(
    influx_client: InfluxDBClient,
    sensor: pd.Series,
    last_ts: int,
):
    """
    Runs Outdoor Back-Up Pipeline.

    Inputs:
        - influx_client: InfluxDBClient instance with url, token, org and bucket
        - sensor: pd.Series that contains all needed info of that sensor
        - last_ts: timestamp of the last outdoor record stored for the sensor
    """

    historic_result = extract_outdoor_historic(sensor, since_datetime=last_ts)

    if historic_result and len(historic_result) != 0:
        historic_datapoints = transform_outdoor_historic(
            sensor, historic_result
        )
        ingest_historic(influx_client, sensor, dps_list=historic_datapoints)
        logging.debug(
            f"(OAQ) sensorId [{ sensor.SENSOR_ID}]: back-up completed "
            + f"({len(historic_datapoints)} dps)."
        )
    else:
        raise ValueError(
            f"(OAQ) sensorId [{sensor.SENSOR_ID}]: "
            + "could not request historic data."
        )


###############################################################################
# ########################### EXTRACT HISTORICAL RECORDS ######################
###############################################################################


def extract_inbiot_historic(sensor: pd.Series, since_datetime: int) -> dict:
    """
    Retrieves IAQ historical records of a given InBiot sensor from a specified
    datetime. Given from MOST RECENT to OLDEST record.

    Inputs:
        - sensor: pd.Series that contains all needed info of that sensor
        - since_datetime: start datetime to retrieve records, in UNIX seconds
        format

    Output:
        - result: unique dict with GET request response of all records
    """

    try:
        # Dates in format 'YYYY-mm-dd HH:MM:ss'
        start_date = str(datetime.fromtimestamp(since_datetime))
        end_date = datetime.fromtimestamp(time.time()).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        logging.debug(
            "(IAQ) sensorId [%s]: recovering historic data since %s.",
            sensor.SENSOR_ID,
            start_date,
        )

        endpoint_url = (
            Config.aqdr_platform_db["INBIOT_API_URL"]
            + f"/measurements-by-time/{sensor.APIKEY}"
            + f"/{sensor.SENSOR_ID}/{start_date}/{end_date}"
        )
        res = requests.get(endpoint_url, timeout=REQUEST_TIMEOUT)

        if res.status_code != 200:
            raise RetrievalError(
                f"(IAQ) sensorId [{sensor.SENSOR_ID}]: "
                + "could not request historic data."
            )

        result = json.loads(res.content)

        if len(result["systemData"]) == 0:
            logging.error(
                "(IAQ) sensorId [%s}]: no historic data available.",
                sensor.SENSOR_ID,
            )

        return result

    except Exception as error:
        raise RetrievalError(
            f"(IAQ) sensorId [{sensor.SENSOR_ID}]: "
            + "could not request historic data. {error}"
        ) from error


def extract_qlair_historic(
    sensor: pd.Series, since_datetime: int
) -> list[dict]:
    """
    Retrieves IAQ historical records of a given qlair sensor from a datetime.
    Given from OLDEST to MOST RECENT record.

     Inputs:
        - sensor: pd.Series that contains all needed info of that sensor
        - since_datetime: start datetime to retrieve records, in UNIX seconds
        format

    Output:
        - result: list of dicts (i.e. single records) with GET request response
    """

    try:
        endpoint_url = Config.aqdr_platform_db["QLAIR_API_URL"]

        # Dates in format 'YYYY-mm-dd HH:MM:ss': get total range of time needed
        # to recover
        last_dt = datetime.fromtimestamp(since_datetime)
        current_dt = datetime.fromtimestamp(time.time())
        needed_dt_range = current_dt - last_dt

        logging.debug(
            "(IAQ) sensorId [%s]: recovering historic data since %s.",
            sensor.SENSOR_ID,
            last_dt,
        )

        # Qlair API restriction in high-range dt requests: set limit in 15
        # days-period maximum
        qlair_dt_limit = timedelta(days=15)
        # Get number of smaller periods to request historic data - one period
        # at a time
        n_batches = int(np.ceil(needed_dt_range / qlair_dt_limit))
        # List to store every single past record of all subsequent small period
        # requests
        hist_records, dates = list(), list()

        logging.debug(
            "(IAQ) sensorId [%s]: requesting %s batches of "
            + "15 days-length or lower.",
            sensor.SENSOR_ID,
            n_batches,
        )

        # Make one GET request per period until completion of needed_dt_range
        for p in range(n_batches):
            p_init_date = last_dt + qlair_dt_limit * p
            p_end_date = last_dt + qlair_dt_limit * (p + 1)
            res = requests.get(
                endpoint_url,
                headers={"x-api-key": sensor.APIKEY},
                params={
                    "mac": sensor.SENSOR_ID,
                    "start": str(p_init_date),
                    "end": str(p_end_date),
                },
                timeout=REQUEST_TIMEOUT,
            )
            result = json.loads(res.content)

            if result == "No Access":
                continue
            else:
                for record in result:
                    dates.append(
                        datetime.fromtimestamp(
                            record["chemisense"]["sensedtimedate"]
                        )
                    )
                    hist_records.append(record)

        logging.debug(
            "(IAQ) sensorId [%s]: oldest record available %s",
            sensor.SENSOR_ID,
            min(dates),
        )

        return hist_records

    except Exception as error:
        raise RetrievalError(
            f"(IAQ) sensorId [{sensor.SENSOR_ID}]: could not request historic data."
        ) from error


def extract_outdoor_historic(
    sensor: pd.Series, since_datetime: int
) -> list[dict]:
    """
    Retrieves OAQ historical records of a given sensor from a datetime.
    Given from OLDEST to MOST RECENT record.

     Inputs:
        - sensor: pd.Series that contains all needed info of that sensor
        - since_datetime: start datetime to retrieve records, in UNIX seconds
        format

    Output:
        - hist_records_filtered: list of dicts (i.e., single records) with GET
        request response,
        where duplicates are filtered by sensedtimedate
    """

    try:
        endpoint_url = Config.QLAIR_API_URL + "/outdoor_air_quality"

        # Dates in format 'YYYY-mm-dd HH:MM:ss': get total range of time needed
        # to recover
        last_dt = datetime.fromtimestamp(since_datetime)
        current_dt = datetime.fromtimestamp(time.time())
        needed_dt_range = current_dt - last_dt

        logging.debug(
            f"(OAQ) sensorId [{sensor.SENSOR_ID}]: recovering historic data "
            + f"since {last_dt}."
        )

        # Qlair API restriction in high-range dt requests: set limit in 15
        # days-period maximum
        qlair_dt_limit = timedelta(days=15)
        # Get number of smaller periods to request historic data - one period
        # at a time
        n_batches = int(np.ceil(needed_dt_range / qlair_dt_limit))
        # List to store every single past record of all subsequent small period
        # requests
        hist_records = list()

        logging.debug(
            "(OAQ) sensorId [%s]: requesting %s batches of 15 "
            + "days-length or lower.",
            sensor.SENSOR_ID,
            n_batches,
        )

        # Make one GET request per period until completion of needed_dt_range
        for p in range(n_batches):
            p_init_date = last_dt + qlair_dt_limit * p
            p_end_date = last_dt + qlair_dt_limit * (p + 1)
            res = requests.get(
                endpoint_url,
                headers={"x-api-key": sensor.APIKEY_OAQ},
                params={
                    "building_id": sensor.BUILDING,
                    "start": str(p_init_date),
                    "end": str(p_end_date),
                },
                timeout=REQUEST_TIMEOUT,
            )
            result = json.loads(res.content)

            if result == "No Access":
                continue
            else:
                for record in result:
                    hist_records.append(record)

        # Discard redundant records every hour (cache already added ts)
        # and only add record if sensedtimedate is posterior to general
        # since_datetime (since requests are done by eventdatetime and
        # sensedtimedate is desired here [eventdatetime!=sensedtimedate])
        hist_records_filtered, ts, dates = list(), list(), list()

        for rec in hist_records:
            if rec["sensedtimedate"] in ts:
                continue
            elif int(rec["sensedtimedate"]) - since_datetime > 0:
                ts.append(rec["sensedtimedate"])
                dates.append(datetime.fromtimestamp(rec["sensedtimedate"]))
                hist_records_filtered.append(rec)

        if len(dates) > 0:
            logging.debug(
                "(OAQ) sensorId [%s]: oldest record available %s.",
                sensor.SENSOR_ID,
                min(dates),
            )

        return hist_records_filtered

    except Exception as error:
        raise RetrievalError(
            f"(OAQ) sensorId [{sensor.SENSOR_ID}]: could not request historic "
            + "data."
        ) from error


###############################################################################
# ########################## TRANSFORM HISTORICAL RECORDS #####################
###############################################################################


class TransformError(Exception):
    """There was an error on the AQ Transform process (Transform of ETL)."""

    def __init__(self, message):
        self.msg = message


def transform_inbiot_historic(
    sensor: pd.Series, historic_result: dict
) -> list[Point]:
    """
    Processes IAQ InBiot dict of historical records of a given sensor.

    Inputs:
        - sensor: pd.Series that contains all needed info of that sensor
        - historic_result: unique dict with historical records per parameter
          from Extract step

    Output:
        - historic_datapoints: list of datapoints from historical records
          ready to be ingested
    """
    try:
        historic_datapoints = list()
        historic_measurements = historic_result["systemData"]

        for record in historic_measurements:
            param = record["type"]
            param_historic_records = record["measurements"]
            # nb_records = len(param_historic_records)

            if param in IB_MODEL_CORRESPONDENCE.values():
                param_key = list(
                    filter(
                        lambda x: IB_MODEL_CORRESPONDENCE[x] == param,
                        IB_MODEL_CORRESPONDENCE,
                    )
                )[0]
                # Now, for each historic record build a datapoint and append
                for rec in param_historic_records:
                    ts = int(rec["date"] / 1000)
                    # dt = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
                    r = {param_key: float(f"{rec['value']:.2f}")}
                    # Transform each single record with own timestamp to datapoint
                    dp = {
                        "measurement": Config.aqdr_ts_db[
                            "INFLUXDB_MEASUREMENT"
                        ],
                        "tags": {
                            "AQ": "IAQ",
                            "id_pilot": sensor.PILOT,
                            "scenario": sensor.SCENARIO[:3],
                            "sub_scenario": sensor.SCENARIO,
                            "area": str(sensor.SCENARIO)
                            + str(sensor.AREA).zfill(3),
                            "sensor_id": sensor.SENSOR_ID,
                        },
                        "fields": r,
                        "time": ts,
                    }
                    data_point = Point.from_dict(dp, write_precision="s")
                    # Store all datapoints
                    historic_datapoints.append(data_point)

        logging.debug(
            "(IAQ) sensorId [%s]: %s historic records.",
            sensor.SENSOR_ID,
            len(historic_datapoints),
        )
        return historic_datapoints
    except Exception as error:
        raise TransformError(
            f"(IAQ) sensorId [{sensor.SENSOR_ID}]: could not transform historic data."
        ) from error


def transform_qlair_historic(
    sensor: pd.Series, historic_result: list[dict]
) -> list[Point]:
    """
    Processes IAQ qlair list of historical records of a given sensor.

    Inputs:
        - sensor: pd.Series that contains all needed info of that sensor
        - historic_result: list of dicts (i.e., single historical records)
          from Extract step

    Output:
        - historic_datapoints: list of datapoints from historical records
          ready to be ingested
    """

    try:
        # Treat each of the past records retrieved individually and transform
        historic_datapoints = list()

        logging.debug(
            "(IAQ) sensorId [%s]: %s historic records.",
            sensor.SENSOR_ID,
            len(historic_result),
        )

        for result in historic_result:
            datapoint = transform_mannhummel(sensor, req_result=result)
            historic_datapoints.append(datapoint)

        return historic_datapoints

    except Exception as error:
        raise TransformError(
            f"(IAQ) sensorId [{sensor.SENSOR_ID}]: could not transform "
            + "historic data."
        ) from error


def transform_outdoor_historic(
    sensor: pd.Series, historic_result: list[dict]
) -> list[Point]:
    """
    Processes OAQ list of historical records of a given sensor.

    Inputs:
        - sensor: pd.Series that contains all needed info of that sensor
        - historic_result: list of dicts (i.e., single historical records)
          from Extract step

    Output:
        - historic_datapoints: list of datapoints from historical records
          ready to be ingested
    """

    try:
        # Treat each of the past records retrieved individually and transform
        historic_datapoints = list()

        logging.debug(
            "(OAQ) sensorId [%s]: %s historic records.",
            sensor.SENSOR_ID,
            len(historic_result),
        )

        for result in historic_result:
            datapoint = transform_outdoor(sensor, req_result=result)
            historic_datapoints.append(datapoint)

        return historic_datapoints

    except Exception as error:
        raise TransformError(
            f"(OAQ) sensorId [{sensor.SENSOR_ID}]: could not "
            + "transform historic data."
        ) from error


###############################################################################
# ######################### INGEST/LOAD HISTORICAL RECORDS ####################
###############################################################################


class IngestionError(Exception):
    """There was an error on the AQ Ingestion process (Load of ETL)."""

    def __init__(self, message):
        self.msg = message


def ingest_historic(
    influxdb_client, sensor: pd.Series, dps_list: list[Point]
) -> None:
    """
    Ingests provided list of historical datapoints in InfluxDB through
    InfluxDB Client.

    Inputs:
        - influxdb_client: InfluxDBClient instance with DB url, token and org
        - sensor: pd.Series that contains all needed info of that sensor
        - dps_list: list of datapoints of historical records, already pointing
          to a InfluxDB measurement
    """

    write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)

    try:
        write_api.write(
            bucket=influxdb_client.bucket,
            org=influxdb_client.org,
            record=dps_list,
        )

    except Exception as error:
        raise IngestionError(
            f"sensorId [{sensor.SENSOR_ID}]: could not ingest historic data."
        ) from error


def transform_inbiot(sensor: pd.Series, req_result: dict) -> Point:
    """
    Processes IAQ InBiot record of a given sensor.

    Inputs:
        - sensor: pd.Series that contains all needed info of that sensor
        - req_result: raw OAQ record from Extract step

    Output:
        - data_point: datapoint record ready to be ingested
    """

    try:
        record = IAQ_RECORD_SCHEMA.copy()

        for var in req_result["systemData"]:
            param = var["type"]
            if param in IB_MODEL_CORRESPONDENCE.values():
                param_key = list(
                    filter(
                        lambda x: IB_MODEL_CORRESPONDENCE[x] == param,
                        IB_MODEL_CORRESPONDENCE,
                    )
                )[0]
                var_value = var["measurements"][0]["value"]
                record[param_key] = float(f"{var_value:.2f}")

        # Record to datapoint
        dp = {
            "measurement": Config.aqdr_platform_db["INFLUXDB_MEASUREMENT"],
            "tags": {
                "AQ": "IAQ",
                "id_pilot": sensor.PILOT,
                "scenario": sensor.SCENARIO[:3],
                "sub_scenario": sensor.SCENARIO,
                "area": str(sensor.SCENARIO) + str(sensor.AREA).zfill(3),
                "sensor_id": sensor.SENSOR_ID,
            },
            "fields": record,
            "time": int(
                req_result["systemData"][0]["measurements"][0]["date"] / 1000
            ),
        }

        data_point = Point.from_dict(dp, write_precision="s")
        return data_point

    except Exception as error:
        raise TransformError(
            f"(IAQ) sensorId [{sensor.SENSOR_ID}]: could not transform data."
        ) from error


def transform_mannhummel(sensor: pd.Series, req_result: dict) -> Point:
    """
    Processes IAQ qlair record of a given sensor.

    Inputs:
        - sensor: pd.Series that contains all needed info of that sensor
        - req_result: raw OAQ record from Extract step

    Output:
        - dataPoint: datapoint record ready to be ingested
    """

    try:
        record = IAQ_RECORD_SCHEMA.copy()

        for param in req_result["chemisense"].keys():
            if param in MH_MODEL_CORRESPONDENCE.values():
                param_key = list(
                    filter(
                        lambda x: MH_MODEL_CORRESPONDENCE[x] == param,
                        MH_MODEL_CORRESPONDENCE,
                    )
                )[0]
                var_value = req_result["chemisense"][param]
                record[param_key] = float(f"{var_value:.2f}")

        # Record to datapoint
        dp = {
            "measurement": Config.aqdr_platform_db["INFLUXDB_MEASUREMENT"],
            "tags": {
                "AQ": "IAQ",
                "id_pilot": sensor.PILOT,
                "scenario": sensor.SCENARIO[:3],
                "sub_scenario": sensor.SCENARIO,
                "area": str(sensor.SCENARIO) + str(sensor.AREA).zfill(3),
                "sensor_id": sensor.SENSOR_ID,
            },
            "fields": record,
            "time": int(req_result["chemisense"]["sensedtimedate"]),
        }

        data_point = Point.from_dict(dp, write_precision="s")
        return data_point

    except Exception as error:
        raise TransformError(
            f"(IAQ) sensorId [{sensor.SENSOR_ID}]: could not transform data."
        ) from error


def transform_outdoor(
    sensor: pd.Series, req_result: dict, outdoor_cache: dict = None
) -> tuple[Point, dict]:
    """
    Processes raw OAQ record of a given sensor and stores it in temporal cache
    dictionary.

    Inputs:
        - sensor: pd.Series that contains all needed info of that sensor
        - req_result: raw OAQ record from Extract step
        - outdoor_cache: dict with cached records, organized by building
          number (optional: not provided in OAQ historic since cache is not
          sed there)

    Output:
        - dataPoint: datapoint record ready to be ingested
        - outdoor_cache: updated dict with OAQ cached records (opt)
    """
    record = OAQ_RECORD_SCHEMA.copy()

    try:
        for param in req_result["pollutants"].keys():
            if param in OUTDOOR_CORRESPONDENCE.values():
                param_key = list(
                    filter(
                        lambda x: OUTDOOR_CORRESPONDENCE[x] == param,
                        OUTDOOR_CORRESPONDENCE,
                    )
                )[0]
                var_value = req_result["pollutants"][param]
                record[param_key] = (
                    float(f"{var_value:.2f}") if var_value else None
                )

        # Record to datapoint
        dp = {
            "measurement": Config.aqdr_platform_db["INFLUXDB_MEASUREMENT"],
            "tags": {
                "AQ": "OAQ",
                "id_pilot": sensor.PILOT,
                "scenario": sensor.SCENARIO[:3],
                "sub_scenario": sensor.SCENARIO,
                "area": str(sensor.SCENARIO) + str(sensor.AREA).zfill(3),
                "sensor_id": sensor.SENSOR_ID,
            },
            "fields": record,
            "time": int(req_result["sensedtimedate"]),
        }

        data_point = Point.from_dict(dp, write_precision="s")

        if outdoor_cache is not None:  # OAQ latest input
            # Add data_point to outdoor dict cache
            outdoor_cache[sensor.BUILDING] = data_point
            return data_point, outdoor_cache
        else:  # OAQ historic input
            return data_point

    except Exception as error:
        raise TransformError(
            f"(OAQ) sensorId [{sensor.SENSOR_ID}]: could not transform data."
        ) from error


# Data Schema of Indoor and Outdoor parameters supported (hardcoded)
IAQ_RECORD_SCHEMA = {
    "temperature": None,
    "humidity": None,
    "co2": None,
    "tvocs": None,
    "pm1": None,
    "pm10": None,
    "pm25": None,
    "formaldehyde": None,
}

OAQ_RECORD_SCHEMA = {
    "out_temperature": None,
    "out_humidity": None,
    "out_o3": None,
    "out_pm25": None,
    "out_pm10": None,
    "out_co": None,
    "out_no2": None,
    "out_so2": None,
}


# Correspondence K-V pairs (DB varname - IB varname in sensor response)
IB_MODEL_CORRESPONDENCE = {
    "temperature": "temperature",
    "humidity": "humidity",
    "co2": "co2",
    "tvocs": "vocs",
    "pm1": "pm1",
    "pm10": "pm10",
    "pm25": "pm25",
    "formaldehyde": "formaldehyde",
}


# Correspondence K-V pairs (DB varname - MH varname in sensor response)
MH_MODEL_CORRESPONDENCE = {
    "temperature": "t",
    "humidity": "h",
    "co2": "cotwo",
    "tvocs": "voc_ppb",
    "pm1": "pmone",
    "pm10": "pmten",
    "pm25": "pmtwo",
}


# Correspondence K-V pairs (DB varname-varname in Outdoor AQ response) mapping
OUTDOOR_CORRESPONDENCE = {
    "out_temperature": "t",
    "out_humidity": "h",
    "out_o3": "o3",
    "out_pm25": "pm2.5",
    "out_pm10": "pm10",
    "out_co": "co",
    "out_no2": "no2",
    "out_so2": "so2",
}
