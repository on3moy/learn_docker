# 🐋 Learn Docker with Flask + uv

This repo provides a hands-on walkthrough of how to:
- Build your first Dockerized Python app using [`uv`](https://github.com/astral-sh/uv) for dependency management
- Use `uv` **without needing `.venv` or `uv init`**
- Create an animated, stylish Flask web app with a **random quote and emoji button**
- Understand how Docker builds, runs, maps ports, and can share environments

---

## 🧠 Learning Objectives

- Install and test Docker
- Write a `Dockerfile` that uses `python:3.12-slim-bookworm`
- Install `uv` inside a container
- Use `uv venv` and `uv pip install flask` in Docker
- Set up environment variables like `VIRTUAL_ENV` and `PATH`
- Serve a Flask app using `CMD ["python", "app.py"]`
- Expose your Flask app on `localhost:5000`
- Style HTML/CSS with VS Code's Slate theme and beautiful button animations
- Share the environment using a Docker image

---

## ⚙️ Install Docker (Windows)

Install Docker Desktop via terminal:

```bash
winget install Docker.DockerDesktop
```

💡 After installation:
- Start Docker Desktop manually or set it to launch on login

---

## 🧪 Verify Docker Works

Check Docker version:
```bash
docker --version
```

Test by running a simple container:
```bash
docker run hello-world
```

---

## 📦 Build the Flask + uv Docker Image

1. Clone or copy this repo.
2. Make sure you're in the same directory as the `Dockerfile` and `app.py`.
3. Build the image:

```bash
docker build -t flask-uv .
```

---

## ▶️ Run the App

```bash
docker run -p 5000:5000 flask-uv
```

Then open:
> http://localhost:5000

---

## 💡 What You’ll See

- A random **quote** and **emoji** from a curated list
- A beautiful animated button (VS Code slate color palette)
- Every click triggers a page refresh with a new quote

---

## 💭 How the Dockerfile Works

No need to `uv init` or create a `.venv` locally — the `Dockerfile` does it all:

```dockerfile
FROM python:3.12-slim-bookworm

# Install uv
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin:$PATH"

# Set up and activate venv
RUN uv venv /opt/venv
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Flask inside the uv venv
RUN uv pip install flask

# Copy all files and folders (Make sure to include .dockerignore)
COPY . .

# Run the app
CMD ["python", "app.py"]
```

---

## 🧽 Dev Tips

| Task | Command |
|------|---------|
| Stop container | Press `CTRL+C` (foreground) or `docker stop <id>` |
| Remove stopped containers | `docker container prune` |
| Rebuild image after `app.py` changes | `docker build -t flask-uv .` |

---

## 🧠 Next Steps (Ideas)

- Add an `/api/quote` endpoint for AJAX
- Deploy with a WSGI server (Gunicorn + Nginx)
- Push image to Docker Hub
- Add live hot reload in dev mode using volume mounts

---

## 📚 Credits

- [Flask](https://flask.palletsprojects.com/)
- [uv](https://github.com/astral-sh/uv)
- [Docker](https://www.docker.com/)
- Emoji list curated manually 🎉

---

## 🏁 Final Notes

This project was built to solidify foundational Docker knowledge. It’s beginner-friendly, production-minded, and easy to extend.

## 👩‍💻 Author

Moy Patel

"Just a Pythonista learning how to containerize joy 🐳💻"