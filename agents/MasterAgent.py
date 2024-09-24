from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel
from typing import List, Literal
from configs.ConfigStates import *
from utils.tools import load_checkpoint, save_checkpoint, end_convo

class GameMaster:
    def __init__(self):
        self.tools = [load_checkpoint, save_checkpoint, end_convo]
        self.llm = llm_huge.bind_tools(self.tools)
        self.members = ["ChatAgent", "EnvironmentAgent"]
        self.options = ["FINISH"] + self.members

    def __call__(self, state: AgentState):

        print("MasterAgent.py Line 12 Called")
        print(state.get("next", []))

        if state.get("next", []) == []:
            print("Checking Tools")
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
            
            # Use the dictionary as input to invoke
            response = llm_tool_prompt.invoke(input_dict)

            # i want to see response and also the input for the llm
            print(input_dict,"\n\n")
            print(response,"\n\n")
            state["messages"].append(response)
            
            #print(state)
            # remove most recent AIMesage
            




            if state.get("messages", [])[-1].tool_calls:
                return {"next": "tools"}
            
            if state["messages"] and isinstance(state["messages"][-1], AIMessage):
                state["messages"].pop()

        if state.get("next", []) == "tools":
            print("Cleaning up after tools")
            
            return {"next": END}
        
        




        message = state.get("messages", [])[-1].content

        status = self._is_env([message])

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