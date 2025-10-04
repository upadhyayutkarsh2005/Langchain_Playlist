# features/document_qa/vectorstore.py
import os
from pathlib import Path
from typing import List
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langchain.vectorstores import Chroma
import os

# Directory to persist chroma vectorstores
VECTORS_BASE = Path("data/vectorstores")
VECTORS_BASE.mkdir(parents=True, exist_ok=True)

def build_vectorstore_from_text(text: str, persist_dir_name: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Splits `text` into chunks and builds/persists a Chroma vectorstore.
    Returns the Chroma vectorstore object.
    """
    # Split text
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = splitter.split_text(text)

    docs = [Document(page_content=t) for t in texts]

    # Create embeddings
    embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=os.getenv("GOOGLE_API_KEY"))  # uses GOOGLE_API_KEY from env

    persist_dir = str(VECTORS_BASE / persist_dir_name)
    persist_dir_path = Path(persist_dir)
    persist_dir_path.mkdir(parents=True, exist_ok=True)

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embedding,  # This is correct for LangChain's Chroma wrapper
        persist_directory=persist_dir
    )
    return vectordb 

