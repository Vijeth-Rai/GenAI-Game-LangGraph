from contextlib import asynccontextmanager, contextmanager
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Sequence, Tuple

from langchain_core.runnables import RunnableConfig
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo import MongoClient, UpdateOne
from pymongo.database import Database as MongoDatabase

from langgraph.checkpoint.base import (
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
    get_checkpoint_id,
)
from agents.tools import *


class MongoDBSaver(BaseCheckpointSaver):
    """A checkpoint saver that stores checkpoints in a MongoDB database."""

    client: MongoClient
    db: MongoDatabase

    def __init__(self,client: MongoClient,db_name: str) -> None:
        super().__init__()
        self.llm = llm
        self.client = client
        self.db = self.client[db_name]

    @classmethod
    @contextmanager
    def from_conn_info(cls, *, host: str, port: int, db_name: str) -> Iterator["MongoDBSaver"]:
        client = None
        try:
            client = MongoClient(host=host, port=port)
            yield MongoDBSaver(client, db_name)
        finally:
            if client:
                client.close()

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        pass

    def list(self, config: Optional[RunnableConfig], *, filter: Optional[Dict[str, Any]] = None, before: Optional[RunnableConfig] = None, limit: Optional[int] = None) -> Iterator[CheckpointTuple]:
        pass



    def put(self,config: RunnableConfig,checkpoint: Checkpoint,metadata: CheckpointMetadata,new_versions: ChannelVersions,) -> RunnableConfig:
        
        thread_id = config["configurable"]["thread_id"]
        new_messages = checkpoint.get('channel_values', {}).get('messages', [])

        message_type_map = {
            'human': 'HumanMessage',
            'ai': 'AIMessage'
        }

        formatted_new_messages = []
        for message in new_messages:
            message_type = message_type_map.get(message.type, message.type)
            formatted_message = {
                'type': message_type,
                'content': message.content
            }
            formatted_new_messages.append(formatted_message)


        #print("New messages", formatted_new_messages)
        # Retrieve the current document
        current_doc = self.db["checkpoints"].find_one({"thread_id": thread_id})

        formatted_old_messages = []
        if current_doc:
            for msg in current_doc.get("messages", []):
                # print("doc", msg)
                # print("type", msg["type"])
                # print("content", msg["content"])
                formatted_message = {
                    'type': msg["type"],
                    'content': msg["content"],
                }
                if formatted_message not in formatted_new_messages:
                    formatted_old_messages.append(formatted_message)

        #print("Old messages", formatted_old_messages)


        # Convert the dictionary back to a list, sorted by original order
        all_messages = formatted_old_messages + formatted_new_messages
        update_doc = self._decide(all_messages, thread_id, current_doc)
        

        # Use upsert to either update the existing document or create a new one if it does not exist
        self.db["checkpoints"].update_one({"thread_id": thread_id}, {"$set": update_doc}, upsert=True)

        return {
            "configurable": {
                "thread_id": thread_id,
            }
        }


        
    def _decide(self, messages, thread_id, current_doc):
        max_messages = 4
        return_data = {}
        return_data["thread_id"] = thread_id
        return_data["messages"] = messages
        if len(messages) > max_messages:
            return_data["long_memory"] = current_doc.get("long_memory", "")
            return_data["short_memory"] = self._create_short_memory(messages[-max_messages:])
            return_data["long_memory"] = self._update_long_memory(return_data["short_memory"], return_data["long_memory"])
            return_data["messages"] = return_data["messages"][-1:]
        
        return return_data

    
    def _create_short_memory(self, messages) -> str:
        summary_prompt = f"Note down important details from the conversation below:\n\n{messages}"
        response = self.llm.invoke(summary_prompt).content
        print("Short memory created successfully.")
        return response

    def _update_long_memory(self, short_memory: str, long_memory: str) -> str:
        update_prompt = f"Current long-term memory: {long_memory}\n\nNew information: {short_memory}\n\nUpdate the long-term memory to include the new information concisely."
        response = self.llm.invoke(update_prompt).content
        print("Long memory updated successfully.")
        return response

    def put_writes(self, config: RunnableConfig, writes: Sequence[Tuple[str, Any]], task_id: str,) -> None:
        pass