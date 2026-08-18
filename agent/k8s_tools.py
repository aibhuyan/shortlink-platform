import subprocess

from langchain_core.tools import tool


def _kubectl(args: list[str]) -> str:
    """Run a kubectl command and return its output (or an error string)."""
    result = subprocess.run(
        ["kubectl", *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"Error running kubectl {' '.join(args)}:\n{result.stderr.strip()}"
    return result.stdout.strip()


@tool
def list_pods(namespace: str = "shortlink") -> str:
    """List the pods in a Kubernetes namespace, with their status and restart count.

    Args:
        namespace: the Kubernetes namespace to inspect (default: shortlink).
    """
    output = _kubectl(["get", "pods", "-n", namespace, "--no-headers"])
    return output or f"No pods found in namespace '{namespace}'."
