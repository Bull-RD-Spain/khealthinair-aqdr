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
This code check for Grafana initializataion as K-HEALTHinAIR AQDR Platform:
- Note that this should be independent and compatible with the initializations
  done through the installation in Kubernetes via HELM chart
- Organization: Changes the default 'Main org' to a more descriptive org
  name (K-HEALTHinAIR) and should match the AUTH_ANONYMOUS_ORG_NAME
- Users: Check existence of expected Users, and create them if not there
"""

import sys
import time
import logging
from logging.handlers import RotatingFileHandler

# import os
import yaml
from urllib3.exceptions import MaxRetryError

from grafana_client import Configuration
from grafana_client.api_client import ApiClient

from modules.config import Config
from modules.organizations import Organizations
from modules.users import Users
from modules.teams import Teams
from modules.folder_permissions import FolderPermissions


def main():
    """Main function to initialize Grafana for K-HEALTHinAIR project."""
    logging.info(
        "\n┌─────────────────────────────────────────────────────────────┐\n"
        + "│        K-HEALTHinAIR AQDR UI Platform initialization        │\n"
        + "└─────────────────────────────────────────────────────────────┘"
    )

    logging.info(
        "START Grafana initialization for K-HEALTHinAIR project "
        + "[%s] logged as %s, in 20 seconds...",
        Config.GRAFANA_API_ENDPOINT,
        Config.GF_SECURITY_ADMIN_USER,
    )
    time.sleep(20)

    try:
        config = load_config_from_yaml(
            "/aqdr-ui/grafana-initialization/aqdr-ui-init-conf.yaml"
        )
        # config = load_config_from_yaml(
        #    os.path.join(
        #        os.path.dirname(os.path.abspath(__file__)),
        #        "aqdr-ui-init-conf.yaml",
        #    )
        # )
    except ValueError as error:
        logging.error(
            "File aqdr-ui-init-conf.yaml couldn't be loaded: %s", str(error)
        )
        sys.exit(1)

    api_client = ApiClient(
        Configuration(
            host=Config.GRAFANA_API_ENDPOINT,
            username=Config.GF_SECURITY_ADMIN_USER,
            password=Config.GF_SECURITY_ADMIN_PASSWORD,
        )
    )

    try:
        # Check and update organization name
        organizations = Organizations(api_client, config)
        organizations.update_default_organization_name()

        # Check and create users
        users = Users(api_client, config)
        users.create_users()

        # Check and create teams
        teams = Teams(api_client, config)
        teams.create_teams()

        # Check and create folder_permissions
        folder_permissions = FolderPermissions(api_client, config)
        folder_permissions.create_folder_permissions()

    except MaxRetryError as error:
        logging.error(
            "Connexion to %s with user %s error: %s",
            Config.GRAFANA_API_ENDPOINT,
            Config.GF_SECURITY_ADMIN_USER,
            str(error.reason),
        )
        sys.exit(1)

    logging.info("END Grafana initialization for K-HEALTHinAIR project.")


def load_config_from_yaml(file_path):
    """Load configuration from YAML file."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file)
            return config
    except FileNotFoundError:
        logging.error("File '%s' not found.", file_path)
        sys.exit(1)
    except yaml.YAMLError as error:
        logging.error("Error parsing YAML file: %s", error)
        sys.exit(1)


if __name__ == "__main__":

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handlerStdout = logging.StreamHandler(sys.stdout)
    handlerFile = RotatingFileHandler(
        "./aqdr-ui-initialization.log",
        mode="a",
        maxBytes=5 * 1024 * 1024,
        backupCount=2,
        encoding="utf-8",
        delay=0,
    )
    handlerStdout.setFormatter(formatter)
    handlerFile.setFormatter(formatter)
    logger = logging.getLogger("root")
    logger.setLevel(Config.APP_LOG_LEVEL)
    logger.addHandler(handlerStdout)
    logger.addHandler(handlerFile)

    main()
