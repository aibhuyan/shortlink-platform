from langchain_core.messages import HumanMessage
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from k8s_tools import list_pods, describe_pod, get_pod_logs, get_events

llm = ChatOllama(model="qwen3.5:2b", temperature=0.0, num_ctx=8192)

agent = create_agent(
    llm,
    tools=[list_pods, describe_pod, get_pod_logs, get_events],
    system_prompt=(
        "You are a Kubernetes operations assistant for the 'shortlink' namespace. "
        "Use the tools to inspect the cluster before answering: list_pods to see pods, "
        "describe_pod and get_pod_logs to diagnose a failing pod, get_events for warnings. "
        "Base every answer ONLY on tool output — never invent pod names, statuses, or logs. "
         "Use the fewest tools necessary — for a failing pod, its logs usually reveal the cause. "
        "After gathering evidence, ALWAYS end with a short answer explaining the cause; "
        "never stop after a tool call without answering."
    ),
)


def run(question: str) -> None:
    result = agent.invoke({"messages": [("user", question)]})
    # Show which tools the agent called, so we can see its reasoning
    for message in result["messages"]:
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
