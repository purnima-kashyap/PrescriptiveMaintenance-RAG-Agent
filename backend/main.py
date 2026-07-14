from fastapi import FastAPI

app = FastAPI(
    title="Prescriptive Maintenance RAG",
    version="1.0.0"
)


@app.get("/")
def home():
    return {
        "message": "Prescriptive Maintenance Backend Running"
    }