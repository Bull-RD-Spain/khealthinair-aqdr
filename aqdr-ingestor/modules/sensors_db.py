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
Module with functions to interact with AQDR Platform DB, based on PostgreSQL,
where the AQDR-Platform-DB and table with the maintenance of the devices is stored.
"""

import logging
import pandas as pd
import psycopg
from modules.exceptions import RetrievalError
from modules.config import Config

sensors_db_name: str = Config.aqdr_platform_db["SENSORS_DB_NAME"]
sensors_db_user: str = Config.aqdr_platform_db["SENSORS_DB_USER"]
sensors_db_password: str = Config.aqdr_platform_db["SENSORS_DB_PASSWORD"]
sensors_db_host: str = Config.aqdr_platform_db["SENSORS_DB_HOST"]
sensors_db_port: str = Config.aqdr_platform_db["SENSORS_DB_PORT"]
sensors_db_table: str = Config.aqdr_platform_db["SENSORS_DB_TABLE"]


def is_sensors_database_empty():
    """Checks if AQDR-Platform-DB has at least one sensor device registered.

    Returns
    -------
        True if there are no sensors in AQDR-Platform-DB, False otherwise.
    """

    logging.info(
        "Checking AQDR Platform DB sensor devices listed, host [%s:%s], "
        + "with user [%s] in DB/Table [%s/%s]",
        sensors_db_host,
        sensors_db_port,
        sensors_db_user,
        sensors_db_name,
        sensors_db_table,
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
        cursor.execute(f"SELECT COUNT(*) FROM {sensors_db_table}")
        n_sensors = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if n_sensors > 0:
            logging.info(
                "AQDR-platform-db sensors table contains [%s] entries",
                n_sensors,
            )
            return False
        else:
            return True
    except (
        psycopg.OperationalError,
        psycopg.DatabaseError,
    ) as e:
        raise RetrievalError(f"Could not connect to DB: {e}") from e
    except (Exception,) as e:
        raise RetrievalError(f"Could not connect to DB: {e}") from e


def get_registered_sensors():
    """
    Retrieves all registered sensors in AQDR-Platform-DB.

    Returns
    -------
        sensors_description: pd.DataFrame of all registered.
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

        # Select all existing records
        cursor.execute(
            "SELECT sensor_id,apikey,provider,pilot,"
            + "SUBSTRING(scenario FROM 1 FOR 3) AS scenario,"
            + "scenario AS sub_scenario,area,outdoor_apikey,building,"
            + f"inclusion_time FROM {sensors_db_table} "
            + "ORDER BY provider,pilot,scenario,area,building,inclusion_time"
        )
        records = cursor.fetchall()

        sensors_data = []
        for sensor in records:
            sensors_data.append(sensor)

        cursor.close()
        conn.close()

        sensors_description = pd.DataFrame(
            sensors_data,
            columns=[
                "SENSOR_ID",
                "APIKEY",
                "PROVIDER",
                "PILOT",
                "SCENARIO",
                "SUB_SCENARIO",
                "AREA",
                "APIKEY_OAQ",
                "BUILDING",
                "INCLUSION_TIME",
            ],
        )
        sensors_description.reset_index(drop=True, inplace=True)
        return sensors_description

    except psycopg.DatabaseError as e:
        logging.error("Could not connect to AQDR-Platform-DB [%s]", e)
        return None
