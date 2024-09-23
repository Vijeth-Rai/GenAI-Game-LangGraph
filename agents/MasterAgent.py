from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel
from typing import List, Literal
from configs.ConfigStates import *

class GameMaster:
    def __init__(self):
        self.llm = llm
        self.members = ["ChatAgent", "EnvironmentAgent"]
        self.options = ["FINISH"] + self.members

    def __call__(self, state: AgentState):
        print("MasterAgent.py Line 12 Called")

        message = state.get("messages", [])[-1].content
        status = self._is_env([message])
        #print(status)
        if status.answer == "True" and state.get("next", []) != "EnvironmentAgent":
            return {"next": "EnvironmentAgent"}
        
        if state.get("next", []) != "ChatAgent":
            return {"next": "ChatAgent"}
        
        return {"next": END}





    def _is_env(self, messages):
        system_prompt = (
            "You are an environment/place detector. "
            "You are given a message and you will determine whether it involves an environment/place or not. "
            "You will always respond with either True or False"
            "Below is the message:\n"
        )

        class EnvDetected(BaseModel):
            answer: Literal["True", "False"]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", messages[0]),  # Assuming messages is a list with at least one message
            ]
        )

        env_detector_chain = (
            prompt
            | self.llm.with_structured_output(EnvDetected)
        )

        return env_detector_chain.invoke({"messages": messages})