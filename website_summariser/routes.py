# routes.py

from fastapi import FastAPI, Form
from logic import summarize_website
from fastapi.middleware.cors import CORSMiddleware
import fastapi.middleware.cors as cors

app = FastAPI()

cors.allow_origins = ["*"]
cors.allow_credentials = True
cors.allow_methods = ["*"]
cors.allow_headers = ["*"]  

@app.post("/summarize/")
async def summarize(url: str = Form(...)):
    summary = summarize_website(url)
    return {"summary": summary}