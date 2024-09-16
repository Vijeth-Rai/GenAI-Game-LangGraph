from utils.imports import *
from configs.ConfigStates import *
from configs.ConfigEnv import *
from agents.MemoryAgent import *

config = {"configurable": {"thread_id": 1}}

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-groq-8b-8192-tool-use-preview"
)

@tool
def load_checkpoint(query: str) -> AgentState:
    """Use this to load a checkpoint"""
    checkpoint = collection.find_one({"thread_id": "latest"})
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
def save_checkpoint(query: str) -> str:
    """Use this to save a checkpoint"""
    checkpoint_save_from = collection.find_one({"thread_id": "1"})
    checkpoint_save_from["messages"] = checkpoint_save_from["messages"][:-1]
    if checkpoint_save_from:
        # Remove the _id field from the document to be inserted
        if '_id' in checkpoint_save_from:
            del checkpoint_save_from['_id']

        if 'thread_id' in checkpoint_save_from:
            del checkpoint_save_from['thread_id']
        
        collection.update_one(
            {"thread_id": "latest"},
            {"$set": checkpoint_save_from},
            upsert=True
        )

        return "Checkpoint saved successfully."
    else:
        return "No checkpoint data found for thread_id '1'."


@tool
def get_weather(location: str):
    """Call to get the current weather."""
    if location.lower() in ["sf", "san francisco"]:
        return "It's 60 degrees and foggy."
    else:
        return "It's 90 degrees and sunny."
