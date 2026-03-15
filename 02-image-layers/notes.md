# Module 02 — Image Layers

## What this module covers

Docker's layer cache mechanism — what a layer is, what invalidates a cache,
and why the order of instructions in a Dockerfile is an architectural decision
that directly controls your rebuild speed.

---

## Background: what is a Docker image layer?

A Docker image is not a single monolithic file. It is a stack of read-only
**layers**. Each instruction in your Dockerfile that produces filesystem changes
(`FROM`, `RUN`, `COPY`, `ADD`) creates one new layer.

When you run a container, Docker adds one thin **read-write layer** on top — this
is where your app writes files at runtime. The image layers underneath are
never modified.

```
┌───────────────────────────────────────┐  ← container read-write layer
├───────────────────────────────────────┤  ← COPY app.py .
├───────────────────────────────────────┤  ← RUN pip install ...
├───────────────────────────────────────┤  ← COPY requirements.txt .
├───────────────────────────────────────┤  ← WORKDIR /app
├───────────────────────────────────────┤  ← ENV PYTHONDONTWRITEBYTECODE=1
└───────────────────────────────────────┘  ← FROM python:3.12-slim (base layers)
```

**Why does this matter?** Docker caches each layer independently. If a layer's
inputs are unchanged, Docker reuses the cached result and skips the instruction.
Once any layer is invalidated, ALL layers below it must also be rebuilt — the
cache invalidation cascades downward.

---

## The experiment

Follow these steps exactly. The difference in rebuild times will be dramatic.

### Setup

```bash
# Change into the module directory.
#
# cd           — change the current working directory
# 02-image-layers — the module directory (relative to the repo root)
cd 02-image-layers
```

### Build 1: Cold build — unoptimized (no cache exists yet)

```bash
# Build the unoptimized image for the first time.
#
# docker       — the Docker CLI binary
# build        — construct an image from a Dockerfile
# -f           — (--file) specify a Dockerfile with a non-default name.
#                Without -f Docker looks for a file literally named "Dockerfile".
#                Here we have two Dockerfiles so we must be explicit.
# Dockerfile.unoptimized — the Dockerfile to use for this build
# -t           — (--tag) name and tag the resulting image
# layers-bad:1.0.0 — image name "layers-bad", version "1.0.0"
# .            — build context: current directory
docker build -f Dockerfile.unoptimized -t layers-bad:1.0.0 .
```

**What to observe:** All steps run from scratch. The pip install step downloads
Flask from PyPI. Note the total elapsed time displayed at the end of the build.

### Build 2: Cold build — optimized (no cache exists yet)

```bash
# Build the optimized image for the first time.
docker build -f Dockerfile.optimized -t layers-good:1.0.0 .
```

**What to observe:** Again, all steps run from scratch. pip install runs.
Both cold builds take approximately the same time — the optimisation only
helps on *subsequent* builds after files change.

### Simulate app code change

```bash
# Append a blank line to app.py to simulate editing the application code.
#
# echo         — print a string to stdout
# ""           — an empty string (produces a blank line)
# >>           — redirect stdout, appending to the file (>> appends; > overwrites)
# app.py       — the target file
echo "" >> app.py
```

### Build 3: Rebuild unoptimized after code change

```bash
# Rebuild the unoptimized image after the simulated code change.
# Watch the output carefully — specifically which steps show "CACHED".
docker build -f Dockerfile.unoptimized -t layers-bad:1.0.0 .
```

**What to observe in the output:**

```
[1/8] FROM python:3.12-slim            ← CACHED (base image unchanged)
[2/8] ENV PYTHONDONTWRITEBYTECODE=1    ← CACHED
[3/8] ENV PYTHONUNBUFFERED=1           ← CACHED
[4/8] WORKDIR /app                     ← CACHED
[5/8] COPY . .                         ← CACHE MISS — app.py changed!
[6/8] RUN uv pip install ...           ← CACHE MISS — parent layer changed!
[7/8] RUN addgroup ... adduser ...     ← CACHE MISS — parent layer changed!
[8/8] USER appuser                     ← CACHE MISS — parent layer changed!
```

pip install runs again, downloading Flask from PyPI. Even though
`requirements.txt` did not change at all. This wastes 10–30 seconds.

### Build 4: Rebuild optimized after code change

```bash
# Rebuild the optimized image after the same code change.
docker build -f Dockerfile.optimized -t layers-good:1.0.0 .
```

**What to observe in the output:**

```
[1/9] FROM python:3.12-slim            ← CACHED
[2/9] ENV PYTHONDONTWRITEBYTECODE=1    ← CACHED
[3/9] ENV PYTHONUNBUFFERED=1           ← CACHED
[4/9] WORKDIR /app                     ← CACHED
[5/9] COPY requirements.txt .          ← CACHED — requirements.txt unchanged!
[6/9] RUN uv pip install ...           ← CACHED — requirements.txt unchanged!
[7/9] COPY app.py .                    ← CACHE MISS — app.py changed
[8/9] RUN addgroup ... adduser ...     ← rebuilt, but instantaneous
[9/9] CMD ...                          ← rebuilt, instantaneous
```

pip install is **CACHED**. The rebuild takes under 2 seconds.

### Clean up

```bash
# Remove both images to reclaim disk space.
#
# docker       — the Docker CLI binary
# image        — image management subcommand group
# rm           — remove the specified images by name:tag
# layers-bad:1.0.0 layers-good:1.0.0 — both images in one command
docker image rm layers-bad:1.0.0 layers-good:1.0.0
```

---

## Summary: the rule

> **Copy dependency manifests first. Install dependencies. Then copy source code.**

The moment you understand that instruction order determines which expensive
build steps are cached and which are not, you will never write a Dockerfile
the naive way again.

| Pattern | Code change rebuild time | requirements.txt change rebuild time |
|---------|--------------------------|--------------------------------------|
| Unoptimized (`COPY . .` first) | Slow — pip runs every time | Slow |
| Optimized (requirements first) | Fast — pip is cached | Slow (expected) |

---

## What you learned in this module

1. Every Dockerfile instruction that modifies the filesystem creates an immutable layer.
2. Docker caches layers by content hash. A cache hit skips the instruction entirely.
3. A cache miss cascades: all layers below the miss are also invalidated.
4. The order of `COPY` and `RUN` instructions is architectural — it determines rebuild speed.
5. The golden rule: copy `requirements.txt` first, run `uv pip install`, then copy source code.

**Next:** [03-volumes](../03-volumes/) — understand Docker volumes and how to persist data beyond the container lifecycle.
