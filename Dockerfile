FROM python:3.12-slim-bookworm

# Install curl and certs required for uv install script
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download and install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Add uv to PATH
ENV PATH="/root/.local/bin:$PATH"

RUN uv venv /opt/venv
# Use the virtual environment automatically
ENV VIRTUAL_ENV=/opt/venv
# Place entry points in the environment at the front of the path
ENV PATH="/opt/venv/bin:$PATH"

# Install Flask in the virtual environment (this was the key bug)
RUN uv pip install flask

# Copy app after env is ready
COPY . .

# Run the app using uv's venv
CMD ["python", "app.py"]
