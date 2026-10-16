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
This module is used to set configuration variables from environmental variables
and configure some of them with defaults. Consider to add the entries in the
DNS resolver (hosts files) with the service names to facilitate debug
127.0.0.1 aqdr-platform-db
127.0.0.1 aqdr-api
"""

import os


class Config:
    """Class to set configuration variables from environmental variables."""

    try:
        APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "DEBUG")
        AQDR_API_CONTEXTPATH = os.getenv("AQDR_API_CONTEXTPATH", "/api")
        # Mandatory, no default: checked at startup in aqdr_api.py
        AQDR_API_AUTH_SECRET_KEY = os.getenv("AQDR_API_AUTH_SECRET_KEY")
        AQDR_API_USERS_FILE = os.getenv(
            "AQDR_API_USERS_FILE", "/app/config/aqdr-api-users.json"
        )
    except KeyError as error:
        raise ValueError(
            "Tried accessing the env variables AQDR-API but some failed"
        ) from error

    # AQDR-Platform-DB (Sensors)
    try:
        aqdr_platform_db = dict(
            SENSORS_DB_NAME=os.getenv("SENSORS_DB_NAME", "sensors"),
            SENSORS_DB_TABLE=os.getenv("SENSORS_DB_TABLE", "sensors"),
            SENSORS_DB_USER=os.getenv("SENSORS_DB_USER", "sensors"),
            SENSORS_DB_PASSWORD=os.getenv("SENSORS_DB_PASSWORD"),
            SENSORS_DB_HOST=os.getenv("SENSORS_DB_HOST", "aqdr-platform-db"),
            SENSORS_DB_PORT=os.getenv("SENSORS_DB_PORT", "8082"),
            INBIOT_API_URL=os.getenv(
                "INBIOT_API_URL", "https://myinbiotpublicapi.com"
            ),
            QLAIR_API_URL=os.getenv(
                "QLAIR_API_URL", "https://api.v2.i-qlair.eu"
            ),
            KUNAK_API_URL=os.getenv(
                "KUNAK_API_URL", "https://kunakcloud.com/openAPIv0/v1"
            ),
        )
    except KeyError as error:
        raise ValueError(
            "Tried accessing the env variables AQDR-API but some failed"
        ) from error

    # AQDR-TS-DB (Influx)
    try:
        aqdr_ts_db = dict(
            INFLUXDB_URL=os.getenv("INFLUXDB_URL", "http://aqdr-ts-db:8086"),
            DOCKER_INFLUXDB_INIT_ORG=os.getenv(
                "DOCKER_INFLUXDB_INIT_ORG", "K-HEALTHinAIR"
            ),
            DOCKER_INFLUXDB_INIT_BUCKET=os.getenv(
                "DOCKER_INFLUXDB_INIT_BUCKET", "AIR_QUALITY"
            ),
            INFLUXDB_MEASUREMENT=os.getenv(
                "INFLUXDB_MEASUREMENT", "CONTINUOUS_MONITORING_"
            ),
            DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=os.getenv(
                "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"
            ),
        )
    except KeyError as error:
        raise ValueError(
            "Tried accessing the env variables AQDR-API but some failed"
        ) from error
