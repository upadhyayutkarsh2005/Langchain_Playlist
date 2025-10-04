# features/email_drafter/gmail_api.py
import os
import json
import base64
from pathlib import Path
from typing import Optional

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN_PATH = Path("data/google_token.json")
TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)

# Scopes needed to send email and view/send drafts
SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile"
]

def _load_client_config():
    """
    Expect either:
     - environment variable GOOGLE_OAUTH_CLIENT_CONFIG containing JSON string of the client config, OR
     - a local file path set in GOOGLE_OAUTH_CLIENT_SECRETS pointing to client_secret.json
    The client config must be in the form client_secret JSON as returned by Google Cloud Console.
    """
    client_secrets_path = os.getenv("GOOGLE_OAUTH_CLIENT_SECRETS")
    client_config_env = os.getenv("GOOGLE_OAUTH_CLIENT_CONFIG_JSON")
    if client_secrets_path and Path(client_secrets_path).exists():
        return client_secrets_path  # path accepted by Flow.from_client_secrets_file
    elif client_config_env:
        # write it to a temp file
        cfg = json.loads(client_config_env)
        tmp = Path("data/google_client_secret_tmp.json")
        tmp.write_text(json.dumps(cfg))
        return str(tmp)
    else:
        raise EnvironmentError("Provide OAuth client config: set GOOGLE_OAUTH_CLIENT_SECRETS (file path) or GOOGLE_OAUTH_CLIENT_CONFIG_JSON (JSON).")

def create_auth_url(redirect_uri: str) -> str:
    """
    Build an OAuth consent URL. The redirect_uri must match the one configured in GCP console.
    """
    client_secrets = _load_client_config()
    flow = Flow.from_client_secrets_file(
        client_secrets,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline", include_granted_scopes="true")
    return auth_url

def fetch_and_store_token(authorization_response_url: str, redirect_uri: str) -> dict:
    """
    Exchange the authorization response (full callback URL) for tokens and persist locally.
    Returns token info dict.
    """
    client_secrets = _load_client_config()
    flow = Flow.from_client_secrets_file(
        client_secrets,
        scopes=SCOPES,
        redirect_uri=redirect_uri
    )
    # The authorization_response_url is the full callback URL including code and state
    flow.fetch_token(authorization_response=authorization_response_url)
    creds = flow.credentials
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": creds.scopes
    }
    TOKEN_PATH.write_text(json.dumps(token_data))
    return token_data

def load_credentials() -> Optional[Credentials]:
    if not TOKEN_PATH.exists():
        return None
    raw = json.loads(TOKEN_PATH.read_text())
    creds = Credentials(
        token=raw.get("token"),
        refresh_token=raw.get("refresh_token"),
        token_uri=raw.get("token_uri"),
        client_id=raw.get("client_id"),
        client_secret=raw.get("client_secret"),
        scopes=raw.get("scopes")
    )
    return creds

def send_message_raw(to_email: str, subject: str, body_text: str) -> dict:
    """
    Send an email using saved credentials.
    Returns the Gmail API response (message resource) on success.
    """
    creds = load_credentials()
    if not creds:
        raise RuntimeError("No stored Google credentials. Complete OAuth flow first.")
    try:
        service = build("gmail", "v1", credentials=creds)
        from email.mime.text import MIMEText
        message = MIMEText(body_text)
        message["to"] = to_email
        message["subject"] = subject
        # 'me' refers to the authenticated user
        raw_str = base64.urlsafe_b64encode(message.as_bytes()).decode()
        send_req = {"raw": raw_str}
        result = service.users().messages().send(userId="me", body=send_req).execute()
        return result
    except HttpError as e:
        raise RuntimeError(f"Gmail API error: {e}")