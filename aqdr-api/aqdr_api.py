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

# -*- coding: utf-8 -*-
"""Air Quality Data Repository API

Script to deploy an API to query measurements from InfluxDB database for
further AI/ML analysis
"""
import logging
import debugpy
import os
import sys
from datetime import datetime, timedelta
from typing import Annotated

import influxdb_client
import pandas as pd
import uvicorn
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    FastAPI,
    HTTPException,
    Query,
    status,
)
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from modules.authentication import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    Token,
    User,
    api_users_db,
    authenticate_user,
    create_access_token,
    credentials_exception,
    get_current_user,
)
from modules.config import Config
from modules.docs import (
    API_DESCRIPTION_HEADER,
    contact,
    license_info,
    tags_metadata,
)
from modules.enums import (
    DEScenarios,
    ESScenarios,
    FileFormat,
    NLScenarios,
    NOScenarios,
    Pilots,
    POAScenarios,
    Providers,
    Scenarios,
)
from modules.influx import query_influx_data
from modules.sensors import (
    _is_sensor_registered,
    check_sensor,
    delete_sensor_data,
    get_registered_sensors,
    get_sensor_description,
    is_sensors_database_empty,
    register_sensor,
    unregister_sensor,
)

# from fastapi_keycloak import FastAPIKeycloak, OIDCUser, UsernamePassword,
# HTTPMethod, KeycloakUser, KeycloakGroup


class EndpointFilter(logging.Filter):
    """Filter endpoints not wanted to happear in the logs"""

    def __init__(self, excluded_endpoints: list[str]) -> None:
        super().__init__()  # Call the __init__ method from the base class
        self.excluded_endpoints = excluded_endpoints

    def filter(self, record: logging.LogRecord) -> bool:
        return (
            record.args
            and len(record.args) >= 3
            and record.args[2] not in self.excluded_endpoints
        )


influx_client = influxdb_client.InfluxDBClient(
    url=Config.aqdr_ts_db["INFLUXDB_URL"],
    token=Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_ADMIN_TOKEN"],
    org=Config.aqdr_ts_db["DOCKER_INFLUXDB_INIT_ORG"],
    timeout=(10_000, 1_000_000),
)

# Get and AQDR_API_CONTEXTPATH env vars
CONTEXTPATH = Config.AQDR_API_CONTEXTPATH

# async def not_found_error(request: Request, exc: HTTPException):
#    """Endpoint to provide a Template as response to 404 HTTP errors"""
#    return templates.TemplateResponse(
#        "404.html", {"request": request}, status_code=404, context=exc.detail
#    )
# templates = Jinja2Templates(directory="templates")
# exception_handlers = {404: not_found_error}

# Custom FastAPI design and settings
# Use a @route with CONTEXTPATH as prefix instead of root_path=CONTEXTPATH,
app = FastAPI(
    title="K-HEALTHinAIR Air Quality Data Repository API",
    description=API_DESCRIPTION_HEADER,
    version="2.0.0",
    contact=contact,
    license_info=license_info,
    docs_url=CONTEXTPATH + "/docs",
    openapi_url=CONTEXTPATH + "/openapi.json",
    openapi_tags=tags_metadata,
    # https://swagger.io/docs/open-source-tools/swagger-ui/usage/configuration/
    swagger_ui_parameters={
        "useUnsafeMarkdown": True,
        "syntaxHighlight.theme": "outline",
        "docExpansion": "none",
        "defaultModelsExpandDepth": -1,
    },
    redoc_url=None,
    # exception_handlers=exception_handlers,
)
# idp = FastAPIKeycloak(
#    server_url= SERVER_URL + ":8080/auth",
#    client_id="aqdr-api",
#    client_secret="",
#    admin_client_secret="",
#    realm="aqdr-api-realm",
#    callback_uri=SERVER_URL +":8080/callback"
# )
# idp.add_swagger_config(app)

# To keep aligned in is needed to share subdomain and decide by ContextPath
router = APIRouter(prefix=CONTEXTPATH)


@app.get("/", include_in_schema=False)
def home_root():
    """Redirect to the Swagger UI page."""
    return RedirectResponse(
        url=app.docs_url,
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )


@app.get(router.prefix, include_in_schema=False)
def home_root_prefix():
    """Redirect to the Swagger UI page."""
    return RedirectResponse(
        url=app.docs_url,
        status_code=status.HTTP_308_PERMANENT_REDIRECT,
    )


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Return the favicon.ico file."""
    return FileResponse(os.path.join("static", "favicon.ico"))


@app.get(
    "/health/ready",
    tags=["Admin"],
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)",
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def get_health() -> str:
    """Perform a Health Check. Note is under root app no router CONTEXTPATH"""
    return "{'status': 'UP'}"


@router.post("/token", response_model=Token, include_in_schema=False)
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """Authentication endpoint to create JWT.
    Each time username and password are provided through
    OAuth2PasswordRequestForm, creates and returns JWT Access Token if valid
    credentials and authentication.
    """

    user = authenticate_user(
        api_users_db, form_data.username, form_data.password
    )
    if not user:
        raise credentials_exception

    logging.info(
        "Requesting access token for username [%s]...", form_data.username
    )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/de",
    tags=["DE Pilot"],
    summary="Endpoint to get Air Quality data of Germany pilot.",
)
def query_measurements_germany(
    user: Annotated[User, Depends(get_current_user)],
    file_format: FileFormat = Query(
        description="Desired format of the output file with Air Quality data."
    ),
    scenario: DEScenarios = Query(
        description="Type of scenario of the pilot."
    ),
    sub_scenario: int = Query(
        description="Code of the specific scenario of the pilot. "
        + "E.g.: '*2*' or '*02*' are both valid.",
        ge=0o1,
        le=99,
        default=None,
    ),
    area: int = Query(
        description="Code of the specific area of the scenario. "
        + "E.g.: '*5*', '*05*', or '*005*' are all valid.",
        ge=0o1,
        le=999,
        default=None,
    ),
    start_datetime: str = Query(
        description="Starting date to retrieve data in ISO 8601 date format "
        + "(*yyyy-mm-dd).",
        default="2023-03-01",
    ),
    end_datetime: str = Query(
        description="End date to retrieve data in ISO 8601 date format "
        + "(*yyyy-mm-dd*, default: now).",
        default=None,
    ),
):
    """Endpoint to get Air Quality data of Germany pilot."""
    if sub_scenario is None and area is not None:
        raise HTTPException(
            status_code=400,
            detail="Area cannot be set if subscenario is None.",
        )

    if "AQ" not in user.access and "DE" not in user.access:
        raise HTTPException(
            status_code=401, detail="Invalid authentication for AQ endpoint."
        )

    sub_scenario = str(sub_scenario).zfill(2) if sub_scenario else None
    area = str(area).zfill(3) if area else None
    pilot_tag = "DE"
    file = query_influx_data(
        influx_client,
        pilot_tag,
        scenario.value,
        sub_scenario,
        area,
        file_format,
        start_datetime,
        end_datetime,
    )
    return file


@router.get(
    "/es",
    tags=["ES Pilot"],
    summary="Endpoint to get Air Quality data of Spain pilot.",
)
def query_measurements_spain(
    user: Annotated[User, Depends(get_current_user)],
    file_format: FileFormat = Query(
        description="Desired format of the output file with Air Quality data."
    ),
    scenario: ESScenarios = Query(
        description="Type of scenario of the pilot."
    ),
    sub_scenario: int = Query(
        description="Code of the specific scenario of the pilot. "
        + "E.g.: '*2*' or '*02*' are both valid.",
        ge=0o1,
        le=99,
        default=None,
    ),
    area: int = Query(
        description="Code of the specific area of the scenario. "
        + "E.g.: '*5*', '*05*', or '*005*' are all valid.",
        ge=0o1,
        le=999,
        default=None,
    ),
    start_datetime: str = Query(
        description="Starting date to retrieve data in ISO 8601 date format."
        + "(*yyyy-mm-dd*).",
        default="2023-03-01",
    ),
    end_datetime: str = Query(
        description="End date to retrieve data in ISO 8601 date format "
        + "(*yyyy-mm-dd*, default: now).",
        default=None,
    ),
):
    """Endpoint to get Air Quality data of Spain pilot."""
    if sub_scenario is None and area is not None:
        raise HTTPException(
            status_code=400,
            detail="Area cannot be set if subscenario is None.",
        )

    if "AQ" not in user.access and "ES" not in user.access:
        raise HTTPException(
            status_code=401, detail="Invalid authentication for AQ endpoint."
        )

    sub_scenario = str(sub_scenario).zfill(2) if sub_scenario else None
    area = str(area).zfill(3) if area else None
    pilot_tag = "ES"
    file = query_influx_data(
        influx_client,
        pilot_tag,
        scenario.value,
        sub_scenario,
        area,
        file_format,
        start_datetime,
        end_datetime,
    )
    return file


@router.get(
    "/nl",
    tags=["NL Pilot"],
    summary="Endpoint to get Air Quality data of the Netherlands pilot.",
)
def query_measurements_netherlands(
    user: Annotated[User, Depends(get_current_user)],
    file_format: FileFormat = Query(
        description="Desired format of the output file with Air Quality data."
    ),
    scenario: NLScenarios = Query(
        description="Type of scenario of the pilot."
    ),
    sub_scenario: int = Query(
        description="Code of the specific scenario of the pilot. "
        + "E.g.: '*2*' or '*02*' are both valid.",
        ge=0o1,
        le=99,
        default=None,
    ),
    area: int = Query(
        description="Code of the specific area of the scenario. "
        + "E.g.: '*5*', '*05*', or '*005*' are all valid.",
        ge=0o1,
        le=999,
        default=None,
    ),
    start_datetime: str = Query(
        description="Starting date to retrieve data in ISO 8601 date format."
        + "(*yyyy-mm-dd*).",
        default="2023-03-01",
    ),
    end_datetime: str = Query(
        description="End date to retrieve data in ISO 8601 date format "
        + "(*yyyy-mm-dd*, default: now).",
        default=None,
    ),
):
    """Endpoint to get Air Quality data of The Netherlands pilot."""
    if sub_scenario is None and area is not None:
        raise HTTPException(
            status_code=400,
            detail="Area cannot be set if subscenario is None.",
        )

    if "AQ" not in user.access and "NL" not in user.access:
        raise HTTPException(
            status_code=401, detail="Invalid authentication for AQ endpoint."
        )

    sub_scenario = str(sub_scenario).zfill(2) if sub_scenario else None
    area = str(area).zfill(3) if area else None
    pilot_tag = "NL"
    file = query_influx_data(
        influx_client,
        pilot_tag,
        scenario.value,
        sub_scenario,
        area,
        file_format,
        start_datetime,
        end_datetime,
    )
    return file


@router.get(
    "/no",
    tags=["NO Pilot"],
    summary="Endpoint to get Air Quality data of Norway pilot.",
)
def query_measurements_norway(
    user: Annotated[User, Depends(get_current_user)],
    file_format: FileFormat = Query(
        description="Desired format of the output file with Air Quality data."
    ),
    scenario: NOScenarios = Query(
        description="Type of scenario of the pilot."
    ),
    sub_scenario: int = Query(
        description="Code of the specific scenario of the pilot. "
        + "E.g.: '*2*' or '*02*' are both valid.",
        ge=0o1,
        le=99,
        default=None,
    ),
    area: int = Query(
        description="Code of the specific area of the scenario. "
        + "E.g.: '*5*', '*05*', or '*005*' are all valid.",
        ge=0o1,
        le=999,
        default=None,
    ),
    start_datetime: str = Query(
        description="Starting date to retrieve data in ISO 8601 date format."
        + "(*yyyy-mm-dd*).",
        default="2023-03-01",
    ),
    end_datetime: str = Query(
        description="End date to retrieve data in ISO 8601 date format "
        + "(*yyyy-mm-dd*, default: now).",
        default=None,
    ),
):
    """Endpoint to get Air Quality data of Norway pilot."""
    if sub_scenario is None and area is not None:
        raise HTTPException(
            status_code=400,
            detail="Area cannot be set if subscenario is None.",
        )

    if "AQ" not in user.access and "NO" not in user.access:
        raise HTTPException(
            status_code=401, detail="Invalid authentication for AQ endpoint."
        )

    sub_scenario = str(sub_scenario).zfill(2) if sub_scenario else None
    area = str(area).zfill(3) if area else None
    pilot_tag = "NO"
    file = query_influx_data(
        influx_client,
        pilot_tag,
        scenario.value,
        sub_scenario,
        area,
        file_format,
        start_datetime,
        end_datetime,
    )
    return file


@router.get(
    "/pl",
    tags=["PL/AT Pilot"],
    summary="Endpoint to get Air Quality data of Poland pilot.",
)
def query_measurements_poland(
    user: Annotated[User, Depends(get_current_user)],
    file_format: FileFormat = Query(
        description="Desired format of the output file with Air Quality data."
    ),
    scenario: POAScenarios = Query(
        description="Type of scenario of the pilot."
    ),
    sub_scenario: int = Query(
        description="Code of the specific scenario of the pilot. "
        + "E.g.: '*2*' or '*02*' are both valid.",
        ge=0o1,
        le=99,
        default=None,
    ),
    area: int = Query(
        description="Code of the specific area of the scenario. "
        + "E.g.: '*5*', '*05*', or '*005*' are all valid.",
        ge=0o1,
        le=999,
        default=None,
    ),
    start_datetime: str = Query(
        description="Starting date to retrieve data in ISO 8601 date format."
        + "(*yyyy-mm-dd*).",
        default="2023-03-01",
    ),
    end_datetime: str = Query(
        description="End date to retrieve data in ISO 8601 date format "
        + "(*yyyy-mm-dd*, default: now).",
        default=None,
    ),
):
    """Endpoint to get Air Quality data of Poland pilot."""
    if sub_scenario is None and area is not None:
        raise HTTPException(
            status_code=400,
            detail="Area cannot be set if subscenario is None.",
        )

    if "AQ" not in user.access and "PL" not in user.access:
        raise HTTPException(
            status_code=401, detail="Invalid authentication for AQ endpoint."
        )

    sub_scenario = str(sub_scenario).zfill(2) if sub_scenario else None
    area = str(area).zfill(3) if area else None
    pilot_tag = "PL"
    file = query_influx_data(
        influx_client,
        pilot_tag,
        scenario.value,
        sub_scenario,
        area,
        file_format,
        start_datetime,
        end_datetime,
    )
    return file


@router.get(
    "/at",
    tags=["PL/AT Pilot"],
    summary="Endpoint to get Air Quality data of Austria pilot.",
)
def query_measurements_austria(
    user: Annotated[User, Depends(get_current_user)],
    file_format: FileFormat = Query(
        description="Desired format of the output file with Air Quality data."
    ),
    scenario: POAScenarios = Query(
        description="Type of scenario of the pilot."
    ),
    sub_scenario: int = Query(
        description="Code of the specific scenario of the pilot. "
        + "E.g.: '*2*' or '*02*' are both valid.",
        ge=0o1,
        le=99,
        default=None,
    ),
    area: int = Query(
        description="Code of the specific area of the scenario. "
        + "E.g.: '*5*', '*05*', or '*005*' are all valid.",
        ge=0o1,
        le=999,
        default=None,
    ),
    start_datetime: str = Query(
        description="Starting date to retrieve data in ISO 8601 date format."
        + "(*yyyy-mm-dd*).",
        default="2023-03-01",
    ),
    end_datetime: str = Query(
        description="End date to retrieve data in ISO 8601 date format "
        + "(*yyyy-mm-dd*, default: now).",
        default=None,
    ),
):
    """Endpoint to get Air Quality data of Austria pilot."""
    if sub_scenario is None and area is not None:
        raise HTTPException(
            status_code=400,
            detail="Area cannot be set if no Value for subscenario.",
        )

    if "AQ" not in user.access and "AT" not in user.access:
        raise HTTPException(
            status_code=401, detail="Invalid authentication for AQ endpoint."
        )

    sub_scenario = str(sub_scenario).zfill(2) if sub_scenario else None
    area = str(area).zfill(3) if area else None
    pilot_tag = "AT"
    file = query_influx_data(
        influx_client,
        pilot_tag,
        scenario.value,
        sub_scenario,
        area,
        file_format,
        start_datetime,
        end_datetime,
    )
    return file


@router.post(
    "/sensors/{sensor_id}",
    tags=["Sensors"],
    summary="Endpoint to register a new sensor device in K-HEALTHinAIR "
    + "Platform AQDR.",
    description="**Register a sensor device in K-HEALTHinAIR Platform AQDR.** "
    "<br><br> "
    "To complete a successful registration, you should fill in all the fields "
    "of the form so that the description of the device you want to register "
    "is complete. Although some fields have automated "
    "validation mechanisms that will trigger errors if you try to ingest "
    "invalid information, “scenario” and “area” fields must be completed "
    "carefully since there is no actual way to check for the validity and "
    "correctness of these labels.<br><br>"
    "All form fields/parameters are mandatory for the sensor registration. "
    "<a href='static/K-HEALTHinAir_SensorsRegistration_v2.0.0.pdf' target="
    "'_blank'>Sensors Administration User Guide (AQDR API Sensors)</a><br><br>"
    "**K-HEALTHinAIR ID Convention guidelines must be followed.** <br><br>"
    "<img src='static/sensors_id_convention.png' alt='sensors_id_convention'>"
    "<br>"
    "**NOTE**: Please notice that once you successfully register a device, the"
    " values of the form fields remain the same. For this reason, registering "
    "sensors in a coherent order could be helpful for you to save time "
    "and perform this process in a more efficient manner. ",
)
async def add_sensor(
    user: Annotated[User, Depends(get_current_user)],
    sensor_id: str,
    apikey: str = Query(
        description="API Key associated with specific sensor_id for indoor "
        + "data."
    ),
    provider: Providers = Query(
        description="Type of the sensor (IB: inBiot, MH: qlair)"
    ),
    pilot: Pilots = Query(description="Pilot location of the sensor device."),
    scenario: str = Query(
        description="Scenario location of the sensor (3-letter + 2-digit code"
        ").",
        examples=["HOM02"],
        #   pattern=r"[A-Z]{3}(?!00)\d{2}",
    ),
    area: int = Query(
        description="Area location of the sensor.",
        examples=["005"],
        ge=0o1,
        le=999,
    ),
    outdoor_apikey: str = Query(
        description="API Key associated with specific building for outdoor "
        + "data."
    ),
    building: int = Query(description="Building ID for Outdoor Air Quality."),
    inclussion: str = Query(
        description="Inclussion date of the sensor (DD/MM/YYYY).",
        examples=["01/03/2023"],
        default="01/03/2023",
        pattern=r"\d{2}/\d{2}/\d{4}",
    ),
):
    """Register a sensor device in K-HEALTHinAIR Platform AQDR."""
    if pilot not in user.access:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication. Not enough permissions to "
            + "register this device.",
        )

    # Args validation
    sensor_providers = [sp.value for sp in Providers]
    pilots = [p.value for p in Pilots]
    scenarios = [s.value for s in Scenarios]
    scen_valid_numbering = [str(x).zfill(2) for x in list(range(1, 100, 1))]
    area_valid_numbering = [str(x).zfill(3) for x in list(range(1, 1000, 1))]

    if _is_sensor_registered(sensor_id):
        raise HTTPException(
            status_code=409,
            detail=f"SensorID [{sensor_id}] already registered in Platform.",
        )

    if provider not in sensor_providers:
        raise HTTPException(
            status_code=422,
            detail="Incorrect provider [{provider}]. Please choose from "
            + f"{sensor_providers}.",
        )

    if pilot not in pilots:
        raise HTTPException(
            status_code=422,
            detail=f"Incorrect pilot [{pilot.value}]. "
            + f"Please choose from {pilots}.",
        )

    if scenario[:3] not in scenarios:
        raise HTTPException(
            status_code=422,
            detail=f"Incorrect scenario. Please choose from {scenarios}.",
        )
    elif scenario[-2:] not in scen_valid_numbering or len(scenario) != 5:
        raise HTTPException(
            status_code=422,
            detail="Incorrect subscenario [{scenario}]. "
            + "Must choose from [1, 99].",
        )

    if str(area).zfill(3) not in area_valid_numbering:
        raise HTTPException(
            status_code=422,
            detail="Incorrect area [{area}]. Must choose from [1, 999].",
        )

    inclusion_time = datetime.strptime(inclussion, "%d/%m/%Y")
    if inclusion_time < datetime(2023, 3, 1):
        raise HTTPException(
            status_code=400,
            detail="The provided date must not be earlier than 01/03/2023.",
        )

    # Build pd.Series sensor for back-up purposes
    sensor = pd.Series(
        {
            "SENSOR_ID": sensor_id,
            "APIKEY": apikey,
            "PROVIDER": provider,
            "PILOT": pilot.value,
            "SCENARIO": scenario,
            "AREA": area,
            "APIKEY_OAQ": outdoor_apikey,
            "BUILDING": building,
        }
    )

    # First, check sensor validity
    check_sensor(sensor)

    # Then register device in AQDR-Platform-DB
    register_sensor(
        sensor_id,
        apikey,
        provider,
        pilot.value,
        scenario,
        area,
        outdoor_apikey,
        building,
        inclusion_time,
    )

    logging.info("User [%s]: REGISTER/[%s].", user.username, sensor_id)

    return f"SensorID [{sensor_id}] successfully registered."


@router.get(
    "/sensors",
    tags=["Sensors"],
    summary="Endpoint to get information about all sensor devices registered "
    + "in K-HEALTHinAIR Platform AQDR.",
    description="**Get all registered sensor devices in K-HEALTHinAIR "
    + "Platform AQDR.**<br>This endpoint returns the details of all of the "
    + "sensors registered in the platform.",
)
def get_all_registered_sensors(
    user: Annotated[User, Depends(get_current_user)],
):
    """Get all registered sensor devices in K-HEALTHinAIR Platform AQDR."""
    if "sensors" not in user.access:
        raise HTTPException(status_code=401, detail="Invalid authentication.")

    if is_sensors_database_empty():
        raise HTTPException(
            status_code=404, detail="No sensors found in AQDR-Platform-DB."
        ) from None

    file = get_registered_sensors()
    logging.info("User [%s]: GET/all.", user.username)

    return file


@router.get(
    "/sensors/{sensor_id}",
    tags=["Sensors"],
    summary="Endpoint to get labels and description added to specific sensor "
    + "device in K-HEALTHinAIR Platform AQDR.",
    description="**Get information about certain registered sensor device in "
    + "K-HEALTHinAIR Platform AQDR.**<br>This endpoint returns the details of "
    + "a single sensor identified by its sensor_id.",
)
def get_registered_sensor(
    user: Annotated[User, Depends(get_current_user)],
    sensor_id: str,
):
    """Get information about certain registered sensor device in K-HEALTHinAIR"
    + "Platform AQDR."""
    if "sensors" not in user.access:
        raise HTTPException(status_code=401, detail="Invalid authentication.")

    if _is_sensor_registered(sensor_id):
        sensor_info = get_sensor_description(sensor_id)
        logging.info("User [%s]: GET/[%s].", user.username, sensor_id)
        return sensor_info
    else:
        raise HTTPException(
            status_code=404,
            detail=f"SensorID [{sensor_id}] "
            + "does not exist in AQDR-Platform-DB.",
        )


@router.delete(
    "/sensors/{sensor_id}",
    tags=["Sensors"],
    summary="Endpoint to delete an existing sensor device from K-HEALTHinAIR "
    + "Platform AQDR.",
    description="**Delete a sensor device registered in K-HEALTHinAIR "
    "Platform AQDR.** <br><br> "
    "<img src='static/warning.gif' alt='warning' height='15px'> "
    "<b>WARNING</b>, please note this will delete permanently the specified "
    "sensor from K-HEALTHinAIR Platform AQDR and will therefore no longer be "
    "considered in AQDR. It will also lead to deleting <b>all the past air "
    "quality records</b> that have been ingested and stored in AQDR.<br>"
    "This operation is intended to support very specific situations in which "
    "the previous description of a device was incorrect (e.g., if you have "
    "accidentally registered a sensor with a wrong location tag, or if the "
    "tag of that sensor needs to be updated). In these cases, you must delete "
    "the sensor device first, and then register it again.",
)
async def delete_sensor(
    user: Annotated[User, Depends(get_current_user)],
    background_tasks: BackgroundTasks,
    sensor_id: str,
):
    """Delete sensor"""
    if "sensors" not in user.access:
        raise HTTPException(status_code=401, detail="Invalid authentication.")

    if _is_sensor_registered(sensor_id):
        # Only allowed users
        sensor_info = get_sensor_description(sensor_id)
        if sensor_info["pilot"] not in user.access:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication. Not enough permissions to "
                + "delete this device.",
            )

        background_tasks.add_task(delete_sensor_data, sensor_id)
        logging.info("User [%s]: DELETE/[%s].", user.username, sensor_id)

        unregister_sensor(sensor_id)
        logging.info("User [%s]: DELETE/[%s].", user.username, sensor_id)

    else:
        raise HTTPException(
            status_code=404,
            detail=f"SensorID [{sensor_id}] does not exist in DB.",
        )

    return f"SensorID [{sensor_id}] successfully deleted."


# @router.get(
#    "/sensors/sensors-status",
#    tags=["Sensors"],
#    summary="Endpoint to get a summary of the sensors along some stadistics.",
#    description="**Get a summary of the sensors along some stadistics.**",
# )
# def get_sensors_status(
#    user: Annotated[User, Depends(get_current_user)],
# ):
#    """Get a summary of the sensors along some stadistics."""
#    if "sensors" not in user.access:
#        raise HTTPException(status_code=401, detail="Invalid authentication.")

#    sensors_status = get_sensors_summary()
#    logging.info("User [%s]: Requestion sensors status")
#    return sensors_status


# Add debugpy hook
def start_debugger():
    """Start the debugger."""
    print("Enabling debugguer...")
    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()


if __name__ == "__main__":
    os.makedirs("/logs/api/", exist_ok=True)
    LOG_FILENAME = "/logs/api/aqdr-api.log"

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(LOG_FILENAME, mode="a"),
            logging.StreamHandler(),
        ],
    )
    # Avoid passlib AttributeError:module 'bcrypt' has no attribute '__about__'
    logging.getLogger("passlib").setLevel(logging.ERROR)
    logger = logging.getLogger()

    app.mount(
        CONTEXTPATH + "/static", StaticFiles(directory="static"), name="static"
    )
    app.include_router(router)

    try:
        logger.setLevel(Config.APP_LOG_LEVEL)
    except ValueError:
        logger.warning("No or invalid log level, defaulting to INFO.")
        logger.setLevel("INFO")

    if not Config.AQDR_API_AUTH_SECRET_KEY:
        logging.critical(
            "AQDR_API_AUTH_SECRET_KEY is not set, refusing to start."
        )
        sys.exit(1)

    logging.info(
        "AQDR-API started running on CONTEXTPATH: %s",
        CONTEXTPATH,
    )

    # Avoid healthcheck traces in log, match livenessProbe and readinessProbe
    logging.getLogger("uvicorn.access").addFilter(
        EndpointFilter(["/health/ready", CONTEXTPATH + "/static"])
    )
    #start_debugger()
    uvicorn.run(app, host="0.0.0.0", port=8083, log_level="info")
