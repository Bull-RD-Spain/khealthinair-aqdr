# K-HEALTHinAIR Air Quality Data Repository (AQDR) - AQDR-API

Module responsible for enabling direct communication with AQDR Database and
facilitates some GET endpoints to retrieve continuously monitored air quality
data that is stored in it, allowing to query data until several levels of
hierarchy (Pilot, Scenario, Subscenario and Area levels). It also enables sensor
devices' administration (i.e., registering a newly installed sensor, deleting a
sensor, etc.) through several dedicated endpoints.

## Description

The **AQDR-API** is an API (based on FastAPI) for Air Quality Data Repository (AQDR)
that enables to leverage the monitoring Air Quality of the project.

It is designed for two main purposes:

1. Facilitating the retrieval of **continuously monitored air quality data from our Air Quality Data Repository Time-Series Database**,
allowing to query data according to several levels of hierarchy (Pilot, Scenario, Subscenario and Area levels).
To perform these queries, AQDR must be up and running (DB + Ingestor) and both parts must be pointing to the same InfluxDB-based Organization and Bucket.

2. **Sensors devices management** for INB and M+H sensor devices. Several operations are granted through their associated endpoints:
    - **GET /sensors/{sensor_id}:** Extracts the information of a specified sensor (pilot, scenario, area locations and given tags,
    apikeys, etc.)
    - **POST /sensors/{sensor_id}:** Registers a sensor in K-HEALTHinAIR Platform AQDR. For successfull registration, all required fields
    should be filled in following provided, ID-compliant guidelines. Then, the sensor is included into
    SensorsDB and its historic data is retrieved to be ingested into Air Quality Data Repository TSDB.
    - **DELETE /sensors/{sensor_id}:** Unregisters a sensor from SensorsDB and deletes all its historic datapoints from Air
    Quality Data Repository TSDB of the platform.
    - **GET /sensors:** Offers an Excel file with the information of all registered sensor devices in K-HEALTHinAIR Platform AQDR
    (and therefore SensorsDB), together with their associated tags and description.

## Project organization

    │
    ├── aqdr_api.py           <- Script for AQ API stand-up and main configuration
    ├── modules               <- Modules directory: API modules, custom enums and other utils
    ├── static                <- Images and assets
    ├── Dockerfile            <- Dockerfile for base image of the project
    ├── poetry.lock           <- Poetry Lock file (do not edit)
    ├── pyproject.toml        <- Requirements file and Poetry dependencies
    └── README.md             <- The top-level README for developers using this project

## Prerrequisites

In order to run this component, you should have this project code checked out, from GitHub repository.
This project is a Python-based one. VSCode with DevContainer extension and Docker are the only tools
needed to reproduce the environment.

## Local configuration

To run this entire project locally using docker-compose:

- Firstly, build AQDR API image:
`docker build -t aqdr-api:latest .`

- Then, from the home directory of the project:
`cd deployment/docker-compose_dev_comtainer`
`cp khealthinair-aqdr.env.example khealthinair-aqdr.env` (and fill in the values)
`docker-compose --env-file khealthinair-aqdr.env up`

To stand up AQDR API, the following environment variables must be set:

- APP_LOG_LEVEL=DEBUG
- INFLUXDB_URL=http://aqdr-ts-db:8086
- INFLUXDB_MEASUREMENT=CONTINUOUS_MONITORING_
- DOCKER_INFLUXDB_INIT_ORG=K-HEALTHinAIR # InfluxDB organization where target DB is located
- DOCKER_INFLUXDB_INIT_BUCKET=AIR_QUALITY # InfluxDB bucket where target DB is located
- DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=********
- AQDR_API_CONTEXTPATH=/api
- AQDR_API_AUTH_SECRET_KEY=******** # mandatory
- AQDR_API_USERS_FILE=/app/config/aqdr-api-users.json # JSON file with the API users
- SENSORS_DB_HOST=aqdr-platform-db # host of the database, e.g. host.docker.internal
- SENSORS_DB_PORT=5432 # Networked service-to-service communication uses the CONTAINER_PORT not HOST_PORT
- SENSORS_DB_TABLE=sensors
- SENSORS_DB_NAME=sensors
- SENSORS_DB_USER=sensors
- SENSORS_DB_PASSWORD=********
- INBIOT_API_URL=https://myinbiotpublicapi.com
- QLAIR_API_URL =https://api.v2.i-qlair.eu
- KUNAK_API_URL=https://kunakcloud.com/openAPIv0/v1

In this way, AQDR API will be running on http://localhost:8083/air-quality-api by default.

**NOTE**: for the POST/sensor endpoint, some other environment variables need to be set in order to
successfully include historic datapoints of the sensor_id specified into AQDR TSDB (INBIOT_API_URL_LATEST,
INBIOT_API_URL_HISTORIC, MANNHUMMEL_API_URL, OUTDOOR_AIR_QUALITY_ENDPOINT).

## Security

Air Quality Data Repository API is **secured based on authentication scheme OAuth 2.0** with password and hashing and uses **JWT (JSON Web Tokens)**.
This means that a valid username and password is needed to be authenticated and therefore having access to K-HEALTHinAIR AQDR TSDB data through AQDR API.

Several users have been created:

- Generic user
- Pilot Administrator user (for sensors administration)
- UNL/cartif/csic users for data analisys
- Provider user (INB/M+H, for sensors administration)

**NOTE**: AUTH_SECRET_KEY environment variable is used to sign JWT and ensure secure sessions.

The users list is not kept in the code repository. It is loaded at startup from a JSON file with hashed passwords, whose path is set with the `AQDR_API_USERS_FILE` environment variable (default `/app/config/aqdr-api-users.json`), while there is no credential manager component.
Use [`config/aqdr-api-users.example.json`](config/aqdr-api-users.example.json) as a template. The real `aqdr-api-users.json` is ignored by git and must be mounted into the container (the docker-compose files under `deployment/` already do this).
If the file is missing or invalid, the API starts but nobody can authenticate. If `AQDR_API_AUTH_SECRET_KEY` is not set, the API refuses to start.

To hash a password, a simple python script can be used
``` python
from passlib.context import CryptContext
wd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def encode_password(password: str) -> str:
    hashed_password = wd_context.hash(password)
    return hashed_password
if __name__ == "__main__":
    password = input("Enter the password to encode: ")
    encoded_password = encode_password(password)
    print("Encoded password:", encoded_password)`
```
