# core/tools.py
from langchain.tools import Tool
from features.web_search.search_tool import web_search
from features.web_search.summariser import summarize_results
from features.doc_qa.retriever import get_retriever_from_persist_dir, build_retrieval_qa_chain
from features.email_drafter.email_generator import generate_email_draft
from features.reminder.reminder_manager import add_reminder_logic, list_reminders_logic

def get_web_search_tool(llm, num_results: int = 5):
    """
    Returns a LangChain Tool which takes a query string and returns a
    summarized answer plus top links.
    """

    def run_search(query: str):
        results = web_search(query, num_results=num_results)
        summary = summarize_results(llm, results)
        sources = "\n".join([f"{i+1}. {r['title']} - {r['link']}" for i, r in enumerate(results)])
        return f"Summary:\n{summary}\n\nTop sources:\n{sources}"

    return Tool(
        name="web_search",
        func=run_search,
        description="Use this to search the web and return a concise summary with top links. Input: a plain-text search query."
    )
    
def get_document_qa_tool(llm, persist_dir_name: str):
    """
    Returns a Tool that answers queries using the vectorstore at `persist_dir_name`.
    Use this when you already uploaded a document and built the vectorstore.
    """

    retriever = get_retriever_from_persist_dir(persist_dir_name)

    qa_chain = build_retrieval_qa_chain(llm, retriever)

    def run_doc_qa(query: str) -> str:
        """
        Accepts a natural language query (string) and returns an answer grounded in uploaded docs.
        """
        result = qa_chain.run(query)
        return str(result)

    return Tool(
        name=f"doc_qa_{persist_dir_name}",
        func=run_doc_qa,
        description=f"Use to answer questions from uploaded document store `{persist_dir_name}`. Input: question string."
    )
    
    
def get_email_draft_tool():
    """
    Tool interface for agent: input JSON-like string describing to|purpose|context|tone
    For simplicity, input is a plain string with fields separated by '||' or a short instruction.
    """
    def tool_func(instr: str):
        # A simple parser. Expect format: to:someone@example.com || purpose:... || context:... || tone:...
        parts = [p.strip() for p in instr.split("||")]
        data = {}
        for p in parts:
            if ":" in p:
                k, v = p.split(":", 1)
                data[k.strip()] = v.strip()
        to = data.get("to", "")
        purpose = data.get("purpose", instr)
        context = data.get("context", "")
        tone = data.get("tone", "polite")
        length = data.get("length", "medium")
        draft = generate_email_draft(to, purpose, context, tone, length)
        return f"Subject: {draft['subject']}\n\nBody:\n{draft['body']}"
    return Tool(name="email_drafter", func=tool_func, description="Draft emails. Input format: 'to:... || purpose:... || context:... || tone:...'")

def get_add_reminder_tool():
    """
    Tool interface for agent: input is natural language text describing the reminder.
    """
    return Tool(
        name="add_reminder",
        func=add_reminder_logic,
        description="Add a reminder. Input: natural language text describing the reminder and time."
    )   


