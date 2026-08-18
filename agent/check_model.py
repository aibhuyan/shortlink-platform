from langchain_ollama import ChatOllama

# ChatOllama connects to the local Ollama server (default http://localhost:11434)
llm = ChatOllama(model="qwen3.5:2b")

resp = llm.invoke("In one short sentence, what is Kubernetes?")
print(resp.content)
