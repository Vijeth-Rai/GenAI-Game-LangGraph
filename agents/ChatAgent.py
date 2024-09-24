from utils.imports import *
from configs.ConfigStates import *
from configs.ConfigEnv import *
from typing import List, Literal  # Add this line
from utils.tools import *
from main import config
from agents.graph import *

class ChatAgent:
    def __init__(self):
        self.llm = llm
        self.collection = collection
        self.max_messages = 5
        self.thread_id = config["configurable"]["thread_id"]
        self.return_data = {}
        print("initialized chatbot")

    def __call__(self, state: AgentState):
        print("ChatAgent.py Line 19 Called")
        state = self._load_checkpoint(state)
        messages = state.get("messages", "")
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}
    

    def _load_checkpoint(self, state):
        checkpoint = self.collection.find_one({"thread_id": self.thread_id})
        if checkpoint:
            #print("chatbot 28", checkpoint)
            formatted_messages = [eval(f'{msg["type"]}(content={repr(msg["content"])})') for msg in checkpoint['messages']]
            state["messages"] = formatted_messages + state["messages"]
            return state 
        else:
            #print("Starting New")
            return state

            
    


