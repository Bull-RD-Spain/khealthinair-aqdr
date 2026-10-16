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
""" Module for ETL pipelines (latest)"""

import logging
import time
from datetime import datetime, timedelta, timezone
import pandas as pd
from influxdb_client import InfluxDBClient
from modules.backfilling import _record_is_recent
from modules.config import Config
from modules.oaq_cache import OAQCache
from modules.exceptions import IngestionError, RetrievalError, TransformError
from modules.inbiot_sensor import InbiotSensor
from modules.kunak_sensor import KunakSensor
from modules.qlair_sensor import QlairSensor
from modules.sensor import Sensor

IND_INBIOT_PERIODICITY = int(Config.IND_INBIOT_PERIODICITY)
IND_QLAIR_PERIODICITY = int(Config.IND_QLAIR_PERIODICITY)
OUTDOOR_PERIODICITY = int(Config.OUTDOOR_PERIODICITY)
KUNAK_BUILDING_IDS = [int(x) for x in Config.KUNAK_BUILDING_IDS]


def run_ind_etl_pipeline_inbiot(
    influx_client: InfluxDBClient, registered_sensors: pd.DataFrame
):
    """ETL pipeline for Indoor Air Quality data (inBiot).

    1. Checks for sensor devices updates in AQDR-Platform-DB. If no sensors,
    skip pipeline run. If connection error, cache last stored sensor devices
    description.
    2. For each sensor, perform ETL process for its latest record available.
    If ETL fails, skip sensor and continue to the next one.

    API Usage (https://docs.myinbiotpublicapi.com/#section/API-Usage)
    There are several things that may be taken into account:

    API Key is personal and non-transferable. You must be sure of storing it
    roperly to ensure security.
    Response format is JSON
    Access to API is limited to 6 requests per hour, and this restriction
    applies to each end-point and system individually.
    The maximum time range that can be requested for historical data is 31 days

    Parameters
    ----------
        influx_client: client for InfluxDB v2.
        registered_sensors: DataFrame with registered sensors.
    """

    logging.info("_____ IAQ ETL pipeline [inBiot] started...")
    try:
        num_sensors = len(registered_sensors)

        if num_sensors == 0:
            logging.warning(
                "(IAQ) No inBiot sensors found in AQDR-Platform-DB."
            )
            return
        else:
            logging.info(
                "(IAQ) Found [%s] inBiot sensors in AQDR-Platform-DB",
                num_sensors,
            )

    except RetrievalError:
        logging.warning(
            "(IAQ) Could not connect to AQDR-Platform-DB. "
            + "Skipping pipeline run..."
        )
        return

    if not isinstance(registered_sensors, pd.DataFrame):
        logging.error("registered_sensors is not a DataFrame.")

    total_sensors = len(registered_sensors)
    registered_sensors.reset_index(drop=True, inplace=True)
    for index, device in registered_sensors.iterrows():
        logging.info(
            "(IAQ) sensorId [%s/%s] %s%s%03d (ETL IAQ Pipeline) [%3d/%d] [inBiot].",
            device.PROVIDER,
            device.SENSOR_ID,
            device.PILOT,
            device.SUB_SCENARIO,
            device.AREA,
            index + 1,
            total_sensors,
        )

        sensor = InbiotSensor(
            sensor_id=device.SENSOR_ID,
            apikey=device.APIKEY,
            provider=device.PROVIDER,
            pilot=device.PILOT,
            scenario=device.SCENARIO,
            sub_scenario=device.SUB_SCENARIO,
            area=device.AREA,
            outdoor_apikey=device.APIKEY_OAQ,
            building=device.BUILDING,
            inclusion_time=datetime.fromtimestamp(
                device.INCLUSION_TIME.timestamp(), timezone.utc
            ),
        )

        try:
            # Extract Step
            result = sensor.ind_extract()
            if result is None or len(result) == 0:
                continue

            # Transform Step
            datapoint = sensor.ind_transform(
                result, measurement=Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"]
            )
            # Load Step
            ind_record_ts = int(
                result["systemData"][0]["measurements"][0]["date"] / 1000
            )
            if _record_is_recent(ind_record_ts, IND_INBIOT_PERIODICITY * 2):
                sensor.load_datapoint(datapoint, influx_client)
                logging.info(
                    "(IAQ) sensorId [%s/%s]: datapoint %s(%d) added [inBiot]",
                    sensor.provider,
                    sensor.sensor_id[:5] + "...",
                    datetime.fromtimestamp(
                        ind_record_ts, timezone.utc
                    ).strftime("%d-%m-%Y %H:%M:%S"),
                    ind_record_ts,
                )
            else:
                logging.info(
                    "(IAQ) sensorId [%s/%s]: "
                    + "last datapoint not recent %s(%d) [inBiot]",
                    sensor.provider,
                    sensor.sensor_id[:5] + "...",
                    datetime.fromtimestamp(
                        ind_record_ts, timezone.utc
                    ).strftime("%d-%m-%Y %H:%M:%S"),
                    ind_record_ts,
                )

        except (RetrievalError, TransformError) as e:
            logging.error(e.msg)
            continue
        except IngestionError as e:
            logging.error("(IAQ) %s", e.msg)
            continue

    logging.info("_____ IAQ ETL pipeline [inBiot] finished.")


def run_ind_etl_pipeline_qlair(
    influx_client: InfluxDBClient, registered_sensors: pd.DataFrame
):
    """ETL pipeline for Indoor Air Quality data [qlair].

    1. Checks for sensor devices updates in AQDR-Platform-DB. If no sensors,
    skip pipeline run. If connection error, cache last stored sensor devices
    description.
    2. For each sensor, perform ETL process for its latest record available.
    If ETL fails, skip sensor and continue to the next one.

    Parameters
    ----------
        influx_client: client for InfluxDB v2.
        registered_sensors: DataFrame with registered sensors.
    """

    logging.info("_____ IAQ ETL pipeline [qlair] started...")

    try:
        num_sensors = len(registered_sensors)

        if num_sensors == 0:
            logging.warning("No qlair sensors found in AQDR-Platform-DB.")
            return
        else:
            logging.info(
                "(IAQ) Found [%s] qlair sensors in AQDR-Platform-DB",
                num_sensors,
            )

    except ConnectionError:
        logging.warning(
            "(IAQ) Could not connect to AQDR-Platform-DB. "
            + "Skipping pipeline run..."
        )
        return
    except RetrievalError as e:
        logging.warning(
            "(IAQ) An error occurred while retrieving registered sensors: %s",
            str(e),
        )
        return

    total_sensors = len(registered_sensors)
    registered_sensors.reset_index(drop=True, inplace=True)
    for index, device in registered_sensors.iterrows():
        logging.info(
            "(IAQ) sensorId [%s/%s] %s%s%03d (ETL IAQ Pipeline) [%3d/%d] [qlair].",
            device.PROVIDER,
            device.SENSOR_ID,
            device.PILOT,
            device.SUB_SCENARIO,
            device.AREA,
            index + 1,
            total_sensors,
        )

        sensor = QlairSensor(
            sensor_id=device.SENSOR_ID,
            apikey=device.APIKEY,
            provider=device.PROVIDER,
            pilot=device.PILOT,
            scenario=device.SCENARIO,
            sub_scenario=device.SUB_SCENARIO,
            area=device.AREA,
            outdoor_apikey=device.APIKEY_OAQ,
            building=device.BUILDING,
            inclusion_time=datetime.fromtimestamp(
                device.INCLUSION_TIME.timestamp(), timezone.utc
            ),
        )

        try:
            # Extract Step
            result = sensor.ind_extract()
            if result is None or len(result) == 0:
                continue

            # Transform Step
            datapoint = sensor.ind_transform(
                result, measurement=Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"]
            )
            # Load Step
            ind_record_ts = int(result["chemisense"]["sensedtimedate"])
            if _record_is_recent(ind_record_ts, IND_QLAIR_PERIODICITY * 2):
                sensor.load_datapoint(datapoint, influx_client)
                logging.info(
                    "(IAQ) sensorId [%s/%s]: datapoint %s(%d) added [qlair]",
                    sensor.provider,
                    sensor.sensor_id[:5] + "...",
                    datetime.fromtimestamp(
                        ind_record_ts, timezone.utc
                    ).strftime("%d-%m-%Y %H:%M:%S"),
                    ind_record_ts,
                )
            else:
                logging.info(
                    "(IAQ) sensorId [%s/%s]: "
                    + "last datapoint not recent %s(%d) [qlair]",
                    sensor.provider,
                    sensor.sensor_id[:5] + "...",
                    datetime.fromtimestamp(
                        ind_record_ts, timezone.utc
                    ).strftime("%d-%m-%Y %H:%M:%S"),
                    ind_record_ts,
                )

        except (RetrievalError, TransformError) as e:
            logging.error(e.msg)
            continue
        except IngestionError as e:
            logging.error("(IAQ) %s", e.msg)
            continue

    logging.info("_____ IAQ ETL pipeline [qlair] finished.")


def run_out_etl_pipeline(
    influx_client: InfluxDBClient, registered_sensors: pd.DataFrame
):
    """ETL pipeline for Outdoor Air Quality data (INBIOT & QLAIR).

    1. Checks for sensor devices updates in AQDR-Platform-DB. If no sensors or
    connection error, skip pipeline run.
    2. For each sensor, perform ETL process for its latest record available.
    If ETL fails, skip sensor and continue to the next one.

    In case of being in a building where Kunak sensors is installed, a parallel
    pipeline to ingest such datapoints is executed.

    An OAQ_CACHE dict is maintained to store already queried buildings,
    and each building is first searched in it to check if the record could
    be cached instead of queried again.

    Parameters
    ----------
        influx_client: client for InfluxDB v2.
        registered_sensors: DataFrame with registered sensors.
    """

    logging.info("_____ OAQ ETL pipeline started...")

    try:
        num_sensors = len(registered_sensors)

        if num_sensors == 0:
            logging.warning(
                "(OAQ) No qlair/inBiot sensors found in AQDR-Platform-DB."
            )
            return
        logging.info(
            "(OAQ) Found [%s] qlair/inBiot sensors in AQDR-Platform-DB",
            num_sensors,
        )
    except ConnectionError:
        logging.warning(
            "(OAQ) Could not connect to AQDR-Platform-DB. Skipping pipeline..."
        )
        return

    except TimeoutError:
        logging.warning(
            "(OAQ) Connection to AQDR-Platform-DB timed-out. "
            + "Skipping pipeline..."
        )
        return

    total_sensors = len(registered_sensors)

    registered_sensors.reset_index(drop=True, inplace=True)
    for index, device in registered_sensors.iterrows():
        logging.debug(
            "(OAQ) sensorId [%s/%s] %s%s%03d (ETL OAQ Pipeline) [%3d/%d]",
            device.PROVIDER,
            device.SENSOR_ID,
            device.PILOT,
            device.SUB_SCENARIO,
            device.AREA,
            index + 1,
            total_sensors,
        )

        try:
            sensor = Sensor(
                sensor_id=device.SENSOR_ID,
                apikey=device.APIKEY,
                provider=device.PROVIDER,
                pilot=device.PILOT,
                scenario=device.SCENARIO,
                sub_scenario=device.SUB_SCENARIO,
                area=device.AREA,
                outdoor_apikey=device.APIKEY_OAQ,
                building=device.BUILDING,
                inclusion_time=datetime.fromtimestamp(
                    device.INCLUSION_TIME.timestamp(), timezone.utc
                ),
            )

            init_date = (
                datetime.now(timezone.utc)
                - timedelta(minutes=(int(Config.OUTDOOR_PERIODICITY) + 1))
            ).replace(microsecond=0)
            init_ts = int(time.mktime(init_date.timetuple()))

            _out_etl_pipeline_qlair(influx_client, sensor, init_ts)

            # Kunak Paralell serie for NO Pilot
            if int(sensor.building) in KUNAK_BUILDING_IDS:
                _out_etl_pipeline_kunak(influx_client, sensor, init_ts)

        except (RetrievalError, TransformError) as e:
            logging.error(e.msg)
            continue
        except IngestionError as e:
            logging.error("(OAQ) %s", e.msg)
            continue

    logging.info("_____ OAQ ETL pipeline finished.")


def _out_etl_pipeline_qlair(
    influx_client: InfluxDBClient, sensor: Sensor, init_ts: datetime
):
    """Section dealing with Qlair OAQ data"""
    cache_dps = OAQCache.get_from_cache_all_since(
        "qlair", sensor.building, init_ts
    )
    influx_dps = []

    if cache_dps and len(cache_dps) > 0:
        logging.debug(
            "(OAQ) sensorId [%s/%s]: Using cache (%d dps) for "
            + "building [%d] [qlair]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
            len(cache_dps),
            sensor.building,
        )

        # Transform Step
        influx_dps = OAQCache.to_influxdb_points(
            cache_dps,
            measurement=Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"],
            sensor=sensor,
        )

        # Load Step
        sensor.load_datapoint(influx_dps, influx_client)
        logging.info(
            "(OAQ) sensorId [%s/%s]: datapoint/s added from cache [qlair]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
        )
    else:
        qlair_record = QlairSensor.out_extract(sensor)
        # In case building id DO not exits, will not be pollutant in resutls!
        out_record = QlairSensor.out_record_build(sensor, qlair_record)
        out_record_ts = int(qlair_record["sensedtimedate"])

        # Transform Step
        datapoint = QlairSensor.out_transform_to_dp(
            sensor,
            out_record,
            int(out_record_ts),
            measurement=Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"],
        )

        # Load Step
        sensor.load_datapoint(datapoint, influx_client)
        logging.info(
            "(OAQ) sensorId [%s/%s]: datapoint %s(%d) added [qlair]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
            datetime.fromtimestamp(out_record_ts, timezone.utc).strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
            out_record_ts,
        )


def _out_etl_pipeline_kunak(
    influx_client: InfluxDBClient, sensor: Sensor, init_ts: datetime
):
    """Section dealing with Kunak OAQ data
    In order to limit the number of requests to the Kunak API,
    for any of the Config.KUNAK_BUILDING_IDS move to cache as
    "68" and once recovered, use again the original building id
    """
    cache_dps = OAQCache.get_from_cache_all_since(
        "kunak", sensor.building, init_ts
    )

    influx_dps = []

    if cache_dps and len(cache_dps) > 0:
        logging.debug(
            "(OAQ) sensorId [%s/%s]: Using cache (%d dps) for "
            + "building [%d] [kunak]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
            len(cache_dps),
            sensor.building,
        )

        # Transform Step
        influx_dps = OAQCache.to_influxdb_points(
            cache_dps,
            measurement=Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"],
            sensor=sensor,
        )

        # Load Step
        sensor.load_datapoint(influx_dps, influx_client)
        logging.info(
            "(OAQ) sensorId [%s/%s]: datapoint/s added from cache [kunak]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
        )
    else:
        kunak_records = KunakSensor.out_extract(sensor)
        if len(kunak_records) == 0:
            logging.warning(
                "(OAQ) sensorId [%s/%s]: NO records from kunak",
                sensor.provider,
                sensor.sensor_id[:5] + "...",
            )
        else:
            # Records grouped by ts
            for kunak_record in kunak_records:
                out_record = KunakSensor.out_record_build(kunak_record)
                out_record_ts = int(kunak_record["ts"]) / 1000

                # Transform Step
                influx_dp = KunakSensor.out_transform_to_dp(
                    sensor,
                    out_record,
                    int(out_record_ts),
                    measurement=Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"],
                )
                influx_dps.append(influx_dp)

            if influx_dps and len(influx_dps) != 0:
                # Load Step
                sensor.load_datapoint(influx_dps, influx_client)
                logging.info(
                    "(OAQ) sensorId [%s/%s]: datapoint/s added "
                    + "from cache [kunak]",
                    sensor.provider,
                    sensor.sensor_id[:5] + "...",
                )
