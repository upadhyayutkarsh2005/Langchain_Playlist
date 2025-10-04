# features/web_search/search_tool.py
import os
from serpapi import GoogleSearch

def web_search(query: str, num_results: int = 5):
    """
    Uses SerpAPI (Google) to fetch top results.
    Requires SERPAPI_API_KEY env var.
    Returns list of dicts: {title, snippet, link}
    """
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise EnvironmentError("SERPAPI_API_KEY not set. Get one at https://serpapi.com/")

    params = {
        "engine": "google",
        "q": query,
        "api_key": api_key,
        "num": num_results,
        "hl": "en"
    }
    search = GoogleSearch(params)
    data = search.get_dict()
    results = data.get("organic_results") or []
    out = []
    for r in results[:num_results]:
        out.append({
            "title": r.get("title"),
            "snippet": r.get("snippet") or r.get("rich_snippet", {}).get("top", {}).get("extensions", [""])[0],
            "link": r.get("link")
        })
    return out