# PyPNM Docker Install & Usage

PyPNM ships with Docker assets so you can run the API quickly on a workstation, lab host, or VM. This guide covers the common flows:

- Install the published release image via the helper script.
- Use the deploy bundle (tarball) directly.
- Manual steps for hosts without GitHub access.

## Table of Contents

- [Fast path (helper script)](#fast-path-helper-script)
- [Deploy bundle flow (tarball)](#deploy-bundle-flow-tarball)
- [Manual/no-network notes](#manualno-network-notes)
- [Docker prerequisites](#docker-prerequisites)

## Fast path (helper script)

```bash
TAG="v0.9.23.0"
PORT=8080

curl -fsSLo install-pypnm-docker-container.sh \
  https://raw.githubusercontent.com/mgarcia01752/PyPNM/main/scripts/install-pypnm-docker-container.sh

chmod +x install-pypnm-docker-container.sh

sudo ./install-pypnm-docker-container.sh --tag ${TAG} --port ${PORT}
```

What the script does:

- Downloads the deploy bundle (falls back to tag source if the asset is missing).
- Seeds `deploy/config/system.json` and `deploy/compose/.env`.
- Pulls `ghcr.io/mgarcia01752/pypnm:${TAG}` and starts the stack in `/opt/pypnm/compose`.
- Prints next steps (logs, reload docs, config-menu).

After install (from `/opt/pypnm/compose`):

```bash
sudo docker compose logs -f --tail=200 pypnm-api
curl -I http://127.0.0.1:${PORT}/docs
sudo docker compose run --rm config-menu

# Reload after config changes, this assumes IP/PORT is set as above:
curl -X GET http://127.0.0.1:${PORT}/pypnm/system/webService/reload -H 'accept: application/json'
```

## Deploy bundle flow (tarball)

```bash
TAG="v0.9.23.0"
WORKING_DIR="PyPNM-${TAG}"

mkdir -p "${WORKING_DIR}"
cd "${WORKING_DIR}"

wget "https://github.com/mgarcia01752/PyPNM/archive/refs/tags/${TAG}.tar.gz"
tar -xvf "${TAG}.tar.gz" --strip-components=1

cd deploy
./install.sh

cd compose
sudo docker compose pull
sudo docker compose up -d
```

Edit `deploy/config/system.json` as needed, then reload the service (curl or `sudo docker compose restart pypnm-api`).

## Manual/no-network notes

- If the host cannot reach GitHub, copy the `deploy/` folder from a clone or a downloaded tarball and run `deploy/install.sh`.
- The helper script falls back to the tag archive and then to `main` if the deploy asset is missing.
- The runtime config lives in `deploy/config/system.json`; config-menu and the API share this file.

## Docker prerequisites

You need Docker Engine + the Compose plugin. On Ubuntu 22.04/24.04:

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<'EOF'
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

Verify:

```bash
docker --version
docker compose version
sudo docker run --rm hello-world
```

Optional (non-production): add your user to the docker group for password-less commands:

```bash
sudo groupadd docker || true
sudo usermod -aG docker "$USER"
```

Open a new shell afterward.
