import streamlit as st
import requests

st.set_page_config(page_title="TailorTalk", page_icon="🤖")
st.title("TailorTalk 🤖📅")
st.write("Talk to me to book a meeting on your calendar!")

# ✅ Initialize state if not already
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "user_input": "",
        "intent": "",
        "date": "",
        "time": "",
        "confirmed": False,
        "reply": ""
    }

# ✅ Chat input box
user_input = st.chat_input("Ask me to book something...")
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    st.chat_message("user").write(user_input)

    # ✅ Update state with user input
    st.session_state.agent_state["user_input"] = user_input

    # ✅ Send full state to backend
    response = requests.post("http://127.0.0.1:8000/chat", json=st.session_state.agent_state)
    new_state = response.json()

    # ✅ Save updated state
    st.session_state.agent_state = new_state
    reply = new_state.get("reply", "Sorry, I didn't get that.")

    st.session_state.chat_history.append(("assistant", reply))
    st.chat_message("assistant").write(reply)

# ✅ Display chat history
for role, msg in st.session_state.chat_history:
    st.chat_message(role).write(msg)
