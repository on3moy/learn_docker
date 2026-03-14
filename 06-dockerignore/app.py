"""
Module 06 — .dockerignore
Simple Flask application used to demonstrate how .dockerignore controls what
gets sent to the Docker daemon as the build context.

The lesson is in the .dockerignore file and notes.md — not in this app.
This app exists so the Dockerfile has something to build and run.

Endpoints:
    /        — JSON greeting
    /health  — JSON health status
"""

from flask import Flask, jsonify, Response


app: Flask = Flask(__name__)


@app.route("/")
def index() -> Response:
    """Root endpoint."""
    return jsonify({
        "message": "Hello from the dockerignore module!",
        "module": "06-dockerignore",
        "hint": "Check .dockerignore to see what was excluded from the build context.",
    })


@app.route("/health")
def health() -> Response:
    """Health endpoint — called by the HEALTHCHECK instruction."""
    return jsonify({
        "status": "healthy",
        "module": "06-dockerignore",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
