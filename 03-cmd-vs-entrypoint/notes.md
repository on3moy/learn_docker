# Module 03 — CMD vs ENTRYPOINT

## What this module covers

The difference between CMD and ENTRYPOINT, shell form vs exec form, PID 1
signal handling, and the recommended ENTRYPOINT + CMD production pattern.

---

## Quick-reference decision table

| Situation | Use |
|-----------|-----|
| Your container is a service (Flask, Postgres, Redis) | `ENTRYPOINT ["executable"]` + `CMD ["default", "args"]` |
| Your container is a CLI tool (arguments vary per run) | `ENTRYPOINT ["executable"]` + `CMD ["--help"]` as default |
| One-off script container, simple default | `CMD ["python", "script.py"]` alone |
| Never use in production | Shell form of either instruction |

---

## Build the three images

```bash
# Change into the module directory.
#
# cd                    — change working directory
# 03-cmd-vs-entrypoint  — the module folder
cd 03-cmd-vs-entrypoint
```

```bash
# Build the CMD-only image.
#
# docker       — the Docker CLI binary
# build        — construct an image from a Dockerfile
# -f           — (--file) specify the Dockerfile by name (non-default filename)
# Dockerfile.cmd — the Dockerfile to build from
# -t           — (--tag) name and tag the image
# cmd-demo:1.0.0 — image name and version
# .            — build context (current directory)
docker build -f Dockerfile.cmd -t cmd-demo:1.0.0 .
```

```bash
# Build the ENTRYPOINT-only image.
docker build -f Dockerfile.entrypoint -t ep-demo:1.0.0 .
```

```bash
# Build the ENTRYPOINT + CMD (combined) image.
docker build -f Dockerfile.both -t both-demo:1.0.0 .
```

---

## Experiment 1 — CMD is fully replaceable

```bash
# Run cmd-demo with NO extra arguments.
# Uses CMD as-is: python args.py
#
# docker       — the Docker CLI binary
# run          — create and start a container
# --rm         — (--remove) automatically remove the container when it exits.
#                Ideal for one-shot containers where you don't need to inspect
#                the container after it stops. Keeps `docker ps -a` clean.
# cmd-demo:1.0.0 — the image to run
docker run --rm cmd-demo:1.0.0
```

Expected output:
```
sys.argv[0] = args.py
sys.argv[1:] = []  (no extra arguments)
```

```bash
# Run cmd-demo WITH extra arguments — they REPLACE the CMD entirely.
#
# docker run --rm cmd-demo:1.0.0  ← the image
# python args.py hello world      ← these trailing words REPLACE the entire CMD
docker run --rm cmd-demo:1.0.0 python args.py hello world
```

Expected output:
```
sys.argv[0] = args.py
sys.argv[1:] = ['hello', 'world']
```

```bash
# Run cmd-demo with a completely different command — demonstrates total override.
# The container runs /bin/sh instead of python args.py.
docker run --rm -it cmd-demo:1.0.0 /bin/sh
```

---

## Experiment 2 — ENTRYPOINT arguments are appended, not replaced

```bash
# Run ep-demo with NO extra arguments.
# Runs: python args.py
docker run --rm ep-demo:1.0.0
```

Expected: `sys.argv[1:]` is empty.

```bash
# Run ep-demo WITH extra arguments.
# Runs: python args.py hello world
# "hello world" is APPENDED to the ENTRYPOINT, not replacing it.
docker run --rm ep-demo:1.0.0 hello world
```

Expected: `sys.argv[1:]` is `['hello', 'world']`.

```bash
# Try passing /bin/sh as an "argument" — it is appended, not a replacement.
# Runs: python args.py /bin/sh  (very different from the CMD experiment!)
docker run --rm ep-demo:1.0.0 /bin/sh
```

Expected: `sys.argv[1:]` is `['/bin/sh']`. Notice no shell spawned.

```bash
# To actually override ENTRYPOINT you must use the explicit --entrypoint flag.
#
# --entrypoint /bin/sh — override the ENTRYPOINT instruction
# -it                  — allocate a pseudo-TTY and keep stdin open
docker run --rm --entrypoint /bin/sh -it ep-demo:1.0.0
```

---

## Experiment 3 — ENTRYPOINT + CMD (the recommended production pattern)

```bash
# Run both-demo with NO extra arguments.
# ENTRYPOINT is: ["python", "args.py"]
# CMD is:        ["--default-arg", "from-CMD"]
# Combined run:  python args.py --default-arg from-CMD
docker run --rm both-demo:1.0.0
```

Expected: `sys.argv[1:]` is `['--default-arg', 'from-CMD']`.

```bash
# Run both-demo WITH extra arguments.
# The runtime arguments REPLACE CMD (not ENTRYPOINT).
# Runs: python args.py custom-argument
docker run --rm both-demo:1.0.0 custom-argument
```

Expected: `sys.argv[1:]` is `['custom-argument']`.
The default `--default-arg from-CMD` was replaced by `custom-argument`.

---

## Shell form vs exec form — the definitive comparison

| | Shell form | Exec form |
|-|------------|-----------|
| Syntax | `CMD python app.py` | `CMD ["python", "app.py"]` |
| Docker wraps in | `/bin/sh -c "python app.py"` | Nothing — runs directly |
| PID 1 | `/bin/sh` | `python` |
| Receives SIGTERM? | No — /bin/sh swallows signals | Yes — directly |
| Graceful shutdown | Broken | Works |
| Shell variable expansion | Yes (`$MY_VAR` works) | No (use `ENV` instead) |
| docker run arg appended | Broken with ENTRYPOINT | Works correctly |
| **Use in production?** | **Never** | **Always** |

### Why PID 1 matters

Every Linux process tree has exactly one process at the top: PID 1.
In a container, PID 1 is whatever you put in CMD or ENTRYPOINT.

`docker stop` sends **SIGTERM** to PID 1 to request a graceful shutdown.
It waits (default 10 seconds), then sends **SIGKILL** to force-terminate.

If `/bin/sh` is PID 1 (shell form), it does not forward SIGTERM to its children
by default. Python never gets the signal, can never drain connections or flush
logs, and gets killed brutally after the timeout.

If `python` is PID 1 (exec form), it receives SIGTERM and can handle it.

---

## Clean up

```bash
# Remove all three images to reclaim disk space.
docker image rm cmd-demo:1.0.0 ep-demo:1.0.0 both-demo:1.0.0
```

---

## What you learned in this module

1. `CMD` defines a replaceable default command. Any trailing arguments in `docker run` replace it entirely.
2. `ENTRYPOINT` defines a fixed executable. Trailing arguments in `docker run` are appended to it, not replacing it.
3. `ENTRYPOINT` + `CMD` together is the production pattern: fixed executable, overridable defaults.
4. Shell form puts `/bin/sh` as PID 1, breaking signal handling. Never use shell form.
5. Exec form (JSON array) puts your process as PID 1. Signals work. Use it always.

**Next:** [04-build-and-tag](../04-build-and-tag/) — master the full image lifecycle and understand tagging conventions.
