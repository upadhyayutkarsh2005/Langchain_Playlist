# logic.py

import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from dotenv import load_dotenv
load_dotenv()



api_key = os.getenv("GOOGLE_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = "true"

if langchain_api_key:
    os.environ["LANGCHAIN_API_KEY"] = langchain_api_key




def load_pdf(file_path: str):
    """Extract text from PDF file"""
    pdf_reader = PdfReader(file_path)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text() or ""
    return text


def create_vectorstore(text: str):
    """Convert text into vector embeddings using Gemini"""
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )

    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
    return vectorstore


def build_qa_chain(vectorstore):
    """Build the RetrievalQA chain with Gemini"""
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro-latest",
        google_api_key=api_key,
        temperature=0
    )

    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectorstore.as_retriever(),
        chain_type="stuff"
    )
    return qa_chain


def answer_query(file_path: str, query: str):
    """Load PDF, build QA chain, and answer user query"""
    text = load_pdf(file_path)
    vectorstore = create_vectorstore(text)
    qa_chain = build_qa_chain(vectorstore)

    response = qa_chain.run(query)
    return response