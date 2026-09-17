import asyncio
import json
import os
import dotenv
from pydantic import BaseModel
import streamlit as st
from fastmcp import Client
from langchain_groq import ChatGroq
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.tools import BaseTool

# Load environment variables
dotenv.load_dotenv()

# Page configuration
st.set_page_config(page_title="MCP AI Assistant", page_icon="🤖", layout="centered")
st.title("🤖 MCP Agent Chatbot with Streamlit")

# Define Input Schemas
class EmailInput(BaseModel):
    to: str
    subject: str
    body: str

class AddInput(BaseModel):
    a: int
    b: int

# Initialize FastMCP Client pointing to the root server URL
client = Client("http://127.0.0.1:8000/mcp")

async def call_mcp_tool(tool_name: str, **kwargs):
    async with client:
        return await client.call_tool(tool_name, kwargs)

async def get_all_tools():
    async with client:
        return await client.list_tools()

# Fetch tools once and cache or load them safely
# Fetch tools once and cache or load them safely
@st.cache_resource
def load_mcp_tools_metadata():
    try:
        return asyncio.run(get_all_tools())
    except Exception as e:
        st.error(f"⚠️ Debug Error: {str(e)}")
        return None

mcp_tools = load_mcp_tools_metadata()
if not mcp_tools:
    st.error("⚠️ Could not connect to the MCP Server. Make sure `ai_mcp.py` is running on port 8000!")
    st.stop()
else:
    st.sidebar.success(f"Connected to MCP Server! Tools available: {[t.name for t in mcp_tools]}")

# Define LangChain/LangGraph Tool Wrapper
class MCPTool(BaseTool):
    name: str
    description: str
    mcp_tool_name: str

    class Config:
        arbitrary_types_allowed = True

    def _run(self, **kwargs) -> str:
        result = asyncio.run(call_mcp_tool(self.mcp_tool_name, **kwargs))
        return str(result)

    async def _arun(self, tool_input: str) -> str:
        params = json.loads(tool_input)
        result = await call_mcp_tool(self.mcp_tool_name, **params)
        return str(result)

tools = [
    MCPTool(
        name="send_email",
        description="Send an email. Requires: to (email), subject, body",
        mcp_tool_name="send_email",
        args_schema=EmailInput
    ),
    MCPTool(
        name="add",
        description="Add two numbers. Requires: a (int), b (int)",
        mcp_tool_name="add",
        args_schema=AddInput
    ),
]

# Initialize LLM & Agent Graph
@st.cache_resource
def get_agent():
    llm = ChatGroq(
        model="openai/gpt-oss-120b",
        temperature=0,
        api_key=os.getenv("GROQ_API_KEY")
    )
    memory = InMemorySaver()
    return create_agent(
        model=llm,
        tools=tools,
        checkpointer=memory,
        system_prompt="You are a helpful assistant capable of executing tools."
    )

helpful_assistant = get_agent()

# Streamlit Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display prior chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# React to user input
if user_input := st.chat_input("Ask me to send an email or do math..."):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking and executing tools..."):
            try:
                # Invoke LangGraph agent
                response = helpful_assistant.invoke(
                    {"messages": [{"role": "user", "content": user_input}]},
                    config={"configurable": {"thread_id": "123"}}
                )
                assistant_reply = response["messages"][-1].content if "messages" in response else str(response)
            except Exception as e:
                assistant_reply = f"An error occurred: {str(e)}"
            
            st.markdown(assistant_reply)
            st.session_state.messages.append({"role": "assistant", "content": assistant_reply})