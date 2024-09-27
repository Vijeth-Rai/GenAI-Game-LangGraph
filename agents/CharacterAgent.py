from utils.imports import *
from configs.ConfigEnv import *
from configs.ConfigStates import *
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel, Field
from typing import Literal, List

class CharDetected(BaseModel):
    is_detected: Literal["False", "True"] 

class CharDetected_v2(BaseModel):
    names: List[str]

class CharDescription(BaseModel):
    name: str
    description: str

class CharDescription_extended(BaseModel):
    name: str
    titles: List[str]
    race: str
    gender: str
    backstory: str
    description: str

class CharacterAgent:
    def __init__(self):
        self.collection = collection
        self.thread_id = "1"
        self.llm = llm

    def __call__(self, state: AgentState):
        messages = state.get("messages", [])
        if messages[-1].type == "human":
            self._is_char_human(state, messages[-1].content)
        elif messages[-1].type == "ai":
            self._is_char_ai(messages[-1].content)

    def _is_char_human(self, state, message):        
        names = self._get_char_descriptions_v2(message)
        new_message = message

        for name in names:
            matching_char = self.collection.find_one(
                {
                    "thread_id": self.thread_id,
                    "characters.name": name
                },
                {"characters.$": 1}
            )
            
            if matching_char and "characters" in matching_char:
                char_info = matching_char["characters"][0]
                new_message += f"\nUse this to be consistent about Character/Person: {char_info['name']} \n Description: {char_info['description']}"

        state["messages"] = state["messages"][:-1]
        state["messages"].append(HumanMessage(content=new_message))
        return state

    def _is_char_ai(self, message):
        names = self._get_char_descriptions_v2(message)
        for name in names:
            char_info = self._get_char_description(message, name)
            
            # Check for duplicates
            existing_character = self.collection.find_one({
                "thread_id": self.thread_id,
                "$or": [
                    {"characters.name": {"$in": [char_info["name"]] + char_info["titles"]}},
                    {"characters.titles": {"$in": [char_info["name"]] + char_info["titles"]}}
                ]
            })

            if existing_character:
                existing_char = existing_character["characters"][0]
                
                if existing_char["name"] == char_info["name"]:
                    # Condition 1: Name already exists
                    new_titles = list(set(existing_char["titles"] + char_info["titles"]))
                    if new_titles != existing_char["titles"]:
                        self.collection.update_one(
                            {"thread_id": self.thread_id, "characters.name": existing_char["name"]},
                            {"$set": {"characters.$.titles": new_titles}}
                        )
                        print(f"Updated titles for character '{existing_char['name']}'")
                    else:
                        print(f"Character '{existing_char['name']}' already exists, no updates needed.")
                else:
                    # Conditions 2, 3, or 4: Title exists as name, or name/title exists in other titles
                    merged_titles = list(set(existing_char["titles"] + char_info["titles"] + [existing_char["name"], char_info["name"]]))
                    merged_name = existing_char["name"] if existing_char["name"] in merged_titles else char_info["name"]
                    merged_titles.remove(merged_name)
                    
                    self.collection.update_one(
                        {"thread_id": self.thread_id, "characters.name": existing_char["name"]},
                        {"$set": {
                            "characters.$.name": merged_name,
                            "characters.$.titles": merged_titles,
                            "characters.$.race": char_info["race"],
                            "characters.$.gender": char_info["gender"],
                            "characters.$.backstory": char_info["backstory"],
                            "characters.$.description": char_info["description"]
                        }}
                    )
                    print(f"Updated character '{merged_name}' with merged information.")
            else:
                # No duplicates found, insert new character
                self.collection.update_one(
                    {"thread_id": self.thread_id},
                    {"$push": {"characters": char_info}}
                )
                #print(f"Inserted new character '{char_info['name']}' into the database.")

    def _get_char_descriptions_v2(self, message):
        system_prompt = (
            "You are character/person description extractor."
            "You are given a message and you will extract the names of all characters/persons from the message."
            "You will respond with a list of names of the characters/persons only."
            f"Below is the message:\n {[message]}"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        char_detector_chain = (
            prompt
            | llm_huge.with_structured_output(CharDetected_v2)
        )

        result = char_detector_chain.invoke({"messages": [message]})

        return result.names

    def _get_char_description(self, message, name):
        system_prompt = (
            f"You are character/person description extractor for the character named {name}."
            " You are given a message from an AI and you will extract the description of the character/person from the message."
            " The format of your response should be as follows: Name: <name>, Description: <description>"
            f" Below is the message:\n {[message]}"
        )
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        char_description_chain = (
            prompt
            | self.llm.with_structured_output(CharDescription) 
        )

        result = char_description_chain.invoke({"messages": [message]})
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                
        return self._get_char_description_extended(result)

    def _get_char_description_extended(self, input):
        name = input.name
        description = input.description

        system_prompt = (
            " You will be given name and description of a character/person."
            " You will extract name, titles, race, gender, backstory and description of the character/person from the description."
            " Titles: Extract any specific titles or unique designations the character/person is known by (e.g., 'The Brave,' 'King of the North'). Exclude professions or roles like 'comedian' or 'swordsman,' unless they are used as a unique designation."
            " In the case where the description does not provide all the information needed, you will use your best judgement to fill in the missing information."
            " You will respond with the name, titles, race, gender, backstory and description of the character/person."
            " The format of your response should be as follows: Name: <name>, Titles: <titles>, Race: <race>, Gender: <gender>, Backstory: <backstory>, Description: <description>"
            " The Description should be a detailed description of the character/person, including their physical appearance, mannerisms, and any other distinguishing features."
            f" Below is the name and description of the character/person:\n Name: {name}\n Description: {description}"
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        char_description_extended_chain = (
            prompt
            | llm_huge.with_structured_output(CharDescription_extended)
        )

        result = char_description_extended_chain.invoke({"messages": [description]})

        # Clean up name and titles
        cleaned_name = self._clean_name(result.name)
        cleaned_titles = [self._clean_name(title) for title in result.titles]

        return {
            "name": cleaned_name,
            "titles": cleaned_titles,
            "race": result.race,
            "gender": result.gender,
            "backstory": result.backstory,
            "description": result.description
        }

    def _clean_name(self, name):
        # Remove articles and common titles at the beginning of the name
        words_to_remove = ['the', 'a', 'an', 'mr', 'mrs', 'ms', 'miss', 'dr', 'prof']
        name_parts = name.lower().split()
        while name_parts and name_parts[0] in words_to_remove:
            name_parts.pop(0)
        return ' '.join(name_parts).capitalize()

    def _setup_char_detector_chain(self, system_prompt, message):
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        char_detector_chain = (
            prompt
            | llm_huge.with_structured_output(CharDetected)
        )

        return char_detector_chain.invoke({"messages": [message]})
