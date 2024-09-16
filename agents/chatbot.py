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
        print("initialized chatbot")

    def __call__(self, state: AgentState):
        thread_id = config["configurable"]["thread_id"]
        checkpoint = self.collection.find_one({"thread_id": thread_id})

        #("==========================Checkpoint=========================")
        #print(checkpoint)

        #print("==========================Formatted=========================")
        formatted_messages = [eval(f'{msg["type"]}(content={repr(msg["content"])})') for msg in checkpoint['messages']]
        #print(formatted_messages)

        #print("==========================State=========================")
        #print(state["messages"])

        #print("========================Custom====================")
                
        
        messages_with_context = formatted_messages + state["messages"]
        
        response = self.llm.invoke(messages_with_context)
        
        return {"messages": state["messages"] + [response]}
