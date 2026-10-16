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
Module with Air Quality API custom Enums
"""

from enum import Enum


class Pilots(str, Enum):
    """Pilot sites of the AQDR API."""

    AT = "AT"
    ES = "ES"
    DE = "DE"
    NL = "NL"
    NO = "NO"
    PL = "PL"


class Scenarios(str, Enum):
    """Scenarios of the AQDR API."""

    HOS = "HOS"
    MKT = "MKT"
    MET = "MET"
    HOM = "HOM"
    CAN = "CAN"
    LEC = "LEC"
    RET = "RET"
    RES = "RES"
    SCH = "SCH"


class Providers(str, Enum):
    """Providers of the AQDR API."""

    IB = "IB"
    MH = "MH"


class ESScenarios(str, Enum):
    """Scenarios of the Spain pilot site of the AQDR API."""

    HOS = "HOS"
    MKT = "MKT"
    MET = "MET"
    HOM = "HOM"


class DEScenarios(str, Enum):
    """Scenarios of the Germany pilot site of the AQDR API."""

    CAN = "CAN"
    LEC = "LEC"


class NLScenarios(str, Enum):
    """Scenarios of the Netherlands pilot site of the AQDR API."""

    HOS = "HOS"
    RET = "RET"
    HOM = "HOM"


class NOScenarios(str, Enum):
    """Scenarios of the Norway pilot site of the AQDR API."""

    CAN = "CAN"
    RES = "RES"
    LEC = "LEC"


class POAScenarios(str, Enum):
    """Scenarios of the Poland/Austria pilot site of the AQDR API."""

    HOM = "HOM"
    SCH = "SCH"


# Output file format with measurements
class FileFormat(Enum):
    """Output file format with measurements."""

    CSV = "csv"
    EXCEL = "xlsx"


# Units of measurement dictionary
PARAMETERS_UNITS_DICT = {
    "IAQ Parameters": [
        "temperature",
        "humidity",
        "co2",
        "tvocs",
        "pm1",
        "pm10",
        "pm25",
        "formaldehyde",
    ],
    "IAQ Units": [
        "ºC",
        "%RH",
        "ppm",
        "ppb",
        "µg/m³",
        "µg/m³",
        "µg/m³",
        "µg/m³",
    ],
    "OAQ Parameters": [
        "out_temperature",
        "out_humidity",
        "out_o3",
        "out_pm25",
        "out_pm10",
        "out_co",
        "out_no2",
        "out_so2",
    ],
    "OAQ Units": ["ºC", "%RH", "µg/m³", "µg/m³", "µg/m³", "ppb", "ppb", "ppb",
                  ],
}
