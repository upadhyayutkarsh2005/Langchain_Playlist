# features/email_drafter/prompt_template.py
from langchain.prompts import PromptTemplate

EMAIL_PROMPT = PromptTemplate(
    input_variables=["recipient", "purpose", "context", "tone", "length"],
    template=(
        "You are a helpful assistant that writes professional emails.\n\n"
        "Recipient: {recipient}\n"
        "Purpose: {purpose}\n"
        "Context / additional info: {context}\n"
        "Tone: {tone} (e.g., formal, polite, friendly, short)\n"
        "Length: {length} (short/medium/long)\n\n"
        "Write a complete email. Provide output in this exact format:\n\n"
        "Subject: <brief subject line>\n\n"
        "Body:\n<the message body, include greeting and sign-off>\n\n"
        "END"
    )
)