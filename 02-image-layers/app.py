"""
Module 02 — Image Layers
Flask application used to demonstrate Docker's layer cache mechanism.

This app is intentionally identical to the one in module 01. The lesson is in
the two Dockerfiles (Dockerfile.unoptimized and Dockerfile.optimized), not in
the application code. Read those Dockerfiles to understand why the order of
instructions in a Dockerfile is an architectural decision that directly controls
your rebuild speed.

Endpoints:
    /        — JSON greeting
    /health  — JSON health status (called by the HEALTHCHECK instruction)
"""

from flask import Flask, jsonify, Response


app: Flask = Flask(__name__)


@app.route("/")
def index() -> Response:
    """Root endpoint — confirms the server is running."""
    return jsonify({
        "message": "Hello from the image-layers module!",
        "module": "02-image-layers",
        "lesson": "Edit this file, then rebuild both Dockerfiles to see the cache difference.",
    })


@app.route("/health")
def health() -> Response:
    """Health endpoint — called by the HEALTHCHECK instruction in both Dockerfiles."""
    return jsonify({
        "status": "healthy",
        "module": "02-image-layers",
    })


if __name__ == "__main__":
    # 0.0.0.0 — accept connections from outside the container (required for
    # docker run -p to work). See module 01 notes for a full explanation.
    app.run(host="0.0.0.0", port=5000, debug=False)
