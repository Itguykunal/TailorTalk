from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .agent import generate_reply_from_agent

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔁 Store session in memory (demo only, use Redis/DB in production)
session_state = {
    "user_input": "",
    "intent": "",
    "date": "",
    "time": "",
    "confirmed": False,
    "reply": ""
}

class Message(BaseModel):
    user_input: str

@app.post("/chat")
def chat(message: Message):
    session_state["user_input"] = message.user_input
    session_state["reply"] = ""  # Clear old reply
    updated_state = generate_reply_from_agent(session_state)
    
    # Update session_state with latest info
    for k in ["intent", "date", "time", "confirmed", "reply"]:
        session_state[k] = updated_state.get(k, session_state[k])
        
    return {"reply": session_state["reply"]}

@app.get("/")
def read_root():
    return {"message": "TailorTalk API is running!"}
