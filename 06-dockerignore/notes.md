# Module 06 — .dockerignore

## What this module covers

The Docker build context — what it is, why it matters, and how `.dockerignore`
controls it. How to measure build context size before and after exclusions, and
why leaking secrets through the context is a real threat.

---

## Background: the build context lifecycle

When you run `docker build .`:

```
your filesystem
       │
       ▼
Docker CLI bundles files into a tar archive  ← .dockerignore exclusions happen HERE
       │
       ▼
archive sent over Unix socket to Docker daemon
       │
       ▼
daemon unpacks archive → makes files available to COPY/ADD instructions
       │
       ▼
Dockerfile instructions execute using files from the unpacked archive
```

Key insight: **exclusions happen before transmission, not at COPY time.**
A file excluded by `.dockerignore` never reaches the daemon, even if a
`COPY . .` instruction would normally copy it. Conversely, a file NOT excluded
is transmitted and cached by the daemon even if no `COPY` ever touches it.

---

## The files intentionally in this module

| File | Why it's here |
|------|---------------|
| `secrets.env` | Simulates a developer's local credentials file |
| `big-data/placeholder.txt` | Simulates a large data directory |
| *(imaginary)* `__pycache__/` | Python bytecode — excluded by .dockerignore |
| *(imaginary)* `.git/` | Git history — excluded by .dockerignore |

---

## Experiment 1 — Measure build context size with `du`

```bash
# Measure the total disk usage of the current directory recursively.
#
# du           — "disk usage" — reports disk space used by files and directories
# -s           — (--summarize) show only the total for each argument, not
#                every subdirectory recursively. Without -s you would see
#                a line per file — overwhelming for large directories.
# -h           — (--human-readable) print sizes as 1K, 234M, 2G instead of
#                raw 512-byte block counts, which are hard to read mentally.
# .            — measure the current directory
du -sh .
```

This gives you the raw total before Docker filtering. Compare it with the
build context size Docker reports at the start of the build (next experiment).

```bash
# Measure disk usage of specific subdirectories to understand what's large.
#
# du           — disk usage
# -sh          — summarize + human-readable (same flags as above)
# big-data/    — measure the big-data directory specifically
# secrets.env  — measure the secrets file
# .git/        — measure the git history directory (if it exists at root level)
du -sh big-data/ secrets.env
```

---

## Experiment 2 — See the build context size in docker build output

```bash
# Build WITHOUT a .dockerignore to see the full context size.
# First, temporarily rename .dockerignore so Docker ignores it.
#
# mv           — move (rename) a file
# .dockerignore         — the file to rename
# .dockerignore.backup  — the new name (Docker will not read this)
mv .dockerignore .dockerignore.backup
```

```bash
# Build the image without any exclusions.
#
# docker       — the Docker CLI binary
# build        — construct an image from a Dockerfile
# -t ignore-test:no-ignore — name the image for this experiment
# .            — send the entire current directory as the build context
#
# WHAT TO OBSERVE: The very first line of output shows the build context size:
#   Sending build context to Docker daemon  X.XXXMB
# Note this number — it includes secrets.env, big-data/, and everything else.
docker build -t ignore-test:no-ignore .
```

```bash
# Restore the .dockerignore file.
#
# mv           — move (rename) back to the original name
mv .dockerignore.backup .dockerignore
```

```bash
# Build again WITH the .dockerignore in place.
#
# Compare the "Sending build context" line — it should be dramatically smaller.
docker build -t ignore-test:with-ignore .
```

**What to observe:** The "Sending build context" size drops significantly
because `secrets.env`, `big-data/`, `.git/`, `__pycache__/`, and documentation
files are all excluded before the archive is even assembled.

---

## Experiment 3 — Verify excluded files are NOT in the image

```bash
# Run a container from the image and list /app to confirm only app.py
# and the installed packages are present — no secrets.env, no big-data/.
#
# docker       — the Docker CLI binary
# run          — create and start a container
# --rm         — auto-remove when the command exits
# -it          — interactive with a pseudo-TTY
# ignore-test:with-ignore — the image with .dockerignore applied
# ls -la /app  — list the contents of the /app working directory
#   ls         — list directory contents
#   -l         — long format: permissions, owner, size, timestamp
#   -a         — include hidden files (those starting with .)
#   /app       — the WORKDIR we set in the Dockerfile
docker run --rm -it ignore-test:with-ignore ls -la /app
```

Expected output: only `app.py` and any installed package files. No `secrets.env`,
no `big-data/`, no `notes.md`. The `.dockerignore` did its job.

```bash
# Confirm secrets.env is absent by trying to cat it — should error.
#
# docker       — the Docker CLI binary
# run          — start a container
# --rm         — auto-remove when done
# ignore-test:with-ignore — the image
# cat /app/secrets.env — attempt to read the secrets file
#   cat        — concatenate and print file contents
#   /app/secrets.env — the path where it would be if it were included
docker run --rm ignore-test:with-ignore cat /app/secrets.env
```

Expected output: `cat: /app/secrets.env: No such file or directory`
The file is absent because .dockerignore excluded it from the build context
before the daemon ever received it.

---

## Experiment 4 — The danger of COPY . . without .dockerignore

This experiment illustrates what happens when developers forget `.dockerignore`.

```bash
# Rename the .dockerignore again to simulate it being absent.
mv .dockerignore .dockerignore.backup
```

```bash
# Build a test image that uses COPY . . (copies everything in context).
# We will use a one-liner Dockerfile for this demonstration.
#
# The <<'EOF' ... EOF syntax is a "here-document" — it passes multi-line
# text directly to the command without creating a temporary file.
docker build -t ignore-test:dangerous - <<'EOF'
FROM python:3.12-slim
WORKDIR /app
COPY . .
CMD ["cat", "/app/secrets.env"]
EOF
```

```bash
# Run the dangerous image — it prints the "secrets" directly to stdout.
#
# docker run   — run a container
# --rm         — auto-remove when done
# ignore-test:dangerous — the image that COPYed everything including secrets
docker run --rm ignore-test:dangerous
```

Expected output: the contents of `secrets.env` — fake credentials printed
to the terminal. In a real project these would be real database passwords
and API keys, now baked into a shareable image.

```bash
# Restore the .dockerignore.
mv .dockerignore.backup .dockerignore
```

```bash
# Clean up the dangerous test image.
docker image rm ignore-test:dangerous ignore-test:no-ignore ignore-test:with-ignore
```

---

## Best practices checklist

- [ ] Every project directory has a `.dockerignore`
- [ ] `*.env`, `.env`, and any secret files are excluded
- [ ] Large data directories are excluded (fetch data at runtime from object storage)
- [ ] `.git/` is excluded (commit history has no place in a runtime image)
- [ ] `__pycache__/` and `*.pyc` are excluded (platform-specific, regenerated at runtime)
- [ ] `node_modules/`, `.venv/`, `venv/` are excluded (OS-specific, rebuilt by Dockerfile)
- [ ] Documentation (`*.md`, `notes.md`) is excluded if not needed at runtime
- [ ] CI/CD pipelines verify context size doesn't grow unexpectedly

---

## What you learned in this module

1. The build context is assembled and transmitted BEFORE Docker reads the Dockerfile.
2. Excluded files never reach the daemon — not transmitted, not cacheable, not COPYable.
3. `secrets.env` exclusion is security-critical: baked-in credentials are a real threat.
4. `big-data/` exclusion is a performance necessity: large contexts slow every build.
5. `__pycache__/` is platform-specific bytecode — never include it in a Linux container image.
6. `.git/` exposes commit history and inflates context — always exclude it.
7. Use `du -sh` to measure raw directory size; compare with Docker's "Sending build context" line.
8. A `.dockerignore` is not optional — it is a security and performance baseline.

---

**You have completed the Docker Foundations learning path!**

Review the [README](../README.md) cheat sheet to consolidate everything you have learned.
