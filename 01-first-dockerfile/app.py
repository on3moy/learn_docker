"""
Module 01 — First Dockerfile
Flask application for the introductory Docker module.

This file is intentionally simple so you can focus on the Dockerfile concepts
rather than the application code. There are two endpoints:

    /        — returns a JSON greeting, proves the server is running
    /health  — returns JSON status, called by the Dockerfile's HEALTHCHECK

Python version: 3.12
"""

# flask: the web framework our container will serve.
# Flask is a lightweight WSGI framework — it handles HTTP routing, request
# parsing, and response building without forcing you to write raw socket code.
#
# jsonify: converts a Python dict into a proper HTTP response with:
#   Content-Type: application/json
#   HTTP 200 status code (default)
# Without jsonify you would have to manually set the Content-Type header.
from flask import Flask, jsonify

# Response is the Flask type returned by view functions.
# We import it solely for the type hint on the return type so that static
# analysis tools (mypy, Pyright, Pylance) can verify correctness.
from flask import Response


# Flask(__name__) creates the application object.
# __name__ is the current module's name (in this case "__main__" when run
# directly, or "app" when imported as a module).
# Flask uses __name__ to locate template and static asset directories —
# passing __name__ is always correct for a single-file application.
app: Flask = Flask(__name__)


@app.route("/")
def index() -> Response:
    """Return a JSON greeting at the root endpoint.

    In production this might return API docs or redirect to a UI.
    Here it proves the server is up and accepting connections.
    """
    # jsonify wraps the dict in a Flask Response object.
    # The HTTP status code defaults to 200 OK.
    return jsonify({
        "message": "Hello from your first Docker container!",
        "module": "01-first-dockerfile",
        "hint": "Try /health to see what the HEALTHCHECK endpoint returns.",
    })


@app.route("/health")
def health() -> Response:
    """Return a JSON health status at /health.

    The Dockerfile's HEALTHCHECK instruction calls this endpoint periodically.
    Orchestrators (Docker Swarm, Kubernetes) use the result to decide:
      - Whether to route traffic to this container replica
      - Whether to restart the container automatically
      - What to display in `docker ps` under the STATUS column

    A real health check might also test database connectivity, cache
    availability, or disk space. Here we keep it simple: if Flask is running
    and can return a response, the service is healthy.

    Return 200 OK = healthy.
    Any non-2xx status or connection failure = unhealthy.
    """
    return jsonify({
        "status": "healthy",
        "module": "01-first-dockerfile",
    })


# ── Entry point ───────────────────────────────────────────────────────────────
# This block only executes when the script is run directly:
#   python app.py
# It does NOT execute when app.py is imported as a module (e.g. by pytest).
# This is standard Python idiom.
if __name__ == "__main__":
    # host="0.0.0.0" — listen on ALL network interfaces inside the container.
    #
    # If you used the default "127.0.0.1" (localhost), the Flask server would
    # only accept connections originating from within the container itself.
    # Your `docker run -p 5000:5000` port mapping would appear to silently
    # fail — you would get "connection refused" from the host machine.
    # Always use 0.0.0.0 for containerised Flask apps.
    #
    # port=5000 — the port Flask listens on inside the container.
    # This must match the EXPOSE instruction in the Dockerfile and the
    # container-side of -p in docker run (e.g. -p 8080:5000 maps
    # host port 8080 → container port 5000).
    #
    # debug=False — NEVER enable Flask debug mode in a container that may be
    # exposed publicly. The Werkzeug interactive debugger bundled with
    # debug=True allows arbitrary Python code execution from a browser —
    # it is a remote code execution vulnerability in disguise.
    app.run(host="0.0.0.0", port=5000, debug=False)
