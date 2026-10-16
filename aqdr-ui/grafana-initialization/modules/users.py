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


"""This module is responsible for creating users in Grafana."""

import sys
import os
import logging
import secrets
import string

from typing import List
from grafana_client.models.org_user_dto import OrgUserDTO
from grafana_client import AdminCreateUserForm, AdminUsersApi, OrgsApi
from grafana_client.exceptions import ApiException

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
ORG_ID = 1
API_CLIENT = None
CONFIG_FILE = None
ORGS_API = None
ADMIN_USERS_API = None


class Users:
    """This class is responsible for creating users in Grafana."""

    def __init__(self, api_client, config_file):
        """Initialize the Users class."""
        Users.apiClient = api_client
        Users.config_file = config_file
        Users.orgs_api = OrgsApi(api_client)
        Users.admin_users_api = AdminUsersApi(api_client)

    def create_users(self):
        """Check existence of expected Users, and create them if not there."""
        logging.info("Start of users check and creation.")
        admin_create_user_form = AdminCreateUserForm()
        existing_users = List[OrgUserDTO]
        existing_users = Users.orgs_api.get_org_users(ORG_ID)
        for group, group_data in Users.config_file.items():
            if group == "users":
                for item in group_data:
                    for key, value in item.items():
                        if key == "login":
                            admin_create_user_form.login = value
                        elif key == "name":
                            admin_create_user_form.name = value
                        elif key == "email":
                            admin_create_user_form.email = value
                        elif key == "orgId":
                            admin_create_user_form.org_id = value
                        elif key == "password":
                            if value:
                                admin_create_user_form.password = value
                            else:
                                admin_create_user_form.password = (
                                    Users.generate_random_password()
                                )

                    logging.info(
                        "Checking user [%s] %s",
                        admin_create_user_form.login,
                        admin_create_user_form.name,
                    )
                    if any(
                        u.login == admin_create_user_form.login
                        for u in existing_users
                    ):
                        logging.info(
                            "[%s] User already exists, skipping...",
                            admin_create_user_form.login,
                        )
                    else:
                        logging.info(
                            "[%s] User does not exist, creating...",
                            admin_create_user_form.login,
                        )
                        try:
                            Users.admin_users_api.admin_create_user(
                                admin_create_user_form
                            )
                        except ApiException as e:
                            logging.error(
                                "Failed to create user [%s]: %s",
                                admin_create_user_form.login,
                                str(e),
                            )
        logging.info("End of users check and creation.")

    def id_from_login(self, login: str):
        """Get user ID from login."""
        users = Users.orgs_api.get_org_users(ORG_ID)
        for user in users:
            if user.login == login:
                return user.user_id
        return None

    def generate_random_password(length=10):
        characters = string.ascii_letters + string.digits + string.punctuation
        password = "".join(secrets.choice(characters) for _ in range(length))
        return password
