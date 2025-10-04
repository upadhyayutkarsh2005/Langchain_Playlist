# features/document_qa/retriever.py
from typing import Optional
from langchain.chains import RetrievalQA
from langchain.llms.base import LLM
from langchain.vectorstores import Chroma
from langchain.docstore.document import Document
from langchain.llms import OpenAI  
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os 
# fallback if you want to create local llm

def get_retriever_from_persist_dir(persist_dir_name: str, search_k: int = 5):
    persist_dir = f"data/vectorstores/{persist_dir_name}"
    embedding = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=os.getenv("GOOGLE_API_KEY")
    )
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embedding)
    retriever = vectordb.as_retriever(search_kwargs={"k": search_k})
    return retriever

def build_retrieval_qa_chain(llm: LLM, retriever, chain_type: str = "stuff"):
    """
    Build a RetrievalQA chain using the provided LLM and retriever.
    `chain_type` can be "stuff", "map_reduce", etc.
    """
    qa_chain = RetrievalQA.from_chain_type(llm=llm, chain_type=chain_type, retriever=retriever)
    return qa_chain
