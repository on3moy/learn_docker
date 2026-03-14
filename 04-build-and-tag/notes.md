# Module 04 — Build and Tag

## What this module covers

The full image lifecycle: building, tagging, listing, removing, and pruning
images. Tagging conventions used in real projects, and how tags map to
registry push paths.

---

## The image lifecycle at a glance

```
docker build   →   image exists locally
docker tag     →   image gets an additional name/tag alias
docker image ls →  inspect all local images
docker image rm →  delete a specific image
docker image prune → delete dangling images
```

---

## Step 1 — Build with a precise tag

```bash
# Build an image and give it a specific semantic version tag.
#
# docker       — the Docker CLI binary
# build        — construct an image from a Dockerfile in the build context
# -t myapp:1.0.0 — (--tag) name the image "myapp" and tag it "1.0.0"
#                  name:  the repository name — lowercase, hyphens ok.
#                         In a real registry this becomes username/imagename.
#                  tag:   identifies the version. Omitting the tag defaults to
#                         "latest" — a floating label, not a stable identifier.
# .            — the build context: send everything in the current directory
#                (minus .dockerignore exclusions) to the Docker daemon
docker build -t myapp:1.0.0 .
```

```bash
# Build the same code with a second tag — useful to also mark it "latest".
# This does NOT rebuild the image; it just adds another name to it.
# However, building with -t myapp:latest tags the image at build time.
docker build -t myapp:latest .
```

---

## Step 2 — Inspect local images

```bash
# List all images stored on this machine.
#
# docker       — the Docker CLI binary
# image        — the image management subcommand group
# ls           — list images (equivalent to the older `docker images`)
docker image ls
```

**Example output and column explanations:**

```
REPOSITORY   TAG      IMAGE ID       CREATED         SIZE
myapp        1.0.0    a3f91c2b4d88   2 minutes ago   148MB
myapp        latest   a3f91c2b4d88   2 minutes ago   148MB
python       3.12-slim f5c0ba3e1e12  3 days ago      130MB
```

| Column | Meaning |
|--------|---------|
| `REPOSITORY` | The image name. In a registry this is `registry/username/imagename`. |
| `TAG` | The version label attached to this name. `latest` is a conventional name, not a guarantee of freshness or stability. Two rows with the same IMAGE ID and different tags are the same image with two aliases. |
| `IMAGE ID` | The first 12 characters of the SHA256 digest of the image manifest. Unique per unique set of layers. If two rows show the same IMAGE ID they point to identical layers. |
| `CREATED` | How long ago this image was built or pulled. |
| `SIZE` | Total uncompressed size of all layers in the image. The base image layers are counted once even if shared between multiple images. |

```bash
# Show ALL images including intermediate build layers.
#
# -a           — (--all) include intermediate layers that are not tagged.
#                These accumulate during multi-stage or failed builds.
#                Normally you don't need to see these.
docker image ls -a
```

```bash
# Filter the list to images with a specific name.
#
# myapp        — filter to show only images whose REPOSITORY is "myapp"
docker image ls myapp
```

---

## Step 3 — Add an additional tag to an existing image

```bash
# Add a second tag to an existing image without rebuilding.
#
# docker       — the Docker CLI binary
# tag          — create a new name:tag alias for an existing image
# myapp:1.0.0  — the SOURCE image (name:tag or image ID)
# myapp:stable — the TARGET name:tag to create as an alias
#
# IMPORTANT: this does NOT copy the image. Both tags point to the exact
# same layers. Deleting one tag does not delete the other.
docker tag myapp:1.0.0 myapp:stable
```

---

## Step 4 — Tagging conventions

### `latest`

```
myapp:latest
```

- Automatically assumed when you omit the tag.
- Convention: points to the most recently built or promoted image.
- **Avoid in production.** "latest" is a floating label — `docker pull myapp:latest`
  today and next week may pull different images. Hard to audit, roll back, or debug.

### Semantic versioning (semver)

```
myapp:1.0.0
myapp:1.0.1   ← patch: backwards-compatible bug fix
myapp:1.1.0   ← minor: new feature, backwards-compatible
myapp:2.0.0   ← major: breaking change
```

- Explicit, auditable, easy to roll back.
- `docker run myapp:1.0.0` always runs the same image, today and in five years.
- The recommended convention for published images.

### Git SHA-based tags

```bash
# Tag an image with the current git commit SHA.
#
# git          — the Git version control binary
# rev-parse    — parse a git revision to its full form
# --short HEAD — short form (7-8 characters) of the current commit hash
# $()          — command substitution: inserts the output of git rev-parse
docker build -t myapp:$(git rev-parse --short HEAD) .
```

Produces tags like `myapp:a3f91c2`. Used in CI/CD pipelines to trace exactly
which commit produced which image. Combine with semver:

```
myapp:1.0.0          ← human-readable version
myapp:a3f91c2        ← traceability back to git history
myapp:latest         ← points to current, not version pinned
```

---

## Step 5 — Remove images

```bash
# Remove a specific image by its name:tag.
#
# docker       — the Docker CLI binary
# image        — image management subcommand group
# rm           — remove the specified image(s)
# myapp:stable — remove this specific tag
#
# If this is the LAST tag pointing to these layers, the layers are deleted.
# If other tags still point to the same layers (e.g. myapp:1.0.0 still exists),
# only the "myapp:stable" tag alias is removed — the layers stay.
docker image rm myapp:stable
```

```bash
# Remove by IMAGE ID instead of name:tag.
#
# a3f91c2b4d88 — the IMAGE ID (first 12 chars of the SHA256 digest).
#                Only works if exactly one tag points to this ID.
#                If multiple tags point to it, you must remove by name:tag.
docker image rm a3f91c2b4d88
```

```bash
# Force-remove an image even if a container (stopped) is using it.
#
# -f           — (--force) remove the image even if a container references it.
#                The container layer still exists until the container is removed.
#                Use with caution — the image disappears from `docker image ls`
#                but the disk space is not freed until the container is removed.
docker image rm -f myapp:1.0.0
```

---

## Step 6 — Prune dangling images

```bash
# Remove all "dangling" images — untagged layers with no name.
#
# docker       — the Docker CLI binary
# image        — image management subcommand group
# prune        — remove unused images
#
# WHAT IS A DANGLING IMAGE?
# When you rebuild an image with the same tag (e.g. myapp:1.0.0), the old
# image layers lose their tag. They become "dangling" — they have no
# REPOSITORY or TAG (shown as <none> in `docker image ls`). They accumulate
# on disk over time but are never used.
#
# `docker image prune` removes these orphaned layers.
# It asks for confirmation before deleting.
docker image prune
```

```bash
# Remove ALL unused images — not just dangling ones, but also images that
# exist locally but are not referenced by any container (running or stopped).
#
# -a           — (--all) include non-dangling unused images
# -f           — (--force) skip the confirmation prompt
#
# USE WITH CARE on a development machine — this removes base images like
# python:3.12-slim that you may want to keep for faster future builds.
docker image prune -a -f
```

---

## What is a registry? How do tags map to push paths?

A **registry** is a server that stores and serves Docker images. Docker Hub
(`hub.docker.com`) is the default public registry. You can also run private
registries (AWS ECR, Google Artifact Registry, GitHub Container Registry,
a self-hosted Harbor instance).

A full image reference looks like:

```
registry.example.com/username/imagename:tag
┬───────────────────  ┬───────  ┬─────────  ┬──
│                     │         │            └── tag: version identifier
│                     │         └────────────── image name (repository)
│                     └──────────────────────── username or org namespace
└────────────────────────────────────────────── registry hostname
                                                (omitted = Docker Hub default)
```

**Examples:**

```bash
# Docker Hub (default registry, username "myperson"):
docker tag myapp:1.0.0 myperson/myapp:1.0.0

# GitHub Container Registry:
docker tag myapp:1.0.0 ghcr.io/myperson/myapp:1.0.0

# AWS ECR:
docker tag myapp:1.0.0 123456789.dkr.ecr.us-east-1.amazonaws.com/myapp:1.0.0

# Pushing (not done in this module — for reference):
# docker push myperson/myapp:1.0.0
```

The tag is the identifier that tells the registry which version to serve when
someone does `docker pull myperson/myapp:1.0.0`. Without a tag, `latest` is
assumed — which, in a registry context, often points to an outdated image.

---

## Clean up

```bash
# Remove all images built in this module.
docker image rm myapp:1.0.0 myapp:latest 2>/dev/null; docker image prune -f
```

---

## What you learned in this module

1. `docker build -t name:tag .` — the core build command and what every part means.
2. `docker image ls` — what each column means; IMAGE ID identifies identical layers.
3. `docker tag` — adds an alias without copying layers.
4. `docker image rm` — by name:tag vs by IMAGE ID; last tag removes layers.
5. `docker image prune` — what dangling images are and when they accumulate.
6. Tagging conventions: `latest` (avoid in prod), semver (recommended), git-SHA (CI/CD).
7. Registry anatomy: `registry/username/imagename:tag` and how tags map to push paths.

**Next:** [05-run-flags](../05-run-flags/) — run containers like a professional using every important `docker run` flag.
