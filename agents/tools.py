from utils.imports import *
from configs.ConfigStates import *
from configs.ConfigEnv import *
from agents.MemoryAgent import *

config = {"configurable": {"thread_id": 1}}

llm = ChatGroq(
    groq_api_key=groq_api_key,
    model_name="llama3-groq-8b-8192-tool-use-preview"
)