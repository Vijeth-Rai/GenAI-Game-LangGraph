from agents.chatbot import *
from agents.MemoryAgent import StateSaver
from langgraph.prebuilt import ToolNode


def should_continue(state: MessagesState) -> Literal["tools", END]: # type: ignore
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def setup_graph():
    chatbot = Chatbot()
    #memory = StateSaver()
    
    #tools = memory.get_tools()
    #tool_node = ToolNode(tools)

    graph_builder = StateGraph(AgentState)

    #graph_builder.add_node("memory", memory)
    graph_builder.add_node("chatbot", chatbot)
    #graph_builder.add_node("tools", tool_node)

    graph_builder.add_edge(START, "chatbot")
    #graph_builder.add_conditional_edges("chatbot", should_continue)
    #graph_builder.add_edge("tools", "chatbot")
    #graph_builder.add_edge("memory", END)


    return graph_builder