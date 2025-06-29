import streamlit as st
from agent import generate_reply_from_agent  # ✅ You’re using local agent.py

st.set_page_config(page_title="TailorTalk", page_icon="🤖")
st.title("TailorTalk 🤖📅")
st.write("Talk to me to book a meeting on your calendar!")

# ✅ Initialize state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "user_input": "",
        "intent": "",
        "date": "",
        "time": "",
        "confirmed": False,
        "reply": "",
        "bookings": []
    }
# ✅ Show welcome message once per session

if "welcome_shown" not in st.session_state:
    welcome_message = """👋 Welcome to TailorTalk! I'm your meeting assistant.

You can say things like:
- "Book a meeting on 26 Dec at 2pm"
- "Cancel or delete the meeting on Dec 26"
- "List all my meetings"
- "Reschedule my meet on Dec 26 to Dec 27 at 6pm"
- "Am I free on Dec 26?"
- "Suggest me any free time"

Let me know how I can help you today!"""
    st.session_state.chat_history.append(("assistant", welcome_message))
    st.session_state.welcome_shown = True

# ✅ Chat input box
user_input = st.chat_input("Ask me to book something...")
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").write(user_input)

    st.session_state.agent_state["user_input"] = user_input

    # ✅ Call agent directly
    new_state = generate_reply_from_agent(st.session_state.agent_state)

    st.session_state.agent_state = new_state
    reply = new_state.get("reply", "Sorry, I didn't get that.")

    st.session_state.chat_history.append(("assistant", reply))
    st.chat_message("assistant").write(reply)

# ✅ Show history
for role, msg in st.session_state.chat_history:
    st.chat_message(role).write(msg)
