# features/email_drafter/email_generator.py
from langchain.chains import LLMChain
from core.llm import get_llm
from .prompt_template import EMAIL_PROMPT
import re
from typing import Dict

llm = get_llm()

def generate_email_draft(recipient: str, purpose: str, context: str = "", tone: str = "polite", length: str = "medium") -> Dict[str,str]:
    """
    Returns a dict with keys: subject, body, raw (raw model output).
    """
    chain = LLMChain(llm=llm, prompt=EMAIL_PROMPT)
    out = chain.run({
        "recipient": recipient,
        "purpose": purpose,
        "context": context or "",
        "tone": tone,
        "length": length
    })

    # The prompt requests a specific format. Try to parse subject and body robustly.
    subject = ""
    body = out
    # Try to extract "Subject: ..." and "Body:" sections
    subj_match = re.search(r"Subject:\s*(.*)", out)
    body_match = re.search(r"Body:\s*(.*)", out, flags=re.DOTALL)
    if subj_match:
        subject = subj_match.group(1).strip()
    if body_match:
        body = body_match.group(1).strip()

    return {"subject": subject, "body": body, "raw": out}