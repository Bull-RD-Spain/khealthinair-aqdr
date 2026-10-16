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

# -*- coding: utf-8 -*-
"""Air Quality Data Repository Ingestor

Script to automate IAQ and OAQ measurements periodic ingestion in InfluxDB
(ETL Pipelines) from air quality devices third party API services.
"""

import logging
import os
import sys
import time

import influxdb_client
import schedule
from modules.backfilling import initial_backfilling
from modules.config import Config
from modules.etl_flows import (
    run_ind_etl_pipeline_inbiot,
    run_ind_etl_pipeline_qlair,
    run_out_etl_pipeline,
)
from modules.exceptions import IngestionError, RetrievalError, TransformError
from modules.kunak_sensor import KunakSensor
from modules.sensor import Sensor
from modules.sensors_db import (
    get_registered_sensors,
    is_sensors_database_empty,
)


def run_ingestor():
    """
    Stands up Air Quality Data Repository Ingestor and schedules ETL pipelines.

    1. Setup client for Time-Series Database (InfluxDBClient).
    2. Load registered sensors in the AQDR-Platform-DB.
    3. Performs historical data retrieval of sensors on stand-up (backfilling).
    4. Runs initial batch iteration of automated ETL pipelines.
    5. Schedules automated runs of ETL processes (sensors updates on-the-fly).
    """

    # 1. Setup client for AQDR-TS-DB (InfluxDBClient).
    influx_client = influxdb_client.InfluxDBClient(
        url=Config.aqdr_ts_db["INFLUXDB_URL"],
        token=Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"],
        org=Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_ORG"],
    )

    if is_sensors_database_empty():
        raise RetrievalError("No sensors registerd found in the "
        + "AQDR-Platform-DB.")
    else:
        logging.info("(IAQ): %s", list(Sensor.ind_model.keys()))
        logging.info("(OAQ) qlair: %s", list(Sensor.out_model.keys()))
        logging.info("(OAQ) kunak: %s", list(KunakSensor.out_model_kunak))

        # 2. Load registered sensors in the AQDR-Platform-DB.
        sensors_description = get_registered_sensors()

        ### DEBUG, keep just few sensors ##############
        # debug_sensor_ids_to_keep = [
        #    "c01245d137d99d2d03fbf0c63434ce3d6f396362",
        #    "aa447c54f6541ae64d35f313058f3e7dfeefeaa3",
        #    "2ce4178250c108b0620884224f3063ce6542b1f2",
        #    "3418dfaf9268fdfc1d7a1cd75b2381e764c83f8b",
        #    "76670ed3117e4450bee7a19774c0d3c5",
        # ]
        # sensors_description.drop(
        #    sensors_description[
        #        ~sensors_description["SENSOR_ID"].isin(
        #            debug_sensor_ids_to_keep
        #        )
        #    ].index,
        #    inplace=True,
        # )

        # 3. Performs historical data retrieval of sensors on stand-up.
        initial_backfilling(influx_client, sensors_description)

        # 4. Runs initial batch iteration of automated ETL pipelines.
        run_ind_etl_pipeline_qlair(
            influx_client,
            sensors_description[sensors_description["PROVIDER"] == "MH"],
        )
        run_ind_etl_pipeline_inbiot(
            influx_client,
            sensors_description[sensors_description["PROVIDER"] == "IB"],
        )
        run_out_etl_pipeline(influx_client, sensors_description)

        # 5. Schedules runs of ETL processes (sensors updates on-the-fly).
        schedule.every(int(Config.IND_QLAIR_PERIODICITY)).minutes.do(
            lambda: run_ind_etl_pipeline_qlair(
                influx_client,
                sensors_description[sensors_description["PROVIDER"] == "MH"],
            )
        )
        schedule.every(int(Config.IND_INBIOT_PERIODICITY)).minutes.do(
            lambda: run_ind_etl_pipeline_inbiot(
                influx_client,
                sensors_description[sensors_description["PROVIDER"] == "IB"],
            )
        )
        schedule.every(int(Config.OUTDOOR_PERIODICITY)).minutes.do(
            lambda: run_out_etl_pipeline(influx_client, sensors_description)
        )

        while True:
            schedule.run_pending()


if __name__ == "__main__":
    os.makedirs("/logs/ingestor/", exist_ok=True)
    # log_filename = "/logs/ingestor/aqdr-ingestor.log"

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            # logging.FileHandler(log_filename, mode="a"),
            logging.StreamHandler(),
        ],
    )
    logger = logging.getLogger()
    logger.setLevel(Config.APP_LOG_LEVEL)
    logging.getLogger("schedule").setLevel(logging.WARNING)
    logging.getLogger("charset_normalizer").setLevel(logging.ERROR)
    logging.getLogger("chardet").setLevel(logging.ERROR)
    if not Config.KUNAK_API_BASIC_AUTH:
        logging.critical("KUNAK_API_BASIC_AUTH is not set, refusing to start.")
        sys.exit(1)

    logging.info("AQDR-Ingestor started")

    try:
        run_ingestor()
    except (
        RetrievalError,
        TransformError,
        IngestionError,
    ) as error:
        logging.critical("%s", error)
        logging.info("AQDR-Ingestor reloading in 10 minutes...")
        time.sleep(600)
        run_ingestor()
    except (SystemExit, RuntimeError) as error:
        logging.fatal(
            "AQDR-Ingestor SystemExit|RuntimeError: %s",
            error.args[0],
        )
        sys.exit(1)
