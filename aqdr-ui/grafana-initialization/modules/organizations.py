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
This code check for Grafana initialization as K-HEALTHinAIR AQDR:
- Check existence of expected Users, and create them if not there
- Check the folder permissions, and create them if not there
"""

import sys
import os
import logging
from requests import RequestException

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from grafana_client.models.update_org_form import UpdateOrgForm
from grafana_client import OrgsApi

API_CLIENT = None
CONFIG_FILE = None
ORGS_API = None


class Organizations:
    """This class is responsible for updating organization name in Grafana."""

    def __init__(self, api_client, config_file):
        """Initialize the Organizaapi_clientss."""
        Organizations.api_client = api_client
        Organizations.config_file = config_file
        Organizations.orgs_api = OrgsApi(api_client)

    def update_default_organization_name(self):
        """Update the default organization name."""
        logging.info("Start of organization name update.")
        for group, group_data in Organizations.config_file.items():
            if group == "organization":

                try:
                    org_details_dto = Organizations.orgs_api.get_org_by_id(1)
                except RequestException as bre:
                    logging.error("Error %s", bre)

                if org_details_dto.name != group_data.get("name"):
                    logging.info(
                        "Updating organization name to [%s]",
                        group_data.get("name"),
                    )
                    org = UpdateOrgForm()
                    org.name = group_data.get("name")
                    Organizations.orgs_api.update_org(1, org)
                else:
                    logging.info(
                        "Organization name is already [%s], skipping...",
                        group_data.get("name"),
                    )
        # logging.info("End of organization name update.")
