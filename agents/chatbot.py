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
        print("initialized chatbot")

    def __call__(self, state: AgentState):
        state = self._decide(state)
        response = self.llm.invoke(state["messages"])
        return {"messages": [response]}
    

    def _load_checkpoint(self, thread_id, state):
        checkpoint = self.collection.find_one({"thread_id": thread_id})
        if checkpoint:
            formatted_messages = [eval(f'{msg["type"]}(content={repr(msg["content"])})') for msg in checkpoint['messages']]
            state["messages"] = formatted_messages + state["messages"]
            return state 
        else:
            print("Starting New")

            
    def _decide(self, state):
        state = self._load_checkpoint(self.thread_id, state)
        messages = state["messages"]
        print(len(messages))
        if len(messages) > self.max_messages:
            state["short_memory"] = self._create_short_memory(messages[-self.max_messages:])
            state["long_memory"] = self._update_long_memory(self.state["short_memory"])
        return state

    
    def _create_short_memory(self, messages: List[BaseMessage]) -> str:
        summary_prompt = f"Note down important details from the conversation below:\n\n{messages}"
        response = self.llm.invoke(summary_prompt).content
        print("Short memory created successfully.")
        return response

    def _update_long_memory(self, short_memory: str) -> str:
        update_prompt = f"Current long-term memory: {self.state.get('long_memory', '')}\n\nNew information: {short_memory}\n\nUpdate the long-term memory to include the new information concisely."
        response = self.llm.invoke(update_prompt).content
        print("Long memory updated successfully.")
        return response
    

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
