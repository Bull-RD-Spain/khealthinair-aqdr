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


""" This module is responsible for creating teams in Grafana. """

import sys
import os
import logging

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from grafana_client.exceptions import BadRequestException
from grafana_client.models.create_team_command import CreateTeamCommand
from grafana_client import TeamsApi
from grafana_client.models.add_team_member_command import (
    AddTeamMemberCommand,
)
from modules.users import Users

API_CLIENT = None
CONFIG_FILE = None
TEAMS_API = None
USERS = None


class Teams:
    """This class is responsible for creating teams in Grafana."""

    def __init__(self, api_client, config_file):
        """Initialize the Teams class."""
        Teams.apiClient = api_client
        Teams.config_file = config_file
        Teams.teams_api = TeamsApi(api_client)
        Teams.users = Users(api_client, config_file)

    def create_teams(self):
        """Check existence of expected Teams, and create them if not there."""
        logging.info("Start of teams check and creation.")
        add_team_member_commands = []
        existing_teams = Teams.teams_api.search_teams(1, 10)
        for group, group_data in Teams.config_file.items():
            if group == "teams":
                for item in group_data:
                    for key, value in item.items():
                        if key == "name":
                            create_team_command = CreateTeamCommand()
                            create_team_command.name = value
                            if any(
                                t.name == create_team_command.name
                                for t in existing_teams.teams
                            ):
                                logging.info(
                                    "Team [%s] already exists, skipping...",
                                    create_team_command.name,
                                )
                            else:
                                logging.info(
                                    "Team [%s] does not exist creating...",
                                    create_team_command.name,
                                )
                                try:
                                    Teams.teams_api.create_team(
                                        create_team_command.to_dict()
                                    )
                                except BadRequestException as bre:
                                    logging.warning("Error %s", bre.body)

                        elif key == "members":
                            for u in value:
                                logging.info(
                                    "Team [%s], to add member %s...",
                                    create_team_command.name,
                                    u["login"],
                                )
                                team_id = Teams.id_from_name(
                                    self, create_team_command.name
                                )
                                user_id = Users.id_from_login(self, u["login"])
                                if team_id and user_id:
                                    team_members = (
                                        Teams.teams_api.get_team_members(
                                            str(team_id)
                                        )
                                    )
                                    if any(
                                        member.user_id == user_id
                                        for member in team_members
                                    ):
                                        logging.info(
                                            "User %s is already a member of "
                                            + "Team %s, skipping...",
                                            u["login"],
                                            create_team_command.name,
                                        )
                                        continue

                                add_team_member_commands.append(
                                    AddTeamMemberCommand(
                                        user_id=Users.id_from_login(
                                            self, u["login"]
                                        )
                                    )
                                )
                                # Pending to add permission,
                                # defaultPermissionTypeinteger =
                                #   Member.permission = (
                                #    0 if u["permission"] == "Admin" else 1
                                # )  # 0:Admin or 1:Member
                                # update_team_member_command =
                                #   UpdateTeamMemberCommand()
                                # update_team_member_command.team_id =
                                #   tr({create_team_command.name})
                                # update_team_member_command.user_id =
                                #   str(Users.id_from_login(self, u["login"]))
                                # update_team_member_command.permission =
                                #   (0 if u["permission"] == "Admin" else 1)
                                # try:
                                #    Teams.teams_api.update_team_member(
                                #        update_team_member_command.to_dict()
                                #    )
                                # except BadRequestException as bre:
                                #    logging.warn("Error %s", {bre.body})

                        if (
                            create_team_command.name != ""
                            and len(add_team_member_commands) > 0
                        ):
                            for (
                                add_team_member_command
                            ) in add_team_member_commands:
                                try:
                                    Teams.teams_api.add_team_member(
                                        str(
                                            Teams.id_from_name(
                                                self, create_team_command.name
                                            )
                                        ),
                                        add_team_member_command.to_dict(),
                                    )
                                except BadRequestException as bre:
                                    logging.warning("Error %s", bre.body)
        logging.info("End of teams check and creation.")

    def id_from_name(self, name: str):
        """Get the ID of a team by its name."""
        result = Teams.teams_api.search_teams(1, 1, name)
        if result.teams:
            return result.teams[0].id
        return None
