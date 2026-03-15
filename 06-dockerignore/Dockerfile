# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# Module 06 — .dockerignore
# Standard Flask Dockerfile. The lesson in this module is the .dockerignore
# file — read that file alongside this one.
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Bring in the uv binary. See module 01 for a full explanation of this pattern.
# NOTE: Pin the tag in production (e.g. uv:0.5.11). :latest used for learning.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY requirements.txt .

# uv pip install --system --no-cache: drop-in for pip install --no-cache-dir.
# --system installs into system Python (no venv needed inside a container).
RUN uv pip install --system --no-cache -r requirements.txt

# COPY app.py specifically (not COPY . .) to demonstrate that even with a
# selective COPY, the entire build context was still sent to the daemon.
# .dockerignore controls what reaches the daemon, not what COPY picks up.
COPY app.py .

RUN addgroup --system appuser \
    && adduser --system --no-create-home --ingroup appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
