# core/agent.py
from langchain.agents import initialize_agent, AgentType
from langchain.memory import ConversationBufferMemory

def build_agent(llm, tools, verbose: bool = False):
    """
    Initialize a LangChain agent with memory and provided tools.
    `tools` is a list of Tool objects (e.g. get_web_search_tool(...))
    """
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
    agent_executor = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=verbose,
        memory=memory
    )
    return agent_executor
