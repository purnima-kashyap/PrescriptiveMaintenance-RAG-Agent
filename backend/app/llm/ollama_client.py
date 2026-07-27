import asyncio
from langchain_ollama import ChatOllama

llm = ChatOllama(
     model="llama3.1",
    temperature=0,
    num_predict=1500,
)


async def generate_response_async(prompt: str) -> str:
    """
    Async-safe LLM call. Offloads the blocking Ollama .invoke() call to a
    background thread so it doesn't freeze the FastAPI event loop while
    the model generates a response.
    """
    response = await asyncio.to_thread(llm.invoke, prompt)
    return response.content