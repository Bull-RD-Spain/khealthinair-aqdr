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
Grafana-Initialization Config
"""

import os


class Config:
    """Class to set configuration variables from environmental variables."""

    # ###### AQDR-UI ######
    try:
        APP_LOG_LEVEL = os.getenv("APP_LOG_LEVEL", "DEBUG")
        GRAFANA_API_ENDPOINT = os.getenv(
            "GRAFANA_API_ENDPOINT", "http://localhost:3000/api"
        )
        GF_SECURITY_ADMIN_USER = os.getenv(
            "GF_SECURITY_ADMIN_USER", "khealthinair_admin"
        )
        GF_SECURITY_ADMIN_PASSWORD = os.getenv(
            "GF_SECURITY_ADMIN_PASSWORD", ""
        )
        GF_SMTP_ENABLED = os.getenv("GF_SMTP_ENABLED", "true")
        GF_SMTP_HOST = os.getenv("GF_SMTP_HOST", "smtp.titan.email:465")
        GF_SMTP_USER = os.getenv("GF_SMTP_USER", "noreply@k-healthinair.eu")
        GF_SMTP_PASSWORD = os.getenv("GF_SMTP_PASSWORD", "")
        GF_SMTP_SKIP_VERIFY = os.getenv("GF_SMTP_SKIP_VERIFY", "true")
        GF_SMTP_FROM_NAME = os.getenv(
            "GF_SMTP_FROM_NAME", "K-HEALTHinAIR Platform AQDR"
        )
        GF_SMTP_FROM_ADDRESS = os.getenv(
            "GF_SMTP_FROM_ADDRESS", "noreply@k-healthinair.eu"
        )

    except KeyError as error:
        raise ValueError(
            "Tried accessing the environmental variables AQDR-Ingestor but "
            + "some failed"
        ) from error
