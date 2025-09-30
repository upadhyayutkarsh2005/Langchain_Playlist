
from pydantic import BaseModel
from fastapi import FastAPI
from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
from logic import chatbot

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

@app.post("/chat")
def chat(req: ChatRequest):
    response = chatbot.run(human_input=req.message)
    return {"response": response}