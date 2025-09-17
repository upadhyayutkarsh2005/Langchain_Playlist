from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_community.llms import ollama


os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

app=FastAPI()
    title="learning langchain"
    version="0.1",
    description="learning langchain with google gemini and streamlit"

    
)
