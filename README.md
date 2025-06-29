# 🧠 CalendarGPT — AI Meeting Scheduler (LangGraph + FastAPI + Streamlit Ready)


[![Streamlit App](https://img.shields.io/badge/Try%20App-Streamlit-green?logo=streamlit)](https://tailortalk-ady49vihq3mrhlw9xajk4v.streamlit.app/)

**[👉 Click here to try the app](https://tailortalk-ady49vihq3mrhlw9xajk4v.streamlit.app/)**


CalendarGPT is a conversational AI assistant that helps users **book, cancel, list, or reschedule meetings** using natural language. It uses a local `calendar_data.json` file instead of a real calendar — making it **lightweight, fast, and demo-friendly**.

---

## ⚙️ Features

✅ Natural language understanding  
✅ Book meetings with date/time  
✅ Cancel or reschedule meetings  
✅ List upcoming meetings  
✅ Check your availability  
✅ Suggest free time slots  
✅ Offline support (via JSON)  
✅ Streamlit-ready frontend

---

## 🛠 Tech Stack

- **LangGraph** – AI State Machine  
- **LangChain + Together AI** – LLM-based intent extraction  
- **FastAPI** – Backend API  
- **Streamlit** – Optional chat UI  
- **JSON** – Local booking storage

---

## 🚀 What Can You Say?

Examples of what CalendarGPT understands:

- `"Book a meeting on 26 Dec at 2pm"`  
- `"Delete my meeting on Dec 26"`  
- `"List all my meetings"`  
- `"Reschedule my Dec 26 meeting to Dec 27 at 6pm"`  
- `"Am I free on Dec 26?"`  
- `"Suggest me some free time this week"`  

---

## 🧠 How It Works

1. You say:

```

Book a meeting between 3 to 5 PM on July 10

```

2. CalendarGPT:
- Extracts intent (`book_meeting`)
- Parses date & time
- Adds the event to `calendar_data.json`
- Confirms your booking ✅

---

## 📁 Project Structure

```

calendarGPT/
│
├── FRONTEND/
│   ├── main.py              # FastAPI app
│   ├── agent.py             # LangGraph logic + LLM prompts
│   ├── calendar\_data.json   # Local storage for bookings
│   └── requirements.txt

````

---

## 🧪 Example Queries

### POST `/chat`
```json
{ "user_input": "Do I have anything scheduled for Friday?" }
````

✅ Response:

```json
📅 You're available on June 28.
```

---

### POST `/chat`

```json
{ "user_input": "Reschedule my meeting from July 1 5pm to July 3 4pm" }
```

✅ Response:

```json
🔁 Your meeting has been rescheduled to July 3 at 4pm.
```

---

## 🖥 Run Locally

1. Clone the repo:

   ```bash
   git clone https://github.com/your-username/calendarGPT.git
   cd calendarGPT/backend
   ```

2. Set up environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the backend server:

   ```bash
   uvicorn main:app --reload
   ```

4. Open your browser:

   ```
   http://localhost:8000
   ```

---

## ✅ Example `calendar_data.json`

```json
{
  "bookings": [
    "July 7 at 3pm",
    "July 8 at 10am"
  ]
}
```

## 📬 Contact

Got feedback or want to contribute?
Open an issue or pull request. Happy scheduling! 🙌
