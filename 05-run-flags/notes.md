# Module 05 — Run Flags

## What this module covers

Every important `docker run` flag with a detailed explanation of what it does,
when to use it, and when NOT to use it.

---

## Build the image first

```bash
# Build the run-flags image.
#
# docker       — the Docker CLI binary
# build        — construct an image from a Dockerfile
# -t run-flags:1.0.0 — name and tag the image
# .            — build context (current directory)
docker build -t run-flags:1.0.0 .
```

---

## `-d` / `--detach` — Run in the background

```bash
# Run the container detached — returns immediately, prints the container ID.
#
# docker       — the Docker CLI binary
# run          — create and start a container
# -d           — (--detach) run in the background. Without -d your terminal
#                is attached to the container's stdout/stderr and blocks.
#                Ctrl-C would stop the container. With -d Docker prints the
#                64-character container ID and returns you to your shell.
# run-flags:1.0.0 — the image to run
docker run -d run-flags:1.0.0
```

---

## `-p` / `--publish` — Map ports

```bash
# Map host port 8080 to container port 5000.
#
# docker       — the Docker CLI binary
# run          — create and start a container
# -d           — run detached (background)
# -p 8080:5000 — (--publish) format is <host-port>:<container-port>
#                HOST PORT (left):      the port opened on your laptop/server.
#                                       You reach the app at localhost:8080.
#                CONTAINER PORT (right): the port the app listens on inside
#                                       the container (Flask uses 5000).
#                These can differ — use a different host port if 5000 is taken.
#                Omitting -p entirely means the app is only reachable from
#                inside the container itself (useful for testing or debugging).
# run-flags:1.0.0 — the image name
docker run -d -p 8080:5000 run-flags:1.0.0
```

**Test it:**

```bash
# Send a GET request to the host port to verify the port mapping works.
#
# curl         — command-line HTTP client
# -s           — (--silent) suppress progress meter
# http://localhost:8080/
#   localhost  — your own machine
#   :8080      — the HOST port we mapped in -p above
curl -s http://localhost:8080/
```

---

## `-e` / `--env` and `--env-file` — Environment variables

```bash
# Pass a single environment variable into the container.
#
# docker       — the Docker CLI binary
# run          — create and start a container
# -d           — detached
# -p 5000:5000 — port mapping
# -e APP_ENV=production
#              — (--env) inject one KEY=VALUE pair as an environment variable.
#                The app reads APP_ENV via os.environ.get("APP_ENV") in app.py.
#                Visible at http://localhost:5000/config
# run-flags:1.0.0 — the image
docker run -d -p 5000:5000 -e APP_ENV=production run-flags:1.0.0
```

```bash
# Pass multiple env vars individually.
#
# You can repeat -e as many times as needed. Each -e injects one variable.
docker run -d -p 5000:5000 \
    -e APP_ENV=staging \
    -e LOG_LEVEL=debug \
    -e DEBUG_MODE=true \
    run-flags:1.0.0
```

```bash
# Pass all variables from a file — cleaner than many -e flags.
#
# --env-file sample.env
#              — read KEY=VALUE pairs from sample.env and inject them all.
#                Lines starting with # are treated as comments and ignored.
#                Empty lines are ignored.
#                No quoting is needed in the file (values are literal strings).
#
# SECURITY NOTE on -e vs --env-file:
# When you use `-e SECRET=abc123`, that value appears in:
#   - `docker inspect` output (readable by anyone with Docker access)
#   - Your shell history (e.g. ~/.bash_history, ~/.zsh_history)
# --env-file keeps the values out of your shell history, but the file itself
# must be protected and never committed to version control.
# For production secrets use a dedicated secrets manager.
docker run -d -p 5000:5000 --env-file sample.env run-flags:1.0.0
```

**Test the config endpoint:**

```bash
# Call /config to see which env vars are active in the running container.
#
# curl         — command-line HTTP client
# -s           — silent (no progress meter)
# http://localhost:5000/config — the Flask endpoint that reads and returns env vars
curl -s http://localhost:5000/config
```

```bash
# Pretty-print the JSON response using Python's built-in json module.
#
# curl -s ...  — fetch the JSON body silently
# |            — pipe stdout of curl to stdin of the next command
# python3      — the Python 3 interpreter
# -m json.tool — run the json.tool module as a script (pretty-prints JSON)
curl -s http://localhost:5000/config | python3 -m json.tool
```

---

## `-v` / `--volume` — Bind mounts

```bash
# Mount a host directory into the container (read-write).
#
# docker       — the Docker CLI binary
# run          — create and start a container
# -d           — detached
# -p 5000:5000 — port mapping
# -v $(pwd)/logs:/app/logs
#              — (--volume) bind mount: map a host directory into the container.
#                Format: <host-path>:<container-path>[:<mode>]
#                HOST PATH (left):   the directory on your machine.
#                $(pwd)/logs          — current directory + /logs subfolder.
#                CONTAINER PATH:     where it appears inside the container.
#                /app/logs            — the app can write logs here and they
#                                      appear on your host immediately.
#                MODE (optional):    rw (read-write, the default) or ro (read-only).
#                Use ro to prevent the container from modifying host files —
#                a useful security control for config files and secrets.
# run-flags:1.0.0 — the image
docker run -d -p 5000:5000 -v "$(pwd)/logs:/app/logs" run-flags:1.0.0
```

```bash
# Mount a config file as read-only (container can read it, not modify it).
#
# :ro          — read-only mode. The container will get a permission denied
#                error if it tries to write to this path.
docker run -d -p 5000:5000 -v "$(pwd)/sample.env:/app/config.env:ro" run-flags:1.0.0
```

---

## `--name` — Name the container

```bash
# Assign a human-readable name to the container.
#
# docker       — the Docker CLI binary
# run          — create and start a container
# -d           — detached
# -p 5000:5000 — port mapping
# --name config-server
#              — assign the name "config-server" to this container.
#                Without --name Docker assigns a random name like "goofy_morse".
#                A named container lets you use the name in subsequent commands:
#                  docker logs config-server
#                  docker stop config-server
#                  docker exec -it config-server /bin/bash
#                  docker inspect config-server
#                Much easier than copying a 64-char container ID.
# run-flags:1.0.0 — the image
docker run -d -p 5000:5000 --name config-server run-flags:1.0.0
```

```bash
# Stop the named container.
docker stop config-server
```

```bash
# Remove the named container.
docker rm config-server
```

---

## `--rm` — Auto-remove on exit

```bash
# Automatically remove the container when it exits.
#
# docker       — the Docker CLI binary
# run          — create and start a container
# --rm         — delete the container as soon as it stops.
#                Without --rm, stopped containers accumulate in `docker ps -a`
#                and consume disk space (their writable layer remains on disk).
#
# WHEN TO USE --rm:
#   - One-shot tasks: running a script, database migration, format check
#   - Interactive debugging sessions (docker run -it --rm image /bin/bash)
#   - Any container you know you will not need to inspect after it exits
#
# WHEN NOT TO USE --rm:
#   - Containers that crash — you need to inspect the logs and filesystem
#     state AFTER the crash to debug. --rm deletes that evidence immediately.
#   - Long-lived services you might want to restart (docker start <name>)
# run-flags:1.0.0 — the image
docker run --rm -p 5000:5000 run-flags:1.0.0
```

---

## `--restart` — Restart policies

```bash
# Run with "no" restart policy (the default — never restart automatically).
#
# --restart no — if the container exits for any reason, leave it stopped.
#                This is the default. Fine for one-shot tasks.
docker run -d --restart no run-flags:1.0.0
```

```bash
# Restart only on non-zero exit codes (application errors).
#
# --restart on-failure — restart if the container exits with a non-zero code.
#                        Does NOT restart if explicitly stopped with docker stop.
#                        Good for services that might crash due to transient errors.
#                        Optionally limit restart attempts:
#                          --restart on-failure:3  (max 3 restarts)
docker run -d --restart on-failure run-flags:1.0.0
```

```bash
# Always restart, even after explicit docker stop.
#
# --restart always — restart regardless of exit code, even after daemon restart.
#                    docker stop followed by docker start will restart it.
#                    The container also restarts if the Docker daemon restarts
#                    (e.g. after a reboot). Use for critical services.
docker run -d --restart always run-flags:1.0.0
```

```bash
# Always restart UNLESS explicitly stopped.
#
# --restart unless-stopped — like "always" but respects an explicit docker stop.
#                            If you run docker stop, the container stays stopped
#                            even after a Docker daemon restart.
#                            The most common production policy for services.
docker run -d --restart unless-stopped run-flags:1.0.0
```

---

## `-it` — Interactive terminal

```bash
# Run an interactive shell inside a new container.
#
# docker       — the Docker CLI binary
# run          — create and start a container
# -i           — (--interactive) keep stdin open. Without -i you cannot type
#                commands into the container — your keystrokes go nowhere.
# -t           — (--tty) allocate a pseudo-TTY (terminal device).
#                Without -t the shell runs in "dumb" mode: no prompt, no
#                colour, no line editing, no tab completion. Like running a
#                command piped through a non-terminal.
#                Together, -it gives you a fully interactive terminal session.
# --rm         — remove the container when you exit the shell
# run-flags:1.0.0 — the image
# /bin/bash    — the command to run (replaces CMD)
docker run -it --rm run-flags:1.0.0 /bin/bash
```

---

## `--network` — Container networking

```bash
# Run a container on a named Docker network.
#
# --network my-net — connect the container to "my-net".
#                    Containers on the same network can reach each other by
#                    container name (Docker's built-in DNS resolution).
#                    Covered in depth in the Docker networking module.
#                    Brief intro here only.
#
# Create a network first:
# docker network create my-net
docker run -d --network my-net --name api run-flags:1.0.0
```

---

## `--cpus` and `--memory` — Resource limits

```bash
# Limit the container to half a CPU core and 256 MB of RAM.
#
# docker       — the Docker CLI binary
# run          — create and start a container
# -d           — detached
# -p 5000:5000 — port mapping
# --cpus 0.5   — limit to 0.5 CPU cores (50% of one core).
#                0.5 means the container can use at most half of one CPU's
#                processing time. 2.0 means two full cores.
#                Without this limit a runaway process can consume 100% of
#                all CPUs on the host, starving other containers and services.
# --memory 256m — limit to 256 megabytes of RAM.
#                 m suffix = megabytes; g suffix = gigabytes.
#                 If the container tries to allocate more, the Linux kernel's
#                 OOM (Out Of Memory) killer terminates the process.
#                 You will see the container exit with code 137 (SIGKILL by OOM).
#
# These flags correspond directly to `deploy.resources.limits` in
# Docker Compose files:
#   deploy:
#     resources:
#       limits:
#         cpus: "0.5"
#         memory: 256M
docker run -d -p 5000:5000 --cpus 0.5 --memory 256m run-flags:1.0.0
```

---

## Try it yourself

Experiment with different `--env` values and observe the `/config` response:

```bash
# Run 1: development defaults (no env vars specified)
docker run -d -p 5001:5000 --name dev-config run-flags:1.0.0

# Run 2: production config via -e flags
docker run -d -p 5002:5000 --name prod-config \
    -e APP_ENV=production \
    -e LOG_LEVEL=warn \
    -e DEBUG_MODE=false \
    run-flags:1.0.0

# Run 3: staging config via --env-file
docker run -d -p 5003:5000 --name staging-config \
    --env-file sample.env \
    run-flags:1.0.0
```

```bash
# Compare the /config output across all three running containers.
#
# echo         — print text to stdout (used here as a visual label)
echo "=== Dev (defaults) ===" && curl -s http://localhost:5001/config | python3 -m json.tool
echo "=== Prod (-e flags) ===" && curl -s http://localhost:5002/config | python3 -m json.tool
echo "=== Staging (--env-file) ===" && curl -s http://localhost:5003/config | python3 -m json.tool
```

```bash
# Clean up all three containers.
#
# docker stop  — gracefully stop the containers
# dev-config prod-config staging-config — multiple names in one command
docker stop dev-config prod-config staging-config

# docker rm    — remove the stopped containers
docker rm dev-config prod-config staging-config
```

---

## What you learned in this module

1. `-d` — detach and run in the background; `-f` on `docker logs` follows output.
2. `-p host:container` — port mapping; left is host, right is container.
3. `-e KEY=VAL` — single env var; `--env-file` for multiple (keeps shell history clean).
4. `-v host:container[:ro]` — bind mount; `:ro` for read-only protection.
5. `--name` — human-readable container names simplify all subsequent commands.
6. `--rm` — auto-cleanup for one-shot tasks; avoid it when you need post-crash inspection.
7. `--restart` — `unless-stopped` is the most common production policy.
8. `-it` — `-i` keeps stdin open, `-t` gives a real terminal; combine for interactive shells.
9. `--cpus` and `--memory` — resource limits protect the host from runaway containers.

**Next:** [06-dockerignore](../06-dockerignore/) — understand the build context and why `.dockerignore` is security-critical.
