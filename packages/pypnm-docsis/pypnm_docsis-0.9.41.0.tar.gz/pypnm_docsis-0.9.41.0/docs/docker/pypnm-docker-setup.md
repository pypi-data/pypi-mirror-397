# PyPNM Docker Prerequisites

PyPNM ships with Docker assets so we can build, run, and test the API consistently on any Ubuntu 22.04 or 24.04 system.  
This guide is focused solely on installing Docker Engine (plus Buildx and the Docker Compose plugin). Follow it on a fresh VM, workstation, or CI runner before working with PyPNM’s containers.

## Table Of Contents

[1. Remove Conflicting Packages (Optional)](#1-remove-conflicting-packages-optional)  
[2. Install Repository Prerequisites](#2-install-repository-prerequisites)  
[3. Add The Docker apt Repository](#3-add-the-docker-apt-repository)  
[4. Install Docker Engine, Buildx, And Compose](#4-install-docker-engine-buildx-and-compose)  
[5. Verify The Installation](#5-verify-the-installation)  
[6. Optional: Allow Docker Without sudo](#6-optional-allow-docker-without-sudo)  
[7. Next Steps](#7-next-steps)

## 1. Remove Conflicting Packages (Optional)

Clear out community Docker builds so the official Docker repository takes precedence:

```bash
sudo apt-get update
sudo apt-get remove -y docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc || true
```

## 2. Install Repository Prerequisites

```bash
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg

sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```

## 3. Add The Docker apt Repository

```bash
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<'EOF'
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Signed-By: /etc/apt/keyrings/docker.asc
EOF
```

## 4. Install Docker Engine, Buildx, And Compose

```bash
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

These packages provide everything PyPNM needs to build images locally and inside GitHub Actions.

## 5. Verify The Installation

```bash
docker --version
docker compose version
sudo docker run --rm hello-world
```

Seeing the “Hello from Docker!” message confirms the daemon works.

## 6. Optional: Allow Docker Without sudo

Add your user to the `docker` group if you prefer password-less Docker commands:

```bash
sudo groupadd docker || true
sudo usermod -aG docker "$USER"
```

Open a new shell (or log out/in), then re-run `docker run --rm hello-world`.  
Only enable this on machines where you are comfortable with Docker’s root-equivalent access.

## 7. Next Steps

1. Clone the PyPNM repository (if you have not already).  
2. Use the provided `Dockerfile` and `docker-compose.yml` in the repo root.  
3. Run `docker compose build` followed by `docker compose up` to start the API locally or in CI.
