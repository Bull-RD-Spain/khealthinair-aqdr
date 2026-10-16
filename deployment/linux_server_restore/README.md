# AQDR - K-HEALTHinAIR — Deployment and Restore Instructions

## Prerequisites

- Docker and docker-compose installed
- Access to the private registry (set it as `REGISTRY_HOST` in `.env`)

```bash
docker login <REGISTRY_HOST>
```

---

## File structure

All files must be in `~/khia/` with the following structure:

```
~/khia/
├── docker-compose.yaml
├── .env                          ← edit before running
├── aqdr-api-users.json           ← API users (see aqdr-api/config/aqdr-api-users.example.json)
├── restore_aqdr.sh
├── init-scripts/
│   ├── 00-aqdr-platform-db-init.sh
│   ├── 01-aqdr-platform-db-init.sql
│   └── aqdr-ts-db-init.sh
└── db_backups/
    ├── postgres/
    │   └── postgres_sensors_DATE.sql
    └── influx/
        └── backup_DATE/
```

---

## Step 1 — Edit the .env file

Open `~/khia/.env` and adjust the following values for your environment:

```
# IP or hostname of your server (to access Grafana from the browser)
GRAFANA_INGRESS_URL=http://YOUR_IP:3000

# PostgreSQL credentials (you can leave them as they are or change them)
POSTGRES_PASSWORD=your_password
SENSORS_DB_PASSWORD=your_password
ADMINER_PASSWORD=your_password

# InfluxDB credentials (you can leave them, the restore will overwrite them)
DOCKER_INFLUXDB_INIT_PASSWORD=your_password
```

> The InfluxDB token (`DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` and
> `KHIA_DSOURCE_AUTH_TOKEN`) is updated automatically by the restore
> script — there's no need to touch it.

`AQDR_API_AUTH_SECRET_KEY` is mandatory: the API refuses to start without it
(generate one with `openssl rand -hex 32`). The API users are read from
`~/khia/aqdr-api-users.json`, created from
`aqdr-api/config/aqdr-api-users.example.json`.

---

## Step 2 — Grant permissions to the script

```bash
chmod +x ~/khia/restore_aqdr.sh
```

---

## Step 3 — Run the restore

```bash
bash ~/khia/restore_aqdr.sh \
  ~/khia/db_backups/postgres/postgres_sensors_DATE.sql \
  ~/khia/db_backups/influx/backup_DATE \
  INFLUX_TOKEN_FROM_BACKUP
```

The `INFLUX_TOKEN_FROM_BACKUP` will be provided to you by the K-HEALTHinAIR
team together with the backup files.

The script takes approximately **3-5 minutes** and shows step-by-step progress.
At the end it displays the access URLs.

---

## Accessing the services

| Service   | URL                        | User                  |
|-----------|----------------------------|------------------------|
| Grafana   | http://YOUR_IP:3000        | khealthinair_admin    |
| Adminer   | http://YOUR_IP:8084        | khealthinair_admin    |
| InfluxDB  | http://YOUR_IP:8086        | khealthinair_admin    |

---

## If you need to repeat the restore (previous data)

The script automatically cleans up the previous data before restoring.
Just run Step 3 again with the new backup files.

```bash
docker-compose down -v   # removes containers and volumes
bash ~/khia/restore_aqdr.sh <pg_backup> <influx_backup> <token>
```