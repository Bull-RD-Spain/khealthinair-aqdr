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

""" Module for initial backfilling and data recovery utils. """

import logging
from datetime import datetime, timedelta, timezone
from functools import reduce
from typing import Union

import pandas as pd
from influxdb_client import InfluxDBClient
from modules.config import Config
from modules.exceptions import BackFillingError
from modules.inbiot_sensor import InbiotSensor
from modules.kunak_sensor import KunakSensor
from modules.oaq_cache import OAQCache
from modules.qlair_sensor import QlairSensor
from modules.sensor import Sensor

INFLUXDB_MEASUREMENT = Config.aqdr_ts_db["INFLUXDB_MEASUREMENT"]
IND_INBIOT_PERIODICITY = int(Config.IND_INBIOT_PERIODICITY)
IND_QLAIR_PERIODICITY = int(Config.IND_QLAIR_PERIODICITY)
OUTDOOR_PERIODICITY = int(Config.OUTDOOR_PERIODICITY)
KUNAK_BUILDING_IDS = [int(x) for x in Config.KUNAK_BUILDING_IDS]


def initial_backfilling(
    influx_client: InfluxDBClient, registered_sensors: pd.DataFrame
):
    """
    Performs AQDR-TS-DB backfilling processes to recover the last records that
    could have been ommited while the ingestor was stopped.

    1. Extracts last record of each sensor_id registered (for IAQ and OAQ).
    This is done separately since IAQ/OAQ sources could be different for the
    same sensor, so one of them could have failed without affecting the other.
    2. For each device to be considered by *registered_sensors*, extracts the
    timestamp of its last stored record in AQDR-TS-DB.
    3. Checks whether data recovery is actually needed based on the periodicity
    criteria established and available by the data source (recent enough).
    4. If needed, performs data retrieval since the timestamp of last record
    (for IAQ/OAQ separately).

    Parameters
    ----------
        registered_sensors (pd.DataFrame): dataframe of sensor devices
        description to be considered.
        influx_client: client for InfluxDB v2.
    """

    logging.info("_____ AQDR Backfilling processes start...")

    # Get last records for backfilling (IAQ/OAQ separately)
    ind_last_datapoints = _get_last_datapoints_ts_db(
        influx_client, aq_tag="IAQ"
    )
    out_last_datapoints = _get_last_datapoints_ts_db(
        influx_client, aq_tag="OAQ"
    )
    out_last_datapoints_kunak = _get_last_datapoints_ts_db(
        influx_client, aq_tag="OAQ_kunak"
    )

    # Loop sensors to individually check if backfilling is needed
    total_sensors = len(registered_sensors)

    registered_sensors.reset_index(drop=True, inplace=True)
    for index, device in registered_sensors.iterrows():
        logging.info(
            "      sensorId [%s/%s] %s%s%03d Backfilling [%3d/%d]",
            device.PROVIDER,
            device.SENSOR_ID,
            device.PILOT,
            device.SUB_SCENARIO,
            device.AREA,
            index + 1,
            total_sensors,
        )
        sensor = None
        if device.PROVIDER == "IB":
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
        elif device.PROVIDER == "MH":
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
        else:
            logging.error(
                "Sensor Device provider [%s] not a valid one [IB/MH] [%3d/%d]",
                device.PROVIDER,
                index + 1,
                total_sensors,
            )
        if sensor is None:
            continue

        # # 1a. Outdoor Backfilling [qlair]
        # try:
        #     out_last_sensor_ts, out_last_sensor_date = (
        #         _get_last_sensor_timestamp(sensor, out_last_datapoints)
        #     )

        #     if _record_is_recent(
        #         out_last_sensor_ts, recent_period=OUTDOOR_PERIODICITY
        #     ):
        #         logging.info(
        #             "(OAQ) sensorId [%s/%s]: backfilling not needed, "
        #             + "last: %s(%d) [%3d/%d] [qlair]",
        #             sensor.provider,
        #             sensor.sensor_id[:5] + "...",
        #             out_last_sensor_date,
        #             out_last_sensor_ts,
        #             index + 1,
        #             total_sensors,
        #         )
        #     else:
        #         _out_backfilling_pipeline_qlair(
        #             sensor, influx_client, since_ts=out_last_sensor_ts
        #         )

        # except BackFillingError as error:
        #     logging.error(
        #         "(OAQ) sensorId [%s/%s]: backfilling failed (%s) [%3d/%d] ",
        #         sensor.provider,
        #         sensor.sensor_id[:5] + "...",
        #         error.args[0].message,
        #         index + 1,
        #         total_sensors,
        #     )
        #     continue

        # # 1b. Outdoor Backfilling [kunak]
        # # Kunak Paralell serie for NO Pilot
        # if int(sensor.building) in KUNAK_BUILDING_IDS:
        #     try:
        #         out_last_sensor_ts_kunak, out_last_sensor_date_kunak = (
        #             _get_last_sensor_timestamp(
        #                 sensor, out_last_datapoints_kunak
        #             )
        #         )

        #         if _record_is_recent(
        #             out_last_sensor_ts_kunak,
        #             recent_period=OUTDOOR_PERIODICITY,
        #         ):
        #             logging.info(
        #                 "(OAQ) sensorId [%s/%s]: backfilling not needed, "
        #                 + "last: %s(%d) [%3d/%d] [kunak]",
        #                 sensor.provider,
        #                 sensor.sensor_id[:5] + "...",
        #                 out_last_sensor_date_kunak,
        #                 out_last_sensor_ts_kunak,
        #                 index + 1,
        #                 total_sensors,
        #             )
        #         else:
        #             _out_backfilling_pipeline_kunak(
        #                 sensor,
        #                 influx_client,
        #                 since_ts=out_last_sensor_ts_kunak,
        #             )

        #     except BackFillingError as error:
        #         logging.error(
        #             "(OAQ) sensorId [%s/%s]: backfilling failed (%s) [%3d/%d] "
        #             + "[kunak]",
        #             sensor.provider,
        #             sensor.sensor_id[:5] + "...",
        #             error.args[0].message,
        #             index + 1,
        #             total_sensors,
        #         )
        #         continue

        # 2. Indoor Backfilling
        try:
            ind_last_sensor_ts, ind_last_sensor_date = (
                _get_last_sensor_timestamp(sensor, ind_last_datapoints)
            )

            if sensor.provider == "IB" and not _record_is_recent(
                ind_last_sensor_ts,
                recent_period=IND_INBIOT_PERIODICITY,
            ):
                _ind_backfilling_pipeline(
                    sensor, influx_client, since_ts=ind_last_sensor_ts
                )

            elif sensor.provider == "MH" and not _record_is_recent(
                ind_last_sensor_ts, recent_period=IND_QLAIR_PERIODICITY
            ):
                _ind_backfilling_pipeline(
                    sensor, influx_client, since_ts=ind_last_sensor_ts
                )
            else:
                logging.info(
                    "(IAQ) sensorId [%s/%s]: backfilling not needed, "
                    + "last: %s(%d) [%3d/%d]",
                    sensor.provider,
                    sensor.sensor_id[:5] + "...",
                    ind_last_sensor_date,
                    ind_last_sensor_ts,
                    index + 1,
                    total_sensors,
                )
            continue

        except BackFillingError as e:
            logging.error(
                "      sensorId [%s/%s]: backfilling failed [%3d/%d] (%s)",
                sensor.provider,
                sensor.sensor_id[:5] + "...",
                index + 1,
                total_sensors,
                str(e),
            )
            continue

    logging.info("_____ AQDR Backfilling processes finished.")


def _ind_backfilling_pipeline(
    sensor: Union[InbiotSensor, QlairSensor],
    influx_client: InfluxDBClient,
    since_ts: int,
):
    """Runs Indoor Backfilling Pipeline.

    Parameters
    ----------
        - sensor (class.Sensor): Sensor object in [InbiotSensor, QlairSensor].
        - influx_client (InfluxDBClient): client for InfluxDB.
        - since_ts: timestamp of the last (indoor) record stored for the
        specified sensor, from which data will be retrieved.
    """

    # Extract Step
    result = sensor.ind_extract_hist(init_ts=since_ts)
    if result is None or len(result) == 0:
        return

    # Transform Step
    influx_dps = sensor.ind_transform_hist(
        result, measurement=INFLUXDB_MEASUREMENT
    )
    # Load Step
    sensor.load_datapoint(influx_dps, influx_client)
    logging.info(
        "(IAQ) sensorId [%s/%s]: datapoints (%d dps) added",
        sensor.provider,
        sensor.sensor_id[:5] + "...",
        len(influx_dps),
    )


def _out_backfilling_pipeline_qlair(
    sensor: Union[InbiotSensor, QlairSensor],
    influx_client: InfluxDBClient,
    since_ts: int,
):
    """Runs Outdoor Backfilling Pipeline with qlair.

    For all the sensors, qlair will be used to extract the data,
    the data will be extracted from Kunak in a paralell serie,
    so both could be compared to meet one of the analysis objectives

    Parameters
    ----------
        - sensor (class.Sensor): Sensor object in [InbiotSensor, QlairSensor].
        - influx_client (InfluxDBClient): client for InfluxDB.
        - since_ts: timestamp of the last (outdoor) record stored for the
        specified sensor, from which data will be retrieved.
    """

    cache_dps = OAQCache.get_from_cache_all_since(
        "qlair", sensor.building, since_ts
    )
    influx_dps = None

    if not cache_dps or len(cache_dps) == 0:
        # Extract Step
        qlair_records = QlairSensor.out_extract_hist(sensor, init_ts=since_ts)

        if qlair_records and len(qlair_records) != 0:
            # Transform Step
            influx_dps = QlairSensor.out_transform_to_dp_hist(
                sensor,
                qlair_records,
                measurement=INFLUXDB_MEASUREMENT,
            )
    else:
        logging.debug(
            "(OAQ) sensorId [%s/%s]: Using cache (%d dps) for building [%d] "
            + "[qlair]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
            len(cache_dps),
            sensor.building,
        )
        influx_dps = OAQCache.to_influxdb_points(
            cache_dps,
            measurement=INFLUXDB_MEASUREMENT,
            sensor=sensor,
        )

    if influx_dps and len(influx_dps) != 0:
        # Load Step
        sensor.load_datapoint(influx_dps, influx_client)
        logging.info(
            "(OAQ) sensorId [%s/%s]: datapoints (%d dps) added [qlair]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
            len(influx_dps),
        )
    else:
        logging.info(
            "(OAQ) sensorId [%s/%s]: backfilling not needed, "
            + "last: %s(%d) [qlair]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
            datetime.fromtimestamp(since_ts, timezone.utc).strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
            since_ts,
        )


def _out_backfilling_pipeline_kunak(
    sensor: Union[InbiotSensor, QlairSensor],
    influx_client: InfluxDBClient,
    since_ts: int,
):
    """Runs Outdoor Backfilling Pipeline with Kunak.

    For just the buildings related to the specific Kunak sensors,
    the data will be extracted from Kunak in a paralell serie,
    so both could be compared to meet one of the analysis objectives

    Parameters
    ----------
        - sensor (class.Sensor): Sensor object in [InbiotSensor, QlairSensor].
        - influx_client (InfluxDBClient): client for InfluxDB.
        - since_ts: timestamp of the last (outdoor) record stored for the
        specified sensor, from which data will be retrieved, in seconds.
    """

    cache_dps = OAQCache.get_from_cache_all_since(
        "kunak", sensor.building, since_ts
    )
    influx_dps = None

    if not cache_dps or len(cache_dps) == 0:
        # Extract Step
        kunak_records = KunakSensor.out_extract_hist(sensor, init_ts=since_ts)

        if kunak_records and len(kunak_records) != 0:
            # Transform Step
            influx_dps = KunakSensor.out_transform_to_dp_hist(
                sensor,
                kunak_records,
                measurement=INFLUXDB_MEASUREMENT,
            )
    else:
        logging.debug(
            "(OAQ) sensorId [%s/%s]: Using cache (%d dps) for building [%d] "
            + "[kunak].",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
            len(cache_dps),
            sensor.building,
        )
        influx_dps = OAQCache.to_influxdb_points(
            cache_dps,
            measurement=INFLUXDB_MEASUREMENT,
            sensor=sensor,
        )

    if influx_dps and len(influx_dps) != 0:
        # Load Step
        sensor.load_datapoint(influx_dps, influx_client)
        logging.info(
            "(OAQ) sensorId [%s/%s]: datapoints (%d dps) added [kunak]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
            len(influx_dps),
        )
    else:
        logging.info(
            "(OAQ) sensorId [%s/%s]: backfilling not needed, "
            + "last: %s(%d) [kunak]",
            sensor.provider,
            sensor.sensor_id[:5] + "...",
            datetime.fromtimestamp(since_ts, timezone.utc).strftime(
                "%d-%m-%Y %H:%M:%S"
            ),
            since_ts,
        )


# ### Auxiliary functions ### #
def _get_last_datapoints_ts_db(influx_client: InfluxDBClient, aq_tag: str):
    """Extracts all last stored records in InfluxDB per distinct sensor.

    Parameters
    ----------
        influx_client: client for InfluxDB v2.
        aq_tag (str): {IAQ, OAQ} tag to filter records by indoor and outdoor
        separately.
    Returns
    -------
        last_datapoints (pd.DataFrame): last record stored for each sensor in
        AQDR-TS-DB.
    """

    query = f"""from(bucket:
      "{Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_BUCKET"]}")
      |> range(start: 1970-01-01T00:00:00Z, stop: now())
      |> filter(fn: (r) => r._measurement == "{INFLUXDB_MEASUREMENT}")
      |> filter(fn: (r) => r.AQ == "{aq_tag}")
      |> group(columns: ["sensor_id"])
      |> last()
      |> pivot(rowKey: ["_time"], columnKey: ["_field"], valueColumn: "_value")
    """

    try:
        last_datapoints = influx_client.query_api().query_data_frame(
            query, org=influx_client.org
        )

    except Exception as exc:
        raise BackFillingError("Could not connect to AQDR-TS-DB.") from exc

    if isinstance(last_datapoints, list):
        # merges in single dataframe
        last_datapoints = reduce(
            lambda left, right: pd.merge(left, right, how="outer"),
            last_datapoints,
        )

    logging.debug(
        "(%s) Number of sensors with data in the AQDR-TS-DB: %s",
        aq_tag,
        len(last_datapoints),
    )

    return last_datapoints


def _get_last_sensor_timestamp(
    sensor: Sensor, last_datapoints: pd.DataFrame
) -> int:
    """Gets timestamp of last stored record in InfluxDB for a given sensor.

    Parameters
    ----------
        sensor (Sensor): Specific device.
        last_datapoints (pd.DataFrame): all last records in AQDR-TS-DB.
    Returns
    -------
        last_timestamp (int): timestamp of last record in UNIX seconds.
        last_date (str): last_timestamp in date format.
    """

    if (
        last_datapoints.empty
        or ("sensor_id" not in last_datapoints.columns)
        or (sensor.sensor_id not in last_datapoints["sensor_id"].values)
    ):
        # Sensor has never been ingested, use inclusion_time as referene
        last_timestamp = int(sensor.inclusion_time.timestamp())
        # (1677628800) 2023-03-01 OR change to registration day
        # last_date = datetime.fromtimestamp(
        #    last_timestamp, timezone.utc
        # ).strftime("%d-%m-%Y %H:%M:%S")
        last_date = sensor.inclusion_time

        # logging.debug(
        #     "(?AQ) sensorId [%s/%s]: Using inclusion_time %s(%d) "
        #     + "as last_sensor_timestamp...",
        #     sensor.provider,
        #     sensor.sensor_id[:5] + "...",
        #     last_date.strftime("%d-%m-%Y %H:%M:%S"),
        #     last_timestamp,
        # )
        return last_timestamp, last_date

    else:
        # Sensor already in AQDR-TS-DB: search its last stored record timestamp
        last_sensor_record = last_datapoints[
            last_datapoints["sensor_id"] == sensor.sensor_id
        ].iloc[0]
        last_timestamp = int(last_sensor_record["_time"].timestamp())
        last_date = datetime.fromtimestamp(
            last_timestamp, timezone.utc
        ).strftime("%d-%m-%Y %H:%M:%S")

        return last_timestamp, last_date


def _record_is_recent(record_timestamp: int, recent_period: int) -> bool:
    """Checks if given record_timestamp falls in considered "recent enough"
    period (i.e., between *now* and *now - recent_period* backwards).

    Parameters
    ----------
        record_timestamp (int): timestamp of record to check if it is recent.
        recent_period (int): frequency of pipeline, which defines period of
        recent (in minutes).
    Returns
    -------
        True if timestamp is recent enough, False otherwise (so get historic
        data).
    """

    actual_timestamp = datetime.now(timezone.utc)
    record_timestamp = datetime.fromtimestamp(record_timestamp, timezone.utc)
    max_recent_threshold = timedelta(minutes=recent_period)
    lag = actual_timestamp - record_timestamp

    if lag < max_recent_threshold:  # lag falls in considered recent range
        return True
    else:
        return False
