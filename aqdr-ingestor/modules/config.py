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
AQDR-Ingestor Config
"""

import os


class Config:
    """Class to set configuration variables from environmental variables."""

    try:
        APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "DEBUG")
        INBIOT_API_URL = os.getenv(
            "INBIOT_API_URL",
            "https://myinbiotpublicapi.com",
        )
        QLAIR_API_URL = os.getenv(
            "QLAIR_API_URL",
            "https://api.v2.i-qlair.eu",
        )
        KUNAK_API_URL = os.getenv(
            "KUNAK_API_URL", "https://kunakcloud.com/openAPIv0/v1"
        )
        # Mandatory, no default: checked at startup in aqdr_ingestor.py
        KUNAK_API_BASIC_AUTH = os.getenv("KUNAK_API_BASIC_AUTH")
        KUNAK_API_DEVICE = os.getenv("KUNAK_API_DEVICE", "0423310093")
        KUNAK_BUILDING_IDS = [68, 69, 70, 71, 72]
        IND_INBIOT_PERIODICITY = os.getenv(
            "IND_INBIOT_PERIODICITY",
            "10",
        )
        IND_QLAIR_PERIODICITY = os.getenv(
            "IND_QLAIR_PERIODICITY",
            "5",
        )
        OUTDOOR_PERIODICITY = os.getenv(
            "OUTDOOR_PERIODICITY",
            "60",
        )
        INBIOT_API_URL_REQUEST_LIMIT = os.getenv(
            "INBIOT_API_URL_REQUEST_LIMIT",
            "6",
        )
        try:
            limit = int(INBIOT_API_URL_REQUEST_LIMIT)
        except ValueError:
            raise ValueError("INBIOT_API_URL_REQUEST_LIMIT must be an integer")

        # '0' to disable the request limit, at least 2 request are utility ones in advance
        if limit != 0 and limit < 3:
            raise ValueError("INBIOT_API_URL_REQUEST_LIMIT should be 0 or >=3")

    except KeyError as error:
        raise ValueError(
            "Tried accessing the environmental variables AQDR-Ingestor but "
            + "some failed"
        ) from error

    # ###### AQDR-API ######
    try:
        aqdr_api = dict(
            AQDR_API_CONTEXTPATH=os.getenv("AQDR_API_CONTEXTPATH", "/api"),
            AQDR_API_AUTH_SECRET_KEY=os.getenv("AQDR_API_AUTH_SECRET_KEY"),
        )
    except KeyError as error:
        raise ValueError(
            "Tried accessing the environmental variables related with AQDR-API"
        ) from error

    # ###### AQDR-Platform-DB (Sensors) ######
    try:
        aqdr_platform_db = dict(
            SENSORS_DB_HOST=os.getenv("SENSORS_DB_HOST", "aqdr-platform-db"),
            SENSORS_DB_PORT=os.getenv("SENSORS_DB_PORT", "8082"),
            SENSORS_DB_NAME=os.getenv("SENSORS_DB_NAME", "sensors"),
            SENSORS_DB_TABLE=os.getenv("SENSORS_DB_TABLE", "sensors"),
            SENSORS_DB_USER=os.getenv("SENSORS_DB_USER", "sensors"),
            SENSORS_DB_PASSWORD=os.getenv("SENSORS_DB_PASSWORD"),
        )
    except KeyError as error:
        raise ValueError(
            "Tried accessing the environmental variables related with "
            + "AQDR-Platform-DB (Sensors)"
        ) from error

    # ###### AQDR-TS-DB (Influx) ######
    try:
        aqdr_ts_db = dict(
            INFLUXDB_URL=os.getenv("INFLUXDB_URL", "http://localhost:8086"),
            DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=os.getenv(
                "DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"
            ),
            DOCKER_INFLUXDB_INIT_ORG=os.getenv(
                "DOCKER_INFLUXDB_INIT_ORG", "K-HEALTHinAIR"
            ),
            DOCKER_INFLUXDB_INIT_BUCKET=os.getenv(
                "DOCKER_INFLUXDB_INIT_BUCKET", "AIR_QUALITY"
            ),
            INFLUXDB_MEASUREMENT=os.getenv(
                "INFLUXDB_MEASUREMENT", "CONTINUOUS_MONITORING_"
            ),
        )
    except KeyError as error:
        raise ValueError(
            "Tried accessing the environment *_INFLUXDB_* env variables: "
            + error.args[0].message
        ) from error
