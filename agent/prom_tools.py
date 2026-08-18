import requests
from langchain_core.tools import tool

# Requires a port-forward: kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090
PROMETHEUS_URL = "http://localhost:9090"


@tool
def query_prometheus(promql: str) -> str:
    """Run a PromQL query against Prometheus and return the result.

    Use this for metrics questions about the app. Useful metrics:
      - http_requests_total{namespace="shortlink"}  (request counter, labels: handler, method, status)
      - http_request_duration_seconds_bucket        (request latency histogram)
    Example promql for request rate:
      sum(rate(http_requests_total{namespace="shortlink"}[5m]))

    Args:
        promql: a PromQL expression.
    """
    try:
        resp = requests.get(
            f"{PROMETHEUS_URL}/api/v1/query",
            params={"query": promql},
            timeout=10,
        )
    except requests.RequestException as exc:
        return f"Error contacting Prometheus at {PROMETHEUS_URL}: {exc}"

    data = resp.json()
    if data.get("status") != "success":
        return f"Prometheus error: {data.get('error', data)}"

    results = data["data"]["result"]
    if not results:
        return "No data (empty result)."

    lines = []
    for item in results[:20]:
        metric = item.get("metric", {})
        value = item.get("value", [None, None])[1]
        labels = ", ".join(f"{k}={v}" for k, v in metric.items() if k != "__name__")
        lines.append(f"{labels or '(no labels)'} => {value}")
    return "\n".join(lines)
