from uuid import NAMESPACE_OID
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition, BaseTool
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from dotenv import load_dotenv
import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
import requests
import aiosqlite


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

@tool
def get_stock_price(symbol: str) -> dict:
    """
    Fetch latest stock price for a given symbol (e.g. 'AAPL', 'TSLA') 
    using Alpha Vantage with API key in the URL.
    """
    url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey=C9PE94QUEW9VWGFM"
    r = requests.get(url)
    return r.json()

search_tool = DuckDuckGoSearchRun(region="us-en")

def load_mcp_tool() -> list[BaseTool]:
        try:
            return run_async(client.get_tools())

        except Exception:
            return[]
mcp_tools = load_mcp_tool()

tools = [search_tool, get_stock_price, *mcp_tools]
llm_with_tools = llm.bind_tools(tools) if tools else llm


# 3. State
class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# Define nodes
async def chat_node(state: ChatState):
        """LLM node that may answer or request a tool call."""
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

tool_node = ToolNode(tools) if tools else None

# checkpointer
async def _init_checkpointer():
    conn = await aiosqlite.connect(database="chatbot.db", check_same_thread=False)
    return AsyncSqliteSaver(conn=conn)

checkpointer = run_async(_init_checkpointer())
# Graph
graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")

if tool_node:
    graph.add_node("tools", tool_node)
    graph.add_conditional_edges("chat_node",tools_condition)
    graph.add_edge('tools', 'chat_node')
else:
    graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)

async def mian():
    result = await chatbot.ainvoke({"messages": [HumanMessage(content="what is multiply of 155 and 33")]})

    print(result["messages"][-1].content)

if __name__ == '__main__':
    asyncio.run(mian())
