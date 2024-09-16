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


class MongoDBSaver(BaseCheckpointSaver):
    """A checkpoint saver that stores checkpoints in a MongoDB database."""

    client: MongoClient
    db: MongoDatabase

    def __init__(
        self,
        client: MongoClient,
        db_name: str,
    ) -> None:
        super().__init__()
        self.client = client
        self.db = self.client[db_name]

    @classmethod
    @contextmanager
    def from_conn_info(
        cls, *, host: str, port: int, db_name: str
    ) -> Iterator["MongoDBSaver"]:
        client = None
        try:
            client = MongoClient(host=host, port=port)
            yield MongoDBSaver(client, db_name)
        finally:
            if client:
                client.close()

    def get_tuple(self, config: RunnableConfig) -> Optional[CheckpointTuple]:
        """Get a checkpoint tuple from the database.

        This method retrieves a checkpoint tuple from the MongoDB database based on the
        provided config. If the config contains a "checkpoint_id" key, the checkpoint with
        the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
        for the given thread ID is retrieved.

        Args:
            config (RunnableConfig): The config to use for retrieving the checkpoint.

        Returns:
            Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found.
        """
        thread_id = config["configurable"]["thread_id"]
        query = {"thread_id": thread_id}

        doc = self.db["checkpoints"].find_one(query)
        
        if doc:
            checkpoint = doc["messages"]
            return CheckpointTuple(
                {
                    "configurable": {
                        "thread_id": doc["thread_id"],
                    }
                },
                checkpoint,
            )
        return None


    def list(
        self,
        config: Optional[RunnableConfig],
        *,
        filter: Optional[Dict[str, Any]] = None,
        before: Optional[RunnableConfig] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        """List checkpoints from the database.

        This method retrieves a list of checkpoint tuples from the MongoDB database based
        on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).

        Args:
            config (RunnableConfig): The config to use for listing the checkpoints.
            filter (Optional[Dict[str, Any]]): Additional filtering criteria for metadata. Defaults to None.
            before (Optional[RunnableConfig]): If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None.
            limit (Optional[int]): The maximum number of checkpoints to return. Defaults to None.

        Yields:
            Iterator[CheckpointTuple]: An iterator of checkpoint tuples.
        """
        query = {}
        if config is not None:
            query = {
                "thread_id": config["configurable"]["thread_id"],
                "checkpoint_ns": config["configurable"].get("checkpoint_ns", ""),
            }


        if before is not None:
            query["checkpoint_id"] = {"$lt": before["configurable"]["checkpoint_id"]}

        result = self.db["checkpoints"].find(query).sort("checkpoint_id", -1)

        if limit is not None:
            result = result.limit(limit)
        for doc in result:
            checkpoint = self.serde.loads_typed(doc["checkpoint"])
            yield CheckpointTuple(
                {
                    "configurable": {
                        "thread_id": doc["thread_id"],
                        "checkpoint_ns": doc["checkpoint_ns"],
                        "checkpoint_id": doc["checkpoint_id"],
                    }
                },
                checkpoint,
            )

    def put(
        self,
        config: RunnableConfig,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: ChannelVersions,
    ) -> RunnableConfig:
        """Save or update a checkpoint in the MongoDB database.

        If a checkpoint with the same ID exists, it is updated; otherwise, a new checkpoint is created.

        Args:
            config (RunnableConfig): The configuration associated with the checkpoint.
            checkpoint (Checkpoint): The checkpoint data to save or update.
            metadata (CheckpointMetadata): Additional metadata associated with the checkpoint.
            new_versions (ChannelVersions): New channel versions as of this write.

        Returns:
            RunnableConfig: Updated configuration after storing the checkpoint.
        """
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

        update_doc = {
            "thread_id": thread_id,
            "messages": all_messages,
        }

        # Use upsert to either update the existing document or create a new one if it does not exist
        self.db["checkpoints"].update_one({"thread_id": thread_id}, {"$set": update_doc}, upsert=True)

        return {
            "configurable": {
                "thread_id": thread_id,
            }
        }




    def put_writes(
        self,
        config: RunnableConfig,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
    ) -> None:
        """Store intermediate writes linked to a checkpoint.

        This method saves intermediate writes associated with a checkpoint to the MongoDB database.

        Args:
            config (RunnableConfig): Configuration of the related checkpoint.
            writes (Sequence[Tuple[str, Any]]): List of writes to store, each as (channel, value) pair.
            task_id (str): Identifier for the task creating the writes.
        """
        pass