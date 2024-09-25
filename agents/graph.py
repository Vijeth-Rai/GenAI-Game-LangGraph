from agents.ChatAgent import *
from agents.EnvironmentAgent import *
from agents.MasterAgent import *
from agents.CharacterAgent import *
import functools
from langgraph.prebuilt import ToolNode
from utils.tools import load_checkpoint, save_checkpoint, end_convo
from utils.agent_node import *
from agents.StatsAgent import *

def setup_graph():
    tools = [load_checkpoint, save_checkpoint, end_convo]
    tool_node = ToolNode(tools)

    environment_agent = EnvironmentAgent()
    chatbot = ChatAgent() #type: ignore
    stats_agent = StatsAgent()
    master_agent = GameMaster()
    character_agent = CharacterAgent()
    agent_nodes = ["SLE_Tools", "EnvironmentAgent", "CharacterAgent", "StatsAgent", "ChatAgent"]

    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("Master", master_agent)
    graph_builder.add_node("EnvironmentAgent", environment_agent)
    graph_builder.add_node("ChatAgent", chatbot)
    graph_builder.add_node("SLE_Tools", tool_node)
    graph_builder.add_node("CharacterAgent", character_agent)
    graph_builder.add_node("StatsAgent", stats_agent)

    
    graph_builder.set_entry_point("Master")
    
    conditional_map = {k: k for k in agent_nodes}
    conditional_map[END] = END

    graph_builder.add_conditional_edges("Master", lambda x: x["next"], conditional_map)
    for agent in agent_nodes:
        graph_builder.add_edge(agent, "Master")

    

    # Debugging statements to trace state transitions
    
    return graph_builder

