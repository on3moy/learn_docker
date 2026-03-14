"""
Module 04 — Build and Tag
Simple Flask application used as the subject of the build/tag/list/remove
lifecycle experiments in notes.md.

The application itself is not the lesson — the lesson is what happens to this
image in `docker build`, `docker image ls`, `docker image rm`, and `docker tag`.

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
        "message": "Hello from the build-and-tag module!",
        "module": "04-build-and-tag",
    })


@app.route("/health")
def health() -> Response:
    """Health endpoint — called by the HEALTHCHECK instruction."""
    return jsonify({
        "status": "healthy",
        "module": "04-build-and-tag",
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
