from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent
from backend.memory import insert_memory, fetch_memories_by_user, clear_memories_by_user
from backend.expense import (
    insert_expense,
    fetch_expenses,
    fetch_expenses_by_category,
    fetch_total_expenses_between_dates,
    fetch_expenses_between_dates
)
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo   # VERY IMPORTANT

load_dotenv()

 

def get_today_ist():
    ist_offset = timedelta(hours=5, minutes=30)
    ist_time = datetime.utcnow() + ist_offset
    return ist_time.strftime("%Y-%m-%d")

today_ist = get_today_ist()


# Initialize LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.4,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

# Tools
tools = [
    insert_expense,
    fetch_expenses,
    fetch_expenses_by_category,
    fetch_total_expenses_between_dates,
    fetch_expenses_between_dates
]

# Create agent
chatbot_agent = create_agent(llm, tools=tools)


def get_chatbot_response(user_id, user_input):

    # Load previous memory
    previous_memories = fetch_memories_by_user(user_id)

    # ----- SYSTEM PROMPT (CORRECTED + SHORT) -----
    system_prompt = f"""
You are an Expense Manager AI Agent.

Today's date (IST): {today_ist}
user_id: {user_id}
Rules:
1. When adding an expense:
   - If the user gives no date OR says "today", ALWAYS use {today_ist}.
   - Infer category automatically from description (e.g., T-shirt → clothes/shopping).
   - Convert “rs”, "₹", "INR", or “0.5k” → numeric amount.
   - Create a short description if missing.
   - NEVER ask follow-up questions for date or category.

2. When querying expense history:
   - Interpret natural dates: "yesterday", "this month", "last year", "June 2024" etc.
   - Convert to YYYY-MM-DD internally.

3. ALWAYS call tools using EXACT argument names:
   - insert_expense(date, category, amount, description)
   - fetch_expenses()
   - fetch_expenses_by_category(category)
   - fetch_total_expenses_between_dates(start_date, end_date)
   - fetch_expenses_between_dates(start_date, end_date)

Return only:
- A tool call when required
- Or plain text if no tool needed.
"""

    # ----------------------------------------------

    # Build message list
    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add memory
    for mem in previous_memories:
        messages.append({"role": mem[2], "content": mem[3]})

    # Add user message
    messages.append({"role": "user", "content": user_input})

    # Save user input to memory
    insert_memory(user_id, "user", user_input)

    # Invoke agent
    response = chatbot_agent.invoke({"messages": messages})

    # Extract output
    bot_response = response["messages"][-1].content

    # Save bot message
    insert_memory(user_id, "assistant", str(bot_response))

    return bot_response
