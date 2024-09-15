from utils.imports import *
from configs.ConfigEnv import *
from configs.ConfigStates import *

from utils.imports import *
from configs.ConfigEnv import *
from configs.ConfigStates import *

class StateSaver:
    def __init__(self):
        self.collection = collection_checkpoint
        self.llm = llm
        self.max_messages = 5
        print("initialized memory")
        
    def __call__(self, state: AgentState):
        self.state = state
        self.put()
        
    def test(self):
        print("test success")

    def put(self):
        messages = self.state.get("messages", "")
        print(len(messages), self.max_messages)
        if len(messages) > self.max_messages:
            self.state["short_memory"] = self._create_short_memory(messages[-self.max_messages:])
            self.state["long_memory"] = self._update_long_memory(self.state["short_memory"])
            # No need to delete messages from the state as we now maintain a full history
        
        self._save_checkpoint()
        
    def _save_checkpoint(self) -> None:
        checkpoint_data = {
            "messages": [msg.content for msg in self.state.get("messages", [])],
            "short_memory": self.state.get("short_memory", ""),
            "long_memory": self.state.get("long_memory", ""),
            "checkpoint_id": "",  # Ensure this is a unique or appropriate identifier for the checkpoint
        }

        existing_checkpoint = self.collection.find_one({"checkpoint_id": ""})
        if existing_checkpoint:
            # Append new messages to existing ones instead of replacing them
            updated_messages = existing_checkpoint["messages"] + [msg.content for msg in self.state.get("messages", [])]
            checkpoint_data["messages"] = updated_messages
            self.collection.update_one(
                {"checkpoint_id": checkpoint_data["checkpoint_id"]},
                {"$set": checkpoint_data}
            )
        else:
            self.collection.insert_one(checkpoint_data)
        
    def _create_short_memory(self, messages: List[BaseMessage]) -> str:
        summary_prompt = f"Note down important details from the conversation below:\n\n{messages}"
        response = self.llm.invoke(summary_prompt).content
        print("short memory Success")
        return response

    def _update_long_memory(self, short_memory: str) -> str:
        update_prompt = f"Current long-term memory: {self.state.get('long_memory', '')}\n\nNew information: {short_memory}\n\nUpdate the long-term memory to include the new information concisely."
        response = self.llm.invoke(update_prompt).content
        print("long memory Success")
        return response

    @tool
    def load_checkpoint(self, query: str) -> AgentState:
        """Load a checkpoint by its ID."""
        checkpoint = self.collection.find_one({"checkpoint_id": "latest"})
        if checkpoint:
            return AgentState(
                messages=[BaseMessage(content=msg) for msg in checkpoint["messages"]],
                short_memory=checkpoint["short_memory"],
                long_memory=checkpoint["long_memory"]
            )
        else:
            print("No checkpoint data found. Please create one.")

    @tool
    def save_checkpoint(self, query: str = "") -> str:
        """Save the current state as a checkpoint."""
        checkpoint_data = {
            "messages": self.state.get("messages", ""),
            "short_memory": self.state.get("short_memory", ""),
            "long_memory": self.state.get("long_memory", ""),
            "checkpoint_id": "latest",
        }

        existing_checkpoint = self.collection.find_one({"checkpoint_id": "latest"})
        if existing_checkpoint:
            # Append new messages to the existing ones
            updated_messages = existing_checkpoint["messages"] + [msg.content for msg in self.state.get("messages", [])]
            checkpoint_data["messages"] = updated_messages
            self.collection.update_one(
                {"checkpoint_id": "latest"},
                {"$set": checkpoint_data}
            )
        else:
            self.collection.insert_one(checkpoint_data)
        print("Checkpoint saved successfully.")

    def get_tools(self):
        return [self.save_checkpoint, self.load_checkpoint]
