# Module 01 — First Dockerfile

## What this module covers

Writing a Dockerfile from scratch. Every instruction is explained: what it does,
why it exists, and what would break if you removed or changed it.

---

## The Dockerfile instructions — quick reference

| Instruction | Purpose |
|-------------|---------|
| `FROM` | Sets the base image |
| `ENV` | Sets environment variables (build-time and runtime) |
| `WORKDIR` | Sets the working directory for all subsequent steps |
| `COPY` | Copies files from the build context into the image |
| `RUN` | Executes a shell command during the build |
| `EXPOSE` | Documents the port the container listens on |
| `HEALTHCHECK` | Defines how Docker tests container health |
| `USER` | Switches to a non-root user |
| `CMD` | The default command when the container starts |

---

## Step 1 — Build the image

```bash
# Build a Docker image from the Dockerfile in the current directory.
#
# docker       — the Docker CLI binary
# build        — the subcommand: constructs an image from a Dockerfile
# -t           — (--tag) assigns a name and tag to the image.
#                Without -t the image is built with no human-readable name —
#                you would have to reference it by its SHA256 image ID, which
#                is 64 hex characters and impossible to remember.
# first-app    — the image name (repository). Conventionally lowercase with
#                hyphens. In a registry this maps to your username/imagename.
# :1.0.0       — the tag. Tags identify versions of the same image name.
#                Omitting the tag defaults to ":latest" — a floating tag.
#                Avoid ":latest" in production: it hides which version is
#                actually running and makes rollbacks ambiguous.
# .            — the build context. The directory Docker bundles and sends
#                to the Docker daemon to build from. "." means the current
#                directory. Only files in the build context (minus .dockerignore
#                exclusions) can be accessed by COPY/ADD instructions.
#                Keep the context lean — everything in it is sent over a
#                socket even if you never COPY it.
docker build -t first-app:1.0.0 .
```

**What to observe in the output:**

```
[1/6] FROM python:3.12-slim          ← pulling (or using cached) the base image
[2/6] ENV PYTHONDONTWRITEBYTECODE=1  ← setting env var (no cache miss here)
[3/6] WORKDIR /app                   ← creating the working directory
[4/6] COPY requirements.txt .        ← copying the requirements file
[5/6] RUN pip install ...            ← downloading and installing flask
[6/6] COPY app.py .                  ← copying your application code
```

Each `[N/N]` line corresponds to one Dockerfile instruction and one image layer.
On the first build (cold cache), all steps run. On subsequent builds, Docker
prints `CACHED` for any step whose inputs have not changed.

---

## Step 2 — Verify the image exists

```bash
# List all Docker images stored locally.
#
# docker       — the Docker CLI binary
# image        — the subcommand group for image management
# ls           — list images (equivalent to the older `docker images` command)
docker image ls
```

Expected output (columns explained):

```
REPOSITORY   TAG     IMAGE ID       CREATED         SIZE
first-app    1.0.0   a3f91c2b4d88   2 minutes ago   148MB
```

| Column | Meaning |
|--------|---------|
| `REPOSITORY` | The image name you gave with `-t`. In a registry this is `username/imagename`. |
| `TAG` | The version label. `latest` means "most recently built/tagged", not "most stable". |
| `IMAGE ID` | The first 12 characters of the image's SHA256 content hash. Unique per image. |
| `CREATED` | How long ago the image was built. |
| `SIZE` | The total uncompressed size of all image layers combined. |

---

## Step 3 — Run the container

```bash
# Run a container from the image, mapping ports and naming the container.
#
# docker       — the Docker CLI binary
# run          — creates and starts a new container from an image
# -d           — (--detach) run the container in the background.
#                Without -d your terminal is attached and the container
#                output streams to your screen. Ctrl-C would stop the container.
#                With -d Docker prints the container ID and returns you to
#                your shell immediately.
# -p 5000:5000 — (--publish) map host port 5000 to container port 5000.
#                Format: <host-port>:<container-port>
#                The LEFT side is the port you open on your laptop/server.
#                The RIGHT side is the port the app listens on inside the container.
#                These can differ: `-p 8080:5000` means "reach the app on
#                localhost:8080, even though it listens on 5000 inside".
# --name       — assign a human-readable name to the container.
#                Without --name Docker assigns a random name like "zealous_morse".
#                Named containers are easier to reference in:
#                  docker logs my-first-container
#                  docker stop my-first-container
#                  docker exec -it my-first-container /bin/bash
# first-app:1.0.0 — the image to run (name:tag)
docker run -d -p 5000:5000 --name my-first-container first-app:1.0.0
```

---

## Step 4 — Test the endpoints

```bash
# Send an HTTP GET request to the root endpoint and print the response body.
#
# curl         — a command-line HTTP client. Pre-installed on most systems.
# -s           — (--silent) suppress the progress meter and error messages.
#                Without -s curl prints download statistics that clutter the
#                output when all you want is the JSON body.
# http://localhost:5000/
#   localhost  — your own machine (127.0.0.1). The container port is reachable
#               here because of the -p 5000:5000 mapping in docker run.
#   /          — the root endpoint defined in app.py
curl -s http://localhost:5000/
```

Expected response:
```json
{"hint":"Try /health to see what the HEALTHCHECK endpoint returns.","message":"Hello from your first Docker container!","module":"01-first-dockerfile"}
```

```bash
# Test the health endpoint — the same one the HEALTHCHECK instruction calls.
curl -s http://localhost:5000/health
```

Expected response:
```json
{"module":"01-first-dockerfile","status":"healthy"}
```

---

## Step 5 — Inspect the health status

```bash
# List running containers including their health status.
#
# docker       — the Docker CLI binary
# ps           — list containers (from `process status`)
# --format     — customise the output columns using Go template syntax.
#                Without --format you get the default table with many columns.
#                Here we show only the name and status for brevity.
docker ps --format "table {{.Names}}\t{{.Status}}"
```

During the `--start-period` (10 seconds) the STATUS will show `(health: starting)`.
After the first successful health check it changes to `(healthy)`.

```bash
# Inspect the full health check history (last 5 results) for a container.
#
# docker       — the Docker CLI binary
# inspect      — returns all container metadata as JSON
# --format     — Go template to extract just the health information
# my-first-container — the container name we set with --name
docker inspect --format='{{json .State.Health}}' my-first-container
```

---

## Step 6 — View logs

```bash
# Stream live log output from the running container.
#
# docker       — the Docker CLI binary
# logs         — display the stdout/stderr of a container
# -f           — (--follow) stream new log lines in real time (like `tail -f`).
#                Without -f you get a snapshot of logs up to this moment, then
#                the command exits.
# my-first-container — the container to tail
docker logs -f my-first-container
```

Because we set `PYTHONUNBUFFERED=1` in the Dockerfile, Flask's startup message
appears immediately. Without that env var you might see nothing for several
seconds, then a burst of output.

---

## Step 7 — Stop and clean up

```bash
# Stop the running container gracefully.
#
# docker       — the Docker CLI binary
# stop         — sends SIGTERM to the container's PID 1, waits for it to exit
#                (default 10 seconds), then sends SIGKILL if it hasn't stopped.
#                Because we used exec form CMD ["python", "app.py"], Python IS
#                PID 1 and receives SIGTERM directly, enabling a clean shutdown.
# my-first-container — the container name
docker stop my-first-container
```

```bash
# Remove the stopped container (frees disk space used by the container layer).
#
# docker       — the Docker CLI binary
# rm           — remove one or more stopped containers
# my-first-container — the container name
#
# NOTE: This removes the container but NOT the image. The image (first-app:1.0.0)
# still exists locally and you can run a new container from it at any time.
docker rm my-first-container
```

---

## What you learned in this module

1. **FROM** — how to choose and pin a base image (slim vs alpine vs full)
2. **ENV** — why `PYTHONDONTWRITEBYTECODE` and `PYTHONUNBUFFERED` are mandatory in containers
3. **WORKDIR** — keeps your filesystem organised; no need for mkdir
4. **COPY** — prefer over ADD; copy `requirements.txt` first for cache efficiency
5. **RUN** — executes build-time commands; always use `--no-cache-dir` with pip
6. **Non-root user** — security baseline; always create `appuser` and switch to it
7. **EXPOSE** — metadata only, not a port-forwarding instruction
8. **HEALTHCHECK** — gives orchestrators a signal beyond "process is running"
9. **CMD (exec form)** — your app receives signals directly; graceful shutdown works

**Next:** [02-image-layers](../02-image-layers/) — understand how Docker's cache works and why instruction order determines your rebuild speed.
