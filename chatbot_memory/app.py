import streamlit as st
import requests

# FastAPI backend URL
API_URL = "http://127.0.0.1:8000/chat"

st.set_page_config(page_title="Chatbot with Memory", page_icon="🤖", layout="centered")
st.title("🤖 Chatbot with Memory")
st.markdown("This chatbot remembers your conversation history! 🚀")

# Initialize session state for messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").markdown(msg["content"])
    else:
        st.chat_message("assistant").markdown(msg["content"])

# User input
if user_input := st.chat_input("Type your message..."):
    # Show user message
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # Send request to FastAPI backend
        res = requests.post(API_URL, json={"message": user_input})
        data = res.json()
        bot_response = data.get("response", "⚠️ Error: No response from backend.")
    except Exception as e:
        bot_response = f"❌ Error connecting to backend: {e}"

    # Show bot response
    st.chat_message("assistant").markdown(bot_response)
    st.session_state.messages.append({"role": "assistant", "content": bot_response})