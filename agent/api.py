import os

from fastapi import FastAPI
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain_openai import AzureChatOpenAI

from k8s_tools import list_pods, describe_pod, get_pod_logs, get_events

# Model: Azure OpenAI (gpt-4.1-mini). Config comes from env / the mounted Secret.
llm = AzureChatOpenAI(
    azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
    api_key=os.environ["AZURE_OPENAI_API_KEY"],
    azure_deployment=os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini"),
    api_version=os.environ.get("OPENAI_API_VERSION", "2024-10-21"),
    temperature=0,
)

# Read-only diagnostics only (an HTTP service has no interactive y/N approval for writes).
agent = create_agent(
    llm,
    tools=[list_pods, describe_pod, get_pod_logs, get_events],
    system_prompt=(
        "You are a read-only Kubernetes operations assistant for the 'shortlink' namespace. "
        "Use the tools to inspect the cluster and answer based only on real tool output. "
        "Never invent pod names, statuses, or logs. Be concise and practical."
    ),
)

app = FastAPI(title="Shortlink AI Ops Agent")


class Ask(BaseModel):
    question: str


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/ask")
def ask(body: Ask) -> dict:
    result = agent.invoke({"messages": [("user", body.question)]})
    messages = result["messages"]
    tools_used = [
        call["name"]
        for m in messages
        for call in getattr(m, "tool_calls", None) or []
    ]
    return {"answer": messages[-1].content, "tools_used": tools_used}
