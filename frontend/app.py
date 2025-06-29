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
