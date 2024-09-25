from agents.ChatAgent import *
from agents.EnvironmentAgent import *
from agents.MasterAgent import *
from agents.CharacterAgent import *
import functools
from langgraph.prebuilt import ToolNode
from utils.tools import load_checkpoint, save_checkpoint, end_convo
from utils.agent_node import *

# def should_continue(state: MessagesState) -> Literal["tools", "Master"]:
#     messages = state['messages']
    
#     last_message = messages[-1]
    
#     if isinstance(last_message, AIMessage):
#         if last_message.tool_calls:
#             print("tool call used")
#             return "tools"
   
#     return "Master"

def setup_graph():
    tools = [load_checkpoint, save_checkpoint, end_convo]
    tool_node = ToolNode(tools)

    environment_agent = EnvironmentAgent()
    chatbot = ChatAgent() #type: ignore
    master_agent = GameMaster()
    character_agent = CharacterAgent()
    agent_nodes = ["SLE_Tools", "EnvironmentAgent", "CharacterAgent", "ChatAgent"]

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("Master", master_agent)
    graph_builder.add_node("EnvironmentAgent", environment_agent)
    graph_builder.add_node("ChatAgent", chatbot)
    graph_builder.add_node("SLE_Tools", tool_node)
    graph_builder.add_node("CharacterAgent", character_agent)
    graph_builder.add_edge(START, "Master")
    
    conditional_map = {k: k for k in agent_nodes}
    conditional_map[END] = END

    graph_builder.add_conditional_edges("Master", lambda x: x["next"], conditional_map)
    for agent in agent_nodes:
        graph_builder.add_edge(agent, "Master")

    

    # Debugging statements to trace state transitions
    
    return graph_builder

