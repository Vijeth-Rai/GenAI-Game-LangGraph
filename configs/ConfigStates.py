from utils.imports import *
from configs.ConfigEnv import *



class AgentState(MessagesState):
    short_memory: str
    long_memory: str
    next: str
    next_history: List[str]