from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel
from typing import List, Literal
from configs.ConfigStates import *
from utils.tools import load_checkpoint, save_checkpoint, end_convo

config = {"configurable": {"thread_id": "1"}}

class GameMaster:
    def __init__(self):
        self.tools = [load_checkpoint, save_checkpoint, end_convo]
        self.llm = llm_huge.bind_tools(self.tools)
        self.thread_id = config["configurable"]["thread_id"]
        self.members = ["ChatAgent", "EnvironmentAgent"]
        self.options = ["FINISH"] + self.members
        self.collection = collection

    def __call__(self, state: AgentState):

        print("MasterAgent.py Line 12 Called")
        if state.get("messages", [])[-1].type == "human":
            self._update_next_history("END")


        if state.get("next", []) == []:
            system_prompt = (
                f"You have access to the following tools: {self.tools}."
                " You do not need extra information to use the tools."
                " You will respond with whenever needed else respond normally."
                " You do not have memory of any conversation, if asked about any conversation, respond with 'I do not know'"
            )
            prompt = ChatPromptTemplate.from_messages(
                [
                    ("system", system_prompt),
                    MessagesPlaceholder(variable_name="messages"),
                ]
            )
            llm_tool_prompt = prompt | self.llm

            input_dict = {
                "messages": [
                    SystemMessage(content=system_prompt),
                    *state["messages"]
                ]
            }
            
            response = llm_tool_prompt.invoke(input_dict)

            state["messages"].append(response)
           
            




            if state.get("messages", [])[-1].tool_calls:
                return {"next": "tools"}
            
            if state["messages"] and isinstance(state["messages"][-1], AIMessage):
                state["messages"].pop()

        if state.get("next", []) == "tools":
            self._update_next_history("ChatAgent")
            return {"next": END}
        
        




        message = state.get("messages", [])[-1].content

        status = self._is_env([message])

        if status.answer == "True" and state.get("next", []) != "EnvironmentAgent" and not self._in_next_histories("EnvironmentAgent"):
            self._update_next_history("EnvironmentAgent")
            return {"next": "EnvironmentAgent"}
        
        if state.get("next", []) != "ChatAgent" and not self._in_next_histories("ChatAgent"):
            self._update_next_history("ChatAgent")
            return {"next": "ChatAgent"}
        
        self._update_next_history("END")
        return {"next": END}





    def _is_env(self, messages):
        system_prompt = (
            "You are an environment/place detector. "
            "You are given a message and you will determine if it contains the name of an environment/place or not. "
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
    

    def _update_next_history(self, x):
        if x == "END":
            self.collection.update_one(
                {"thread_id": self.thread_id},
                {"$set": {"next_histories": []}}
            )
        else:
            self.collection.update_one(
                {"thread_id": self.thread_id},
                {"$push": {"next_histories": {"$each": [x]}}}
            )

    def _in_next_histories(self, x):
        next_histories = self.collection.find_one({"thread_id": self.thread_id})["next_histories"]
        return x in next_histories