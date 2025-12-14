from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ADD THIS LINE
from backend.chatbot import get_chatbot_response
from fastapi.responses import StreamingResponse
from io import BytesIO
import os


app = FastAPI(title="Personal Finance Chatbot API")

# ==============================
# ADD CORS MIDDLEWARE HERE
# ==============================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://my-moneyai.vercel.app",  # Your Vercel frontend
        "http://localhost:3000",           # Local development
        "http://localhost:5500",           # Live Server default port
        "http://127.0.0.1:5500",          # Alternative localhost
        "http://localhost:8000",           # If running frontend locally
    ],
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# ==============================
# Chatbot Endpoints
# ==============================

# well come endpoint
@app.get("/")
async def welcome():
    return {"message": "Welcome to the Personal Finance Chatbot API!"}



# Define an endpoint for chatbot interaction
@app.post("/chatbot/{user_id}")
async def chatbot_interaction(user_id: str, user_input: str):
    response = get_chatbot_response(user_id, user_input)
    return {"response": response}

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
