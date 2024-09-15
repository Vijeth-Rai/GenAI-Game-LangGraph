from utils.imports import *
from configs.ConfigStates import *
from configs.ConfigEnv import *
from typing import List, Literal  # Add this line
from agents.tools import *

class Chatbot:
    def __init__(self):
        self.llm = llm  
        print("intiialized chabot")

    def __call__(self, state: AgentState):
        
        return {"messages": state["messages"] + [self.llm.invoke(state["messages"])]}
