from datetime import datetime

from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langchain.agents import create_agent


@tool
def get_current_time() -> str:
    """Return the current local date and time as YYYY-MM-DD HH:MM:SS."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


llm = ChatOllama(model="qwen3.5:2b", temperature=0.0)
agent = create_agent(
    llm,
    tools=[get_current_time],
    system_prompt=(
        "You are a concise operations assistant. "
        "Use a tool only when needed, then answer in one short factual sentence. "
        "Do not speculate or add extra reasoning."
    ),
)


def main() -> None:
    result = agent.invoke(
        {"messages": [("user", "What is the current time?")]}
    )
    # Print the whole conversation so we can see the tool call and result
    for message in result["messages"]:
        message.pretty_print()


if __name__ == "__main__":
    main()
