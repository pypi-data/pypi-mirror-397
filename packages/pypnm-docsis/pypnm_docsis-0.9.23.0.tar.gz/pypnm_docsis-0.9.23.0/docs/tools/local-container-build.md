# Local Container Preflight (`tools/local_container_build.sh`)

Use this helper to validate the Docker images locally before cutting a release.

## Usage

- Build images only:

```bash
./tools/local_container_build.sh
```

- Build + smoke test (start compose, wait for `pypnm-api` health, then tear down):

```bash
./tools/local_container_build.sh --smoke
```

## Requirements

- Docker and the docker compose plugin.
- Daemon access (run with `sudo` or add your user to the `docker` group if needed).

## What it does

1. Builds compose images (`docker compose --progress plain build`).
2. If `--smoke` is set, brings up the stack, waits for `pypnm-api` to become healthy, then tears down (`docker compose down --volumes`).
