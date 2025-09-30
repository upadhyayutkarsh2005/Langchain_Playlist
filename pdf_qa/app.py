# frontend.py

import streamlit as st
import requests

st.set_page_config(page_title="📄 PDF Q&A Bot (Gemini)", layout="wide")

st.title("📄 PDF Q&A Bot (Gemini)")

backend_url = "http://127.0.0.1:8000/ask-pdf/"

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    query = st.text_input("Ask a question about the PDF:")

    if st.button("Get Answer"):
        if query.strip() == "":
            st.warning("Please enter a question.")
        else:
            with st.spinner("Thinking with Gemini..."):
                files = {"file": uploaded_file}
                data = {"query": query}
                response = requests.post(backend_url, files=files, data=data)

                if response.status_code == 200:
                    st.success(response.json()["answer"])
                else:
                    st.error("Error communicating with backend.")