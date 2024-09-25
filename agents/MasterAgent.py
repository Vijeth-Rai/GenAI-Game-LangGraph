from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel
from typing import List, Literal
from configs.ConfigStates import *
from utils.tools import load_checkpoint, save_checkpoint, end_convo
from concurrent.futures import ThreadPoolExecutor, as_completed

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

        #print("MasterAgent.py Line 12 Called")
        if state.get("messages", [])[-1].type == "human":
            self._update_next_history("END")

        # tools check
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
                return {"next": "SLE_Tools"}
            
            if state["messages"] and isinstance(state["messages"][-1], AIMessage):
                state["messages"].pop()

        if state.get("next", []) == "SLE_Tools":
            self._update_next_history("ChatAgent")
            return {"next": END}
        
        # end of tools check


        

        message = state.get("messages", [])[-1].content

        # Parallelize environment and character checks
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_env = executor.submit(self._is_env, [message])
            future_char = executor.submit(self._is_char, [message])

            for future in as_completed([future_env, future_char]):
                if future == future_env:
                    status_env = future.result()
                    if status_env.answer == "True" and state.get("next", []) != "EnvironmentAgent" and not self._in_next_histories("EnvironmentAgent"):
                        self._update_next_history("EnvironmentAgent")
                        return {"next": "EnvironmentAgent"}
                elif future == future_char:
                    status_char = future.result()
                    if status_char.answer == "True" and state.get("next", []) != "CharacterAgent" and not self._in_next_histories("CharacterAgent"):
                        self._update_next_history("CharacterAgent")
                        return {"next": "CharacterAgent"}

        if state.get("next", []) != "ChatAgent" and not self._in_next_histories("ChatAgent"):
            self._update_next_history("ChatAgent")
            return {"next": "ChatAgent"}
        

        self._update_next_history("END")
        return {"next": END}



    def _is_char(self, messages):
        latest_message = messages[-1]
        system_prompt = (
            "You are an character/person detector. "
            "You are given a message and you will determine if it contains the name of an character/person or not. "
            "Do not consider the name of the environment/place in the message to be the name of the character/person. "
            "If you are not 100% sure, respond with False"
            "You will always respond with either True or False"
            "Below is the message:\n"
        )

        class CharDetected(BaseModel):
            answer: Literal["True", "False"]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", latest_message),  
            ]
        )

        char_detector_chain = (
            prompt
            | self.llm.with_structured_output(CharDetected)
        )

        return char_detector_chain.invoke({"messages": messages})

    def _is_env(self, messages):
        latest_message = messages[-1]
        system_prompt = (
            "You are an environment/place detector. "
            "You are given a message and you will determine if it contains the name of an environment/place or not. "
            "Do not consider the name of the person/character in the message to be the name of the environment/place. "
            "If you are not 100% sure, respond with False"
            "You will always respond with either True or False"
            "Below is the message:\n"
        )

        class EnvDetected(BaseModel):
            answer: Literal["True", "False"]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("user", messages[-1]),  
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
        try:    
            next_histories = self.collection.find_one({"thread_id": self.thread_id})["next_histories"]
            return x in next_histories
        except:
            return False