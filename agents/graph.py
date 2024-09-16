from agents.chatbot import *
from agents.MemoryAgent import StateSaver
from langgraph.prebuilt import ToolNode
from agents.tools import *

def should_continue(state: MessagesState) -> Literal["tools", END]: # type: ignore
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        #print("Yes")
        return "tools"
    return END


def setup_graph():
    
    tools = [load_checkpoint, save_checkpoint, end_convo]
    tool_node = ToolNode(tools)
    llm_with_tools = llm.bind_tools(tools)

    chatbot = Chatbot(llm_with_tools)
    

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", should_continue)
    graph_builder.add_edge("tools", "chatbot")


    return graph_builder