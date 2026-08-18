from datetime import datetime

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent

from k8s_tools import list_pods


@tool
def get_current_time() -> str:
    """Return the current local date and time as YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


llm = ChatOllama(model="qwen3.5:2b", temperature=0.0)
agent = create_agent(
    llm,
    tools=[get_current_time, list_pods],
    system_prompt=(
        "You are a Kubernetes operations assistant. "
        "Use the provided tools to inspect the cluster before answering. "
        "Base your answer only on the tool output — never invent pod names or statuses. "
        "Answer concisely."
    ),
)


def main() -> None:
    result = agent.invoke(
        {"messages": [("user", "What pods are running in the shortlink namespace, and are any unhealthy?")]}
    )
    # Print the whole conversation so we can see the tool call and result
    for message in result["messages"]:
        message.pretty_print()


if __name__ == "__main__":
    main()
