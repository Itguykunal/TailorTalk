from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain.chat_models import ChatOpenAI
from langchain_core.runnables import RunnableLambda
import json
import re
import dateparser
from datetime import datetime
from dateparser.search import search_dates

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), "calendar_data.json")

def load_bookings():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f).get("bookings", [])

def save_bookings(bookings):
    with open(DATA_FILE, "w") as f:
        json.dump({"bookings": bookings}, f, indent=2)

MONTHS_MAP = {
    "jan": "January", "feb": "February", "mar": "March", "apr": "April",
    "may": "May", "jun": "June", "jul": "July", "aug": "August",
    "sep": "September", "oct": "October", "nov": "November", "dec": "December"
}

def normalize_date(date_str: str) -> str:
    date_str = date_str.lower().strip()
    # Handle both "12 aug" and "aug 12"
    tokens = date_str.replace(",", "").split()
    if len(tokens) == 2:
        # Case: "12 aug" or "aug 12"
        if tokens[0].isdigit() and tokens[1][:3] in MONTHS_MAP:
            return f"{MONTHS_MAP[tokens[1][:3]]} {int(tokens[0])}"
        elif tokens[1].isdigit() and tokens[0][:3] in MONTHS_MAP:
            return f"{MONTHS_MAP[tokens[0][:3]]} {int(tokens[1])}"
    return date_str.title()



# ✅ Together AI API key
together_api_key = "c8c553fd602770256bd6aaa0322003d8b515e23af2081676a2f249388c1b5a52"

# ✅ LLM setup
llm = ChatOpenAI(
    openai_api_key=together_api_key,
    base_url="https://api.together.xyz/v1",
    model="mistralai/Mixtral-8x7B-Instruct-v0.1",
    temperature=0.7
)

# ✅ LangGraph state schema
class State(TypedDict):
    user_input: str
    intent: str
    date: str
    time: str
    confirmed: bool
    reply: str
    bookings: list[str]


# 🧠 Extract structured meeting info
def llm_extract_info(state: dict):
    prompt = f"""
You are a smart AI assistant helping users schedule meetings.

So far, here's what you know:
- Intent: {state['intent']}
- Date: {state['date']}
- Time: {state['time']}

Now the user said:
"{state['user_input']}"

Your task is to extract and update ONLY the parts mentioned in this new message.

Examples of intent:
- "Do I have anything scheduled?" → check_availability
- "Is my afternoon free?" → check_availability
- "What's my availability on Friday?" → check_availability

Extract:
1. Intent — "book_meeting", "check_availability", or "none"
2. Date — full format like "June 25", "26 December", "next Friday", "tomorrow"
3. Time — clear time like "4pm", "11am", "16:00", "evening", etc.

Interpret vague phrases:
- "evening" → "6pm"
- "morning" → "10am"
- "noon" → "12pm"
- "night" → "9pm"

Return this JSON format:
{{
  "intent": "...",
  "date": "...",
  "time": "..."
}}
Use empty string ("") if a field is not provided or unclear.
Important: Only return the JSON block. Do not include any explanation before or after it.

"""

    response = llm.invoke(prompt)

    try:
        # Extract JSON from model response using regex
        json_match = re.search(r"\{.*\}", response.content, re.DOTALL)
        if json_match:
            parsed = json.loads(json_match.group())

            if parsed.get("intent"):
                state["intent"] = parsed["intent"]
            if parsed.get("date"):
                state["date"] = parsed["date"]
            if parsed.get("time"):
                state["time"] = parsed["time"]
        else:
            print("❌ No JSON found in LLM response.")
    except Exception as e:
        print("❌ Parsing failed:", e)
    return state

def llm_confirm(state: dict):
    # Normalize date if given
    if state.get("date"):
        parsed = dateparser.parse(state["date"])
        if parsed:
            state["date"] = parsed.strftime("%B %-d")

    # If both are present, confirm the booking
    if state.get("date") and state.get("time"):
        booking = f"{state['date']} at {state['time']}"
        bookings = load_bookings()
        if booking not in bookings:
          bookings.append(booking)
          save_bookings(bookings)
        state["confirmed"] = True
        state["reply"] = f"✅ Your meeting has been booked for {booking}."

        # ✅ Clear state to avoid accidental reuse
        state["intent"] = ""
        state["date"] = ""
        state["time"] = ""

    # If only date is present, ask for time
    elif state.get("date") and not state.get("time"):
        state["confirmed"] = False
        state["reply"] = f"🕒 Got the date — {state['date']}. What time would you like?"

    # If only time is present, ask for date
    elif state.get("time") and not state.get("date"):
        state["confirmed"] = False
        state["reply"] = f"📅 Got the time — {state['time']}. What date should I book it for?"

    return state

def reply(state: dict):
    import re
    user_input = state["user_input"].lower()
    bookings = load_bookings()   

        # Prevent LLM from using stale date/time in reply
    if state["confirmed"]:
        state["intent"] = ""
        state["date"] = ""
        state["time"] = ""

    # ✅ Cancel/Delete meeting
    if any(word in user_input for word in ["cancel", "delete", "remove"]) and "meeting" in user_input:
        results = search_dates(user_input)
        if results:
            parsed_date = results[0][1]
            normalized_date = parsed_date.strftime("%B %-d")
            for b in bookings:
                if normalized_date.lower() in b.lower():
                    bookings.remove(b)
                    save_bookings(bookings)
                    state["reply"] = f"🗑️ Your meeting on {b} has been canceled."
                    return state
            state["reply"] = f"❌ I couldn't find any meeting on {normalized_date} to cancel."
        else:
            state["reply"] = "Please specify the date of the meeting you'd like to cancel."
        return state

    # ✅ Reschedule meeting
    # ✅ Reschedule meeting
    if "reschedule" in user_input or "move" in user_input or "change" in user_input:
        results = search_dates(user_input)
        if results and len(results) >= 2:
            old_datetime = results[0][1]
            new_datetime = results[1][1]

            old_date = old_datetime.strftime("%B %-d")
            new_date = new_datetime.strftime("%B %-d")
            new_time = new_datetime.strftime("%-I%p").lower()

            found = False
            for b in bookings:
                if old_date.lower() in b.lower():
                    bookings.remove(b)
                    found = True
                    break

            new_booking = f"{new_date} at {new_time}"
            if new_booking not in bookings:
                bookings.append(new_booking)
                save_bookings(bookings)
            if found:
                state["reply"] = f"🔁 Your meeting has been rescheduled to {new_booking}."
            else:
                state["reply"] = f"✅ Scheduled new meeting on {new_booking} (no previous meeting found for {old_date})."

            state["date"] = new_date
            state["time"] = new_time
            state["confirmed"] = True
        else:
            state["reply"] = "Please mention both the current and new date/time clearly to reschedule."
        return state

    # ✅ List all bookings
    if any(word in user_input for word in ["list", "show", "what", "my", "all", "see"]) and \
       any(word in user_input for word in ["booking", "bookings", "meeting", "meetings", "schedule"]):
        if bookings:
            booking_list = "\n".join(f"- {b}" for b in bookings)
            state["reply"] = f"📅 Here are your scheduled meetings:\n{booking_list}"
        else:
            state["reply"] = "📭 You have no confirmed meetings yet."
        return state

    # ✅ Handle natural phrases like "next Monday afternoon", "tomorrow morning", etc.
    # ✅ Handle "tomorrow morning", "next Friday evening", etc.
    if (
        any(phrase in user_input for phrase in ["morning", "afternoon", "evening", "night", "tomorrow", "next"])
        and not state.get("confirmed")
    ):
        results = search_dates(user_input)
        if results:
            extracted_date = results[0][1].strftime("%B %-d")

            # Match vague time to specific
            if "afternoon" in user_input:
                extracted_time = "3pm"
            elif "morning" in user_input:
                extracted_time = "10am"
            elif "evening" in user_input or "night" in user_input:
                extracted_time = "6pm"
            else:
                extracted_time = ""

            # Set into state — let llm_confirm handle final logic
            state["date"] = extracted_date
            state["time"] = extracted_time
            state["intent"] = "book_meeting"
            return state

    # ✅ Check if user is asking about availability
    if state.get("intent") == "check_availability":
        raw_date = state.get("date", "").strip()
        raw_time = state.get("time", "").strip().lower()

        # ⬇️ If date is provided → normal check
        if raw_date:
            parsed_date = dateparser.parse(raw_date)
            if parsed_date:
                normalized_date = parsed_date.strftime("%B %-d").lower()
                time_conflict = False
                date_conflict = False

                for b in bookings:
                    if " at " in b:
                        b_date, b_time = b.split(" at ")
                        b_date = b_date.strip().lower()
                        b_time = b_time.strip().lower()

                        if b_date == normalized_date:
                            date_conflict = True
                            if raw_time and raw_time in b_time:
                                time_conflict = True

                if raw_time:
                    if time_conflict:
                        state["reply"] = f"❌ You already have a meeting on {parsed_date.strftime('%B %-d')} at {raw_time}."
                    else:
                        state["reply"] = f"✅ You're available on {parsed_date.strftime('%B %-d')} at {raw_time}."
                else:
                    if date_conflict:
                        state["reply"] = f"❌ You already have a meeting on {parsed_date.strftime('%B %-d')}."
                    else:
                        state["reply"] = f"✅ You're available on {parsed_date.strftime('%B %-d')}."
            else:
                state["reply"] = "I couldn't understand the date you mentioned. Can you rephrase it?"
            return state

     # ✅ Suggest slots if checking availability without a specific date
    if state.get("intent") == "check_availability" and not state.get("date").strip():
        from datetime import timedelta
        today = datetime.now()
        suggestions = []
        for i in range(1, 8):
            day = today + timedelta(days=i)
            day_str = day.strftime("%B %-d")
            if not any(day_str in b for b in bookings):
                suggestions.append(f"{day_str} at 10am")
            if len(suggestions) >= 5:
                break

        if suggestions:
            options = "\n".join(f"- {s}" for s in suggestions)
            state["reply"] = f"📆 You're free on:\n{options}\nWould you like to book one?"
        else:
            state["reply"] = "❌ You're fully booked in the next few days!"
        return state

    # ✅ Handle time ranges like "between 3 and 5pm", "from 2pm to 4pm", or "from 2 until 4pm"
    range_match = re.search(
        r"(?:between|from)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s+(?:and|to|until)\s+(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
        user_input
    )

    if range_match:
        start_hour = int(range_match.group(1))
        start_min = range_match.group(2) or "00"
        start_period = range_match.group(3) or "am"
        end_hour = int(range_match.group(4))
        end_min = range_match.group(5) or "00"
        end_period = range_match.group(6) or "pm"

        start = f"{start_hour}:{start_min} {start_period}"
        end = f"{end_hour}:{end_min} {end_period}"

        # 🔍 Get only actual date like "July 7"
        for match in search_dates(user_input):
            if match[1] > datetime.now():
                extracted_date = match[1].strftime("%B %-d")
                break
        else:
            extracted_date = None

        if extracted_date:
            booking = f"{extracted_date} at {start_hour}{start_period}"

            if booking not in bookings:
                bookings.append(booking)
                save_bookings(bookings)
                state["reply"] = f"✅ Your meeting has been booked between {start} and {end} on {extracted_date}."
                state["date"] = extracted_date
                state["time"] = f"{start_hour}{start_period}"
                state["confirmed"] = True
            else:
                state["reply"] = f"❌ You already have a meeting at {start_hour}{start_period} on {extracted_date}."
        else:
            state["reply"] = f"🗓️ Got your preferred time {start}–{end}. Please confirm the date."
        return state





    # ✅ Fallback to LLM for natural chat
    prompt = f"""
You are a friendly and concise AI assistant helping the user schedule meetings.

Known Info:
- Intent: {state['intent']}
- Date: {state['date']}
- Time: {state['time']}
- Confirmed: {state['confirmed']}
- Bookings: {load_bookings()}

The user said:
"{state['user_input']}"

Write a short, friendly, helpful reply (1–2 sentences only). Avoid repeating confirmed info.

Reply:
"""
    response = llm.invoke(prompt)
    state["reply"] = response.content.strip()
    return state

# 🌐 LangGraph setup
graph = StateGraph(State)
graph.add_node("llm_extract", RunnableLambda(llm_extract_info))
graph.add_node("llm_confirm", RunnableLambda(llm_confirm))
graph.add_node("generate_reply", RunnableLambda(reply))

graph.set_entry_point("llm_extract")
graph.add_edge("llm_extract", "llm_confirm")
graph.add_edge("llm_confirm", "generate_reply")
graph.add_edge("generate_reply", END)

agent = graph.compile()

# 🌟 Entry function (takes full state)
def generate_reply_from_agent(state: dict):
    state["bookings"] = load_bookings()  # ✅ ensure always fresh
    return agent.invoke(state)

