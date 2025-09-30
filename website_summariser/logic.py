import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.summarize import load_summarize_chain
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import Document
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

def fetch_website_text(url: str) -> str:
    """Fetch website HTML and extract readable text"""
    response = requests.get(url, timeout=10)
    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts/styles
    for tag in soup(["script", "style"]):
        tag.decompose() 

    text = soup.get_text(separator="\n")
    # Clean multiple newlines
    text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
    return text

def summarize_website(url: str) -> str:
    """Fetch website and summarize content using Gemini"""
    text = fetch_website_text(url)

    # Split text into chunks
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    # Convert each chunk into a Document
    docs = [Document(page_content=chunk) for chunk in chunks]

    # Initialize Gemini chat model
    llm = ChatGoogleGenerativeAI(
        model="models/gemini-pro-latest",  # or "gemini-1.5-pro-preview"
        google_api_key=api_key,
        temperature=0.7
    )

    # Load summarization chain (map_reduce works well for long content)
    chain = load_summarize_chain(llm, chain_type="map_reduce")
    summary = chain.run(docs)
    return summary