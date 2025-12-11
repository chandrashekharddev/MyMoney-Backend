from fastapi import FastAPI
from backend.chatbot import get_chatbot_response
from fastapi.responses import StreamingResponse
from io import BytesIO
from pydantic import BaseModel
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
import os


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
    
    # For testing - you can remove this in production
    "*",  # Allows all origins (for testing only)
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Allowed HTTP methods
    allow_headers=["*"],  # Allowed headers
)

# Add this to your main.py
@app.get("/test-cors")
async def test_cors():
    
    return {
        "message": "CORS test successful!",
        "cors_enabled": True,
        "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "note": "This endpoint should be accessible from your Vercel frontend"}

# ==============================
# Chatbot Endpoints
# ==============================

# well come endpoint
@app.get("/")
async def welcome():
    return {"message": "Welcome to the Personal Finance Chatbot API!"}



# Define an endpoint for chatbot interaction
class ChatbotRequest(BaseModel):
    user_input: str
# Update your endpoint
@app.post("/chatbot/{user_id}")
async def chatbot_interaction(user_id: str, request: ChatbotRequest):
    response = get_chatbot_response(user_id, request.user_input)
    return {"response":response}

# @app.post("/chatbot/{user_id}")
# async def chatbot_interaction(user_id: str, user_input: str):
#     response = get_chatbot_response(user_id, user_input)
#     return {"response": response}

# fetch memory for user_id
@app.get("/memory/{user_id}")
async def get_memory(user_id: str):
    from backend.memory import fetch_memories_by_user
    memories = fetch_memories_by_user(user_id)
    return {"memories": memories}

# fetch all expenses
@app.get("/expenses")
async def get_all_expenses(user_id:str):
    from backend.expense import fetch_expense
    expenses = fetch_expense(user_id)
    return {"expenses": expenses}

# ==============================
# Visualization Endpoints
# ==============================

# @app.get("/visuals/daily_spending/{user_id}")
# async def get_daily_spending_visual(user_id: int):
#     from backend.expense import fetch_daily_spending
#     from backend.visuals import plot_daily_spending
#     # Fetch data
#     data = fetch_daily_spending(user_id)
#     dates = [row[0] for row in data]
#     amounts = [row[1] for row in data]
#     # Generate plot
#     img = plot_daily_spending(dates, amounts)
#     # # Save to a temporary file and return the path
#     # temp_path = f"temp_daily_spending_{user_id}.png"
#     # img.save(temp_path)
#     return img

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