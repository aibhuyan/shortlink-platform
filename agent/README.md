# Shortlink AI Ops Agent

A natural-language **Kubernetes operations agent** for the shortlink platform, built with **LangGraph** and a **local LLM via Ollama**. It inspects the cluster, diagnoses failures, queries metrics, and can take guarded actions — and it exposes **its own metrics** to Grafana (LLMOps).

> "The model decides; the harness executes, constrains, and recovers." This agent *is* a small harness around a local model.

## What it can do

**Read-only diagnostics** (safe):
- `list_pods`, `describe_pod`, `get_pod_logs`, `get_events` — inspect and diagnose.
- `query_prometheus(promql)` — ask about request rate, latency, errors.

**Guarded writes** (human-in-the-loop — each asks for `y/N` approval before running):
- `scale_deployment`, `restart_deployment`.

Plus: **conversation memory** (follow-up questions work) and **self-metrics** pushed to Prometheus/Grafana.

## Architecture

```
you → agent (LangGraph ReAct loop) → tools (kubectl / Prometheus API) → cluster
                     │
         local model via Ollama (qwen)
                     │
     pushes agent_* metrics → Pushgateway → Prometheus → Grafana
```

## Prerequisites

- **Ollama** running with a tool-calling model: `ollama pull qwen3.5:2b` (a small model; see caveats below).
- A **kind cluster** with the app deployed and monitoring installed:
  ```bash
  kind create cluster --name shortlink
  docker compose build
  kind load docker-image shortlink-platform-backend:latest --name shortlink
  kind load docker-image shortlink-platform-frontend:latest --name shortlink
  helm install shortlink chart -n shortlink --create-namespace --set postgres.password=devpass
  helm install monitoring prometheus-community/kube-prometheus-stack -n monitoring --create-namespace --set grafana.adminPassword=admin
  helm upgrade shortlink chart -n shortlink --reuse-values --set serviceMonitor.enabled=true
  helm install pushgateway prometheus-community/prometheus-pushgateway -n monitoring --set serviceMonitor.enabled=true --set serviceMonitor.additionalLabels.release=monitoring
  ```

## Run it

Port-forwards (separate terminals) — needed for the Prometheus tool and metrics push:
```bash
kubectl port-forward -n monitoring svc/monitoring-kube-prometheus-prometheus 9090:9090   # query_prometheus
kubectl port-forward -n monitoring svc/pushgateway-prometheus-pushgateway 9091:9091       # agent self-metrics
```

Then:
```bash
uv run python agent.py
```
Ask things like:
- `What pods are running in shortlink?`
- `Why is the migrate pod in Error?`
- `What is the request rate to the backend?`
- `Scale the backend deployment to 3 replicas.`  ← will ask for approval

## The Grafana dashboard

Import `grafana-agent-dashboard.json` (Grafana → Dashboards → New → Import) to see the agent's own activity: questions answered, average answer time, and tool-call counts/rate.

## Notes on the small model

A ~2B local model is used for privacy/cost. It's marginal at multi-step tool-calling, so the harness adds guardrails:
- `temperature=0` and a tight system prompt,
- `num_ctx=8192` and truncated tool output (context management),
- a **tool-less fallback** that forces a final answer when the model loops.

The model is a one-line swap in LangChain (`ChatOllama` → `AzureChatOpenAI` / a bigger Ollama model) for more reliability.

## Files

- `agent.py` — the agent (model, tools, memory, loop, metrics).
- `k8s_tools.py` — kubectl-based read + guarded-write tools.
- `prom_tools.py` — the Prometheus query tool.
- `metrics.py` — pushes the agent's own metrics to the Pushgateway.
- `grafana-agent-dashboard.json` — the LLMOps dashboard.
