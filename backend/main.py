from fastapi import FastAPI, Request
from fastapi.responses import Response
from backend.chatbot import get_chatbot_response
from fastapi.responses import StreamingResponse
from io import BytesIO
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import os
import uvicorn

app = FastAPI(title="Personal Finance Chatbot API")

# List of allowed origins
origins = [
    # Your Vercel frontend
    "https://expence-tracker1-zeta.vercel.app",
    "https://expence-tracker1.vercel.app",
    
    # Development origins
    "http://localhost:8000",
    "http://localhost:3000",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:3000",
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# ADD THIS: Handler for HEAD requests (required by Render health check)
@app.api_route("/", methods=["GET", "HEAD"])
async def root(request: Request):
    if request.method == "HEAD":
        return Response(status_code=200)
    return {"message": "Welcome to the Personal Finance Chatbot API!"}

# ADD THIS: Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running"}

# Remove the old @app.get("/") and replace with the one above

# Update your chatbot endpoint
class ChatbotRequest(BaseModel):
    user_input: str

@app.post("/chatbot/{user_id}")
async def chatbot_interaction(user_id: str, request: ChatbotRequest):
    response = get_chatbot_response(user_id, request.user_input)
    return {"response": response}

# fetch memory for user_id
@app.get("/memory/{user_id}")
async def get_memory(user_id: str):
    from backend.memory import fetch_memories_by_user
    memories = fetch_memories_by_user(user_id)
    return {"memories": memories}

# fetch all expenses
@app.get("/expenses")
async def get_all_expenses(user_id: str):
    from backend.expense import fetch_expense
    expenses = fetch_expense(user_id)
    return {"expenses": expenses}

@app.get("/visuals/daily_spending/{user_id}")
async def get_daily_spending_visual(user_id: int):
    from backend.expense import fetch_daily_spending
    from backend.visuals import plot_daily_spending

    # Fetch data
    data = fetch_daily_spending(user_id)
    dates = [row[0] for row in data]
    amounts = [row[1] for row in data]

    # Generate PIL Image
    img = plot_daily_spending(dates, amounts)

    # Convert PIL → bytes
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return StreamingResponse(buffer, media_type="image/png")

# ADD THIS: Server startup for Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(app, host="0.0.0.0", port=port)
