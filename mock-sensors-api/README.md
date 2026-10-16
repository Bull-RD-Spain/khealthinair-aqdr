# Mock Sensor APIs — Inbiot, Qlair & Kunak

Standalone mock server that simulates the three external sensor APIs for local testing of the AQDR Ingestor. It is deployed separately from the AQDR stack so it can be started and stopped without affecting the rest of the platform.

## Structure

```
mock-sensors-api/
├── docker-compose.yaml    # Standalone Compose file
├── .env.example           # Template for the mock configuration (.env)
├── Dockerfile             # Image based on python:3.11-slim
├── mock_server.py         # FastAPI server with the three mocks
└── README.md
```

## Simulated endpoints

### Inbiot

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/last-measurements/{apikey}/{sensor_id}` | Latest indoor reading |
| GET | `/measurements-by-time/{apikey}/{sensor_id}/{init}/{end}` | Indoor history |

Generated data: temperature, humidity, co2, tvocs, pm1, pm10, pm25, formaldehyde.

### Qlair

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/open/indoor_air_quality?mac=...&start=...&end=...` | Indoor (latest or history) |
| GET | `/open/outdoor_air_quality?building_id=...&start=...&end=...` | Outdoor (latest or history) |

Headers: accepts `x-api-key` (any value). Indoor data: full chemisense. Outdoor data: pollutants, aqi, weather.

### Kunak

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rest/devices/{id}/reads/fromGroupByTs` | Readings since a timestamp |
| POST | `/rest/devices/{id}/reads/fromToGroupByTs` | Readings between two timestamps |

Headers: accepts `Authorization: Basic ...` (any value). Data: PM1, PM2.5, PM10, Temp ext, Humidity ext, NO2 GCc, VOCs GCc, Pressure.

## Configuration

Variables in `.env` (create it with `cp .env.example .env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `MOCK_PORT` | 8888 | Server port |
| `MOCK_NUM_READINGS` | 24 | Readings per historical request |
| `MOCK_INTERVAL_MIN` | 60 | Minutes between generated readings |

For **load testing**, change:

```dotenv
MOCK_NUM_READINGS=1000
MOCK_INTERVAL_MIN=5
```

## Usage

```bash
# From the repository root
cd mock-sensors-api

# Start
docker-compose up -d

# Verify
curl http://127.0.0.1:8888/health
curl http://127.0.0.1:8888/

# Show logs
docker-compose logs -f

# Stop
docker-compose down
```

## Integration with AQDR

Once the mock is running, change the three URLs in the AQDR `.env` (`deployment/docker-compose-wsl/.env`):

```dotenv
# Before (real APIs)
INBIOT_API_URL=https://myinbiotpublicapi.com
QLAIR_API_URL=https://api.v2.i-qlair.eu
KUNAK_API_URL=https://kunakcloud.com/openAPIv0/v1

# After (local mock)
INBIOT_API_URL=http://mock-sensor-apis:8888
QLAIR_API_URL=http://mock-sensor-apis:8888
KUNAK_API_URL=http://mock-sensor-apis:8888
```

Then restart the services that use the APIs:

```bash
# From the repository root
cd deployment/docker-compose-wsl
docker-compose restart aqdr-api aqdr-ingestor
```

Communication works because both share the `khealthinair-net` network; `mock-sensor-apis` is the mock's container name.

## Platform port

| Port | Service | Module |
|--------|----------|--------|
| 8888 | Mock Sensor APIs | Mock |

## Generated data

Values are random within realistic ranges for each quantity. Some examples:

| Quantity | Range | Unit |
|----------|-------|--------|
| Temperature (indoor) | 18 – 28 | °C |
| CO2 | 350 – 1200 | ppm |
| PM2.5 (outdoor) | 0 – 30 | µg/m³ |
| NO2 | 0 – 80 | µg/m³ |
| Pressure | 990 – 1035 | hPa |
