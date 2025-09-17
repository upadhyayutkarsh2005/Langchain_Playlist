from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.llms import ollama
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()


#langsmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

#PROMPT TEMPLATE

prompt=ChatPromptTemplate.from_messages(
    [
        ("system","You are a helpful assistant. Please response to the user queries"),
        ("user","Question:{question}")
    ]

)


#Streamlit app

st.title("Chatbot with Langchain and Gemini")
input_text = st.text_input("Search the topic you want")

llm = ollama(model="gemma3:37b")
output_parser=StrOutputParser()
chain=prompt | llm | output_parser

if input_text:
    st.write(chain.invoke({"question":input_text}))
