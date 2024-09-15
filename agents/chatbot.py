from utils.imports import *
from configs.ConfigStates import *
from configs.ConfigEnv import *
from datetime import datetime


@tool
def short_memory(query: str):
    """Call this to create summary of latest conversations"""
    return "This is short summary short af."

@tool
def long_memory(query: str):
    """Call this to update the overall summary of the entire conversation"""
    return "This long summary 123123"

tools = [short_memory, long_memory]
tool_node = ToolNode(tools)

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-groq-8b-8192-tool-use-preview"
).bind_tools(tools)


def use_tools(state: MessagesState) -> Literal["tools", END]: # type: ignore
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END


def chatbot(state: AgentState):
    return {"messages": [llm.invoke(state["messages"])]}


def setup_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges(
        "chatbot",
        use_tools,
    )
    graph_builder.add_edge("tools", 'chatbot')

    return graph_builder.compile()
