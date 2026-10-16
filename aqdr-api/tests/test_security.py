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
Tests for modules/authentication
"""

import sys
import os
import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from modules.authentication import authenticate_user, get_user, verify_password
from passlib.context import CryptContext

class TestSecurity:
    """Tests for the Security methods"""

    FAKE_DB = {
        "user_1": {
            "username": "user_1",
            "hashed_password": "$2b$12$RCx3tvVKvn1/2Anj0FIayef8djZ0vDrBdB4lS2pgr0o8hB5kbQyZW",
            "disabled": False,
            "access": ["R"],
            "description": "Description of User1",
        },
        "user_2": {
            "username": "user_2",
            "hashed_password": "JZE9pz2DZZC30nY7shZS.fJy",
            "disabled": False,
            "access": ["R", "W"],
            "description": "Description of User2",
        },
    }

    def test_get_user(self):
        """Tests *get_user* function to ensure it returns the username."""

        assert get_user(self.FAKE_DB, "user_1").username == "user_1"

    @pytest.mark.parametrize(
        "username, password, expected_result",
        [
            ("user_1", "1234", FAKE_DB["user_1"]),
            ("user3", "1234", False),
            ("user_1", "wrong_password", False),
        ],
    )
    def test_authenticate_user(self, username, password, expected_result):
        """Test *authenticate_user* function returns expected result
        (user if authenticated, False if not authenticated)"""
        result = authenticate_user(self.FAKE_DB, username, password)
        if result is None and expected_result is False:
            assert True
        elif isinstance(result, bool):
            assert (
                result == expected_result
            ), f"Expected {expected_result}, got {result}"
        else:
            assert vars(result) == expected_result

    @pytest.mark.parametrize(
        "plain_password, hashed_password, expected_verification",
        [
            (
                "1234",
                "$2b$12$RCx3tvVKvn1/2Anj0FIayef8djZ0vDrBdB4lS2pgr0o8hB5kbQyZW",
                True,
            ),
            (
                "1234",
                "$2b$12$RCx3tvVKvn1/2Anj0FIayef8djZ0vDrBdB4lS2pgr0o8hB5GbQyZW",
                False,
            ),
            (
                "abc",
                "$2b$12$RCx3tvVKvn1/2Anj0FIayef8djZ0vDrBdB4lS2pgr0o8hB5kbQyZW",
                False,
            ),
        ],
    )
    def test_verify_password(
        self, plain_password, hashed_password, expected_verification
    ):
        """Function test_verify_password."""
        verification = verify_password(plain_password, hashed_password)
        assert verification == expected_verification

    def hash_pass(self):
        """Tests *hash_pass* function to help create new useres."""

        # Helper context using Bcrypt hashing algorithm to hash and verify passwords
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        hashed_password = pwd_context.hash("P4ssW0rd")
        print(f"Hashed password: {hashed_password}")
        assert verify_password(self, "P4ssW0rd", hashed_password)
