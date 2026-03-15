# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# Module 01 — First Dockerfile
#
# This Dockerfile is exhaustively commented. Read it top to bottom and you will
# understand every instruction, every flag, and every best-practice decision.
# ─────────────────────────────────────────────────────────────────────────────


# ── FROM ──────────────────────────────────────────────────────────────────────
# FROM specifies the base image — the foundation that every subsequent
# instruction builds on top of.
#
# ┌──────────────────────────────────────────────────────────────────────────┐
# │  IMAGE VARIANT COMPARISON                                                │
# │                                                                          │
# │  python:3.12        — The "full" image. Debian Bookworm plus every       │
# │                        compiler, development header, and system tool     │
# │                        you might ever need. Roughly 1 GB. Great for      │
# │                        building C extensions (numpy, Pillow), terrible   │
# │                        for shipping — you are deploying a compiler.      │
# │                                                                          │
# │  python:3.12-slim   — Debian Bookworm with only the packages required    │
# │                        to run Python. No compilers, no man pages, no     │
# │                        build toolchains. Roughly 130 MB. This is the     │
# │                        right default for most Python web services.       │
# │                                                                          │
# │  python:3.12-alpine — Alpine Linux (musl libc, not glibc). The          │
# │                        smallest image (~50 MB) but musl libc can break   │
# │                        C extension wheels (numpy, pandas, cryptography   │
# │                        all have known issues). Also difficult to debug   │
# │                        because most standard tools are absent. Avoid     │
# │                        unless image size is a hard requirement.          │
# └──────────────────────────────────────────────────────────────────────────┘
#
# WHY python:3.12 AND NOT python:latest?
# ──────────────────────────────────────
# "latest" is a floating tag — it points to a different image every time a new
# Python version is published to Docker Hub. Using it means:
#
#   - Your build is NOT reproducible. The same Dockerfile built today and in
#     six months may produce images running Python 3.12 vs Python 3.15.
#
#   - A Python major/minor upgrade can silently break your app: changed
#     standard library behaviour, removed deprecated APIs, different default
#     SSL settings, etc. — with no change to your source code.
#
#   - In a team, CI and local builds diverge. Different machines produce
#     different images. "Works in CI, fails in prod" becomes a real risk.
#
# Always pin to a specific version tag. For production, also pin the digest:
#
#   Production example (byte-for-byte reproducible):
#   FROM python:3.12-slim@sha256:<digest>
#
#   Find the digest after pulling:
#   docker pull python:3.12-slim
#   docker inspect python:3.12-slim --format '{{index .RepoDigests 0}}'
#
# For this learning repo we use the tag form for readability.
FROM python:3.12-slim


# ── ENV ───────────────────────────────────────────────────────────────────────
# ENV sets environment variables that persist into every subsequent build step
# AND into the running container at runtime.
#
# These two are non-negotiable for every Python container:

# PYTHONDONTWRITEBYTECODE=1
# ─────────────────────────
# By default, Python writes .pyc bytecode cache files alongside your source
# files in __pycache__/ directories. Inside a container this causes problems:
#
#   - The .pyc files are generated fresh on every new image build — they are
#     never reused between builds and just consume layer space for no benefit.
#
#   - If you bind-mount your source code during development, Python will litter
#     your host filesystem with .pyc files owned by the container user (often
#     root), requiring sudo to clean up. Very annoying.
#
# Setting this to 1 tells Python: do not write .pyc files at all.
# Python still compiles to bytecode in memory — you lose no performance.
ENV PYTHONDONTWRITEBYTECODE=1

# PYTHONUNBUFFERED=1
# ───────────────────
# By default Python buffers stdout and stderr — it accumulates output in a
# memory buffer and flushes it in large chunks for efficiency (C-style stdio
# buffering). In a long-running container this means:
#
#   - `print()` statements and log lines may not appear in `docker logs` for
#     several seconds, or at all if the container crashes before the buffer
#     flushes. You would see nothing, then a sudden burst, then silence.
#
#   - Crash output might be lost entirely if the process is killed before
#     the buffer is flushed. You lose the error message you most needed.
#
#   - Log aggregation systems (Datadog, CloudWatch, Loki) that tail container
#     stdout may receive batched or delayed entries, making real-time
#     monitoring unreliable.
#
# Setting this to 1 forces Python to write stdout/stderr directly without
# buffering — every `print()` appears immediately in `docker logs`.
ENV PYTHONUNBUFFERED=1


# ── WORKDIR ───────────────────────────────────────────────────────────────────
# WORKDIR sets the working directory for all subsequent Dockerfile instructions
# (RUN, COPY, ADD, CMD, ENTRYPOINT) and for the container's running process.
#
# Without WORKDIR, all subsequent commands would run from /, the filesystem
# root. Your application files would end up scattered at the root level
# alongside system directories like /bin and /etc — messy and error-prone.
#
# WORKDIR creates the directory if it does not already exist (no mkdir needed).
#
# /app is a conventional choice: short, descriptive, and it does not conflict
# with any standard Linux system directory. You will also see /code and /srv.
WORKDIR /app


# ── COPY requirements.txt (before app code) ───────────────────────────────────
# COPY <source-on-host> <destination-in-image>
#
# WHY COPY requirements.txt BEFORE copying app code?
# ───────────────────────────────────────────────────
# Docker builds images as a stack of layers. Each instruction creates one
# immutable layer. Docker caches layers: if an instruction and ALL its inputs
# are identical to a previous build, Docker reuses the cached layer and skips
# the instruction entirely.
#
# The `pip install` step is expensive: it downloads packages from PyPI,
# potentially compiles C extensions, and writes many files. Caching it is
# essential for a fast developer workflow.
#
# If we copied ALL project files first and THEN ran pip install, the cache
# for the pip layer would be invalidated every time any file changed — even a
# one-character edit to app.py. You would pay the full pip cost on every build.
#
# By copying requirements.txt first and running pip install BEFORE copying
# app code:
#   - A change to app.py only invalidates the COPY app.py layer and below.
#   - pip install stays cached as long as requirements.txt is unchanged.
#   - In practice, you edit app.py dozens of times per session; you change
#     requirements.txt rarely. The cache hit rate for pip is very high.
#
# This ordering is THE most impactful layer-optimisation in a Python Dockerfile.
#
# WHY COPY AND NOT ADD?
# ──────────────────────
# Docker provides two instructions for copying files: COPY and ADD.
# Always prefer COPY unless you specifically need ADD's extra features:
#
#   - ADD silently extracts .tar.gz archives: `ADD app.tar.gz .` unpacks it.
#     If you use ADD by habit, a misnamed .tar.gz file gets extracted
#     unexpectedly — a silent and confusing bug.
#
#   - ADD can fetch files from URLs, but it does NOT cache the download.
#     Every build re-downloads the URL regardless of whether it changed.
#     Use `RUN curl -O <url>` instead — at least curl is explicit.
#
# COPY is explicit, predictable, and does exactly one thing. Prefer it always.
COPY requirements.txt .

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv


# ── RUN ───────────────────────────────────────────────────────────────────────
# RUN executes a shell command DURING the image build, not at container runtime.
# The filesystem changes produced by the command become a new image layer.
#
# pip install --no-cache-dir -r requirements.txt
# ────────────────────────────────────────────────
# pip             — the Python package installer binary
# install         — the subcommand: install one or more packages
# --no-cache-dir  — do NOT write pip's download cache to disk.
#
#                   Normally pip caches downloaded wheel files in ~/.cache/pip
#                   so subsequent runs (on the same machine) don't re-download.
#                   Inside a Docker build, that cache directory lives inside
#                   the layer being built. It is NOT reused between separate
#                   `docker build` invocations — it just sits there consuming
#                   space in the image. Omitting this flag can add 50–150 MB
#                   of cached wheels to your image for zero benefit.
#
#                   Always use --no-cache-dir in Dockerfiles.
#
# -r requirements.txt — install all packages listed in requirements.txt.
#                   -r is shorthand for --requirement.
RUN uv pip install --system --no-cache -r requirements.txt

# ── COPY application code ─────────────────────────────────────────────────────
# Now we copy the application code AFTER installing dependencies.
#
# Edit app.py → only this COPY layer and everything below is invalidated.
# The pip install layer above stays cached. Fast iterative builds.
#
# `.` as the destination means "current WORKDIR" which is /app.
# This copies app.py to /app/app.py inside the image.
COPY app.py .


# ── Non-root user ─────────────────────────────────────────────────────────────
# By default, every Docker container runs as root (UID 0). This feels harmless
# because "it's just a container" — but it is a genuine security risk:
#
#   1. CONTAINER ESCAPE BLAST RADIUS
#      If an attacker exploits a vulnerability in your app and escapes the
#      container namespace (documented CVEs exist for this), they land as root
#      on the host machine. Running as a non-root user caps the damage.
#
#   2. VOLUME PERMISSIONS FOOTGUN
#      Files written by a root container to a bind-mounted volume are owned by
#      root on the host. You then need `sudo rm` to clean them up — annoying
#      and unexpected for developers.
#
#   3. PRINCIPLE OF LEAST PRIVILEGE
#      Your Flask app needs no privileges at all: serving on port 5000 (≥1024)
#      does not require root on Linux. Never grant privileges you don't use.
#
# addgroup --system appgroup
#   Creates a new system group named "appgroup".
#   --system: marks it as a system group (GID < 1000, no password entry).
#   A group is a way to assign shared permissions to multiple users.
#   We create a dedicated group so the user belongs to a controlled,
#   minimal-privilege group rather than a generic one like "users" or "root".
#
# adduser --system --no-create-home --ingroup appgroup appuser
#   Creates a new system user named "appuser" and adds it to "appgroup".
#   --system:          no password, no login shell — this is a service account,
#                      not a human user. It cannot be used to log in interactively.
#   --no-create-home:  skip creating /home/appuser (saves a tiny bit of space;
#                      a service account has no need for a home directory).
#   --ingroup appgroup: assigns appuser to the appgroup group we just created.
#
# NOTE ON NAMING: the group is "appgroup" and the user is "appuser" — two
# distinct things. A group is a permission bucket; a user is the identity
# the process runs as. Keeping the names different avoids confusion.
RUN addgroup --system appgroup \
    && adduser --system --no-create-home --ingroup appgroup appuser

# Give appuser ownership of the working directory so the app can write
# runtime files (logs, temp uploads, etc.) if needed.
RUN chown -R appuser:appgroup /app

# Switch to the non-root user. All subsequent instructions and the container's
# main process will run as appuser, not root.
USER appuser


# ── EXPOSE ────────────────────────────────────────────────────────────────────
# EXPOSE documents that the container listens on this port at runtime.
#
# IMPORTANT: EXPOSE does NOT actually publish the port to the host machine.
# It is metadata — documentation for developers and for tools like
# `docker run -P` (which publishes all EXPOSED ports on random host ports).
#
# To actually reach the container from the host you must still pass
# `-p 5000:5000` (or `-p 8080:5000` etc.) to `docker run`.
EXPOSE 5000


# ── HEALTHCHECK ───────────────────────────────────────────────────────────────
# HEALTHCHECK tells Docker how to test that the container is functioning.
# Docker runs this command on a schedule and uses the exit code to mark the
# container as "healthy", "unhealthy", or "starting".
#
# Without HEALTHCHECK, Docker considers a container "healthy" the moment the
# main process starts — even if the process is hung, deadlocked, or returning
# 500 errors on every request. HEALTHCHECK catches this.
#
# Orchestrators use the health status to:
#   - Route traffic only to healthy replicas (load balancer decisions)
#   - Restart unhealthy containers automatically
#   - Block rolling deploys from proceeding if new containers are unhealthy
#   - Surface status in `docker ps`, Swarm dashboards, and Kubernetes probes
#
# ── FLAG REFERENCE ───────────────────────────────────────────────────────────
#
# --interval=30s
#   How often Docker re-runs the health check command after the container
#   has started. 30 seconds is a sensible default for a web service.
#   Too short → wastes CPU; too long → slow detection of degraded containers.
#
# --timeout=10s
#   If the health check command does not complete within this window, Docker
#   treats it as a failure. Flask responds in milliseconds; 10 seconds is a
#   very generous timeout that accommodates a slow startup spike.
#
# --start-period=10s
#   How long to wait before the first health check runs after the container
#   starts. This grace period allows the app time to initialise (load config,
#   warm caches, connect to a DB) without being prematurely marked unhealthy.
#   Failures during the start period do NOT count against the retries limit.
#   Increase this for applications with a slow cold-start.
#
# --retries=3
#   How many consecutive failures are required before Docker marks the
#   container "unhealthy". 3 × 30s interval = Docker waits ~90 seconds of
#   sustained failure before declaring the container sick.
#
# CMD wget -q --spider http://localhost:5000/health || exit 1
#   wget  — the HTTP client available in Debian slim images (curl is not).
#   -q    — quiet mode: suppress all output. We only care about the exit code.
#   --spider — perform a HEAD request only; do not download the response body.
#             This is lighter than a full GET — we just want to know the server
#             is reachable and returns a 2xx status.
#   || exit 1 — if wget exits non-zero (server unreachable, non-2xx response),
#               explicitly exit with code 1 to signal an unhealthy check.
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:5000/health || exit 1


# ── CMD ───────────────────────────────────────────────────────────────────────
# CMD specifies the default command to run when a container starts.
# It can be overridden entirely by passing a command to `docker run`:
#   docker run myapp:1.0.0 python -c "print('overridden')"
#
# ── EXEC FORM vs SHELL FORM ──────────────────────────────────────────────────
#
# Shell form:   CMD python app.py
#   Docker wraps this in: /bin/sh -c "python app.py"
#   /bin/sh becomes PID 1. python is a child process.
#   When Docker sends SIGTERM to stop the container, it goes to PID 1 (/bin/sh).
#   /bin/sh does NOT forward signals to children by default.
#   Your Python app never receives SIGTERM → cannot do a graceful shutdown.
#   Docker waits 10 seconds, then sends SIGKILL. Data loss or corruption risk.
#
# Exec form:    CMD ["python", "app.py"]
#   Docker runs python directly — no shell wrapper.
#   python IS PID 1 and receives all signals directly.
#   Flask can catch SIGTERM and perform a graceful shutdown (drain connections,
#   flush logs, release locks).
#   Always use exec form for CMD and ENTRYPOINT.
#
CMD ["python", "app.py"]
