from utils.imports import *
from configs.ConfigStates import *
from configs.ConfigEnv import *
from typing import List, Literal  # Add this line
from agents.tools import *
from main import config

class Chatbot:
    def __init__(self):
        self.llm = llm
        self.collection = collection
        self.max_messages = 5
        self.thread_id = config["configurable"]["thread_id"]
        self.return_data = {}
        print("initialized chatbot")

    def __call__(self, state: AgentState):
        state = self._load_checkpoint(state)
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}
    

    def _load_checkpoint(self, state):
        checkpoint = self.collection.find_one({"thread_id": self.thread_id})
        if checkpoint:
            formatted_messages = [eval(f'{msg["type"]}(content={repr(msg["content"])})') for msg in checkpoint['messages']]
            state["messages"] = formatted_messages + state["messages"]
            return state 
        else:
            print("Starting New")
            return ""

            
    @tool
    def load_checkpoint(self, query: str) -> AgentState:
        """Use this to load a checkpoint"""
        checkpoint = self.collection.find_one({"thread_id": "latest"})
        if checkpoint:
            formatted_messages = [eval(f'{msg["type"]}(content={repr(msg["content"])})') for msg in checkpoint['messages']]
            return AgentState(
                messages=formatted_messages,
                short_memory=checkpoint["short_memory"],
                long_memory=checkpoint["long_memory"]
            )
        else:
            print("No checkpoint data found. Please create one.")

    @tool
    def save_checkpoint(self, query: str = "") -> str:
        """Use this to save a checkpoint"""
        checkpoint = self.collection.find_one({"thread_id": ""})
        if checkpoint:
            self.collection.update_one(
                {"thread_id": "latest"},
                {"$set": checkpoint}
            )
        else:
            self.collection.insert_one(checkpoint)
        print("Checkpoint saved successfully.")


    def get_tools(self):
        return [self.save_checkpoint, self.load_checkpoint]
