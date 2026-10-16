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

# docker build --no-cache --progress=plain -t khealthinair/aqdr-api:latest .
FROM python:3.12-slim-bullseye
LABEL version="2.0.0" maintainer="Alberto Acebes <alberto.acebes@eviden.com>"

ENV HOMEDIR=/app
RUN mkdir -p $HOMEDIR
COPY . $HOMEDIR
WORKDIR $HOMEDIR
ENV PYTHONPATH='$PYTHONPATH:$HOMEDIR'

RUN pip install --no-cache-dir --upgrade pip && pip install poetry
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi -vvv --quiet --without dev

# For the healthcheck
RUN apt update --fix-missing && apt install curl -y

# Clean up to reduce image space
#RUN rm -rf /root/.cache/pypoetry/* && rm -rf /var/cache/apk/*
#RUN rm -rf /var/lib/apt/lists/* && apt clean

ENTRYPOINT ["python", "aqdr_api.py"]
