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

# ==============================================================
# AQDR RESTORE - K-HEALTHinAIR
#
# Prerequisites:
#   1. Docker and docker-compose installed
#   2. Have run docker login to the private registry
#   3. Have this structure on the server:
#
#      ~/khia/
#      ├── docker-compose.yaml
#      ├── .env                         ← edit before running
#      ├── restore_aqdr.sh              ← this script
#      ├── init-scripts/
#      │   ├── 00-aqdr-platform-db-init.sh
#      │   ├── 01-aqdr-platform-db-init.sql
#      │   └── aqdr-ts-db-init.sh
#      └── db_backups/
#          ├── postgres/
#          │   └── postgres_sensors_DATE.sql
#          └── influx/
#              └── backup_DATE/        ← folder with the shards
#
# Usage:
#   bash ~/khia/restore_aqdr.sh \
#     ~/khia/db_backups/postgres/postgres_sensors_DATE.sql \
#     ~/khia/db_backups/influx/backup_DATE \
#     INFLUX_TOKEN_FROM_BACKUP
#
# The INFLUX_TOKEN_FROM_BACKUP is the DOCKER_INFLUXDB_INIT_ADMIN_TOKEN
# from the source cluster. It can be obtained with:
#   kubectl get secret <INFLUXDB_SECRET_NAME> -n <NAMESPACE> \
#     -o jsonpath='{.data.DOCKER_INFLUXDB_INIT_ADMIN_TOKEN}' | base64 -d
# ==============================================================

set -e

PG_BACKUP="$1"
INFLUX_BACKUP="$2"
INFLUX_TOKEN="$3"
COMPOSE_DIR="$HOME/khia"

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'

log_step() { echo -e "\n${YELLOW}$1${NC}"; }
log_ok()   { echo -e "  ${GREEN}OK${NC}  $1"; }
log_fail() { echo -e "\n  ${RED}ERROR${NC}  $1\n"; exit 1; }

echo -e "\n${YELLOW}╔═══════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║   RESTORE AQDR - K-HEALTHinAIR           ║${NC}"
echo -e "${YELLOW}╚═══════════════════════════════════════════╝${NC}"
echo "  Date              : $(date)"
echo "  PostgreSQL backup : $PG_BACKUP"
echo "  InfluxDB backup   : $INFLUX_BACKUP"
echo ""

# ── Validate parameters ───────────────────────────────────────
[ -z "$PG_BACKUP" ]       && log_fail "Missing PostgreSQL backup (arg 1).\n  Usage: bash restore_aqdr.sh <pg_backup.sql> <influx_backup_dir> <influx_token>"
[ -z "$INFLUX_BACKUP" ]   && log_fail "Missing InfluxDB backup folder (arg 2)."
[ -z "$INFLUX_TOKEN" ]    && log_fail "Missing InfluxDB token (arg 3)."
[ ! -f "$PG_BACKUP" ]     && log_fail "File not found: $PG_BACKUP"
[ ! -d "$INFLUX_BACKUP" ] && log_fail "Folder not found: $INFLUX_BACKUP"
[ ! -f "$COMPOSE_DIR/docker-compose.yaml" ] && log_fail "docker-compose.yaml not found in $COMPOSE_DIR"
[ ! -f "$COMPOSE_DIR/.env" ]                && log_fail ".env not found in $COMPOSE_DIR"

cd "$COMPOSE_DIR"

# ── 1. Stop and remove existing containers ────────────────────
log_step "[1/7] Stopping and removing existing containers..."
docker stop aqdr-ui aqdr-api aqdr-platform-db-ui aqdr-ts-db aqdr-platform-db 2>/dev/null || true
docker rm   aqdr-ui aqdr-api aqdr-platform-db-ui aqdr-ts-db aqdr-platform-db 2>/dev/null || true
log_ok "Containers removed."

# ── 2. Update token in .env ───────────────────────────────────
log_step "[2/7] Updating InfluxDB token in .env..."
sed -i "s|^KHIA_DSOURCE_AUTH_TOKEN=.*|KHIA_DSOURCE_AUTH_TOKEN=${INFLUX_TOKEN}|" "$COMPOSE_DIR/.env"
sed -i "s|^DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=.*|DOCKER_INFLUXDB_INIT_ADMIN_TOKEN=${INFLUX_TOKEN}|" "$COMPOSE_DIR/.env"
log_ok "Token updated."

# ── 3. Start databases ────────────────────────────────────────
log_step "[3/7] Starting PostgreSQL and InfluxDB..."
docker-compose up -d aqdr-platform-db aqdr-ts-db

echo "  Waiting for them to be healthy (max 200s)..."
for i in $(seq 1 20); do
    PG_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' aqdr-platform-db 2>/dev/null || echo "starting")
    INFLUX_HEALTH=$(docker inspect --format='{{.State.Health.Status}}' aqdr-ts-db 2>/dev/null || echo "starting")
    [ "$PG_HEALTH" = "healthy" ] && [ "$INFLUX_HEALTH" = "healthy" ] && break
    echo "  ($i/20) PG: $PG_HEALTH | Influx: $INFLUX_HEALTH — waiting 10s..."
    sleep 10
done
[ "$PG_HEALTH" != "healthy" ]     && log_fail "PostgreSQL is not healthy after 200s."
[ "$INFLUX_HEALTH" != "healthy" ] && log_fail "InfluxDB is not healthy after 200s."
log_ok "Databases healthy."

# ── 4. Restore PostgreSQL ─────────────────────────────────────
log_step "[4/7] Restoring PostgreSQL (sensors)..."

# Clear previous data if present
docker exec aqdr-platform-db psql -U khealthinair_admin -d sensors \
    -c "TRUNCATE TABLE sensors;" 2>/dev/null || true

# Restore
docker exec -i aqdr-platform-db psql -U khealthinair_admin -d sensors < "$PG_BACKUP" 2>&1 \
    | grep -v "^SET$" | grep -v "^$" || true

COUNT=$(docker exec aqdr-platform-db psql -U khealthinair_admin -d sensors \
    -t -c "SELECT COUNT(*) FROM sensors;" | tr -d ' \n')
log_ok "PostgreSQL restored: $COUNT records."

# ── 5. Restore InfluxDB ───────────────────────────────────────
log_step "[5/7] Restoring InfluxDB (AIR_QUALITY + HEALTH_MONITORING)..."

# Copy backup into the container
docker exec aqdr-ts-db rm -rf /tmp/influx_restore 2>/dev/null || true
docker cp "$INFLUX_BACKUP" aqdr-ts-db:/tmp/influx_restore

# Delete existing buckets (AIR_QUALITY and HEALTH_MONITORING)
for BUCKET in AIR_QUALITY HEALTH_MONITORING; do
    BUCKET_ID=$(docker exec aqdr-ts-db influx bucket list \
        --token "$INFLUX_TOKEN" --org K-HEALTHinAIR \
        --hide-headers 2>/dev/null | grep "$BUCKET" | awk '{print $1}' | head -1)
    if [ -n "$BUCKET_ID" ]; then
        docker exec aqdr-ts-db influx bucket delete \
            --id "$BUCKET_ID" --token "$INFLUX_TOKEN" > /dev/null
        echo "  Bucket $BUCKET deleted."
    fi
done

# Full restore (includes token and metadata)
docker exec aqdr-ts-db influx restore /tmp/influx_restore \
    --token "$INFLUX_TOKEN" --full

# Clean up temporary files
docker exec aqdr-ts-db rm -rf /tmp/influx_restore

# Verify buckets
BUCKETS=$(docker exec aqdr-ts-db influx bucket list \
    --token "$INFLUX_TOKEN" --org K-HEALTHinAIR \
    --hide-headers 2>/dev/null | grep -E "AIR_QUALITY|HEALTH_MONITORING" | wc -l)
[ "$BUCKETS" -lt 2 ] && log_fail "Only $BUCKETS of 2 expected buckets were found."
log_ok "InfluxDB restored: AIR_QUALITY + HEALTH_MONITORING."

# ── 6. Start the remaining services ──────────────────────────
log_step "[6/7] Starting API, Adminer and Grafana..."
docker-compose up -d aqdr-api aqdr-platform-db-ui aqdr-ui
log_ok "Services started."

# ── 7. Verify final state ─────────────────────────────────────
log_step "[7/7] Verifying final state (waiting 30s)..."
sleep 30
docker-compose ps

VM_IP=$(hostname -I | awk '{print $1}')
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   RESTORE completed successfully          ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════╝${NC}"
echo "  PostgreSQL : $COUNT sensors restored"
echo "  InfluxDB   : AIR_QUALITY + HEALTH_MONITORING"
echo ""
echo "  Grafana    : http://${VM_IP}:3000"
echo "  Adminer    : http://${VM_IP}:8084"
echo "  InfluxDB   : http://${VM_IP}:8086"
