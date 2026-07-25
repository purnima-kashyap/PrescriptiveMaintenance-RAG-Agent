from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3.1",
    temperature=0
)

def generate_response(prompt: str) -> str:
    response = llm.invoke(prompt)
    return response.content