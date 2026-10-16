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

""" Module OAQ Cache.

    For a data source (qlair/kunak) + building + time, contains the dictionary
    with the values of a previous request, already in the platform model,
    to be reused in the current request.
    Measurements will be always on the hour (XX:00:00) to facilitate handling
    Timestamp resolution in maintained here in milliseconds although is later
    sent to inFlux with seconds as resolution, so sources should be adjusted
    to timestamps in seconds (10 digits) from the sources:
    - qlair: "sensedtimedate":    NNNNNNNNNN.N (seconds plus decimal),
    - kunak:             "ts": NNNNNNNNNNNNN   (milliseconds)
    An OAQ_CACHE entry has this structure:
    OAQ_CACHE[(source, building, time)] = fields
    where:
        source: Literal["qlair", "kunak"],
        building: int,
        time: int,
        fields: dict,
"""

from typing import Literal
from influxdb_client.client.write.point import Point
from modules.config import Config
from modules.exceptions import TransformError
from modules.sensor import Sensor

OAQ_CACHE = dict()
KUNAK_BUILDING_IDS = [int(x) for x in Config.KUNAK_BUILDING_IDS]


class OAQCache:
    """OAQ Cache class to store OAQ data in memory"""

    # class DPCache:
    #     """DataPointCache class to store a cache datapoint"""

    #     def __init__(self, source, building, time, fields):
    #         self.source = source
    #         self.building = building
    #         self.time = time
    #         self.fields = fields

    @staticmethod
    def insert_oaq_in_cache(
        source: Literal["qlair", "kunak"],
        building: int,
        time: int,
        fields: dict,
    ):
        """Insert a source+building+time entry in OAQ_CACHE"""

        OAQCache._check_ts_in_seconds(time)

        if OAQCache.exist_in_cache(source, building, time):
            return

        building_time_key = (source, building, time)
        OAQ_CACHE[building_time_key] = fields

        # This is because this buildings are in the same area to save API calls
        if int(building) in KUNAK_BUILDING_IDS:
            for b in KUNAK_BUILDING_IDS:
                if str(building) != b:
                    building_time_key = (source, int(b), time)
                    OAQ_CACHE[building_time_key] = fields

    @staticmethod
    def exist_in_cache(
        source: Literal["qlair", "kunak"], building: int, time: int
    ):
        """Check if a source+building+time entry already exist in OAQ_CACHE"""

        OAQCache._check_ts_in_seconds(time)

        source_building_time_key = (source, building, time)
        if source_building_time_key in OAQ_CACHE:
            return OAQ_CACHE[source_building_time_key]
        return None

    @staticmethod
    def get_from_cache_point(
        source: Literal["qlair", "kunak"], building: int, time: int
    ):
        """Extract a source+building+time entry from OAQ_CACHE"""

        source_building_time_key = (source, building, time)
        return OAQ_CACHE.get(source_building_time_key, None)

    @staticmethod
    def get_from_cache_all_since(
        source: Literal["qlair", "kunak"], building: int, since_time: int
    ):
        """Extract a source+building+time entries, from the specified time
        onwards from OAQ_CACHE.
        Is not enought having something but should be from the since time as reference
        """
        if not OAQ_CACHE:
            return []
        else:
            OAQCache._check_ts_in_seconds(since_time)

            first, _ = OAQCache.get_from_cache_first_and_last_building(
                source, building
            )
            if (
                first
                and first[0][2]
                and first[0][2] - since_time
                > (int(Config.OUTDOOR_PERIODICITY) * 60)
            ):
                return []  # Cache is not enough, filled after since_time
            #     now_epoch_time = int(datetime.timestamp(datetime.now()))
            #     diff_in_seconds = now_epoch_time - since_time
            #     items_required = diff_in_seconds // (
            #         int(Config.OUTDOOR_PERIODICITY) * 60
            #     )
            #     logging.debug(
            #         "(OAQ) Expected to get [%s] datapoints from cache",
            #         items_required,
            #     )
            matching_items = [
                item
                for item in OAQ_CACHE.items()
                if item[0][0] == source
                and item[0][1] == building
                and item[0][2]
                >= since_time  # Note >= just of the current entries!
            ]
            return matching_items

    @staticmethod
    def get_from_cache_first_and_last_building(
        source: Literal["qlair", "kunak"], building: int
    ):
        """Extract first and last items for a specific building from OAQ_CACHE"""
        if not OAQ_CACHE:
            return None, None
        else:
            matching_items = [
                item
                for item in OAQ_CACHE.items()
                if item[0][0] == source and item[0][1] == building
            ]
            if not matching_items:
                return None, None
            first = min(matching_items, key=lambda x: x[0][2])
            last = max(matching_items, key=lambda x: x[0][2])
            return first, last

    @staticmethod
    def to_influxdb_points(
        cache_dps: dict,
        measurement: str,
        sensor: Sensor,
    ):
        """Convert a source+building+time dict entry to an InfluxDB Point"""
        influxdb_points = []

        for cache_dp in cache_dps:

            point = Point(measurement).time(
                cache_dp[0][2], write_precision="s"
            )

            if cache_dp[0][0] == "kunak":
                point.tag("AQ", "OAQ_kunak")
            elif cache_dp[0][0] == "qlair":
                point.tag("AQ", "OAQ")
            else:
                raise ValueError(
                    f"Tag AQ en OAQ cache not recognized [{cache_dp[0][0]}]."
                )

            point.tag("id_pilot", sensor.pilot)
            point.tag("scenario", sensor.scenario)
            point.tag("sub_scenario", sensor.sub_scenario)
            point.tag("area", sensor.sub_scenario + str(sensor.area).zfill(3))
            point.tag("sensor_id", sensor.sensor_id)

            for field, value in cache_dp[1].items():
                point.field(field, value)

            influxdb_points.append(point)

        return influxdb_points

    @staticmethod
    def _check_ts_in_seconds(time: int):
        """Check if a timestamp is in seconds"""

        if len(str(time)) != 10 or not isinstance(time, int):
            raise TransformError(
                f"Timestamp time [{time}] do not look one in seconds]."
            )

    @staticmethod
    def _check_ts_in_seconds(time: int):
        """Check if a timestamp is in seconds"""