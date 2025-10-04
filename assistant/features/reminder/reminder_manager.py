# features/reminder/service.py

import os
import json
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from email.mime.text import MIMEText
import base64
import asyncio
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_google_genai import ChatGoogleGenerativeAI
from features.reminder.schema import SessionLocal, Reminder

# Scheduler
scheduler = BackgroundScheduler()
scheduler.start()

# LLM Setup
llm = ChatGoogleGenerativeAI(model="gemini-pro-latest", temperature=0)

reminder_prompt = PromptTemplate(
    input_variables=["task_text"],
    template="""
Extract reminder from text. Return JSON strictly like:
{{
  "task": "...",
  "datetime": "YYYY-MM-DD HH:MM"
}}

Important: If no year is specified, assume the current year (2025). If the date would be in the past, use the next occurrence of that date.

Current date: {current_date}
User input: {task_text}
"""
)
def add_reminder_logic(text: str):
    session = SessionLocal()
    try:
        current_date = datetime.now().strftime("%Y-%m-%d")
        parsed = reminder_chain.invoke({
            "task_text": text,
            "current_date": current_date
        })
    except Exception as e:
        print(f"Error in add_reminder_logic: {e}")
reminder_chain = LLMChain(llm=llm, prompt=reminder_prompt)

# WebSocket Clients
clients = []


async def reminder_ws(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        clients.remove(websocket)


async def push_notification(message: str):
    """Send popup notification to all connected clients"""
    for client in clients:
        try:
            await client.send_text(message)
        except:
            pass


# Gmail Sender
def send_gmail(task: str):
    try:
        creds = Credentials.from_authorized_user_file("/Users/utkarshupadhyay/Computer Science/Langchain/assistant/data/google_token.json")
        service = build("gmail", "v1", credentials=creds)

        message = MIMEText(f"Reminder: {task}")
        message["to"] = os.getenv("MY_EMAIL")  # configure your email in .env
        message["subject"] = "⏰ Reminder Alert"

        raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
        service.users().messages().send(userId="me", body={"raw": raw}).execute()
        print(f"📧 Gmail sent: {task}")
    except Exception as e:
        print("Gmail send failed:", e)


# Reminder Trigger
def trigger_reminder(reminder_id: int, task: str):
    print(f"⏰ Reminder Triggered! Task: {task} (ID: {reminder_id})")
    send_gmail(task)
    asyncio.run(push_notification(f"Reminder: {task}"))

'''
# Add Reminder Logic
def add_reminder_logic(text: str):
    session = SessionLocal()
    parsed = reminder_chain.run(task_text=text)
    if parsed.strip().startswith("```"):
        parsed = parsed.strip().split("```")[1]
    # Remove optional 'json' after ```
    if parsed.strip().startswith("json"):
        parsed = parsed.strip()[4:]
    parsed = parsed.strip()

    try:
        data = json.loads(parsed)
        task = data["task"]
        remind_at = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M")
        if remind_at <= datetime.now():
            raise HTTPException(status_code=400, detail="Reminder time must be in the future.")
        
    except Exception:
        raise HTTPException(status_code=400, detail=f"Failed to parse reminder: {parsed}")

    db_reminder = Reminder(task=task, remind_at=remind_at)
    session.add(db_reminder)
    session.commit()
    session.refresh(db_reminder)

    scheduler.add_job(
        trigger_reminder,
        "date",
        run_date=remind_at,
        args=[db_reminder.id, task],
        id=f"reminder_{db_reminder.id}"
    )

    return db_reminder '''
    
    
def add_reminder_logic(text: str):
    session = SessionLocal()
    try:
        parsed = reminder_chain.invoke({"task_text": text ,"current_date": datetime.now().strftime("%Y-%m-%d")})
        
        # If parsed is a dict, extract the text
        if isinstance(parsed, dict):
            parsed = parsed.get("text", "")
        
        print(f"DEBUG: Raw LLM output: {repr(parsed)}")
        
        # Clean markdown if present
        if parsed.strip().startswith("```"):
            lines = parsed.strip().split("```")
            if len(lines) >= 2:
                parsed = lines[1]
                # Remove optional 'json' after ```
                if parsed.strip().startswith("json"):
                    parsed = parsed.strip()[4:]
        
        parsed = parsed.strip()
        print(f"DEBUG: After markdown cleaning: {repr(parsed)}")
        
        # More comprehensive quote replacement
        import re
        parsed = re.sub(r'["""]', '"', parsed)
        parsed = re.sub(r"[''']", "'", parsed)
        
        print(f"DEBUG: After quote cleaning: {repr(parsed)}")
        
        # Try to parse JSON
        data = json.loads(parsed)
        task = data["task"]
        remind_at = datetime.strptime(data["datetime"], "%Y-%m-%d %H:%M")
        
        print(f"DEBUG: Parsed datetime: {remind_at}")
        print(f"DEBUG: Current time: {datetime.now()}")
        
        # Check if reminder time is in the future
        if remind_at <= datetime.now():
            raise HTTPException(status_code=400, detail="Reminder time must be in the future.")
            
        db_reminder = Reminder(task=task, remind_at=remind_at)
        session.add(db_reminder)
        session.commit()
        session.refresh(db_reminder)

        scheduler.add_job(
            trigger_reminder,
            "date",
            run_date=remind_at,
            args=[db_reminder.id, task],
            id=f"reminder_{db_reminder.id}"
        )
        
        return db_reminder
        
    except HTTPException:
        # Re-raise HTTPException without wrapping it
        raise
    except json.JSONDecodeError as e:
        print(f"DEBUG: JSON decode error: {e}")
        print(f"DEBUG: Problematic text: {repr(parsed)}")
        raise HTTPException(status_code=400, detail=f"Failed to parse reminder JSON: {parsed}")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid datetime format: {e}")
    except Exception as e:
        print(f"DEBUG: Unexpected error: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to parse reminder: {str(e)}")
    finally:
        session.close()


def list_reminders_logic():
    session = SessionLocal()
    return session.query(Reminder).all()