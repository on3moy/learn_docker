# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# Module 03 — Volumes
#
# This Dockerfile builds a Flask app that demonstrates Docker volumes. The key
# additions relative to previous modules:
#   - /data is created and chowned to appuser so the app can write there.
#   - VOLUME ["/data"] declares /data as a persistent mount point.
#
# Read this file alongside notes.md for the full volume lesson.
# ─────────────────────────────────────────────────────────────────────────────


# ── FROM ──────────────────────────────────────────────────────────────────────
# Never use "latest" — it is a floating tag that destroys build reproducibility.
# See module 01 for the full explanation of image variants and pinned tags.
FROM python:3.12-slim


# ── ENV ───────────────────────────────────────────────────────────────────────
# Both env vars are mandatory in every Python container.
# See module 01 for a line-by-line explanation of what each one does.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1


# ── WORKDIR ───────────────────────────────────────────────────────────────────
# Sets /app as the working directory for all subsequent instructions and for
# the container's running process. Created automatically if it does not exist.
WORKDIR /app


# ── COPY uv ───────────────────────────────────────────────────────────────────
# uv is a Rust-based Python package manager from Astral (https://astral.sh).
# It is a drop-in replacement for pip that is significantly faster — especially
# on cold installs — and produces more reproducible dependency resolution.
#
# COPY --from=<image> <src> <dest>
#   This is a multi-stage COPY. Rather than copying from the local build context,
#   Docker pulls the named image from a registry and copies a single file out of
#   it into the current build layer. No intermediary container is created.
#
#   ghcr.io/astral-sh/uv:latest — the official uv image on GitHub Container
#                                 Registry (GHCR). It is a minimal image that
#                                 contains only the statically-linked /uv binary.
#   /uv                         — the path of the binary inside the uv image.
#   /usr/local/bin/uv           — the destination in our image. /usr/local/bin
#                                 is on the default PATH, so we invoke "uv"
#                                 in subsequent RUN instructions without a
#                                 full path prefix.
#
# NOTE: For production, pin to a specific uv release to avoid surprises:
#   COPY --from=ghcr.io/astral-sh/uv:0.5.11 /uv /usr/local/bin/uv
# We use :latest here for learning convenience — the same floating-tag risks
# explained in module 01 apply equally here.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv


# ── COPY requirements.txt (before app code) ───────────────────────────────────
# Copy the dependency manifest before the application code so Docker can cache
# the expensive install step. See module 02 for a thorough explanation of why
# this ordering is the most impactful Dockerfile optimisation for Python.
COPY requirements.txt .


# ── RUN uv pip install ────────────────────────────────────────────────────────
# uv             — the uv package manager binary copied above.
# pip            — uv's pip-compatibility subcommand. Accepts the same flags as
#                  `pip install`, making it a true drop-in replacement.
# install        — install the specified packages.
# --system       — install into the system Python interpreter, not a virtual
#                  environment. Inside Docker the container IS the isolation
#                  boundary — a venv adds overhead without adding safety.
#                  uv requires this flag when no venv is active, as a guard
#                  against accidentally installing outside a venv in development.
# --no-cache     — do not write uv's download cache to disk inside this layer.
#                  The cache would bloat the image with no benefit; Docker's
#                  own layer cache provides install reuse at a higher level.
# -r requirements.txt — install every package listed in requirements.txt.
RUN uv pip install --system --no-cache -r requirements.txt


# ── COPY application code ─────────────────────────────────────────────────────
# Copy app.py AFTER installing dependencies. Editing app.py only invalidates
# this layer and below — the uv pip install layer above stays cached.
COPY app.py .


# ── CREATE /data ──────────────────────────────────────────────────────────────
# /data is the directory where the app writes volume-backed files.
#
# We create it as root (the current user before the USER instruction) so we
# can chown it to appuser in the combined chown step below.
#
# WHY CREATE IT HERE AND NOT LET DOCKER AUTO-CREATE IT?
# ──────────────────────────────────────────────────────
# When a named volume is mounted to a path that already exists in the image,
# Docker initialises the empty volume with the image's contents at that path —
# including ownership and permissions. This is called "volume initialisation"
# and it only happens the first time a named volume is used.
#
# If /data does not exist in the image (or exists but is owned by root), Docker
# creates it owned by root. appuser (a non-root service account) then cannot
# write to it, and every POST /write call fails with a PermissionError.
#
# By creating /data here and chowning it to appuser before the VOLUME
# declaration, we bake correct permissions into the image, which Docker copies
# into newly-initialised named volumes automatically.
#
# IMPORTANT: This only helps for NAMED VOLUMES on their FIRST use.
# For BIND MOUNTS the host directory's permissions always take precedence —
# this chown has no effect on bind mounts.
RUN mkdir -p /data


# ── NON-ROOT USER ─────────────────────────────────────────────────────────────
# Always drop to a non-root user before CMD/ENTRYPOINT.
# See module 01 for the complete security justification.
#
# addgroup --system appgroup
#   Creates a system group named "appgroup" (GID < 1000, no password entry).
#
# adduser --system --no-create-home --ingroup appgroup appuser
#   Creates a non-login system account "appuser" in "appgroup".
#   --system:         no password, no interactive login shell.
#   --no-create-home: no /home/appuser created (service accounts don't need it).
#   --ingroup appgroup: assigns appuser to the appgroup group.
RUN addgroup --system appgroup \
    && adduser --system --no-create-home --ingroup appgroup appuser

# Give appuser ownership of both directories before switching to it:
#   /app  — so appuser can read app.py and write any runtime temp files.
#   /data — so appuser can create and delete files inside the volume path.
#
# chown  — change file owner and group
# -R     — recursive: apply to /app and /data and everything inside them
# appuser:appgroup — the new owner:group
RUN chown -R appuser:appgroup /app /data

# Switch to the non-root user. All subsequent build steps and the running
# container process will operate as appuser, not root.
USER appuser


# ── EXPOSE ────────────────────────────────────────────────────────────────────
# Documents that the container listens on port 5000 at runtime.
# This is metadata only — it does NOT publish the port to the host.
# Use -p 5000:5000 in docker run to actually reach the server.
EXPOSE 5000


# ── HEALTHCHECK ───────────────────────────────────────────────────────────────
# Tells Docker how to verify the container is functioning.
# See module 01 for a full explanation of every flag and why HEALTHCHECK matters.
#
# --interval=30s  — run the check every 30 seconds.
# --timeout=10s   — fail the check if it does not complete within 10 seconds.
# --start-period=10s — grace period after startup before failures are counted.
# --retries=3     — mark unhealthy only after 3 consecutive failures.
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:5000/health || exit 1


# ── VOLUME ────────────────────────────────────────────────────────────────────
# VOLUME declares /data as a volume mount point in this image.
#
# WHAT IT DOES:
# ─────────────
# 1. Communicates intent: "/data holds persistent data". Tools (compose,
#    Kubernetes, IDE plugins) can read this to understand the image's storage
#    requirements without reading the source code.
#
# 2. Provides a safety net: if you start the container WITHOUT -v or --mount,
#    Docker automatically creates an anonymous volume at /data. Data written
#    there is stored in Docker's managed area and persists until the anonymous
#    volume is explicitly removed. Without this instruction, /data would be part
#    of the container's ephemeral read-write layer and would be destroyed on
#    `docker rm`.
#
# 3. Initialises named volumes: the first time a named volume is mounted at
#    /data, Docker copies /data's contents from the image (empty dir, owned by
#    appuser, as set up above) into the volume. Subsequent mounts see whatever
#    the volume accumulated at runtime.
#
# WHAT IT DOES NOT DO:
# ─────────────────────
# - It does NOT persist data across `docker build` runs (only applies at runtime).
# - It does NOT replace the -v flag. Without -v you get an anonymous volume,
#   which is functional but inconvenient to manage. Prefer named volumes.
# - It does NOT affect bind mounts. Bind mounts override this declaration
#   entirely; their permissions come from the host directory.
#
# IMPORTANT ORDERING RULE:
# ─────────────────────────
# Any RUN instruction AFTER this VOLUME declaration cannot write to /data —
# those writes would be discarded because the volume mount shadows the path
# during the RUN step. This is why all setup (mkdir, chown) happened above.
VOLUME ["/data"]


# ── CMD ───────────────────────────────────────────────────────────────────────
# Exec form — Python is PID 1 and receives OS signals directly.
# Shell form would wrap this in /bin/sh -c, making sh PID 1 and preventing
# graceful shutdown. See module 01 for the full exec vs shell form explanation.
CMD ["python", "app.py"]
