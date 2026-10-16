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
Module with Sensors (Continuous Monitoring) Database functions
Note that in terms od DB, SCENARIO is formed by Type+SubScenario (e.g.: HOM01)
Later in the App, SCENARIO Will be 'HOM', and SUB_SCENARIO 'HOM01'
"""

import logging
from datetime import datetime, timezone
from io import BytesIO

import influxdb_client
import pandas as pd
import psycopg
import requests
from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from modules.config import Config
from modules.enums import Providers

sensors_db_name: str = Config.aqdr_platform_db["SENSORS_DB_NAME"]
sensors_db_table: str = Config.aqdr_platform_db["SENSORS_DB_TABLE"]
sensors_db_user: str = Config.aqdr_platform_db["SENSORS_DB_USER"]
sensors_db_password: str = Config.aqdr_platform_db["SENSORS_DB_PASSWORD"]
sensors_db_host: str = Config.aqdr_platform_db["SENSORS_DB_HOST"]
sensors_db_port: str = Config.aqdr_platform_db["SENSORS_DB_PORT"]

influx_url: str = Config.aqdr_ts_db["INFLUXDB_URL"]
influx_token: str = Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"]
influx_org: str = Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_ORG"]
influx_bucket: str = Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_BUCKET"]
influx_measurement: str = Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"]

REQUEST_TIMEOUT = 60


def _is_sensor_registered(sensor_id: str) -> bool:
    """Checks if a given sensor_id is already registered in the Platform,
    searching in the AQDR-Platform-DB."""
    try:
        conn = psycopg.connect(
            dbname=sensors_db_name,
            user=sensors_db_user,
            password=sensors_db_password,
            host=sensors_db_host,
            port=sensors_db_port,
        )
        cursor = conn.cursor()

        # Search if sensor exists
        cursor.execute(
            "SELECT exists "
            f"(SELECT 1 FROM {sensors_db_table} "
            f"WHERE sensor_id = '{sensor_id}' LIMIT 1)"
        )
        result = cursor.fetchall()
        is_registered = result[0][0]

        cursor.close()
        conn.close()

        return is_registered

    except (Exception, psycopg.DatabaseError) as e:
        raise HTTPException(
            status_code=500, detail="Could not connect to AQDR-Platform-DB."
        ) from e


def check_sensor(sensor: pd.Series):
    """
    Checks POSTED sensor's validity (apikeys) before including in Platform.
    Raises BadRequest Exception if any of them fail."""

    # Check existence in API services
    if sensor.PROVIDER == "IB":
        _check_sensor_existence_ib(sensor.SENSOR_ID, sensor.APIKEY)
    elif sensor.PROVIDER == "MH":
        _check_sensor_existence_qlair(sensor.SENSOR_ID, sensor.APIKEY)
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid Provider [{sensor.PROVIDER}], no IB or MH.",
        )


def register_sensor(
    sensor_id: str,
    apikey: str,
    provider: Providers,
    pilot: str,
    scenario: str,
    area: int,
    outdoor_apikey: str,
    building: int,  # Wanted to be moved to 26 characters.
    inclusion_time: datetime,
):
    """Includes new sensor in AQDR-Platform-DB
    where sensors' description will be stored.
    """
    try:
        conn = psycopg.connect(
            dbname=sensors_db_name,
            user=sensors_db_user,
            password=sensors_db_password,
            host=sensors_db_host,
            port=sensors_db_port,
        )
        cursor = conn.cursor()

        # Insert new sensor in AQDR-Platform-DB
        cursor.execute(
            f"INSERT INTO {sensors_db_table} "
            "(sensor_id, apikey, provider, pilot, scenario, area, "
            "outdoor_apikey, building, inclusion_time) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
            (
                sensor_id,
                apikey,
                provider,
                pilot,
                scenario,
                area,
                outdoor_apikey,
                building,
                inclusion_time.astimezone(timezone.utc).replace(microsecond=0).isoformat(),
                #datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
            ),
        )
        conn.commit()

        cursor.close()
        conn.close()

        logging.info(
            "SensorID [%s] successfully registered in AQDR-Platform-DB.",
            sensor_id,
        )

    except (Exception, psycopg.DatabaseError) as e:
        logging.error(
            "SensorID [%s] could not be registered (%s)", sensor_id, e
        )
        raise HTTPException(
            status_code=500,
            detail=f"SensorID [{sensor_id}] could not be registered.",
        ) from e


def get_sensor_description(sensor_id: str):
    """Retrieves the sensor description."""
    try:
        conn = psycopg.connect(
            dbname=sensors_db_name,
            user=sensors_db_user,
            password=sensors_db_password,
            host=sensors_db_host,
            port=sensors_db_port,
        )
        cursor = conn.cursor(row_factory=psycopg.rows.dict_row)

        cursor.execute(
            f"SELECT * FROM {sensors_db_table} "
            f"WHERE sensor_id = '{sensor_id}'"
        )

        sensor_info = cursor.fetchone()
        sensor_info.pop("inclusion_time")  # removes inclusion_tim

        cursor.close()
        conn.close()

        logging.info("SensorID [%s] description available.", sensor_id)

        return sensor_info

    except (Exception, psycopg.DatabaseError) as e:
        logging.error(
            "SensorID [%s] description could not be retrieved (%s)",
            sensor_id,
            e,
        )

        raise HTTPException(
            status_code=500, detail="Could not connect to AQDR-Platform-DB."
        ) from e


def get_registered_sensors():
    """Retrieves all registered sensors in AQDR-Platform-DB."""
    try:
        conn = psycopg.connect(
            dbname=sensors_db_name,
            user=sensors_db_user,
            password=sensors_db_password,
            host=sensors_db_host,
            port=sensors_db_port,
        )
        cursor = conn.cursor()

        # Select all existing records
        cursor.execute(
            "SELECT sensor_id,apikey,provider,pilot,scenario,area,"
            + f"outdoor_apikey,building,inclusion_time FROM {sensors_db_table}"
        )
        records = cursor.fetchall()

        sensors_data = []
        for sensor in records:
            # sensors_data.append(sensor[:-1])  # skip inclusion_time columns
            sensors_data.append(sensor)

        cursor.close()
        conn.close()

        # Build output dataframe
        sensors_df = pd.DataFrame(
            sensors_data,
            columns=[
                "SENSOR_ID",
                "APIKEY",
                "PROVIDER",
                "PILOT",
                "SCENARIO",
                "AREA",
                "APIKEY_OAQ",
                "BUILDING",
                "INCLUSION_TIME",
            ],
        )

        output_file = BytesIO()
        with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
            sensors_df.to_excel(writer, index=None)

        logging.info(
            "Sensors Description File ready for download. "
            + "Number of registered sensors: {%s}",
            len(sensors_data),
        )

        return StreamingResponse(
            iter([output_file.getvalue()]),
            headers={
                "Content-Disposition": "attachment;filename=K-HEALTHinAIR_AQDR_sensors.xlsx"
            },
        )

    except (Exception, psycopg.DatabaseError) as e:
        logging.error(
            "Could not retrieve sensors from AQDR-Platform-DB (%s)", e
        )
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve sensors from AQDR-Platform-DB.",
        ) from e


def is_sensors_database_empty() -> bool:
    """Checks if AQDR-Platform-DB has at least one sensor device registered."""

    logging.debug(
        "Checking if AQDR-Platform-DB is empty... %s/%s/%s:%s",
        sensors_db_name,
        sensors_db_user,
        sensors_db_host,
        sensors_db_port,
    )
    try:
        conn = psycopg.connect(
            dbname=sensors_db_name,
            user=sensors_db_user,
            password=sensors_db_password,
            host=sensors_db_host,
            port=sensors_db_port,
        )
        cursor = conn.cursor()

        # Search if sensor exists
        cursor.execute(f"SELECT COUNT(*) FROM {sensors_db_table}")

        n_sensors = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if n_sensors > 0:
            return False
        else:
            return True

    except (Exception, psycopg.DatabaseError) as e:
        raise HTTPException(
            status_code=500, detail="Could not connect to AQDR-Platform-DB."
        ) from e


def unregister_sensor(sensor_id: str):
    """Deletes a sensor by its sensor_id from AQDR-Platform-DB."""
    try:
        conn = psycopg.connect(
            dbname=sensors_db_name,
            user=sensors_db_user,
            password=sensors_db_password,
            host=sensors_db_host,
            port=sensors_db_port,
        )
        cursor = conn.cursor()

        # Delete sensor by sensor_id
        cursor.execute(
            f"DELETE FROM {sensors_db_table} WHERE sensor_id = '{sensor_id}'"
        )
        conn.commit()

        if _is_sensor_registered(sensor_id):
            raise HTTPException(
                status_code=500,
                detail=f"SensorID [{sensor_id}]: could not delete unregister.",
            )

        cursor.close()
        conn.close()

        logging.info("SensorID [%s] deleted from AQDR-Platform-DB.", sensor_id)
        return f"SensorID [{sensor_id}] successfully deleted from Platform-DB."

    except (Exception, psycopg.DatabaseError) as e:
        logging.error(
            "SensorID [%s]: could not unregister sensor (%s)",
            sensor_id,
            e,
        )
        raise HTTPException(
            status_code=500,
            detail=f"SensorID [{sensor_id}]: could not unregister sensor.",
        ) from e


def delete_sensor_data(sensor_id: str):
    """Deletes all existing datapoints of specified sensor in TAQDR-TS-DB)"""
    try:
        influx_client = influxdb_client.InfluxDBClient(
            url=influx_url,
            token=influx_token,
            org=influx_org,
        )

        delete_api = influx_client.delete_api()

        # Delete every record of this sensor_id in Time-Series DB
        delete_api.delete(
            start="2023-03-01T00:00:00Z",
            stop="2028-01-01T00:00:00Z",
            predicate=f'_measurement="{influx_measurement}" AND sensor_id="{sensor_id}"',
            bucket=influx_bucket,
            org=influx_org,
        )

        logging.info("SensorID [%s] datapoints deleted from AQDR.", sensor_id)

    except Exception as error:
        logging.error(
            "SensorID [%s]: could not delete datapoints from AQFD-TS-DB (%s)",
            sensor_id,
            error,
        )

        raise HTTPException(
            status_code=500, detail="Could not connect to AQFD-TS-DB."
        ) from error


def _exist_sensor_measurement_in_ts_db(
    sensor_id: str,
    sensor: pd.Series,
    influx_client: influxdb_client.InfluxDBClient,
):
    """Checks if sensor_id is being monitored in AQFD-TS-DB (InfluxDB)"""
    try:
        sensor.SENSOR_ID = influxdb_client.InfluxDBClient(
            url=influx_url,
            token=influx_token,
            org=influx_org,
        )
        query_api = influx_client.query_api()
        results = query_api.query(
            f"""from(bucket: "{influx_bucket}")
                |> range(start: 0)
                |> filter(fn: (r) => r._measurement == "{influx_measurement}")
                |> filter(fn: (r) => r.sensor_id == "{sensor_id}")
            """
        )
        if len(results) > 0:
            return True
        else:
            return False

    except Exception as error:
        raise HTTPException(
            status_code=500, detail="Could not connect to AQFD-TS-DB."
        ) from error


def _loop_checking_sensors():
    """Checks if registered sensors are being monitored in AQFD-TS-DB."""
    try:
        conn = psycopg.connect(
            dbname=sensors_db_name,
            user=sensors_db_user,
            password=sensors_db_password,
            host=sensors_db_host,
            port=sensors_db_port,
        )
        cursor = conn.cursor()

        # Search if sensor exists
        cursor.execute(
            f"(SELECT sensor_id, apikey, provider FROM {sensors_db_table}"
        )

        for sensor in cursor.fetchall():
            sensor_id = sensor[0]
            apikey = sensor[1]
            logging.info("Checking sensor [%s]...", sensor_id)

            if sensor[2] == "IB":
                if not _check_sensor_existence_ib(sensor_id, apikey):
                    logging.error(
                        "Sensor [%s] is NOT being monitored in inBiot API.",
                        sensor_id,
                    )
            elif sensor[2] == "MH":
                if not _check_sensor_existence_qlair(sensor_id, apikey):
                    logging.error(
                        "Sensor [%s] is NOT being monitored in Qlair API.",
                        sensor_id,
                    )
            else:
                logging.info("Provider [%s] not recognized", sensor[2])

        cursor.close()
        conn.close()

    except (Exception, psycopg.DatabaseError) as e:
        raise HTTPException(
            status_code=500, detail="Could not connect to AQDR-Platform-DB."
        ) from e


def _check_sensor_existence_ib(sensor_id: str, apikey: str):
    """Checks if sensor_id is being monitored in inBiot API."""
    endpoint_url = (
        f"{Config.aqdr_platform_db['INBIOT_API_URL']}/last-measurements"
        f"/{apikey}/{sensor_id}"
    )
    res = requests.get(endpoint_url, timeout=REQUEST_TIMEOUT)
    if res.status_code == 200:
        return True
    else:  # https://docs.myinbiotpublicapi.com/#section/Types-of-errors
        if res.content == {"message": "system not found"}:  # 404
            reason = "System not found with this device ID"
        elif res.content == {
            "message": "There are no systems with that apikey"
        }:  # 404
            reason = "System not found with this API Key"
        elif res.content == { # TODO check if we can already trust in codes
            "message": "You have reached the request limit per hour"
        }:  # 429
            reason = "please try again in a while (inBiot: max. req reached)"
        else:
            reason = str(res.reason)
        raise HTTPException(
            status_code=400,
            detail=f"Invalid SensorID [{sensor_id}]: {reason}.",
        )


def _check_sensor_existence_qlair(sensor_id: str, apikey: str):
    """Checks if sensor_id is being monitored in Qlair API."""
    endpoint_url = (
        Config.aqdr_platform_db["QLAIR_API_URL"] + "/open/indoor_air_quality"
    )
    res = requests.get(
        endpoint_url,
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
            status_code=400, detail=f"Invalid SensorID [sensor_id]: {reason}."
        )


def _check_outdoor_air_quality_mh(
    sensor_id: str, outdoor_apikey: str, building
):
    """Checks if sensor_id outdoor data could be retrieved via Qlair API."""
    endpoint_url = str(Config.aqdr_platform_db["QLAIR_API_URL"])
    res = requests.get(
        endpoint_url + "/open/outdoor_air_quality",
        headers={"x-api-key": outdoor_apikey},
        params={"building_id": building},
        timeout=REQUEST_TIMEOUT,
    )

    if res.status_code != 200:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid SensorID [{sensor_id}]: "
            + "please check outdoor_apikey-building matching.",
        )
