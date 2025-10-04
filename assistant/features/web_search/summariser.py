# features/web_search/summarizer.py
from langchain.chains.summarize import load_summarize_chain
from langchain.docstore.document import Document
from typing import List, Dict

def summarize_results(llm, results: List[Dict], chain_type: str = "map_reduce"):
    """
    Summarize the list of search results (title + snippet) using a LangChain summarization chain.
    `llm` should be a LangChain LLM instance (from core.llm.get_llm()).
    Returns a short textual summary.
    """
    docs = []
    for r in results:
        content = f"{r.get('title','')}\n{r.get('snippet','')}\nSource: {r.get('link','')}"
        docs.append(Document(page_content=content))

    # map_reduce is robust for multiple short docs
    chain = load_summarize_chain(llm, chain_type=chain_type)
    summary = chain.run(docs)
    return summary