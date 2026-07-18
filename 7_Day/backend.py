from langgraph.graph import START, END, StateGraph
from typing import TypedDict, Annotated
from langgraph.graph.message import BaseMessage, add_messages
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from dotenv import load_dotenv
import os
load_dotenv()


model = ChatOpenAI(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("Grok_Api_key"),
    base_url="https://api.groq.com/openai/v1"
)


class ChatState(TypedDict):
    messages : Annotated[list[BaseMessage], add_messages]


def ai_chat(state:ChatState):
    responce = model.invoke(state["messages"])
    return {"messages":[responce]}


checkpointer = InMemorySaver()
graph = StateGraph(ChatState)
graph.add_node('ai_chat', ai_chat)
graph.add_edge(START, 'ai_chat')
graph.add_edge('ai_chat', END)
chatbot = graph.compile(checkpointer=checkpointer)