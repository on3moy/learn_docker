# syntax=docker/dockerfile:1
# ─────────────────────────────────────────────────────────────────────────────
# Module 03 — CMD vs ENTRYPOINT
# Dockerfile.cmd — demonstrates CMD-only behaviour
#
# When a container is started with CMD only, the entire CMD can be REPLACED
# by passing a command after the image name in `docker run`.
# ─────────────────────────────────────────────────────────────────────────────

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY args.py .

# Non-root user (security baseline — see module 01 for the full explanation).
RUN addgroup --system appuser \
    && adduser --system --no-create-home --ingroup appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# ── CMD ───────────────────────────────────────────────────────────────────────
# CMD specifies the DEFAULT command to run when the container starts.
# This is the entire command — there is no ENTRYPOINT to act as a fixed prefix.
#
# ── WHAT "REPLACEABLE" MEANS ─────────────────────────────────────────────────
# docker run cmd-demo:1.0.0
#   → runs: python args.py          (uses the CMD as-is)
#
# docker run cmd-demo:1.0.0 python args.py hello world
#   → runs: python args.py hello world  (CMD replaced by the trailing arguments)
#
# docker run cmd-demo:1.0.0 /bin/sh
#   → runs: /bin/sh                 (entire CMD replaced — args.py never runs)
#
# This flexibility is useful for utility images where the runtime command
# varies widely. It is NOT the recommended pattern for production services
# because the entrypoint can be inadvertently replaced.
#
# ── EXEC FORM (used here) vs SHELL FORM ──────────────────────────────────────
#
# EXEC FORM:   CMD ["python", "args.py"]
#   Docker executes: python args.py
#   python is PID 1. Signals (SIGTERM, SIGINT) go directly to python.
#   Graceful shutdown works correctly.
#
# SHELL FORM:  CMD python args.py
#   Docker executes: /bin/sh -c "python args.py"
#   /bin/sh is PID 1. python is a child of /bin/sh.
#   SIGTERM goes to /bin/sh which does NOT forward it to python by default.
#   Python receives SIGKILL after the stop timeout — no graceful shutdown.
#
# ALWAYS use exec form. The shell form is a common source of subtle bugs.
CMD ["python", "args.py"]

# ── HEALTHCHECK ───────────────────────────────────────────────────────────────
# This is a script container (runs and exits), not a long-lived service.
# A meaningful HEALTHCHECK is not applicable here, but we include the
# instruction as documentation of the best-practice pattern.
# DISABLE is a valid value — it tells orchestrators "no health check defined".
HEALTHCHECK NONE
