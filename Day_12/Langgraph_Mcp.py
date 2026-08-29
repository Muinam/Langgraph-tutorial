from uuid import NAMESPACE_OID
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.tools import tool
from dotenv import load_dotenv
import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient

load_dotenv()

llm = ChatOpenAI(
    model="llama-3.1-8b-instant",
    api_key=os.getenv("Grok_Api_key"),
    base_url="https://api.groq.com/openai/v1"
)

client = MultiServerMCPClient(
    {
        'arith':{
            'transport': 'stdio',
            'command': 'python3',
            'args': [r"D:\LangGraph\Day_12\mcp\arith_mcp.py"]
        },
        "expense": {
            'transport': "streamable_http",
            'url': "https://relieved-pink-marmoset.fastmcp.app/mcp"
        }
    }
)


# 3. State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


async def build_graph():
     
    tools = await client.get_tools()
    llm_with_tools = llm.bind_tools(tools)
    
    # nodes
    async def chat_node(state: ChatState):
        """LLM node that may answer or request a tool call."""
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")

    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge('tools', 'chat_node')

    chatbot = graph.compile()
    return chatbot

async def mian():
    chatbot = await build_graph()
    result = await chatbot.ainvoke({"messages": [HumanMessage(content="what is multiply of 155 and 33")]})

    print(result["messages"][-1].content)

if __name__ == '__main__':
    asyncio.run(mian())
