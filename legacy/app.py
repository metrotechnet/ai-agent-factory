from dotenv import load_dotenv
from shared.core.base_agent import create_agent
import os

load_dotenv()

# Get agent name from environment or default to ben-nutritionist
agent_name = os.getenv("AGENT_NAME", "ben-nutritionist")

# Create the appropriate agent instance
agent = create_agent(agent_name)
app = agent.app

class QueryRequest(BaseModel):
    question: str
    language: str = "fr"
    timezone: str = "UTC"
    locale: str = "fr-FR"

@app.post("/query")
async def query_agent(request: QueryRequest):
    def generate():
        for chunk in ask_question_stream(
            request.question, 
            language=request.language,
            timezone=request.timezone,
            locale=request.locale
        ):
            yield f"data: {json.dumps({'chunk': chunk})}\n\n"
    
    return StreamingResponse(
        generate(), 
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
def health():
    return {
        "service": "ben-nutritionist-agent",
        "status": "healthy", 
        "version": "2.0.0",
        "features": ["nutrition_ai", "chromadb", "multilingual"]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
