import subprocess

from langchain_core.tools import tool

MAX_OUTPUT_CHARS = 2000  # keep tool output within the small model's context


def _kubectl(args: list[str]) -> str:
    """Run a read-only kubectl command and return its (possibly truncated) output."""
    result = subprocess.run(
        ["kubectl", *args],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return f"Error running kubectl {' '.join(args)}:\n{result.stderr.strip()}"
    out = result.stdout.strip()
    if len(out) > MAX_OUTPUT_CHARS:
        out = out[:MAX_OUTPUT_CHARS] + "\n... (output truncated)"
    return out


@tool
def list_pods(namespace: str = "shortlink") -> str:
    """List the pods in a Kubernetes namespace, with status, restarts, and age.

    Args:
        namespace: the Kubernetes namespace to inspect (default: shortlink).
    """
    output = _kubectl(["get", "pods", "-n", namespace, "--no-headers"])
    return output or f"No pods found in namespace '{namespace}'."


@tool
def describe_pod(pod: str, namespace: str = "shortlink") -> str:
    """Describe a pod (status, containers, and recent events). Use this to diagnose why a pod is failing.

    Args:
        pod: the exact pod name (from list_pods).
        namespace: the namespace (default: shortlink).
    """
    return _kubectl(["describe", "pod", pod, "-n", namespace])


@tool
def get_pod_logs(pod: str, namespace: str = "shortlink", tail: int = 50) -> str:
    """Get the most recent log lines from a pod. Use this to see application errors.

    Args:
        pod: the exact pod name (from list_pods).
        namespace: the namespace (default: shortlink).
        tail: how many recent lines to return (default: 50).
    """
    return _kubectl(["logs", pod, "-n", namespace, "--tail", str(tail)])


@tool
def get_events(namespace: str = "shortlink") -> str:
    """List recent Kubernetes events in a namespace (warnings, restarts, scheduling problems).

    Args:
        namespace: the namespace (default: shortlink).
    """
    output = _kubectl(["get", "events", "-n", namespace, "--sort-by=.lastTimestamp"])
    return output or f"No events in namespace '{namespace}'."


def _confirm(action: str) -> bool:
    """Ask the human to approve a write action before it runs."""
    print(f"\n  ⚠️  The agent wants to: {action}")
    reply = input("     Approve? [y/N] ").strip().lower()
    return reply in {"y", "yes"}


@tool
def scale_deployment(deployment: str, replicas: int, namespace: str = "shortlink") -> str:
    """Scale a Deployment to a number of replicas. Requires human approval before it runs.

    Args:
        deployment: the Deployment name (e.g. backend, frontend).
        replicas: the desired number of replicas.
        namespace: the namespace (default: shortlink).
    """
    if not _confirm(f"scale deployment/{deployment} to {replicas} replicas in '{namespace}'"):
        return "Action cancelled by the user — nothing was changed."
    return _kubectl(["scale", "deployment", deployment, f"--replicas={replicas}", "-n", namespace])


@tool
def restart_deployment(deployment: str, namespace: str = "shortlink") -> str:
    """Do a rolling restart of a Deployment's pods. Requires human approval before it runs.

    Args:
        deployment: the Deployment name (e.g. backend, frontend).
        namespace: the namespace (default: shortlink).
    """
    if not _confirm(f"restart deployment/{deployment} in '{namespace}'"):
        return "Action cancelled by the user — nothing was changed."
    return _kubectl(["rollout", "restart", "deployment", deployment, "-n", namespace])
