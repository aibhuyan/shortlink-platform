from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver

from k8s_tools import (
    list_pods,
    describe_pod,
    get_pod_logs,
    get_events,
    scale_deployment,
    restart_deployment,
)
from prom_tools import query_prometheus

llm = ChatOllama(model="qwen3.5:2b", temperature=0.0, num_ctx=8192)

# Persists conversation state so follow-up questions have context
checkpointer = InMemorySaver()
CONFIG = {"configurable": {"thread_id": "cli-session"}}

agent = create_agent(
    llm,
    tools=[
        list_pods,
        describe_pod,
        get_pod_logs,
        get_events,
        scale_deployment,
        restart_deployment,
        query_prometheus,
    ],
    checkpointer=checkpointer,
    system_prompt=(
        "You are a Kubernetes operations assistant for the 'shortlink' namespace. "
        "Use the read tools to inspect the cluster before answering: list_pods to see pods, "
        "describe_pod and get_pod_logs to diagnose a failing pod, get_events for warnings. "
        "For metrics questions (request rate, latency, errors), use query_prometheus with a PromQL expression. "
        "Base every answer ONLY on tool output — never invent pod names, statuses, or logs. "
        "Use the fewest tools necessary — for a failing pod, its logs usually reveal the cause. "
        "To CHANGE the cluster use scale_deployment or restart_deployment, but ONLY when the "
        "user explicitly asks to scale or restart something; these ask the user to approve first. "
        "After gathering evidence, ALWAYS end with a short answer; never stop after a tool call "
        "without answering."
    ),
)


def run(question: str) -> None:
    result = agent.invoke({"messages": [("user", question)]}, CONFIG)
    messages = result["messages"]
    # Only trace the CURRENT turn: messages after the last human message
    start = max(
        (i for i, m in enumerate(messages) if isinstance(m, HumanMessage)),
        default=0,
    )
    for message in messages[start:]:
        for call in getattr(message, "tool_calls", None) or []:
            print(f"  · tool: {call['name']}({call.get('args', {})})")
    answer = result["messages"][-1].content
    if not answer:
        # Small models sometimes keep calling tools and never write a final answer.
        # Force one: re-ask the RAW model (no tools bound) to summarize the evidence.
        messages = result["messages"] + [
            HumanMessage(
                "Using only the tool results above, answer my original question "
                "in 2-3 plain sentences. Do not call any tools."
            )
        ]
        answer = llm.invoke(messages).content
    print(f"\nagent> {answer or '(no answer produced)'}\n")


def main() -> None:
    print("Kubernetes agent ready. Ask about the cluster. Type 'exit' to quit.\n")
    while True:
        try:
            question = input("you> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nbye")
            break
        if question.lower() in {"exit", "quit"}:
            break
        if not question:
            continue
        run(question)


if __name__ == "__main__":
    main()
