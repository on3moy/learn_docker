"""
Module 03 — CMD vs ENTRYPOINT
A Python script that prints sys.argv so you can observe how Docker passes
arguments to the container process under different CMD/ENTRYPOINT patterns.

When you run this script inside a container, the output reveals exactly what
arguments Docker assembled from the Dockerfile's CMD/ENTRYPOINT instructions
and any extra arguments you passed to `docker run`.

sys.argv is a list:
  sys.argv[0]  — the name of the script itself (always present)
  sys.argv[1:] — any additional arguments passed at the command line
"""

# sys: the standard-library module for system-specific parameters.
# sys.argv is the list of command-line arguments passed to the Python process.
# It is always a list of strings, never integers or other types.
import sys


def main() -> None:
    """Print sys.argv in a readable format so Docker argument behaviour is visible."""
    # Print a header so the output is easy to identify in docker run output.
    print("=" * 50)
    print("Module 03 — CMD vs ENTRYPOINT argument inspector")
    print("=" * 50)

    # sys.argv[0] is always the script name — not an argument you passed.
    print(f"\nScript name  (sys.argv[0]): {sys.argv[0]}")

    # sys.argv[1:] contains the arguments passed after the script name.
    # In a Docker context these come from CMD and/or docker run arguments.
    if len(sys.argv) > 1:
        print(f"Arguments    (sys.argv[1:]): {sys.argv[1:]}")
        print(f"\nFull sys.argv: {sys.argv}")
    else:
        print("Arguments    (sys.argv[1:]): (none — no extra arguments were passed)")
        print(f"\nFull sys.argv: {sys.argv}")

    # Print the total count so it is easy to verify expected argument counts.
    print(f"\nTotal argument count (including script name): {len(sys.argv)}")
    print("=" * 50)


# Standard Python entry point guard.
# Only execute main() when this script is run directly, not when imported.
if __name__ == "__main__":
    main()
