Plan for Website Summarizer
    
    •	Requests / BeautifulSoup → fetch and parse website HTML
	•	Text extraction → get readable text content from HTML
	•	Text splitting → break into chunks for LLM
	•	LLM summarization → using LangChain LLMChain or map_reduce summarization
	•	Optional: Gemini API for the LLM (same as your PDF bot)

 Workflow

	1.	Input a website URL.
	2.	Fetch website HTML using requests.
	3.	Parse and clean text with BeautifulSoup.
	4.	Split text into manageable chunks.
	5.	Send chunks to LLM for summarization.
	6.	Combine outputs into a final summary.

