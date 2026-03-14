# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# Module 04 — Build and Tag
# Standard Flask Dockerfile — used as the subject of the build/tag/lifecycle
# experiments in notes.md.
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first for layer-cache efficiency (see module 02 for detail).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Non-root user for security (see module 01 for the full explanation).
RUN addgroup --system appuser \
    && adduser --system --no-create-home --ingroup appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost:5000/health || exit 1

CMD ["python", "app.py"]
