# core/llm.py
import os
from langchain_community.llms import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
load_dotenv()

def get_llm():
    """
    Simple LLM factory. By default uses OpenAI via OPENAI_API_KEY.
    Set LLM_PROVIDER env variable if you want to extend to other providers.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "openai":
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return OpenAI(temperature=0.2, model_name=model_name)
    elif provider == "gemini":
        model_name = os.getenv("GEMINI_MODEL", "gemini-pro-latest")
        api_key = os.getenv("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER={provider} — add it to core/llm.py")
    
    
'''import os
from langchain.llms import OpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_anthropic import ChatAnthropic

def get_llm():
    """
    LLM factory supporting OpenAI, Gemini (Google), and Claude (Anthropic).
    Set LLM_PROVIDER env variable to 'openai', 'gemini', or 'claude'.
    """
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "openai":
        model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        return OpenAI(temperature=0.2, model_name=model_name)
    elif provider == "gemini":
        model_name = os.getenv("GEMINI_MODEL", "gemini-pro")
        api_key = os.getenv("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)
    elif provider == "claude":
        model_name = os.getenv("CLAUDE_MODEL", "claude-3-opus-20240229")
        api_key = os.getenv("ANTHROPIC_API_KEY")
        return ChatAnthropic(model=model_name, anthropic_api_key=api_key)
    else:
        raise ValueError(f"Unsupported LLM_PROVIDER={provider} — add it to core/llm.py")'''