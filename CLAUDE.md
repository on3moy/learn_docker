# Instructions for project

Build me a Git learning repository called `docker-learn` focused entirely on Docker Foundations.

This is a personal learning repo — every single file must be exhaustively commented as if it is a
teaching document. No comment is too obvious. The goal is that I can read any file in isolation
and fully understand what is happening, why it is happening, and what would break if I changed it.

---

## Non-Negotiable Global Standards

These apply to EVERY file in the repo without exception.

### Docker Best Practices (enforce in every Dockerfile)
- Always use a specific image tag — never `FROM python:latest`. Explain in a comment why
  floating tags like `latest` are dangerous in real projects (non-reproducible builds)
- Always create and switch to a non-root user called `appuser` before the CMD/ENTRYPOINT.
  Comment why running as root inside a container is a security risk even though it feels harmless
- Always include a HEALTHCHECK instruction. Comment what it does, what the flags mean, and
  what orchestrators like Docker Swarm or Kubernetes use it for
- Always use COPY over ADD unless you specifically need ADD's tar-extraction or URL features.
  Comment why ADD has surprising behavior that catches beginners off guard
- Always use exec form for CMD and ENTRYPOINT (["python", "app.py"] not "python app.py").
  Comment the difference between shell form and exec form and why exec form is preferred
  (signal handling, PID 1 behavior)
- Never install packages as root without immediately cleaning the cache in the same RUN instruction.
  Use uv (Astral) for all package installs — never plain pip. Pattern:
  `COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv` then
  `RUN uv pip install --system --no-cache -r requirements.txt` — comment every flag
- Always pin base image digests in a comment next to the FROM line for production awareness,
  even if we use the tag form for readability in learning
- Always set ENV PYTHONDONTWRITEBYTECODE=1 and ENV PYTHONUNBUFFERED=1 — comment exactly
  what each env var does to Python's runtime behavior and why it matters in containers
- Always use a .dockerignore. Even modules that are not the .dockerignore lesson should
  include a minimal .dockerignore

### CLI Command Documentation Standards (enforce in every notes.md)
Every single CLI command shown — docker, pip, python, or bash — must be documented like this:
```bash
  # What this command does and when you would use it
  #
  # docker        — the Docker CLI binary
  # build         — the subcommand: builds an image from a Dockerfile
  # -t            — (--tag) names and optionally tags the image in name:tag format
  #                 without this flag the image is built but has no human-readable name,
  #                 only a SHA256 image ID which is hard to reference later
  # myapp:1.0.0   — the name is "myapp", the tag is "1.0.0"
  #                 omitting the tag defaults to "latest" which is a floating tag — avoid in prod
  # .             — the build context: the directory Docker sends to the daemon to build from
  #                 "." means the current directory. Everything in this directory (minus
  #                 .dockerignore exclusions) is sent to the Docker daemon — keep it lean
  docker build -t myapp:1.0.0 .
```

This format is required for every command shown. No command is shown naked without explanation.
Even `cd`, `ls`, or `cat` commands used in examples must have a brief comment.

### Python Code Standards
- Strict PEP 8 — no padded assignments, 4-space indentation, two blank lines between top-level
  definitions, one blank line between methods
- Type hints on every function signature
- Inline comments explaining what each block does in the context of the Docker lesson
- All requirements.txt files must pin exact versions (e.g. flask==3.1.0) — comment why pinning
  matters for Docker layer cache reproducibility and CI/CD stability
- No inline pip installs in Dockerfiles — always use requirements.txt

---

## Repo Structure

docker-learn/
├── README.md
├── .gitignore
├── 01-first-dockerfile/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── .dockerignore
│   └── notes.md
├── 02-image-layers/
│   ├── Dockerfile.unoptimized
│   ├── Dockerfile.optimized
│   ├── app.py
│   ├── requirements.txt
│   ├── .dockerignore
│   └── notes.md
├── 03-volumes/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── .dockerignore
│   └── notes.md
├── 04-build-and-tag/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── .dockerignore
│   └── notes.md
├── 05-run-flags/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── sample.env
│   ├── .dockerignore
│   └── notes.md
├── 06-dockerignore/
│   ├── Dockerfile
│   ├── app.py
│   ├── requirements.txt
│   ├── .dockerignore
│   ├── secrets.env
│   ├── big-data/placeholder.txt
│   └── notes.md

---

## README.md Requirements
- Purpose of the repo and how to use it as a learning path
- Prerequisites: Docker Engine or Docker Desktop, Python 3.12, Git
- Learning path: numbered order with one sentence on what each module teaches
- Quick-reference cheat sheet of every docker command used across all modules,
  each with a one-line description of when you would reach for it
- Link to official Docker documentation for each major topic covered

---

## Per-Module Requirements

### 01-first-dockerfile
- Base image: `python:3.12-slim`
- Comment on the FROM line must explain:
  - What slim means vs alpine vs the full image (size, libc, debugging tradeoffs)
  - Why 3.12 is pinned and not latest
- Explain WORKDIR, COPY, RUN, EXPOSE, CMD each with a dedicated comment block
- Flask app with `/` returning a JSON greeting and `/health` returning JSON status
- HEALTHCHECK must call the `/health` endpoint — comment every HEALTHCHECK flag:
  --interval, --timeout, --start-period, --retries

### 02-image-layers
- Same app, two Dockerfiles:
  - Dockerfile.unoptimized: copies all files first, then installs dependencies
  - Dockerfile.optimized: copies requirements.txt first, installs deps, then copies app code
- Comments must explain Docker's layer cache mechanism step by step:
  what a layer is, what invalidates a cache, why order of instructions is architectural
- notes.md must include a timed experiment:
  build once (cold), change app.py, build again — compare cache hit/miss behavior between
  the two Dockerfiles with the exact commands, flags explained, and what to observe in output

### 03-volumes
- Flask app (app.py) with POST /write, GET /read, DELETE /clear, GET /health endpoints
  that read and write timestamped JSON files to /data (the volume mount point)
- Dockerfile: creates /data, chowns it to appuser before VOLUME declaration, uses
  VOLUME ["/data"] with an exhaustive comment block explaining what the instruction
  does and does not do
- notes.md must cover:
  - The three storage types: named volumes, bind mounts, tmpfs
  - Why container read-write layers are ephemeral (destroyed on docker rm)
  - Full experiment: write data → stop and REMOVE container → start new container with
    same named volume → prove data persists
  - Every docker volume command: create, ls, inspect, rm, prune — per CLI standard
  - Bind mount syntax (-v /host:/container and -v /host:/container:ro)
  - --mount syntax as a verbose, explicit alternative to -v
  - Decision guide: when to use named volume vs bind mount vs tmpfs
  - Permission note: named volumes use image ownership; bind mounts use host ownership

### 04-build-and-tag
- notes.md covers the full image lifecycle:
  - docker build — every flag explained per the CLI documentation standard above
  - docker image ls — explain every column in the output (REPOSITORY, TAG, IMAGE ID,
    CREATED, SIZE)
  - docker image rm — explain the difference between removing by name vs ID
  - docker image prune — explain dangling images and when this accumulates
  - Tagging conventions: latest, semver (1.0.0), git-sha-based tags — comment tradeoffs
  - What a registry is conceptually and how tags map to push paths (no actual push needed)

### 05-run-flags
- Flask app reads environment variables and returns them at `/config` as JSON
- notes.md documents every important docker run flag with the CLI standard:
  - -d / --detach
  - -p / --publish (host:container format, why both sides matter)
  - -e / --env and --env-file (diff between them, security note on -e in shell history)
  - -v / --volume (bind mount host:container:mode — explain ro vs rw)
  - --name (why naming matters for docker logs, exec, stop by name)
  - --rm (when to use, when NOT to use — debugging containers you want to inspect after crash)
  - --restart (no, on-failure, always, unless-stopped — explain each policy)
  - -it (why -i and -t are separate flags, what a pseudo-TTY is in plain English)
  - --network (brief intro only — covered in the networking module)
  - --cpus and --memory (resource limits, connect back to deploy.resources in Compose)
- "Try it yourself" section: run the container with different --env values and curl /config
  to see the output change. Every curl command must follow the CLI documentation standard

### 06-dockerignore
- Project intentionally contains:
  - secrets.env — a fake secrets file
  - big-data/placeholder.txt — simulates a large data directory
  - A comment-placeholder representing __pycache__ and .git
- .dockerignore must exclude all of them with a comment per line explaining:
  - Why secrets.env is excluded (never bake secrets into an image)
  - Why big-data/ is excluded (build context is sent to Docker daemon over a socket —
    large files slow the build and bloat the image unnecessarily)
  - Why __pycache__ is excluded (bytecode is platform-specific, regenerated at runtime)
  - Why .git is excluded (exposes commit history and inflates context size)
- notes.md must show how to measure build context size before and after .dockerignore
  using docker build output and `du` — every flag on du explained per the CLI standard

---

## Final Instruction

Generate all files completely. No placeholders, no truncation, no "add your code here" stubs.
Every file must be fully usable as written. Every command must be explainable line by line.
Every best practice must have a comment explaining not just what to do but why it matters
and what the consequence is of ignoring it.