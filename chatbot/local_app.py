from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM
import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# LangSmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# Prompt Template
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant. Please respond to the user queries."),
        ("user", "Question: {question}")
    ]
)

# Streamlit app
st.title("Chatbot with LangChain and Ollama")
input_text = st.text_input("Search the topic you want")

# Load Ollama model
llm = OllamaLLM(model="llama2:7b")  # make sure llama2 is pulled with `ollama pull llama2`

# Chain
output_parser = StrOutputParser()
chain = prompt | llm | output_parser

# Run
if input_text:
    response = chain.invoke({"question": input_text})
    st.write(response)