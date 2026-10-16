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


""" Module for custom Exceptions."""

# https://www.tutorialspoint.com/object_oriented_python/object_oriented_python_exception_classes.htm
# Creating Custom exception class


class RetrievalError(Exception):
    """There was an error on the AQ Retrieval process (Extract of ETL)"""

    def __init__(self, message):
        self.msg = message


class TransformError(Exception):
    """There was an error on the AQ Transform process (Transform of ETL)"""

    def __init__(self, message):
        self.msg = message


class IngestionError(Exception):
    """There was an error on the AQ Ingestion process (Load of ETL)"""

    def __init__(self, message):
        self.msg = message


class BackFillingError(Exception):
    """There was an error on the back-up process of the sensor."""

    def __init__(self, message):
        self.msg = message
