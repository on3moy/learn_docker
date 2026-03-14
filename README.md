# Docker Foundations — `docker-learn`

A hands-on learning repository for Docker fundamentals. Every file is exhaustively
commented to serve as a self-contained teaching document. Read any file in isolation
and you will understand what it does, why it does it, and what would break if you
changed it.

---

## Prerequisites

Before you begin, make sure you have the following installed:

| Tool | Version | Install |
|------|---------|---------|
| Docker Engine **or** Docker Desktop | 24.x or newer | https://docs.docker.com/get-docker/ |
| Python | 3.12 | https://www.python.org/downloads/ |
| Git | Any recent version | https://git-scm.com/ |

> **Windows / macOS:** Docker Desktop includes the Docker Engine and Docker Compose.
> **Linux:** Install Docker Engine and Docker Compose as separate packages.

---

## Learning Path

Work through the modules in numbered order. Each one builds on the concepts from the last.

| Module | What you will learn |
|--------|---------------------|
| [01-first-dockerfile](./01-first-dockerfile/) | Write your first Dockerfile from scratch. Understand every instruction: FROM, WORKDIR, COPY, RUN, EXPOSE, CMD, HEALTHCHECK, and the non-root user pattern. |
| [02-image-layers](./02-image-layers/) | Understand Docker's layer cache. See exactly why instruction order is architectural rather than cosmetic, and how to arrange your Dockerfile to maximise cache hits and cut rebuild times. |
| [03-cmd-vs-entrypoint](./03-cmd-vs-entrypoint/) | Demystify CMD vs ENTRYPOINT. Understand shell form vs exec form, signal handling, PID 1 behaviour, and the recommended ENTRYPOINT + CMD production pattern. |
| [04-build-and-tag](./04-build-and-tag/) | Master the full image lifecycle: build, tag, list, remove, and prune. Learn semver and git-SHA tagging conventions and understand how tags map to registry push paths. |
| [05-run-flags](./05-run-flags/) | Run containers like a professional. Cover every important `docker run` flag: detach, port mapping, env vars, volumes, naming, restart policies, and resource limits. |
| [06-dockerignore](./06-dockerignore/) | Understand the Docker build context and why `.dockerignore` is not optional. Learn to exclude secrets, large files, and cache directories — and how to measure the impact. |

---

## Quick-Reference Cheat Sheet

Every `docker` command used across all modules, with a one-line description of when to reach for it.

```bash
# ── IMAGE COMMANDS ────────────────────────────────────────────────────────────

# Build an image from a Dockerfile in the current directory and name it
docker build -t <name>:<tag> .

# Build using a non-default Dockerfile name (e.g. Dockerfile.optimized)
docker build -f Dockerfile.optimized -t <name>:<tag> .

# List all images stored locally — shows REPOSITORY, TAG, IMAGE ID, CREATED, SIZE
docker image ls

# Remove a specific image by name:tag or by IMAGE ID
docker image rm <name>:<tag>

# Remove all dangling images (untagged layers left behind after rebuilds)
docker image prune

# Remove ALL unused images, not just dangling ones — use with caution
docker image prune -a

# Add an additional tag to an existing local image (does not copy — same layers)
docker tag <source>:<tag> <target>:<newtag>

# Inspect all metadata for an image as JSON (architecture, env vars, layers, etc.)
docker inspect <name>:<tag>

# ── CONTAINER COMMANDS ────────────────────────────────────────────────────────

# Run a container in the foreground (your terminal is attached; Ctrl-C stops it)
docker run <name>:<tag>

# Run a container detached in the background; prints the container ID
docker run -d <name>:<tag>

# Map host port 8080 to container port 5000 (host:container)
docker run -p 8080:5000 <name>:<tag>

# Pass a single environment variable into the container
docker run -e MY_VAR=value <name>:<tag>

# Pass all variables from a file into the container
docker run --env-file sample.env <name>:<tag>

# Bind-mount a host directory into the container (read-write)
docker run -v /host/path:/container/path <name>:<tag>

# Bind-mount a host directory into the container (read-only)
docker run -v /host/path:/container/path:ro <name>:<tag>

# Give the container a human-readable name you can use in other commands
docker run --name my-container <name>:<tag>

# Auto-remove the container when it exits (good for one-shot tasks)
docker run --rm <name>:<tag>

# Run with a restart policy so the container restarts on failure
docker run --restart on-failure <name>:<tag>

# Run with an interactive pseudo-TTY attached (great for debugging)
docker run -it <name>:<tag> /bin/bash

# Limit the container to half a CPU and 256 MB of RAM
docker run --cpus 0.5 --memory 256m <name>:<tag>

# List currently running containers
docker ps

# List ALL containers including stopped ones
docker ps -a

# Stop a running container gracefully (SIGTERM → wait → SIGKILL)
docker stop <name-or-id>

# Remove a stopped container
docker rm <name-or-id>

# Stream live log output from a container
docker logs -f <name-or-id>

# Execute an interactive shell inside a running container
docker exec -it <name-or-id> /bin/bash
```

---

## Official Docker Documentation

| Topic | Link |
|-------|------|
| Dockerfile reference | https://docs.docker.com/reference/dockerfile/ |
| `docker build` | https://docs.docker.com/reference/cli/docker/buildx/build/ |
| `docker run` | https://docs.docker.com/reference/cli/docker/container/run/ |
| Image layer caching | https://docs.docker.com/build/cache/ |
| `.dockerignore` | https://docs.docker.com/reference/dockerfile/#dockerignore-file |
| HEALTHCHECK | https://docs.docker.com/reference/dockerfile/#healthcheck |
| CMD vs ENTRYPOINT | https://docs.docker.com/reference/dockerfile/#understand-how-cmd-and-entrypoint-interact |
| `docker image ls` | https://docs.docker.com/reference/cli/docker/image/ls/ |
| Restart policies | https://docs.docker.com/engine/containers/start-containers-automatically/ |
| Resource constraints | https://docs.docker.com/engine/containers/resource_constraints/ |
