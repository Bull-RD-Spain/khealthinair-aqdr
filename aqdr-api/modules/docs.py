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

"""Module with Air Quality API custom documentation in Swagger UI"""

from modules.config import Config

CONTEXTPATH = Config.AQDR_API_CONTEXTPATH

API_DESCRIPTION_HEADER = (
    "<style>@font-face {font-family: 'Quicksand';src: "
    + "url('"
    + CONTEXTPATH
    + "/static/fonts/Quicksand.woff2') format('woff2')}</style>"
    + "<p style='font-family:Quicksand,sans-serif; font-weight:normal;"
    + "font-size:0.9em;text-align:center; margin-left:auto;margin-right:auto'>"
    + "<img src='"
    + CONTEXTPATH
    + "/static/K-HEALTHinAIR_original@3x.png' alt='K-HEALTHinAIR' "
    + "height='50px'><img src='"
    + CONTEXTPATH
    + "/static/EUFunded.png' alt='EU' height='50px'>"
    + "<br><span style='font-weight: bold; font-stretch: extra-expanded;'>"
    + "Knowledge for improving indoor air quality and health</span><br>"
    + "<span>Platform for collecting and sharing the information "
    + "and knowledge generated about chemical and biological indoor air "
    + "pollutants affecting human health.</span></p>"
    + "<p style='font-family:Quicksand,sans-serif;font-size:0.9em;'>"
    + "AQDR API is divided in 5 sections (i.e., pilot sites): "
    + "DE (Germany), ES (Spain), NL (Netherlands), NO (Norway), PL/AT "
    + "(Poland & Austria), and includes also the registererd sensors devices "
    + "list management.</p>"
    + "Please note that for long periods, the amount of data to be processed "
    + "may be so large that it may reach the system size or response times "
    + "limits. Use shorter periods in case of error after taking long time "
    + "for responding and resulting in error."
)

tags_metadata = [
    {
        "name": "DE Pilot",
        "description": "API Endpoints for Germany Pilot (Baden-Wurtemberg).",
    },
    {
        "name": "ES Pilot",
        "description": "API Endpoints for Spain Pilot (Barcelona).",
    },
    {
        "name": "NL Pilot",
        "description": "API Endpoints for the Netherlands Pilot (Rotterdam).",
    },
    {
        "name": "NO Pilot",
        "description": "API Endpoints for Norway Pilot (Grimstad).",
    },
    {
        "name": "PL/AT Pilot",
        "description": "API Endpoints for Poland/Austria Pilot "
        + "(Warsaw, Lodz/Vienna).",
    },
    {
        "name": "Sensors",
        "description": "Sensor devices operations for continuous monitoring.",
    },
]

contact = {
    "name": "Atos/Eviden BDS R&D Spain - Applied AI",
    "url": "https://booklet.evidenresearch.eu/units/applied-ai",
}

license_info = {
    "name": "K-HEALTHinAIR project",
    "url": "https://k-healthinair.eu/",
}
