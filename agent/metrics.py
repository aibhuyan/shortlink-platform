from prometheus_client import CollectorRegistry, Counter, Histogram, push_to_gateway

# Requires: kubectl port-forward -n monitoring svc/pushgateway-prometheus-pushgateway 9091:9091
PUSHGATEWAY = "localhost:9091"
JOB = "shortlink-agent"

registry = CollectorRegistry()

questions_total = Counter(
    "agent_questions_total", "Questions asked to the agent", registry=registry
)
tool_calls_total = Counter(
    "agent_tool_calls_total", "Tool calls made by the agent", ["tool"], registry=registry
)
turn_seconds = Histogram(
    "agent_turn_seconds", "Seconds taken to answer a question", registry=registry
)


def record(tool_names: list[str], duration: float) -> None:
    """Update the agent's metrics and push them to the Pushgateway."""
    questions_total.inc()
    for name in tool_names:
        tool_calls_total.labels(tool=name).inc()
    turn_seconds.observe(duration)
    try:
        push_to_gateway(PUSHGATEWAY, job=JOB, registry=registry)
    except Exception as exc:  # never let metrics break the agent
        print(f"  (metrics push failed: {exc})")
