from utils.imports import *
from configs.ConfigEnv import *
from configs.ConfigStates import *
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.pydantic_v1 import BaseModel, Field
from typing import Literal, List


# to determine if the stats need to be updated
class StatUpdate(BaseModel):
    is_update: Literal["False", "True"] 


# to generate the stats
class StatGenerator(BaseModel):
    health: int = Field(description="Maximum Health of the character (1-100)")  
    mana: int = Field(description="Maximum Mana of the character (1-100)")
    stamina: int = Field(description="Maximum Stamina of the character (1-100)")
    strength: int = Field(description="Strength of the character (1-100)")
    agility: int = Field(description="Agility of the character (1-100)")
    intelligence: int = Field(description="Intelligence of the character (1-100)")
    charisma: int = Field(description="Charisma of the character (1-100)")
    luck: int = Field(description="Luck of the character (1-100)")
    powerlevel: int = Field(description="Level of the character (1-100)")


class StatsAgent:
    def __init__(self):
        self.collection = collection
        self.thread_id = "1"
        self.llm = llm_huge

    def __call__(self, state: AgentState):
        self._initialize_()

        self._update_stats_for_all_characters()



    def _initialize_(self):
        self.document = self.collection.find_one({"thread_id": self.thread_id})

        if self.document is not None:   
            if "stats" not in self.document:
                self.collection.update_one(
                {"thread_id": self.thread_id},
                {"$set": {"stats": []}}
            )



    def _update_stats_for_all_characters(self):
        try:    
            characters = self.document.get("characters", [])
            #print(characters)
        except Exception:
            characters = None

        # print("================")
        # print(characters)
        # print("================")
        if characters is not None:
            stats = self.document.get("stats", [])

            for character in characters:
                self._update_stats_for_character(character, stats)





    def _update_stats_for_character(self, character, stats):
        existing_stat = next((stat for stat in stats if stat["name"] == character["name"]), None)

        if existing_stat:
            if existing_stat["titles"] != character["titles"]:
                self.collection.update_one(
                    {"thread_id": self.thread_id, "stats.name": existing_stat["name"]},
                    {"$set": {"stats.$.titles": character["titles"]}}
                )
        else:
            #print("character", character)
            
            new_stat = self._generate_new_stat(character)
            new_stat["name"] = character["name"]
            new_stat["titles"] = character["titles"]
            self.collection.update_one(
                {"thread_id": self.thread_id},
                {"$push": {"stats": new_stat}}
            )        




    def _generate_new_stat(self, character):
        system_prompt = (
            "Your task is to generate the stats for the character for below template:\n"
            "{StatGenerator}"
            "Given the following information on character:\n"
            "{character}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
        ])

        stat_generator_chain = (
            prompt
            | self.llm.with_structured_output(StatGenerator)
        )

        result = stat_generator_chain.invoke({"character": character, "StatGenerator": StatGenerator})
        #print(result)
        scaled_stats = self.scale_stats(vars(result))
        return scaled_stats
    

    def scale_stats(self, stats):
        level = stats["powerlevel"]
        stats["health"] = int(stats["health"] * (1.1 ** (level - 1)))
        stats["mana"] = int(stats["mana"] * (1.1 ** (level - 1)))
        stats["stamina"] = int(stats["stamina"] * (1.1 ** (level - 1)))
        stats["strength"] = int(stats["strength"] * (1.08 ** (level - 1)))
        stats["agility"] = int(stats["agility"] * (1.08 ** (level - 1)))
        stats["powerlevel"] = int(stats["health"] + stats["mana"] + stats["stamina"] + stats["strength"] + stats["agility"] + stats["intelligence"] + stats["charisma"] + stats["luck"] + stats["powerlevel"])
        return stats




