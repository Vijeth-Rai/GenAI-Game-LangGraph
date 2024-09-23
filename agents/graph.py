from agents.ChatAgent import *
from agents.EnvironmentAgent import *
from agents.MasterAgent import *
import functools
from langgraph.prebuilt import ToolNode
from utils.tools import load_checkpoint, save_checkpoint, end_convo
from utils.agent_node import *

def should_continue(state: MessagesState) -> Literal["tools", "Master", END]:
    messages = state['messages']
    
    last_message = messages[-1]
    last_last_message = messages[-2] if len(messages) > 1 else None
    
    if isinstance(last_message, AIMessage):
        if last_message.type == "tool":
            if last_last_message.type == "tool":
                print("tool call used previously")
                return END
            print("tool call used")
            return "tools"
    
    if len(messages) > 1:
        if isinstance(last_last_message, AIMessage):
            if last_last_message.tool_calls:
                print("tool call used previously")
                return END
   
    return "Master"

def setup_graph():
    tools = [load_checkpoint, save_checkpoint, end_convo]
    tool_node = ToolNode(tools)
    llm_with_tools = llm_huge.bind_tools(tools)

    environment_agent = EnvironmentAgent()
    chatbot = ChatAgent(llm_with_tools)
    master_agent = GameMaster()

    environment_node = functools.partial(agent_node, agent=environment_agent, name="Environment Agent")
    agent_nodes = ["EnvironmentAgent", "ChatAgent"]

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("Master", master_agent)
    graph_builder.add_node("EnvironmentAgent", environment_node)
    graph_builder.add_node("ChatAgent", chatbot)
    graph_builder.add_node("tools", tool_node)

    graph_builder.add_edge(START, "Master")
    
    conditional_map = {k: k for k in agent_nodes}
    conditional_map[END] = END

    graph_builder.add_conditional_edges("Master", lambda x: x["next"], conditional_map)
    for agent in agent_nodes:
        if agent != "ChatAgent":
            graph_builder.add_edge(agent, "Master")

    graph_builder.add_conditional_edges("ChatAgent", should_continue)
    graph_builder.add_edge("tools", "ChatAgent")

    # Debugging statements to trace state transitions
    
    return graph_builder

