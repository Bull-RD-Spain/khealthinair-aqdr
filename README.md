# K-HEALTHinAIR Air Quality Data Repository (AQDR)

## Description

The K-HEALTHinAIR Air Quality Data Repository (AQDR) includes the subcomponents in charge of the aggregation and maganement of the air quality information that comes from the continuous monitoring devices.

### The Platform database (`aqdr-platform-db` and `aqdr-platform-db-ui`)

Based on PostgreSQL, provides storage for the sensor devices for continuous monitoring management and other generic purposes. It also includes an `adminer` service to easily visualize the content through a GUI for internal sensors management purposes.

### The Time-Series database (`aqdr-ts-db`)

Based on InfluxDB, a Time-Series Database, this module stores all indoor (IAQ) and outdoor (OAQ) air quality records continuously monitored by the device sensors, thanks to the ETL (Extract, Transform, Load) processes that AQDR Ingestor performs. Also includes clinical data that by its nature is more optimal to be stored in this type of database and not the one in which the rest of the clinical data is stored (e.g: heart rate).

### The API (`aqdr-api`)

Module responsible for enabling direct communication with AQDR Database and facilitates some GET endpoints to retrieve continuously monitored air quality data that is stored in it, allowing to query data until several levels of hierarchy (Pilot, Scenario, Subscenario and Area levels). It also enables sensor devices' administration (i.e., registering a newly installed sensor, deleting a sensor, etc.) through several dedicated endpoints.

### The Ingestor (`aqdr-ingestor`)

Module responsible for running all scheduled ETL pipelines. It performs the automated ingestion of the data collected by the sensor devices into the platform.

### The UI (`aqdr-ui`)

Based on Grafana, it includes several detailed visualisations based on sensors data and offers scientists greater insights by allowing to play with the data and explore the air quality data from different perspectives. The aqdr-ui also includes an initialization process which fulfils expected Grafana configuration like set of users or default organization name.

## Prerequisites

In order to run this platform, you should have this project code, which contains several sub-componets, checked out from the reference github.gsissc.myatos.net/orgs/GLB-BDS-AI-APPS/khealthinair-aqdr registry.

### Docker-Compose (dev)

Dockerfiles indicated in the `build` directive should be available to build live during the development phase, properties and other arguments are hardcoded.

The files under `.devcontainer` are in turn prepared for use with VSCode's own 'dev containers' functionality, but sensitive data does not have to be kept in the code repository, so it needs to be completed locally (e.g.: SENSORS_DB_PASSWORD, DOCKER_INFLUXDB_INIT_ADMIN_TOKEN, AQDR_API_AUTH_SECRET_KEY...)

### Docker-Compose (prod)

Images indicated in the `image` directive should be already built and available in the registry, properties and other arguments are set to be replaced from and `.env` file.

Note the structure of the project allows set the build's context path from the root, for example the following builds tagged in local repository:

```shell
cd K-HEALTHinAIR/khealthinair-aqdr
docker build -t khealthinair/aqdr-api:latest aqdr-api
docker build -t khealthinair/aqdr-ingestor:latest aqdr-ingestor
docker build -t khealthinair/aqdr-ui:latest aqdr-ui
```

### Kubernetes (dev)

The kubernetes descriptor files located under /deployment/kubernetes uses the complete tag name with `latest` versions in the reference to the images. Configuration should come from resources of type `secrets` (already created in advance and not maintained in the code repository for obvious reasons), and `configMaps` that also should be applied in advance and linked to the deployment files.

### Kubernetes (prod)

For specific components versions, the tag name `latest` should be modified with the specific and previously available tag indication the specific version, e.g.: `2.0.0`. The deployment should be done in the order expected, with resources of type `secret`(not maintained entirely in the code repository) deployed in advance.

## License

Copyright © 2021-2026 Bull SAS

SPDX-License-Identifier: GPL-3.0-or-later

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. See [LICENSE.txt](LICENSE.txt) for the full text, and [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md) for third-party components.
