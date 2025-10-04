# main.py
import os
from fastapi import FastAPI, HTTPException, Query , UploadFile, File , Request, Form
from fastapi.responses import JSONResponse , RedirectResponse, HTMLResponse
import uvicorn
from typing import List
from fastapi import APIRouter 

from core.llm import get_llm
from core.tools import get_web_search_tool , get_document_qa_tool
from core.agent import build_agent

from features.doc_qa.loader import save_upload, extract_text_from_pdf
from features.doc_qa.vectorstore import build_vectorstore_from_text 


from features.email_drafter.email_generator import generate_email_draft
from features.email_drafter.gmail_api import create_auth_url, fetch_and_store_token, send_message_raw, load_credentials
from features.email_drafter.utils import validate_email_fields


from features.reminder.schema import ReminderIn, ReminderOut
from features.reminder.reminder_manager import add_reminder_logic, list_reminders_logic, reminder_ws


app = FastAPI(title="Personal AI Assistant - Minimal Web Search Feature")

# Initialize at startup
llm = get_llm()
web_tool = get_web_search_tool(llm, num_results=int(os.getenv("SEARCH_NUM_RESULTS", "5")))
agent = build_agent(llm, tools=[web_tool], verbose=False)

@app.get("/search")
def search(q: str = Query(..., description="Search query")):
    try:
        response = agent.run(q)
        return {"query": q, "answer": response}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    
    
@app.post("/upload_document")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload a PDF file, extract text, build + persist a vectorstore.
    Returns a store_id which can be used for future queries.
    """
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF uploads are supported at the moment.")

    # Save uploaded file to disk
    saved_path = save_upload(await file.read(), file.filename) if False else None
    # The above won't run because save_upload expects a file-like; instead use file.file
    try:
        saved_path = save_upload(file.file, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save upload: {e}")

    # Extract text
    try:
        text = extract_text_from_pdf(saved_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No extractable text found in PDF.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text from PDF: {e}")

    # Build vectorstore (persist directory named after uploaded filename's stem)
    import uuid
    persist_name = f"{uuid.uuid4().hex}_{os.path.basename(saved_path)}"
    try:
        vectordb = build_vectorstore_from_text(text, persist_dir_name=persist_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to build vectorstore: {e}")

    return JSONResponse({"status": "ok", "store_id": persist_name})

@app.get("/doc_qa")
def doc_qa(q: str = Query(..., description="Question to ask the uploaded document"),
           store_id: str = Query(..., description="store_id returned from /upload_document")):
    """
    Query an uploaded document set. This endpoint dynamically creates a doc-specific tool and runs it.
    """
    try:
        doc_tool = get_document_qa_tool(llm, persist_dir_name=store_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Couldn't load vectorstore for store_id={store_id}: {e}")

    try:
        # If you want the agent to use tools and memory to answer, you could add the doc_tool to a new agent
        # For simplicity we call the tool directly
        answer = doc_tool.run(q)
        return {"question": q, "answer": answer, "store_id": store_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    
    
REDIRECT_URI = os.getenv("GOOGLE_OAUTH_REDIRECT_URI", "http://127.0.0.1:8000/google_oauth_callback")

@app.get("/google_auth_url")
def google_auth_url():
    """
    Returns a URL that the user should open in browser to consent to Gmail scopes.
    """
    try:
        url = create_auth_url(redirect_uri=REDIRECT_URI)
        return {"auth_url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/google_oauth_callback")
def google_oauth_callback(request: Request):
    """
    This endpoint is the redirect URI that Google will call with ?code=...
    Fast way: after user authorizes, Google redirects here. We capture the full URL and exchange for tokens.
    """
    # Build full URL including query string
    full_url = str(request.url)
    try:
        token_info = fetch_and_store_token(authorization_response_url=full_url, redirect_uri=REDIRECT_URI)
        # Redirect to a simple success page or return JSON
        return HTMLResponse("<html><body><h3>Google OAuth completed. You can close this page and return to your app.</h3></body></html>")
    except Exception as e:
        return HTMLResponse(f"<html><body><h3>OAuth failed: {e}</h3></body></html>", status_code=500)

# ------------------------------------------------------------------
# Drafting endpoint
# ------------------------------------------------------------------

@app.post("/draft_email")
def draft_email(to: str = Form(...), purpose: str = Form(...), context: str = Form(""), tone: str = Form("polite"), length: str = Form("medium")):
    """
    Returns an AI-generated draft given form fields:
    - to: recipient email (used in prompt, not validated for sending)
    - purpose: short instruction what the email should do
    - context: additional background info
    - tone: formal/polite/friendly etc.
    - length: short/medium/long
    """
    try:
        validate_email_fields({"to": to, "purpose": purpose})
        draft = generate_email_draft(recipient=to, purpose=purpose, context=context, tone=tone, length=length)
        return {"to": to, "subject": draft["subject"], "body": draft["body"], "raw": draft["raw"]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------
# Send email endpoint
# ------------------------------------------------------------------

@app.post("/send_email")
def send_email(to: str = Form(...), subject: str = Form(...), body: str = Form(...)):
    """
    Send the provided email using stored Gmail credentials (single-user).
    Make sure OAuth is completed via /google_auth_url -> consent -> callback.
    """
    try:
        validate_email_fields({"to": to, "purpose": subject})
        # Will raise if no stored credentials
        creds = load_credentials()
        if not creds:
            raise HTTPException(status_code=400, detail="No Google credentials found. Visit /google_auth_url and complete OAuth flow first.")
        resp = send_message_raw(to_email=to, subject=subject, body_text=body)
        return {"status": "sent", "gmail_response": resp}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ------------------------------------------------------------------
# Simple status endpoint to show if Google token exists
# ------------------------------------------------------------------
@app.get("/gmail_status")
def gmail_status():
    creds = load_credentials()
    return {"authenticated": bool(creds is not None)}

router = APIRouter(prefix="/reminders", tags=["Reminders"])


@app.post("/add", response_model=ReminderOut)
def add_reminder(reminder: ReminderIn):
    return add_reminder_logic(reminder.text)


@app.get("/list", response_model=List[ReminderOut])
def list_reminders():
    return list_reminders_logic()

app.include_router(router)

@app.websocket("/ws")
async def websocket_endpoint(websocket):
    await reminder_ws(websocket)



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)