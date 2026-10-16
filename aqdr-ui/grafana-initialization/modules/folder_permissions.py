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


""" This module is used to check and create folder permissions. """

import sys
import os
import logging
from typing import List

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from grafana_client import FolderPermissionsApi, FoldersApi
from grafana_client.models.dashboard_acl_info_dto import (
    DashboardACLInfoDTO,
)
from grafana_client.models.folder import Folder
from grafana_client.models.folder_search_hit import FolderSearchHit

API_CLIENT = None
CONFIG_FILE = None
FOLDER_API = None
FOLDER_PERMISSIONS_API = None


class FolderPermissions:
    """This class is used to check and create folder permissions."""

    def __init__(self, api_client, config_file):
        """Initialize the FolderPermissions class."""
        FolderPermissions.apiClient = api_client
        FolderPermissions.config_file = config_file
        FolderPermissions.folders_api = FoldersApi(api_client)
        FolderPermissions.folder_permissions_api = FolderPermissionsApi(
            api_client
        )

    def create_folder_permissions(self):
        """This method is used to create folder permissions."""
        logging.info("Start of folder_permissions check and creation.")
        folder = Folder()
        existing_folders = List[FolderSearchHit]
        existing_folders = FolderPermissions.folders_api.get_folders()
        existing_folder_perms = List[DashboardACLInfoDTO]

        for group, group_data in FolderPermissions.config_file.items():
            if group == "folder_permissions":
                for item in group_data:
                    for key, value in item.items():
                        if key == "uid":
                            logging.info("Checking folder uid [%s]...", value)
                            folder.uid = value
                            if any(
                                f.uid == folder.uid for f in existing_folders
                            ):
                                logging.info(
                                    "[%s] exists, check permissions...",
                                    folder.uid,
                                )
                                existing_folder_perms = FolderPermissions.folder_permissions_api.get_folder_permission_list(
                                    folder.uid
                                )
                                for acl_info in existing_folder_perms:
                                    if acl_info.role:
                                        logging.info(
                                            "[%s] Role permission [%s]: %s",
                                            folder.uid,
                                            acl_info.permission_name,
                                            acl_info.role,
                                        )
                                    elif acl_info.team:
                                        logging.info(
                                            "[%s] Team permission [%s]: %s",
                                            folder.uid,
                                            acl_info.permission_name,
                                            acl_info.role,
                                        )
                                    elif acl_info.user_id:
                                        logging.info(
                                            "[%s] User permission [%s]: %s",
                                            folder.uid,
                                            acl_info.permission_name,
                                            acl_info.role,
                                        )
                            else:
                                logging.info(
                                    "[%s] folder don't exist, skip.",
                                    folder.uid,
                                )
                        elif key == "permissions":
                            for p in value:
                                if p.get("userId"):
                                    logging.info(
                                        "[{%s}] User permission "
                                        + f"[{p['userId']}]: "
                                        + f"[{p['permission']}]",
                                        folder.uid,
                                    )
                                elif p["teamId"]:
                                    logging.info(
                                        "[%s] Team Permission [%s]: [%s]",
                                        folder.uid,
                                        p["teamId"],
                                        p["permission"],
                                    )
                        # TODO: Add code to create folder permissions.

        logging.info("End of folder_permissions check and creation.")
