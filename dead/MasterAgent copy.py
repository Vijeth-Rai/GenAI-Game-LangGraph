from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel
from typing import List, Literal
from configs.ConfigStates import *

class GameMaster:
    def __init__(self, llm_with_tools):
        self.llm = llm_with_tools
        self.members = ["ChatAgent", "EnvironmentAgent"]
        self.options = ["END"] + self.members

    def __call__(self, state: AgentState):
        print("MasterAgent.py Line 12 Called")

        message = state.get("messages", [])[-1].content
        status = self._is_env(message)
        #print(status)
        if status.next == "True":
            return END

        return "ChatAgent"





    def _is_env(self, message):
        system_prompt = (
            "You are environment/place detector."
            "You are given a message and you will determine whether it involves an environment/place or not."
            "If the response might involve an environment/place, respond only with True. If the response does not involve an environment/place, respond only with False."
            f"Below is the message:\n {message}"
        )

        class EnvDetected(BaseModel):
            next: Literal["True", "False"]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        env_detector_chain = (
            prompt
            | self.llm.with_structured_output(EnvDetected)
        )

        return env_detector_chain.invoke({"messages": message})