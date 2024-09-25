from utils.imports import *
from configs.ConfigStates import *
from configs.ConfigEnv import *

config = {"configurable": {"thread_id": 1}}


@tool
def load_checkpoint(query: str) -> AgentState:
    """Use this to load a checkpoint. Do not use this unless asked to."""
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
def save_checkpoint(query: str) -> str:
    """Use this to save checkpoint. Do not use this unless asked to."""
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
    """Use this tool to end the conversation when the Human ends the conversation. No need to confirm with the Human."""
    exit()

