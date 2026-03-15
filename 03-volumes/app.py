# ─────────────────────────────────────────────────────────────────────────────
# Module 03 — Volumes
# app.py — Flask application that reads and writes files to a mounted volume.
#
# PURPOSE OF THIS FILE
# ────────────────────
# This app exists to make Docker volumes tangible. It exposes HTTP endpoints
# that write timestamped entries to /data (the volume mount point) and read
# them back. When you stop and remove the container and start a new one with
# the same named volume, you will see the data persists — the volume outlives
# the container.
#
# ROUTES
# ──────
# POST   /write?msg=<text>  — Write a timestamped entry to /data.
# GET    /read              — Read and return all entries in /data.
# DELETE /clear             — Delete all entries from /data (keeps the volume).
# GET    /health            — Health check endpoint (called by HEALTHCHECK).
# GET    /                  — Usage instructions.
# ─────────────────────────────────────────────────────────────────────────────

# os — standard library module for filesystem operations.
# We use os.listdir(), os.path.join(), os.remove(), os.makedirs().
import os

# json — standard library module for serialising Python dicts to JSON strings
# and deserialising JSON strings back to Python dicts.
import json

# datetime, timezone — standard library types.
# datetime.now(timezone.utc) gives a timezone-aware UTC timestamp, eliminating
# ambiguity about which timezone the stamp represents.
from datetime import datetime, timezone

# Flask  — the application class. We create one instance: `app`.
# jsonify — converts a Python dict/list to a Flask Response with
#           Content-Type: application/json set automatically.
# request — a proxy to the current HTTP request. We use request.args to read
#           URL query parameters (e.g. ?msg=hello).
from flask import Flask, jsonify, request


# ─────────────────────────────────────────────────────────────────────────────
# DATA_DIR — the path inside the container where volume-backed files live.
#
# This constant must match:
#   1. The VOLUME ["/data"] declaration in the Dockerfile.
#   2. The container-side path in your docker run -v flag, e.g. -v mydata:/data
#
# If you run the container WITHOUT mounting a volume, Docker still creates an
# anonymous volume at /data (because of the VOLUME declaration in the
# Dockerfile). The app works, but anonymous volumes are named by UUID and hard
# to reference later. Always use a named volume in practice.
# ─────────────────────────────────────────────────────────────────────────────
DATA_DIR: str = "/data"


# ─────────────────────────────────────────────────────────────────────────────
# Instantiate the Flask application.
#
# __name__ tells Flask the name of the current module. Flask uses this to
# resolve template and static file paths relative to the module location.
# For a single-file app there are no templates, but __name__ is always the
# right value to pass here.
# ─────────────────────────────────────────────────────────────────────────────
app = Flask(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Route: GET /
#
# Returns a JSON usage guide. Useful when you curl the container and want a
# reminder of the available endpoints without reading the source code.
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/")
def index() -> tuple:
    """Return a JSON usage guide for this app."""
    return jsonify({
        "module": "03-volumes",
        "description": (
            "A Flask app that reads and writes files to a Docker volume. "
            "Use the endpoints below to write data, read it back, and prove "
            "it persists across container restarts."
        ),
        "routes": {
            "POST /write?msg=<text>": "Write a timestamped entry to /data.",
            "GET /read": "Read and return all entries stored in /data.",
            "DELETE /clear": "Delete all entries from /data (volume is kept).",
            "GET /health": "Health check — returns {status: healthy}.",
        },
        "volume_path": DATA_DIR,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Route: POST /write?msg=<text>
#
# Writes a single JSON file to DATA_DIR. The filename encodes the UTC timestamp
# so that files sort chronologically when listed. The content is a JSON object
# with the timestamp and the user-supplied message.
#
# Example:
#   curl -X POST "http://localhost:5000/write?msg=hello+world"
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/write", methods=["POST"])
def write() -> tuple:
    """Write a timestamped entry to the volume."""
    # Pull the ?msg= query parameter from the URL.
    # request.args is a dict-like object of URL query parameters.
    # We default to "no message provided" if the caller omits the parameter.
    message: str = request.args.get("msg", "no message provided")

    # Generate a UTC timestamp string, e.g. "2026-03-14T12-34-56Z".
    # strftime produces a formatted string directly. We use hyphens instead of
    # colons because colons are illegal in filenames on Windows and some
    # filesystems. The trailing Z denotes UTC (Zulu time).
    timestamp: str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")

    # Build a unique filename from the timestamp.
    # Two writes within the same second will overwrite each other — acceptable
    # for a learning exercise. In production you would append a random suffix.
    filename: str = f"{timestamp}.json"
    filepath: str = os.path.join(DATA_DIR, filename)

    # Construct the dict we will persist to disk.
    entry: dict = {
        "timestamp": timestamp,
        "message": message,
    }

    # Write the entry to disk inside the volume directory.
    # "w" creates the file if it does not exist, or overwrites if it does.
    # json.dump() serialises the dict to a JSON string and writes to the file.
    # indent=2 makes the file human-readable when you cat it directly.
    with open(filepath, "w") as f:
        json.dump(entry, f, indent=2)

    # Return HTTP 201 Created — the correct status code when a new resource is
    # created. Flask defaults to 200 OK; we return the status as the second
    # element of the tuple.
    return jsonify({"written": entry, "file": filename}), 201


# ─────────────────────────────────────────────────────────────────────────────
# Route: GET /read
#
# Lists all .json files in DATA_DIR, reads each, and returns them as a JSON
# array ordered by filename (chronological because filenames are timestamps).
#
# Example:
#   curl http://localhost:5000/read
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/read")
def read() -> tuple:
    """Read and return all entries written to the volume."""
    try:
        # os.listdir() returns bare filenames, not full paths.
        # sorted() gives chronological order since filenames encode the time.
        filenames: list = sorted(os.listdir(DATA_DIR))
    except FileNotFoundError:
        # /data does not exist. This should not happen in a container (the
        # VOLUME declaration ensures the directory exists), but it can happen
        # when running the app directly on the host without creating /data.
        return jsonify({
            "error": f"{DATA_DIR} does not exist.",
            "hint": "Run the app inside Docker with: docker run -v mydata:/data ...",
        }), 500

    entries: list = []

    # Iterate over files, filtering to .json only so any stray files
    # (e.g. .DS_Store on macOS host bind mounts) do not cause errors.
    for fname in filenames:
        if not fname.endswith(".json"):
            continue

        # os.path.join() builds a portable full path. Do not concatenate with
        # "/" directly — it is not portable across operating systems.
        fpath: str = os.path.join(DATA_DIR, fname)

        # Open and deserialise each JSON file back to a Python dict.
        with open(fpath) as f:
            entries.append(json.load(f))

    return jsonify({
        "count": len(entries),
        "entries": entries,
    })


# ─────────────────────────────────────────────────────────────────────────────
# Route: DELETE /clear
#
# Deletes all files inside DATA_DIR. The directory itself and the volume are
# preserved — only the contents are removed. Useful for resetting the
# persistence experiment without destroying the volume.
#
# Example:
#   curl -X DELETE http://localhost:5000/clear
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/clear", methods=["DELETE"])
def clear() -> tuple:
    """Delete all entries from the volume directory."""
    filenames: list = os.listdir(DATA_DIR)
    deleted: int = 0

    for fname in filenames:
        fpath: str = os.path.join(DATA_DIR, fname)

        # os.path.isfile() guards against accidentally deleting subdirectories
        # if any exist inside /data.
        if os.path.isfile(fpath):
            os.remove(fpath)
            deleted += 1

    return jsonify({
        "deleted": deleted,
        "message": "All entries cleared.",
        "note": "The volume itself still exists — only its contents were removed.",
    })


# ─────────────────────────────────────────────────────────────────────────────
# Route: GET /health
#
# Returns a simple JSON health status. Docker's HEALTHCHECK instruction calls
# this endpoint on a schedule to determine whether the container is healthy.
# See the Dockerfile's HEALTHCHECK block for a full explanation of the flags.
# ─────────────────────────────────────────────────────────────────────────────
@app.route("/health")
def health() -> tuple:
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


# ─────────────────────────────────────────────────────────────────────────────
# Entry point
#
# This block only executes when the script is run directly (python app.py).
# It does NOT execute when app.py is imported as a module (e.g. by a WSGI
# server like gunicorn, which imports the `app` object directly).
#
# os.makedirs(DATA_DIR, exist_ok=True)
#   Ensures /data exists before the app accepts any requests.
#   Inside a container with a mounted volume, /data already exists.
#   Outside Docker (local dev), this creates the directory so the app does not
#   crash immediately on the first write attempt.
#   exist_ok=True: do not raise an error if /data already exists.
#
# app.run(host="0.0.0.0", port=5000, debug=False)
#   host="0.0.0.0" — bind to all network interfaces inside the container.
#                    Without this, Flask only listens on 127.0.0.1 (loopback),
#                    which is unreachable from outside the container namespace.
#                    Always use 0.0.0.0 in containerised Flask apps.
#   port=5000      — must match the EXPOSE instruction and the container-side
#                    of the -p host:container mapping in docker run.
#   debug=False    — NEVER enable debug mode in a container. The Werkzeug
#                    interactive debugger allows arbitrary code execution by
#                    anyone who can reach the server — a critical security risk.
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=False)
