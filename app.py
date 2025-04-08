import streamlit as st
import asyncio
import nest_asyncio
import json

nest_asyncio.apply()

if "event_loop" not in st.session_state:
    loop = asyncio.new_event_loop()
    st.session_state.event_loop = loop
    asyncio.set_event_loop(loop)

from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_teddynote.messages import astream_graph, random_uuid
from langchain_core.messages.ai import AIMessageChunk
from langchain_core.messages.tool import ToolMessage
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.runnables import RunnableConfig

load_dotenv(override=True)

st.set_page_config(page_title="Agent with MCP Tools", page_icon="🧠", layout="wide")

st.sidebar.divider()

st.title("Agent with MCP Tools")
st.markdown("Ask questions to the ReAct agent using MCP tools.")

if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = False
    st.session_state.agent = None
    st.session_state.history = []
    st.session_state.mcp_client = None
    st.session_state.timeout_seconds = (
        120 
    )

if "thread_id" not in st.session_state:
    st.session_state.thread_id = random_uuid()
