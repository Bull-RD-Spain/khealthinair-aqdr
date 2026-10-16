# Guide: Local Development Environment with Podman on WSL2

## For simulating and debugging Kubernetes platforms with Docker Compose

---

## Environment Architecture

```
┌─────────────────────────────────────────────────┐
│  Windows (laptop)                               │
│  ┌───────────────────────────────────────────┐  │
│  │  Podman Desktop (optional UI)             │  │
│  └──────────────┬────────────────────────────┘  │
│                 │ socket connection              │
│  ┌──────────────▼────────────────────────────┐  │
│  │  WSL2 - Ubuntu 22.04 LTS                 │  │
│  │                                           │  │
│  │  ┌─────────────┐  ┌────────────────────┐  │  │
│  │  │ Podman 4.x  │  │ docker-compose     │  │  │
│  │  │ (engine)    │◄─│ (standalone)        │  │  │
│  │  └─────────────┘  └────────────────────┘  │  │
│  │         │                                 │  │
│  │  ┌──────▼──────────────────────────────┐  │  │
│  │  │  Containers (your platform)         │  │  │
│  │  │  ┌────┐ ┌────┐ ┌────┐ ┌────┐       │  │  │
│  │  │  │svc1│ │svc2│ │svc3│ │ db │ ...   │  │  │
│  │  │  └────┘ └────┘ └────┘ └────┘       │  │  │
│  │  └─────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────┘  │
└─────────────────────────────────────────────────┘
```

---

## Phase 1: Install Ubuntu 22.04 on WSL2

### 1.1 Enable WSL2 (if not already enabled)

Open **PowerShell as Administrator**:

```powershell
# Enable WSL and the Virtual Machine Platform
wsl --install --no-distribution

# Ensure WSL2 is the default version
wsl --set-default-version 2
```

Restart the machine if prompted.

### 1.2 Install the distro

```powershell
# List available distros
wsl --list --online

# Install Ubuntu 22.04
wsl --install -d Ubuntu-22.04
```

A terminal will open asking you to create a UNIX username and password.

### 1.3 Verify it's running WSL2

```powershell
wsl --list --verbose
```

It should show `VERSION 2` next to Ubuntu-22.04. If it shows 1:

```powershell
wsl --set-version Ubuntu-22.04 2
```

### 1.4 Initial distro setup

Enter the distro and update:

```bash
sudo apt update && sudo apt upgrade -y
```

### 1.5 Stop other WSL distros (optional)

If you have other WSL distros running and want to free up resources:

```powershell
# Check what's running
wsl --list --verbose

# Stop a specific distro
wsl --terminate <distro-name>

# Stop ALL distros and the WSL2 kernel
wsl --shutdown
```

`--terminate` stops only the specified distro; `--shutdown` stops everything
including the shared WSL2 kernel (next launch will take a few extra seconds).

---

## Phase 2: Configure systemd on WSL2

Podman requires systemd for its socket and cgroup management. This phase
must be completed **before** installing and verifying Podman.

### 2.1 Check if systemd is already active

```bash
ps -p 1 -o comm=
```

If it shows `systemd`, skip to step 2.3. If it shows `init`, continue below.

### 2.2 Enable systemd

```bash
sudo tee /etc/wsl.conf << 'EOF'
[boot]
systemd=true

[automount]
enabled=true
options="metadata,umask=22,fmask=11"

[network]
generateResolvConf=true
EOF
```

Then restart the distro from PowerShell:

```powershell
wsl --terminate Ubuntu-22.04
wsl -d Ubuntu-22.04
```

Verify:

```bash
ps -p 1 -o comm=
# Should show: systemd
```

### 2.3 Install dbus-user-session

This package is required for systemd user sessions to work properly in WSL2.
Without it, user-level services like the Podman socket will fail to start.

```bash
sudo apt install -y dbus-user-session
```

After installing, restart the distro from PowerShell:

```powershell
wsl --terminate Ubuntu-22.04
wsl -d Ubuntu-22.04
```

**Note:** You may see a message like `wsl: Failed to start the systemd user
session for '<user>'` when the distro starts. This is a cosmetic WSL warning
and does not affect functionality. Verify by checking that the runtime
directory exists:

```bash
echo $XDG_RUNTIME_DIR
# Should show: /run/user/1000
```

### 2.4 Enable linger

Linger keeps your user's systemd services running even when you don't have
an active login session. Without it, the Podman socket will die when you
close the terminal.

```bash
sudo loginctl enable-linger $(whoami)

# Verify
ls /var/lib/systemd/linger/
# Should show your username
```

---

## Phase 3: Install Podman 4.x on WSL2

### 3.1 Install Podman

Ubuntu 22.04 ships Podman 3.x in the default repos, which is insufficient.
We'll install version 4+ from the official Kubic repository:

```bash
# Add the Kubic repository for an up-to-date Podman
sudo mkdir -p /etc/apt/keyrings

# Download the GPG key
curl -fsSL "https://download.opensuse.org/repositories/devel:kubic:libcontainers:unstable/xUbuntu_22.04/Release.key" \
  | gpg --dearmor \
  | sudo tee /etc/apt/keyrings/devel_kubic_libcontainers_unstable.gpg > /dev/null

# Add the repository
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/devel_kubic_libcontainers_unstable.gpg] \
  https://download.opensuse.org/repositories/devel:kubic:libcontainers:unstable/xUbuntu_22.04/ /" \
  | sudo tee /etc/apt/sources.list.d/devel:kubic:libcontainers:unstable.list

# Install
sudo apt update
sudo apt install -y podman
```

### 3.2 Verify the installation

```bash
podman --version
# Should show 4.x or higher

podman info | grep -i cgroupVersion
# Should show v2 (WSL2 with recent kernels supports it)
```

The output should be clean, with no warnings about systemd or cgroups.
If you see warnings like `The cgroupv2 manager is set to systemd but there
is no systemd user session available`, go back to Phase 2 and make sure
systemd, dbus-user-session, and linger are all correctly configured.

### 3.3 Configure the image registry

Podman doesn't have docker.io configured as a registry by default.
Create or edit the registries config:

```bash
sudo tee /etc/containers/registries.conf.d/docker.conf << 'EOF'
unqualified-search-registries = ["docker.io"]
EOF
```

### 3.4 Verify it works

```bash
podman run --rm docker.io/hello-world
```

**Note:** You may see a warning `"/" is not a shared mount`. This is cosmetic
in WSL2 and does not affect container functionality.

---

## Phase 4: Install Docker Compose standalone

### Why docker-compose instead of podman-compose?

`podman-compose` works, but has limitations with advanced Compose features
(depends_on with healthchecks, profiles, extensions). The standalone
`docker-compose` binary (Compose V2, Apache 2.0 license) is more complete
and can connect to the Podman socket.

### 4.1 Download the binary

```bash
# Get the latest Compose V2 plugin version (standalone Go binary)
COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest \
  | grep '"tag_name"' | sed -E 's/.*"v([^"]+)".*/\1/')

sudo curl -L \
  "https://github.com/docker/compose/releases/download/v${COMPOSE_VERSION}/docker-compose-linux-$(uname -m)" \
  -o /usr/local/bin/docker-compose

sudo chmod +x /usr/local/bin/docker-compose

# Verify
docker-compose version
```

### 4.2 Enable the Podman socket

Docker Compose needs a Docker-API-compatible socket.
Podman can expose one:

```bash
# Enable the Podman socket for your user (rootless)
systemctl --user enable --now podman.socket

# Verify it's active
systemctl --user status podman.socket

# Check the socket exists
ls -la /run/user/$(id -u)/podman/podman.sock
```

### 4.3 Set the environment variable

Append to `~/.bashrc`:

```bash
echo 'export DOCKER_HOST=unix:///run/user/$(id -u)/podman/podman.sock' >> ~/.bashrc
source ~/.bashrc
```

### 4.4 Verify the integration

```bash
# This should respond without errors
docker-compose version

# Test with a minimal compose file
mkdir -p ~/test-compose && cd ~/test-compose

cat > docker-compose.yml << 'EOF'
services:
  test:
    image: docker.io/alpine:latest
    command: echo "Podman + Docker Compose is working!"
EOF

docker-compose up
# Should print the message and exit
docker-compose down

cd ~ && rm -rf ~/test-compose
```

---

## Phase 5: Install Podman Desktop (optional, on Windows)

### 5.1 Download and install

Download from: https://podman-desktop.io/downloads

Install normally on Windows (per-user or system-wide, both work).

### 5.2 Configure the WSL2 connection

When you open Podman Desktop, it may automatically detect a WSL2 connection,
but it will likely appear as **OFF**. The auto-detected connection often
fails to communicate with the Podman engine inside WSL2.

The reliable method is to register the connection manually from the
**Windows side**.

### 5.3 Set up SSH access (required for the connection)

Inside your WSL2 distro:

```bash
# Generate an SSH key (press Enter to accept all defaults)
ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519

# Install the SSH server
sudo apt install -y openssh-server

# Authorize the key for local connections
cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Start the SSH server
sudo service ssh start

# Verify local SSH works (should print the version without asking for password)
ssh -i ~/.ssh/id_ed25519 $(whoami)@localhost "podman info --format '{{.Version.Version}}'"
```

### 5.4 Register the connection from Windows

Open **PowerShell** and run:

```powershell
podman system connection add ubuntu-wsl ssh://<your_user>@localhost/run/user/1000/podman/podman.sock --identity \\wsl$\Ubuntu-22.04\home\<your_user>\.ssh\id_ed25519
```

Replace `<your_user>` with your WSL username (e.g., `john`).

**Note:** The `podman` command must be available in PowerShell. Podman
Desktop installs it automatically. If it's not recognized, check that
Podman Desktop is installed and try restarting your terminal.

### 5.5 Verify in Podman Desktop

Close Podman Desktop completely (system tray > right-click > Quit) and
reopen it. Go to **Settings > Resources**. You should see the `ubuntu-wsl`
connection with status **RUNNING** (green).

If an old auto-detected connection (e.g., `ubuntu-test-ssh`) still appears
as OFF, you can remove it from PowerShell:

```powershell
podman system connection remove ubuntu-test-ssh
```

**Important notes:**

- Do NOT click "Create new..." in the Podman section — that creates a
  separate Podman Machine you don't need.
- Podman Desktop may show a different Podman version (e.g., v5.x) than
  what's installed in WSL2 (e.g., v4.x). This is normal — Desktop bundles
  its own version, but uses your WSL2 engine through the SSH connection.
- The **Compose** extension in Podman Desktop is useful if you want to
  manage compose files from the GUI.

### 5.6 Make SSH auto-start on WSL boot (optional)

By default, the SSH server doesn't start automatically in WSL2.
To make Podman Desktop always able to connect:

```bash
# Inside WSL2
sudo systemctl enable ssh
```

---

## Phase 6: Prepare the environment for your platform

### 6.1 Recommended workspace structure

```
~/projects/
└── my-platform/
    ├── docker-compose.yml          # Main compose file
    ├── docker-compose.override.yml # Overrides for local development
    ├── .env                        # Environment variables
    ├── configs/                    # Service configurations
    └── data/                       # Persistent volumes
```

**IMPORTANT:** All code must live inside the WSL2 native filesystem
(`/home/your_user/...`), NOT in `/mnt/c/...`. The I/O performance
difference is massive (10-50x slower from the Windows filesystem).

### 6.2 Adapt your docker-compose.yml

If your compose file already works with Docker, the changes for Podman
are minimal:

```yaml
# docker-compose.yml - Example with Podman adjustments

services:
  api-gateway:
    image: docker.io/your-registry/api-gateway:latest   # Always use FQDN
    ports:
      - "8080:8080"
    networks:
      - platform-net
    depends_on:
      db:
        condition: service_healthy

  auth-service:
    image: docker.io/your-registry/auth-service:latest
    environment:
      - DB_HOST=db
      - DB_PORT=5432
    networks:
      - platform-net
    depends_on:
      - db

  db:
    image: docker.io/postgres:16-alpine
    environment:
      POSTGRES_DB: platform
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: dev-password
    volumes:
      - db-data:/var/lib/postgresql/data
    networks:
      - platform-net
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin"]
      interval: 5s
      timeout: 5s
      retries: 5

networks:
  platform-net:
    driver: bridge

volumes:
  db-data:
```

### 6.3 Key adjustments for Podman compatibility

**a) Images: always use FQDN**

```yaml
# Wrong (Podman may not resolve)
image: postgres:16

# Correct
image: docker.io/postgres:16
```

**b) Low ports in rootless mode**

If you need ports < 1024 (e.g., 80, 443):

```bash
# Allow your user to bind ports starting from 80
sudo sysctl -w net.ipv4.ip_unprivileged_port_start=80

# Make it permanent
echo "net.ipv4.ip_unprivileged_port_start=80" | sudo tee -a /etc/sysctl.conf
```

**c) DNS between containers**

Verify that `aardvark-dns` is installed (ships with Podman 4+):

```bash
podman info | grep -i dns
# Should show "dnsPlugin": "dnsname" or reference to aardvark
```

If it's not:

```bash
sudo apt install -y aardvark-dns
```

**d) Compose override for development**

Create a `docker-compose.override.yml` for local adjustments:

```yaml
# docker-compose.override.yml
# Automatically applied on top of the main compose file

services:
  api-gateway:
    ports:
      - "8080:8080"
      - "5005:5005"    # Remote debug port
    environment:
      - DEBUG=true
      - LOG_LEVEL=debug
    volumes:
      - ./configs/gateway-dev.yml:/app/config.yml:ro

  auth-service:
    environment:
      - DEBUG=true
    volumes:
      - ./configs/auth-dev.yml:/app/config.yml:ro
```

---

## Phase 7: Day-to-day commands

### Basic operations

```bash
# Start the entire platform
docker-compose up -d

# View logs for all services
docker-compose logs -f

# View logs for a specific service
docker-compose logs -f api-gateway

# Stop everything
docker-compose down

# Stop and remove volumes (full reset)
docker-compose down -v

# Rebuild a service
docker-compose up -d --build auth-service

# Scale a service
docker-compose up -d --scale auth-service=3

# Enter a container
docker-compose exec db psql -U admin -d platform

# Check service status
docker-compose ps
```

### Debugging

```bash
# Inspect the network
podman network ls
podman network inspect <network_name>

# View resource consumption
podman stats

# Inspect a container
podman inspect <container_id>

# View Podman system logs
journalctl --user -u podman.socket

# Check connectivity between services
docker-compose exec api-gateway ping auth-service
docker-compose exec api-gateway nslookup db
```

### Cleanup

```bash
# Clean stopped containers, unused networks, untagged images
podman system prune -a

# Clean orphaned volumes
podman volume prune
```

---

## Phase 8: Troubleshooting

### "Cannot connect to Podman" when using docker-compose

```bash
# Verify the socket is active
systemctl --user status podman.socket

# Restart if needed
systemctl --user restart podman.socket

# Check the DOCKER_HOST variable
echo $DOCKER_HOST
# Should show: unix:///run/user/<your_uid>/podman/podman.sock
```

### Podman shows cgroupv2 / systemd warnings

Symptoms:

```
WARN: The cgroupv2 manager is set to systemd but there is no systemd user session available
WARN: Falling back to --cgroup-manager=cgroupfs
```

This means the systemd user session is not available. Fix in order:

1. **Verify systemd is PID 1:** `ps -p 1 -o comm=` must show `systemd`
2. **Install dbus-user-session:** `sudo apt install -y dbus-user-session`
3. **Restart the distro:** `wsl --terminate Ubuntu-22.04` from PowerShell,
   then relaunch
4. **Enable linger:** `sudo loginctl enable-linger $(whoami)`
5. **Verify XDG_RUNTIME_DIR:** `echo $XDG_RUNTIME_DIR` must show
   `/run/user/1000`

### Containers can't resolve each other by name

```bash
# Verify the network has DNS enabled
podman network inspect platform-net | grep dns

# If not, recreate the network
docker-compose down
podman network rm platform-net
docker-compose up -d   # Network is recreated automatically
```

### Permission errors on volumes

```bash
# Common issue in rootless mode: UID mapping
# Option 1: Add :Z to the volume (SELinux label)
volumes:
  - ./data:/app/data:Z

# Option 2: Adjust permissions
podman unshare chown -R 1000:1000 ./data
```

### WSL2 runs out of memory

Create or edit `%USERPROFILE%\.wslconfig` on Windows:

```ini
[wsl2]
memory=8GB          # Adjust based on your total RAM
swap=4GB
processors=4        # Adjust based on your CPU cores
```

Restart WSL:

```powershell
wsl --shutdown
```

### Podman socket doesn't start after WSL restart

This happens because systemd user services require a "lingering" session:

```bash
# Enable linger for your user
sudo loginctl enable-linger $(whoami)
```

### Podman Desktop shows WSL2 connection as OFF

Podman Desktop's auto-detected connection to WSL2 often fails. The fix
is to manually register the connection from the Windows side:

1. **Inside WSL2**, set up SSH access:
   ```bash
   ssh-keygen -t ed25519 -N "" -f ~/.ssh/id_ed25519
   sudo apt install -y openssh-server
   cat ~/.ssh/id_ed25519.pub >> ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   sudo service ssh start
   ```

2. **In PowerShell**, register the connection:
   ```powershell
   podman system connection add ubuntu-wsl ssh://<user>@localhost/run/user/1000/podman/podman.sock --identity \\wsl$\Ubuntu-22.04\home\<user>\.ssh\id_ed25519
   ```

3. **Restart Podman Desktop** (Quit from system tray, reopen). The
   `ubuntu-wsl` connection should appear as RUNNING.

4. Remove the old broken auto-detected connection if desired:
   ```powershell
   podman system connection remove ubuntu-test-ssh
   ```

### "/" is not a shared mount warning

```
WARN: "/" is not a shared mount, this could cause issues or missing mounts
with rootless containers
```

This is a cosmetic warning specific to WSL2 and does not affect container
functionality. It can be safely ignored.

---

## Installation summary (checklist)

- [ ] WSL2 enabled with updated kernel
- [ ] Ubuntu 22.04 installed and updated
- [ ] systemd enabled in `/etc/wsl.conf`
- [ ] `dbus-user-session` installed
- [ ] Linger enabled (`loginctl enable-linger`)
- [ ] Podman 4.x installed from Kubic repos
- [ ] `podman info` runs without systemd/cgroup warnings
- [ ] docker.io registry configured
- [ ] `podman run hello-world` succeeds
- [ ] Docker Compose V2 standalone installed
- [ ] Podman socket enabled (`systemctl --user`)
- [ ] `DOCKER_HOST` pointing to the Podman socket
- [ ] `docker-compose up` test successful
- [ ] (Optional) SSH server configured in WSL2
- [ ] (Optional) Podman Desktop connection registered from PowerShell
- [ ] (Optional) Podman Desktop shows connection as RUNNING
- [ ] Source code on the WSL2 native filesystem
- [ ] `.wslconfig` with appropriate memory limits
