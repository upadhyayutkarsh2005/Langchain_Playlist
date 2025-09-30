from fastapi import FastAPI
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langserve import add_routes
import streamlit as st
import os
from dotenv import load_dotenv
load_dotenv()
from langchain_ollama import OllamaLLM
import uvicorn



os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

#langsmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
from pydantic import BaseModel

def rebuild_models(cls):
    try:
        cls.model_rebuild(force=True)
    except Exception:
        pass
    for sub in cls.__subclasses__():
        rebuild_models(sub)

# Rebuild all BaseModel subclasses recursively
rebuild_models(BaseModel)

app = FastAPI()

add_routes(
    app,
    ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7),
    path='/chat/google-genai',
    )
model = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)

llm = OllamaLLM(model="llama2:7b")

prompt1 = ChatPromptTemplate.from_template("write me an essay about {topic} with 100 words ")
prompt2=ChatPromptTemplate.from_template("write me a poem about {topic} with 100 words ")

add_routes(
    app,
    prompt1 | model,
    path='/chat/essay',
    
)

add_routes(
    app,
    prompt2 | llm,
    path='/chat/poem',

)
    
    
    
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
