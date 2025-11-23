from dotenv import load_dotenv
from fastapi import FastAPI
from query import ask_question

load_dotenv()

app = FastAPI(title="Personal AI Agent")

@app.post("/query")
def query_agent(question: str):
    answer = ask_question(question)
    return {"answer": answer}

@app.get("/")
def home():
    return {"message": "AI agent is running!"}
