```markdown
# 🧠 TailorTalk — AI Meeting Scheduler (LangGraph + FastAPI + Streamlit Ready)

TailorTalk is a conversational AI assistant that helps users **book, cancel, list, or reschedule meetings** using natural language. Instead of connecting to a real calendar service, it stores all meetings in a local `calendar_data.json` file — making it **lightweight, easy to demo, and fast to deploy**.

---

## ⚙️ Features

✅ Understand natural language  
✅ Book meetings with date/time  
✅ Cancel or reschedule existing bookings  
✅ List all upcoming meetings  
✅ Works offline (JSON-based calendar store)  
✅ Ready for Streamlit or Google Calendar integration

---

## 🛠 Tech Stack

- **LangGraph** (AI State Machine)  
- **LangChain + Together AI** (LLM-powered intent extraction)  
- **FastAPI** (API backend)  
- **Streamlit** (chat UI optional)  
- **JSON** (meeting storage)

---

## 🚀 How It Works

1. The user types something like:
```

Book a meeting between 3 to 5 PM on July 10

```
2. The system:
- Detects intent (`book_meeting`)
- Parses date & time
- Adds the booking to `calendar_data.json`
- Replies with confirmation ✅

---

## 📁 Project Structure

```

tailorTalk/
│
├── backend/
│   ├── main.py                  # FastAPI app
│   ├── agent.py                 # LangGraph logic + LLM prompts
│   ├── calendar\_data.json       # Local storage for bookings
│   └── requirements.txt

````

---

## 🧪 Example Queries

```bash
POST /chat
{
  "user_input": "Do I have anything scheduled for Friday?"
}
````

```json
📅 You're available on June 28.
```

```bash
POST /chat
{
  "user_input": "Reschedule my meeting from July 1 5pm to July 3 4pm"
}
```

```json
🔁 Your meeting has been rescheduled to July 3 at 4pm.
```

---

## 🖥 Run Locally

1. Clone the repo:

   ```bash
   git clone https://github.com/your-username/tailorTalk.git
   cd tailorTalk/backend
   ```

2. Create virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Run the server:

   ```bash
   uvicorn main:app --reload
   ```

4. Hit the endpoint:

   ```
   http://localhost:8000
   ```

---

## ✅ Sample calendar\_data.json

```json
{
  "bookings": [
    "July 7 at 3pm",
    "July 8 at 10am"
  ]
}
```

---

## 🎯 Submission Instructions

If you're submitting this for an assignment or challenge:

* Deploy with Streamlit (optional)
* Push your code to GitHub
* Share the GitHub repo or Streamlit link

---

## 📬 Contact

For questions or improvements, feel free to open issues or submit pull requests 🙌

```
