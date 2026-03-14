"""
Module 05 — Run Flags
Flask application that reads environment variables and returns them as JSON.

This makes the effect of `docker run -e` and `--env-file` immediately visible:
change the env vars at runtime and the /config response changes accordingly.

Endpoints:
    /        — JSON greeting
    /health  — JSON health status (called by HEALTHCHECK)
    /config  — JSON dump of the app's runtime configuration, read from env vars
"""

# os: the standard library module for interacting with the operating system.
# os.environ is a dict-like object that contains the current process's
# environment variables. Every `docker run -e KEY=VALUE` you pass appears here.
import os

from flask import Flask, jsonify, Response


app: Flask = Flask(__name__)


@app.route("/")
def index() -> Response:
    """Root endpoint."""
    return jsonify({
        "message": "Hello from the run-flags module!",
        "module": "05-run-flags",
        "hint": "Hit /config to see the env vars passed to this container.",
    })


@app.route("/health")
def health() -> Response:
    """Health endpoint — called by the Dockerfile HEALTHCHECK."""
    return jsonify({
        "status": "healthy",
        "module": "05-run-flags",
    })


@app.route("/config")
def config() -> Response:
    """Return environment variable values as JSON.

    This endpoint demonstrates the effect of docker run flags:
      -e APP_ENV=production       → APP_ENV appears here
      -e LOG_LEVEL=debug          → LOG_LEVEL appears here
      --env-file sample.env       → all vars in sample.env appear here

    os.environ.get(key, default) reads an env var.
    If the variable is not set, the default value is returned instead of
    raising a KeyError. This makes the app safe to run without every variable
    being explicitly provided.
    """
    # Read a set of named env vars that the sample.env file also defines.
    # Using .get() with defaults so the app works even if no env vars are passed.
    return jsonify({
        "APP_ENV":    os.environ.get("APP_ENV", "development"),
        "LOG_LEVEL":  os.environ.get("LOG_LEVEL", "info"),
        "APP_PORT":   os.environ.get("APP_PORT", "5000"),
        "DEBUG_MODE": os.environ.get("DEBUG_MODE", "false"),
        "APP_SECRET": os.environ.get("APP_SECRET", "(not set — pass via -e or --env-file)"),
    })


if __name__ == "__main__":
    # Read the port from an env var so it can be overridden at runtime:
    #   docker run -e APP_PORT=8080 ...
    # int() converts the string value to an integer that app.run accepts.
    # The default "5000" is used if APP_PORT is not set.
    port: int = int(os.environ.get("APP_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=False)
