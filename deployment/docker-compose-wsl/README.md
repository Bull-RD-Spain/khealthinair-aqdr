# K-HEALTHinAIR AQDR Module — Local Deployment with Docker Compose

Translation of the AQDR module's Kubernetes manifests to Docker Compose for local development on **WSL2 + Podman**.

## Prerequisites

### Base environment

- **WSL2** with Ubuntu 22.04 LTS and systemd enabled
- **Podman 4.x** installed from the Kubic repo, with `dbus-user-session` and `loginctl enable-linger` configured
- **Docker Compose V2 standalone** pointing to the Podman socket via `DOCKER_HOST=unix:///run/user/1000/podman/podman.sock`
- **Podman Desktop** connected over SSH with an ed25519 key

> If the base environment is not set up, follow the step-by-step guide: [WSL2 + Podman environment setup guide](./guide-podman-wsl2_with_troubleshoothing.md)

### Corporate proxy configuration

If you are behind a corporate proxy, local addresses must be excluded so the containers are reachable. Add to `~/.bashrc`:

```bash
export no_proxy="localhost,127.0.0.1,10.89.0.0/16"
export NO_PROXY="localhost,127.0.0.1,10.89.0.0/16"
```

You may also need to add `localhost` and `127.0.0.1` to the proxy exceptions in the Windows network settings (for browser access).

### Private registry credentials

The `aqdr-api`, `aqdr-ingestor` and `aqdr-ui` images are pulled from the private registry set in `REGISTRY_HOST` (`.env`). You must log in before bringing up the stack:

```bash
podman login <REGISTRY_HOST>
```

Docker Compose also needs access to the Podman credentials. If you get an `unauthorized` error, create a symlink:

```bash
mkdir -p ~/.docker
ln -sf ${XDG_RUNTIME_DIR}/containers/auth.json ~/.docker/config.json
```

## File structure

```
deployment/docker-compose-wsl/
├── docker-compose.yaml                         # Compose file with the 6 services
├── .env.example                                # Template for .env (ConfigMaps + Secrets)
├── init-scripts/
│   ├── 00-aqdr-platform-db-init.sh             # Creates the "sensors" user in PostgreSQL
│   ├── 01-aqdr-platform-db-init.sql            # Creates the "sensors" table, permissions, schema
│   └── aqdr-ts-db-init.sh                      # Creates extra buckets in InfluxDB
├── guide-podman-wsl2_with_troubleshoothing.md  # WSL2 + Podman setup guide
└── README.md
```

## Services

| Service | Image | Local port | Description |
|----------|--------|--------------|-------------|
| `aqdr-platform-db` | `postgres:16.4` | 5432 | Platform database (PostgreSQL) |
| `aqdr-platform-db-ui` | `michalhosna/adminer:4.8.1-en_v1` | 8084 | PostgreSQL admin UI |
| `aqdr-ts-db` | `influxdb:2.7.8` | 8086 | Time series database (InfluxDB) |
| `aqdr-api` | `aqdr-api:latest` (private registry) | 8083 | Backend API |
| `aqdr-ingestor` | `aqdr-ingestor:latest` (private registry) | — | Data ingestion worker (no port) |
| `aqdr-ui` | `aqdr-ui:latest` (private registry) | 3000 | Visualization UI (customized Grafana) |

## Kubernetes → Compose mapping

| K8s resource | Compose equivalent |
|---|---|
| `aqdr-platform-db-svc:8082` | `aqdr-platform-db:5432` (actual container port) |
| `aqdr-ts-db-svc:8086` | `aqdr-ts-db:8086` |
| `aqdr-api-svc:8083` | `aqdr-api:8083` |
| `aqdr-ui-svc:3000` | `aqdr-ui:3000` |
| `aqdr-platform-db-ui-svc:8084` | `aqdr-platform-db-ui:8080` (host 8084) |
| Init containers (wait loops) | `depends_on` + `healthcheck` |
| PVCs | Named volumes |
| ConfigMap file mounts | Bind mounts `./init-scripts/` |
| Ingress (HTTPS) | Host port mappings (HTTP) |
| `imagePullSecrets` | Prior `podman login` |
| Adminer sidecar (same Pod) | Separate service in Compose |

### Important port changes

In Kubernetes, the `aqdr-platform-db-svc` Service remapped **8082 → 5432**. In Compose the containers communicate directly on the container port:

- `SENSORS_DB_PORT`: `8082` → `5432`
- `SENSORS_DB_HOST`: `aqdr-platform-db-svc` → `aqdr-platform-db`
- `ADMINER_SERVER`: `aqdr-platform-db-svc:8082` → `aqdr-platform-db:5432`
- `INFLUXDB_URL`: `http://aqdr-ts-db-svc:8086` → `http://aqdr-ts-db:8086`

### Grafana URLs (aqdr-ui)

In K8s the URLs point to the public domain over HTTPS. Locally:

- `GRAFANA_INGRESS_URL` → `http://localhost:3000`
- `KHIA_DSOURCE_URL` → `http://aqdr-ts-db:8086`

## Configuration

### `.env` file

Create it from the template (`cp .env.example .env`). The `.env` file consolidates all values from the Kubernetes ConfigMaps and Secrets. The default values are generic, for local development:

- **Passwords**: simple values (minimum 8 characters for InfluxDB)
- **Tokens**: arbitrary strings, but consistent across services that share the same token (e.g. `DOCKER_INFLUXDB_INIT_ADMIN_TOKEN` and `KHIA_DSOURCE_AUTH_TOKEN` must be equal)
- **External APIs** (Inbiot, Qlair, Kunak): point to the real endpoints but with dummy credentials. They will not work until local mocks are set up.
- **SMTP**: disabled locally (`GF_SMTP_ENABLED=false`)
- **Mandatory secrets**: `aqdr-api` refuses to start without `AQDR_API_AUTH_SECRET_KEY`, and `aqdr-ingestor` without `KUNAK_API_BASIC_AUTH`

### aqdr-api-users.json

The API users (with bcrypt-hashed passwords) are not kept in the repository. Create `./aqdr-api-users.json` from `aqdr-api/config/aqdr-api-users.example.json`; it is mounted into `aqdr-api`. See the `aqdr-api` README for how to hash passwords.

### aqdr-ui-init-conf.yaml (optional)

The K8s deployment mounts a Grafana initialization YAML file from a Secret (`AQDR_UI_INIT_CONFIG_FILE_YAML`). If you have its contents, place it at `./init-scripts/aqdr-ui-init-conf.yaml` and uncomment the corresponding line in `docker-compose.yaml`.

## Usage

```bash
cd deployment/docker-compose-wsl

# Start everything
docker-compose up -d

# Show status
docker-compose ps

# Show logs for all services
docker-compose logs -f

# Show logs for a specific service
docker-compose logs -f aqdr-ts-db

# Stop
docker-compose down

# Stop and delete volumes (full data reset)
docker-compose down -v
```

## Accessing the interfaces

| Interface | URL | Credentials |
|----------|-----|--------------|
| InfluxDB | http://localhost:8086 | `khealthinair_admin` / (see `.env`) |
| Grafana | http://localhost:3000 | `khealthinair_admin` / (see `.env`) |
| Adminer | http://localhost:8084 | `khealthinair_admin` / (see `.env`) |
| AQDR API | http://localhost:8083/api | — |

## Network

The services communicate over the `khealthinair-net` network. This network is created automatically when the stack is brought up (`external: false` with `name: khealthinair-net`), and if it already exists (because another module such as DAQSR is running), it is reused.

This enables communication between modules. For example, the AQDR services can reach the DAQSR module's MinIO at `http://daqsr-minio:9000`.

## Troubleshooting

### InfluxDB: "Error: password is too short"

InfluxDB 2.x requires passwords of at least 8 characters. If this error occurs:

```bash
docker-compose down -v   # -v deletes volumes to clear corrupted state
# Fix the password in .env (minimum 8 characters)
docker-compose up -d
```

### Ports not reachable from WSL2

If `curl http://127.0.0.1:<port>` hangs, check that the proxy variables are not intercepting local traffic:

```bash
echo $HTTP_PROXY
echo $no_proxy
```

If a proxy is configured and `no_proxy` does not include `localhost,127.0.0.1`:

```bash
export no_proxy="localhost,127.0.0.1,10.89.0.0/16"
export NO_PROXY="localhost,127.0.0.1,10.89.0.0/16"
```

Add these to `~/.bashrc` to make them permanent.

### Registry: "unauthorized"

If Docker Compose returns an authentication error when pulling images from the private registry:

```bash
# Check login
podman login --get-login <REGISTRY_HOST>

# If the credentials exist but Compose cannot see them
mkdir -p ~/.docker
ln -sf ${XDG_RUNTIME_DIR}/containers/auth.json ~/.docker/config.json
```

### Network "khealthinair-net" not found

If you see `network khealthinair-net declared as external, but could not be found`, check that the `networks` block in `docker-compose.yaml` uses:

```yaml
networks:
  khealthinair-net:
    external: false
    name: khealthinair-net
```

## To do

- [ ] Mock of the external APIs (Inbiot, Qlair, Kunak) for local ingestion testing
- [ ] Grafana initialization file `aqdr-ui-init-conf.yaml`
