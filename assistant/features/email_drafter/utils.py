# features/email_drafter/utils.py
from typing import Dict

def validate_email_fields(payload: Dict) -> None:
    if "to" not in payload or not payload["to"]:
        raise ValueError("Missing 'to' field (recipient email).")
    if "purpose" not in payload or not payload["purpose"]:
        raise ValueError("Missing 'purpose' field describing the email intent.")