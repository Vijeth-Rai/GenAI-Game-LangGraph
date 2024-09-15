import os
from pymongo import MongoClient
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain.schema import HumanMessage, AIMessage
from langchain_core.messages import BaseMessage, RemoveMessage, SystemMessage
from langgraph.graph import MessagesState, StateGraph, START, END
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode

from typing import Annotated, Literal, TypedDict
