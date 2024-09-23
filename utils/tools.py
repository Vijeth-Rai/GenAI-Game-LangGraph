from utils.imports import *
from configs.ConfigStates import *
from configs.ConfigEnv import *

config = {"configurable": {"thread_id": 1}}

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-groq-70b-8192-tool-use-preview"
)

@tool
def load_checkpoint(query: str) -> AgentState:
    """Use this to load a checkpoint"""
    checkpoint_save_from = collection.find_one({"thread_id": "latest"})
    if checkpoint_save_from:
        if '_id' in checkpoint_save_from:
            del checkpoint_save_from['_id']
        if 'thread_id' in checkpoint_save_from:
            del checkpoint_save_from['thread_id']
        
        collection.update_one(
            {"thread_id": "1"},
            {"$set": checkpoint_save_from},
            upsert=True
        )

        return "Checkpoint loaded successfully."
    else:
        return "No checkpoint data found."

@tool
# make it so this cannot be used twice in a row
def save_checkpoint(query: str) -> str:
    """Use this when user/human asks you to save checkpoint. Do not use this unless asked to."""
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
def end_convo(query: str) -> str:
    """Use this tool to end the conversation when the user says farewell or goodbye."""
    exit()

