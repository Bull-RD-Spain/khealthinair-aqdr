# Loading inBiot historical data into InfluxDB

Script to load IAQ data exported by inBiot (CSV format) directly into InfluxDB, replicating the exact format used by the AQDR ingestor.

## Background

The 12 NORES sensors with no data in InfluxDB could not be ingested through the regular pipeline because:

1. The `inclusion_time` in PostgreSQL was set to `2023-03-01`, a date prior to the actual activation of the sensors.
2. The backfilling process requested data from the inBiot API starting from that date, receiving `404 Not Found` for the months with no measurements.
3. The inBiot rate limit (6 req/hour) exhausted all attempts before reaching the months with actual data (from July 2023 onwards).

inBiot has provided the historical data as CSV files, which this script loads directly into InfluxDB.


## Files

- `load_csv_to_influx.py` — Main loading script.
- `sensors_table.csv` — Export of the PostgreSQL sensors table (required to map each CSV to the correct sensor).
- `update_inclusion_time.sql` — Auto-generated after loading; contains the `UPDATE` statements to fix `inclusion_time` in PostgreSQL.


## Requirements

- Python 3.8+
- `influxdb-client` (`pip install influxdb-client`)
- Access to the InfluxDB instance (URL, token, org)
- Access to the AQDR PostgreSQL database to run the `inclusion_time` UPDATE statements


## Setup

### 1. File structure

```
workdir/
├── load_csv_to_influx.py
├── sensors_table.csv          # PostgreSQL export
└── csv_data/
    ├── data_RES0111.csv       # sensor RES01, area 11
    ├── data_RES0411.csv       # sensor RES04, area 11
    ├── data_RES0511.csv       # sensor RES05, area 11
    └── ...                    # one file per sensor
```

### 2. CSV naming convention

Each file must be named `data_<SCENARIO><AREA>.csv`, where `SCENARIO` and `AREA` correspond to the `scenario` and `area` columns in the PostgreSQL sensors table. Example: `data_RES0411.csv` → scenario `RES04`, area `11` → sensor `115b1cdb...`.

### 3. Expected CSV format

Delimiter `;`, encoding `ISO-8859-1` (latin1), with the following relevant columns:

| Column | InfluxDB field |
|--------|---------------|
| Date (col 0) | timestamp (dd/mm/yyyy) |
| Time (col 1) | timestamp (HH:MM:SS) |
| Temperature °C (col 6) | `temperature` |
| Humidity % (col 7) | `humidity` |
| CO2 ppm (col 8) | `co2` |
| Formaldehyde (col 9) | `formaldehyde` |
| TVOC ppb (col 10) | `tvocs` |
| PM 1.0 (col 11) | `pm1` |
| PM 10 (col 13) | `pm10` |
| PM 2.5 (col 14) | `pm25` |

Weather/Outdoor columns (cols 16-21) are ignored — they have different dates and do not correspond to IAQ data from the sensor.


## Execution

### Step 1 — Dry run (no data written)

Verify that the file-to-sensor mapping is correct and the CSVs parse properly:

```bash
DRY_RUN=true \
SENSORS_TABLE=./sensors_table.csv \
CSV_DIR=./csv_data \
python load_csv_to_influx.py
```

Review the output: it should show each file with its `sensor_id`, the number of parsed points, and the date range.

### Step 2 — Actual load

```bash
export INFLUXDB_URL=http://localhost:8086
export DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=<token>
export DOCKER_INFLUXDB_INIT_ORG=<org>
export DOCKER_INFLUXDB_INIT_BUCKET=AIR_QUALITY    # optional, defaults to AIR_QUALITY
export SENSORS_TABLE=./sensors_table.csv
export CSV_DIR=./csv_data

python load_csv_to_influx.py
```

If running against the production InfluxDB on Kubernetes, first set up port-forwarding:

```bash
kubectl port-forward svc/aqdr-ts-db 8086:8086
```

### Step 3 — Update inclusion_time in PostgreSQL

After loading, the script generates `update_inclusion_time.sql` with one `UPDATE` per sensor. Run it against the AQDR PostgreSQL database:

```bash
psql -h <host> -p <port> -U <user> -d <db> -f update_inclusion_time.sql
```

Or from the PostgreSQL pod in Kubernetes:

```bash
kubectl exec -it <aqdr-platform-db-pod> -- psql -U <user> -d <db> -f -
# paste the SQL contents
```

This fixes the `inclusion_time` for each sensor to point to the date of its first actual data point from the CSV, preventing future backfilling runs from requesting data from inBiot for periods with no measurements.


## Verification

After loading, verify that the data is in InfluxDB. From the InfluxDB pod:

```bash
influx query \
  --host http://localhost:8086 \
  --org "$DOCKER_INFLUXDB_INIT_ORG" \
  --token "$DOCKER_INFLUXDB_INIT_ADMIN_TOKEN" \
  'from(bucket: "AIR_QUALITY")
    |> range(start: -365d)
    |> filter(fn: (r) => r._measurement == "CONTINUOUS_MONITORING_")
    |> filter(fn: (r) => r.sensor_id == "<FULL_SENSOR_ID>")
    |> last()
    |> keep(columns: ["_time","sensor_id","_field","_value"])'
```


## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `INFLUXDB_URL` | `http://localhost:8086` | InfluxDB URL |
| `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` | — | InfluxDB admin token |
| `DOCKER_INFLUXDB_INIT_ORG` | — | InfluxDB organization |
| `DOCKER_INFLUXDB_INIT_BUCKET` | `AIR_QUALITY` | InfluxDB bucket |
| `CSV_DIR` | `./csv_data` | Directory containing the inBiot CSVs |
| `SENSORS_TABLE` | `./sensors_table.csv` | Sensors table export |
| `DRY_RUN` | `false` | Set to `true` to simulate without writing |


## Notes

- The script writes in batches of 5000 points to avoid overloading InfluxDB.
- `None` or empty values in the CSV are skipped (same behavior as the ingestor).
- The PostgreSQL table name in the UPDATE statements is hardcoded as `sensors`. If it differs, edit the `sensors_table_name()` function in the script.
- CSV timestamps are interpreted as UTC, consistent with the ingestor's behavior.
