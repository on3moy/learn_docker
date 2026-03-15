# Module 03 — Volumes

## What this module covers

How Docker volumes work, why containers are ephemeral by default, and how to
persist data that survives container restarts and removals. You will learn the
three types of Docker storage, every volume CLI command, and when to choose each
storage type.

---

## Background: the problem with the container read-write layer

Every running container gets a thin **read-write layer** added on top of the
image's read-only layers. Anything written at runtime (log files, uploaded files,
database records) goes into this layer.

```
┌───────────────────────────────────────┐  ← container read-write layer (ephemeral)
├───────────────────────────────────────┤  ← COPY app.py .           (image layer)
├───────────────────────────────────────┤  ← RUN uv pip install ...  (image layer)
├───────────────────────────────────────┤  ← COPY requirements.txt . (image layer)
└───────────────────────────────────────┘  ← FROM python:3.12-slim   (base layers)
```

**When you run `docker rm` on a container, its read-write layer is permanently
deleted.** Any data written there is gone. This is the default behaviour — Docker
containers are designed to be disposable and stateless.

For truly stateless apps (a simple API that reads from a database) this is fine.
For anything that needs to *produce* persistent data — databases, user uploads,
application logs, ML model checkpoints — you need a **volume**.

---

## The three types of Docker storage

| Type | How it works | Managed by | When to use |
|------|-------------|------------|-------------|
| **Named volume** | Docker manages a directory in its storage area (e.g. `/var/lib/docker/volumes/`) | Docker | Databases, app state, anything you want Docker to own |
| **Bind mount** | A path on the HOST filesystem is mapped into the container | You (the user) | Dev mode live-reload, injecting config from host, sharing files |
| **tmpfs mount** | An in-memory filesystem, never written to disk | OS | Sensitive temporary data (secrets in memory), high-speed scratch space |

This module focuses on **named volumes** and **bind mounts** — the two you will
use in every real project.

---

## The experiment: proving data persists across container restarts

Follow these steps exactly. By the end you will have concrete evidence that a
named volume outlives any individual container.

### Step 1: Build the image

```bash
# Change into the module directory.
#
# cd           — change current working directory
# 03-volumes   — the module directory (relative to the repo root)
cd 03-volumes
```

```bash
# Build the Docker image from the Dockerfile in this directory.
#
# docker       — the Docker CLI binary
# build        — construct an image from a Dockerfile
# -t           — (--tag) assign a human-readable name:tag to the image.
#                Without -t the image is built but has only a SHA256 ID —
#                hard to reference in subsequent commands.
# vol-demo:1.0.0 — name "vol-demo", tag "1.0.0"
# .            — the build context: send the current directory to the daemon.
#                Only files not excluded by .dockerignore are sent.
docker build -t vol-demo:1.0.0 .
```

### Step 2: Create a named volume

```bash
# Create a named Docker volume called "appdata".
#
# docker       — the Docker CLI binary
# volume       — the volume management subcommand group
# create       — create a new named volume
# appdata      — the name we assign to this volume. Choose a name that
#                describes what it holds. This volume is stored in Docker's
#                managed area (e.g. /var/lib/docker/volumes/appdata/ on Linux).
#                You do not need to know the host path — Docker manages it.
docker volume create appdata
```

**What happened:** Docker created an empty directory in its storage area and gave
it the name "appdata". No container is involved yet. The volume exists
independently.

### Step 3: Run the container and mount the volume

```bash
# Run the container with the named volume mounted.
#
# docker       — the Docker CLI binary
# run          — create and start a container
# -d           — (--detach) run in the background; print the container ID and
#                return to the shell. Without -d your terminal is attached and
#                you cannot type further commands until the container stops.
# -p 5000:5000 — (--publish) map host port 5000 to container port 5000.
#                Format: host_port:container_port
#                Without this flag the Flask server is unreachable from your
#                browser or curl — it is only accessible inside the container.
# -v appdata:/data — (--volume) mount the named volume "appdata" at /data
#                inside the container. Format: volume_name:container_path
#                /data is where app.py reads and writes files (DATA_DIR in app.py).
#                Docker initialises the volume with /data's contents from the
#                image if the volume is empty (i.e. on first use).
# --name vol-c1 — give this container a memorable name. Without --name Docker
#                assigns a random name like "eager_curie". Named containers are
#                easier to stop, inspect, and reference in docker logs.
# vol-demo:1.0.0 — the image to create the container from
docker run -d -p 5000:5000 -v appdata:/data --name vol-c1 vol-demo:1.0.0
```

### Step 4: Write some data

```bash
# Send a POST request to write a message to the volume.
#
# curl         — a command-line HTTP client. Installed on macOS and most Linux
#                distros by default. On Windows use curl.exe or PowerShell's
#                Invoke-WebRequest.
# -s           — (--silent) suppress curl's progress meter. We only want the
#                JSON response body, not download speed statistics.
# -X POST      — (--request) use the HTTP POST method.
#                Specifying -X POST here is technically redundant because -d
#                implies POST, but being explicit makes the intent clear.
# "http://localhost:5000/write?msg=first+message"
#                The URL with a query parameter. + is URL-encoded space.
#                Flask's request.args.get("msg") decodes it back to a space.
curl -s -X POST "http://localhost:5000/write?msg=first+message"
```

```bash
# Write a second message so we have more than one entry to read back.
curl -s -X POST "http://localhost:5000/write?msg=second+message"
```

```bash
# Read all entries back to confirm they were written.
#
# curl         — the HTTP client
# -s           — silent: suppress the progress meter
# http://localhost:5000/read — the GET endpoint that lists all /data files
curl -s http://localhost:5000/read
```

You should see a JSON response with `"count": 2` and both messages listed.

### Step 5: Stop and REMOVE the first container

```bash
# Stop the running container gracefully.
#
# docker       — the Docker CLI binary
# stop         — send SIGTERM to the container's main process (PID 1).
#                Docker waits up to 10 seconds for a graceful shutdown, then
#                sends SIGKILL if the process has not exited.
# vol-c1       — the container name we assigned with --name
docker stop vol-c1
```

```bash
# Remove the stopped container entirely. This deletes the container and its
# read-write layer permanently.
#
# docker       — the Docker CLI binary
# rm           — remove one or more stopped containers
# vol-c1       — the container to remove
#
# IMPORTANT: Removing the container does NOT remove the named volume.
# The "appdata" volume is a separate object managed by Docker. It outlives
# any individual container. This is the fundamental guarantee of volumes.
docker rm vol-c1
```

Confirm the container is gone:

```bash
# List all containers — running and stopped.
#
# docker       — the Docker CLI binary
# ps           — list containers (short for "process status")
# -a           — (--all) include stopped containers, not just running ones.
#                Without -a, only running containers are shown.
docker ps -a
```

`vol-c1` should not appear. It is gone.

### Step 6: Start a brand new container with the same volume

```bash
# Start a second container from the same image, but mount the SAME volume.
#
# -v appdata:/data — same volume name "appdata". Docker mounts the existing
#                    volume (with the data we wrote in Step 4) at /data.
#                    The new container sees the files immediately.
# --name vol-c2    — a different container name to make it obvious this is a
#                    completely new container, not a restarted one.
docker run -d -p 5000:5000 -v appdata:/data --name vol-c2 vol-demo:1.0.0
```

```bash
# Read the data inside the new container.
curl -s http://localhost:5000/read
```

**You should see the same two messages from Step 4.** The data was written by
`vol-c1`, which no longer exists. `vol-c2` is a completely new container that
has never written anything. Yet it reads the data perfectly.

This is the core guarantee: **a named volume is independent of any container**.
Data persists as long as the volume exists, regardless of how many containers
are created, stopped, or removed.

### Step 7: Clean up

```bash
# Stop the second container.
docker stop vol-c2
```

```bash
# Remove the second container.
docker rm vol-c2
```

```bash
# Remove the named volume. This permanently deletes all data inside it.
#
# docker       — the Docker CLI binary
# volume       — volume management subcommand group
# rm           — remove the named volume
# appdata      — the volume to delete
#
# Docker will refuse to remove a volume that is currently mounted by a running
# container. Always stop and remove containers before removing their volumes.
docker volume rm appdata
```

```bash
# Remove the image to reclaim disk space.
#
# docker       — the Docker CLI binary
# image        — image management subcommand group
# rm           — remove the image
# vol-demo:1.0.0 — the image name and tag
docker image rm vol-demo:1.0.0
```

---

## Docker volume CLI reference

Every volume management command, documented per the CLI standard.

```bash
# Create a named volume.
#
# docker       — the Docker CLI binary
# volume       — volume management subcommand group
# create       — create a new named volume
# mydata       — the name of the volume. Use descriptive names that indicate
#                what data the volume holds: postgres-data, redis-cache, uploads.
docker volume create mydata
```

```bash
# List all volumes Docker knows about.
#
# docker       — the Docker CLI binary
# volume       — volume management subcommand group
# ls           — list volumes. Output columns:
#                DRIVER — the storage driver (almost always "local" for single-
#                         node setups; cluster drivers like "rexray" for Swarm).
#                VOLUME NAME — the name you gave it, or a UUID for anonymous volumes.
docker volume ls
```

```bash
# Inspect a volume — show all metadata as JSON.
#
# docker       — the Docker CLI binary
# volume       — volume management subcommand group
# inspect      — print detailed metadata for the specified volume
# mydata       — the volume name to inspect
#
# Key fields in the output:
#   Mountpoint — the actual host path where Docker stores the volume data.
#                On Linux: /var/lib/docker/volumes/mydata/_data
#                On Docker Desktop (Mac/Windows): inside the VM's filesystem.
#   CreatedAt  — when the volume was created.
#   Labels     — custom metadata you can attach with --label.
docker volume inspect mydata
```

```bash
# Remove a named volume permanently (irreversible — all data is deleted).
#
# docker       — the Docker CLI binary
# volume       — volume management subcommand group
# rm           — remove one or more volumes
# mydata       — the volume to delete
#
# Docker refuses to remove a volume that is in use by a running (or stopped
# but not removed) container. Remove the container first with `docker rm`.
docker volume rm mydata
```

```bash
# Remove all volumes not currently mounted by any container ("dangling" volumes).
#
# docker       — the Docker CLI binary
# volume       — volume management subcommand group
# prune        — remove unused volumes
#
# When to run this: after a development session where you created many
# anonymous volumes (containers run without -v). They accumulate as UUIDs
# and consume disk space silently. Prune cleans them up.
#
# WARNING: This removes ALL volumes not currently in use, including ones you
# may still care about. Inspect with `docker volume ls` before pruning.
docker volume prune
```

---

## Bind mounts: mapping host paths into containers

A bind mount maps a specific directory on your HOST machine directly into the
container. Unlike named volumes, Docker does not manage the storage location —
you specify the exact host path.

### When to use bind mounts

- **Development**: mount your source code into the container so code changes on
  the host are immediately visible inside the container without a rebuild.
- **Injecting config**: pass a config file from the host into the container at
  a well-known path.
- **Reading host data**: give the container read access to specific host files
  (logs, certificates, etc.).

### Bind mount syntax

```bash
# Run a container with a bind mount (read-write).
#
# docker       — the Docker CLI binary
# run          — create and start a container
# -v /host/absolute/path:/container/path
#   Format: host_path:container_path
#   host_path      — an ABSOLUTE path on the host machine. Relative paths are
#                    not reliably portable across shells and platforms. Always
#                    use absolute paths or the $(pwd) expansion.
#   container_path — the path inside the container where the host directory
#                    appears. Must also be absolute.
#   The default mode is read-write: the container can modify the host directory.
# vol-demo:1.0.0 — the image
docker run -v /absolute/host/path:/data vol-demo:1.0.0
```

```bash
# Bind mount using $(pwd) for the current directory (common in development).
#
# $(pwd)       — shell command substitution: expands to the absolute path of
#                the current working directory. More portable than hardcoding
#                a path that differs between machines.
# :/app        — mount it at /app inside the container — the app's working dir.
#
# Use case: live code reload in development. Edit source on the host; the
# container sees the changes immediately without a rebuild.
docker run -v "$(pwd)":/app vol-demo:1.0.0
```

```bash
# Bind mount in READ-ONLY mode.
#
# :ro          — append :ro after the container path to make the bind mount
#                read-only. The container can read the host files but cannot
#                modify them.
#
# Use case: injecting a config file or a TLS certificate that the container
# should read but never be allowed to overwrite.
docker run -v /host/config:/app/config:ro vol-demo:1.0.0
```

### Bind mount permission note

The container process sees the host directory with whatever permissions the
host directory actually has. If your host directory is owned by UID 1000 and
the container's appuser is UID 999, the container will not be able to write to
it. This is a common gotcha when mixing named volumes (which Docker initialises
with image permissions) and bind mounts (which use host permissions).

---

## The --mount syntax: a more explicit alternative

Docker also supports a `--mount` flag with key=value pairs. It is more verbose
than `-v` but easier to read and catches errors (typos in option names are
rejected instead of silently ignored).

```bash
# Named volume with --mount (equivalent to -v appdata:/data).
#
# docker       — the Docker CLI binary
# run          — create and start a container
# --mount      — the verbose mount flag
# type=volume  — this is a named volume (use type=bind for bind mounts)
# source=appdata — the name of the named volume
# target=/data — the path inside the container to mount it at
# vol-demo:1.0.0 — the image
docker run --mount type=volume,source=appdata,target=/data vol-demo:1.0.0
```

```bash
# Read-only bind mount with --mount.
#
# type=bind      — this is a bind mount, not a named volume
# source=/host/path — the absolute host path (must exist)
# target=/data   — the container path
# readonly       — mount in read-only mode (equivalent to :ro in -v syntax)
docker run --mount type=bind,source=/host/path,target=/data,readonly vol-demo:1.0.0
```

**When to use `--mount`:** In documentation, scripts, and compose files where
clarity matters more than brevity. In quick interactive commands, `-v` is fine.

---

## The VOLUME instruction in the Dockerfile

The `VOLUME ["/data"]` instruction in the Dockerfile does three things:

1. **Documents intent**: signals to anyone reading the Dockerfile that `/data`
   is where persistent data lives. Tools (Docker Compose, IDE plugins, Helm
   charts) can read this to understand the image's storage requirements.

2. **Provides a safety net**: if you start the container WITHOUT `-v`, Docker
   automatically creates an anonymous volume at `/data`. Data written there is
   NOT lost when the container exits (it goes to Docker's managed area), but
   anonymous volumes get UUID names that are awkward to reference. Always prefer
   named volumes in practice.

3. **Initialises named volumes on first use**: the first time an empty named
   volume is mounted at `/data`, Docker copies `/data`'s contents from the image
   into the volume — including ownership (set by `chown` in our Dockerfile). On
   subsequent mounts the volume's own contents are used; the image is not
   consulted again.

### When to SKIP the VOLUME instruction

In real projects you often skip `VOLUME` in the Dockerfile and declare volumes
in `docker-compose.yml` or a Kubernetes `PersistentVolumeClaim`. The instruction
is not required for volumes to work — it is documentation and a safety net.
The choice of storage location belongs in the deployment configuration, not the
image definition.

---

## Named volume vs bind mount: decision guide

| Scenario | Recommendation |
|----------|---------------|
| Database data (Postgres, Redis) | Named volume — let Docker manage the path |
| Dev mode: live-reload source code | Bind mount — so host editor changes are instant |
| Inject a config file from host | Bind mount with `:ro` — read-only for safety |
| App writes logs you want to persist | Named volume — or bind mount to a logs directory |
| Sensitive temp data (secrets in memory) | tmpfs mount — never written to disk |
| CI/CD: isolate each build | Named volume with `--rm` and `docker volume rm` in cleanup |

---

## What you learned in this module

1. Container read-write layers are ephemeral — destroyed on `docker rm`.
2. Named volumes persist independently of any container that uses them.
3. Docker initialises empty named volumes from the image's directory contents
   (ownership and permissions) on first mount.
4. Bind mounts map host paths directly into containers — useful for dev mode
   and config injection.
5. Read-only mounts (`-v path:path:ro`) prevent a container from modifying host
   files — a useful security boundary.
6. `docker volume create/ls/inspect/rm/prune` are the full lifecycle commands
   for named volumes.
7. The `VOLUME` Dockerfile instruction documents intent and provides a fallback
   anonymous volume — it does not replace explicit `-v` flags.

**Next:** [04-build-and-tag](../04-build-and-tag/) — master the full image
lifecycle: build, tag, list, remove, prune, and understand tagging conventions.
