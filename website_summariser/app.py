# frontend.py

import streamlit as st
import requests

st.set_page_config(page_title="🌐 Website Summarizer", layout="centered")
st.title("🌐 Website Summarizer (Gemini)")

backend_url = "http://127.0.0.1:8000/summarize/"

url = st.text_input("Enter website URL:")

if st.button("Summarize Website"):
    if url.strip() == "":
        st.warning("Please enter a valid URL")
    else:
        with st.spinner("Summarizing with Gemini..."):
            response = requests.post(backend_url, data={"url": url})
            if response.status_code == 200:
                st.success(response.json()["summary"])
            else:
                st.error("Error communicating with backend")