from utils.imports import *
from configs.ConfigEnv import *
from configs.ConfigStates import *
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel, Field
from typing import Literal

from typing import List
from typing import Union



class EnvDetected(BaseModel):
    is_detected: Literal["False", "True"] 

class EnvDetected_v2(BaseModel):
    name: str

class EnvDescription(BaseModel):
    name: str
    description: str

class EnvironmentAgent:
    def __init__(self):
        self.collection = collection
        self.thread_id = "1"
        self.llm = llm

    def __call__(self, state: AgentState):
        messages = state.get("messages", [])
        if messages[-1].type == "human":
            self._is_env_human(messages[-1].content)
        elif messages[-1].type == "ai":
            self._is_env_ai(messages[-1].content)


    
        
    def _is_env_human(self, message):        
        name = self._get_env_description_v2(message)
        matching_env = self.collection.find_one(
            {
                "thread_id": self.thread_id,
                "Environment.name": name
            },
            {"Environment.$": 1}
        )
        
        if matching_env and "Environment" in matching_env:
            print("EnvironmentAgent: Line 52: matching_env: ", matching_env["Environment"][0])

            
            #print("status.name: ", status.name)
            #print("here")


    def _is_env_ai(self, message):
        name, description = self._get_env_description(message)
        print("EnvironmentAgent: Line 69: name, description: ", name, description)
        self.collection.update_one(
            {"thread_id": self.thread_id},
            {"$push": {"Environment": {"name": name, "description": description}}}
        )
        print(f"EnvironmentAgent: saved {name} to the database")


    def _get_env_description_v2(self, message):
        system_prompt = (
            "You are environment/place description extractor."
            "You are given a message and you will extract the name of the environment/place from the message."
            "You will respond with the name of the environment/place only."
            f"Below is the message:\n {[message]}"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        env_detector_chain = (
            prompt
            | llm_huge.with_structured_output(EnvDetected_v2)
        )

        result = env_detector_chain.invoke({"messages": [message]})

        return result.name

    def _setup_env_detector_chain(self, system_prompt, message):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        env_detector_chain = (
            prompt
            | llm_huge.with_structured_output(EnvDetected)
        )

        return env_detector_chain.invoke({"messages": [message]})
    

    
    def _get_env_description(self, message):
        system_prompt = (
            "You are environment/place description extractor."
            "You are given a message from an AI and you will extract the name and description of the environment/place from the message."
            f"Below is the message:\n {[message]}"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        env_description_chain = (
            prompt
            | self.llm.with_structured_output(EnvDescription) 
        )

        result = env_description_chain.invoke({"messages": [message]})

        return result.name, result.description

        