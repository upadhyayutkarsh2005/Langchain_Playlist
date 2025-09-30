from fastapi import FastAPI
from pydantic import BaseModel
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory

# Import Gemini integration
from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv

# Load env
load_dotenv()
google_api_key = os.getenv("GOOGLE_API_KEY")

#langsmith tracing
os.environ["LANGCHAIN_TRACING_V2"] = "true"

os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")

# Initialize FastAPI
app = FastAPI()

# LLM using Gemini / Google GenAI
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-pro",    # or another Gemini model (e.g. "gemini-flash", etc.)
    google_api_key=google_api_key,
    temperature=0
)

# Prompt
template = """
You are a friendly chatbot having a conversation with a human.
{chat_history}
Human: {human_input}
AI:"""

prompt = PromptTemplate(
    input_variables=["chat_history", "human_input"],
    template=template
)

# Memory
memory = ConversationBufferMemory(memory_key="chat_history")

# Chain
chatbot = LLMChain(
    llm=llm,
    prompt=prompt,
    memory=memory,
    verbose=True
)

# Request schema
