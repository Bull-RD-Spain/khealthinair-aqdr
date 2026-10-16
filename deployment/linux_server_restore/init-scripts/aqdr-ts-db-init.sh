#!/bin/bash
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

set -e
echo "############ K-HEALTHinAIR Custom Initialization Scripts ############"
echo "## INFLUX_CONFIGS_PATH: $INFLUX_CONFIGS_PATH"
echo "## DOCKER_INFLUXDB_INIT_USERNAME: $DOCKER_INFLUXDB_INIT_USERNAME"
echo "## DOCKER_INFLUXDB_INIT_ORG: $DOCKER_INFLUXDB_INIT_ORG"
echo "## DOCKER_INFLUXDB_INIT_BUCKET: $DOCKER_INFLUXDB_INIT_BUCKET"
echo "## INFLUX_EXTRA_BUCKETS: $INFLUX_EXTRA_BUCKETS"
IFS=' ' read -ra buckets <<< "$INFLUX_EXTRA_BUCKETS"
for bucket in "${buckets[@]}"
do
  echo "Creating Bucket '$bucket'..."
  influx bucket create --org $DOCKER_INFLUXDB_INIT_ORG --name $bucket
done
echo "########################## K-HEALTHinAIR END ########################"

