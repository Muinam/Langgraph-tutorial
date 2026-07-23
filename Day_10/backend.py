from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
import os 
import sqlite3

load_dotenv()

llm = ChatOpenAI(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("Grok_Api_key"),
    base_url="https://api.groq.com/openai/v1"
)


class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    messages = state['messages']
    response = llm.invoke(messages)
    return {"messages": [response]}

con = sqlite3.connect(database='chatbot.db', check_same_thread=False)

# Checkpointer
checkpointer = SqliteSaver(conn=con)

graph = StateGraph(ChatState)
graph.add_node("chat_node", chat_node)
graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


def retrieve_all_threads():
    all_threads = set()
    for checkpoint in checkpointer.list(None):
        all_threads.add(checkpoint.config['configurable']['thread_id'])

    return list(all_threads)


# CONFIG = {'configurable': {'thread_id':'thread_1'}}

# response=chatbot.invoke(
#                 {"messages": [HumanMessage(content='What is my name')]},
#                 config=CONFIG
#             )

# print(response)