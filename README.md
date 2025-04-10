# LangGraph Agent with MCP

## Project Overview

`LangChain-MCP-Adapters` is a toolkit provided by **LangChain AI** that enables AI agents to interact with external tools and data sources through the Model Context Protocol (MCP). This project provides a user-friendly interface for deploying ReAct agents that can access various data sources and APIs through MCP tools.

### Features

- **Streamlit Interface**: User-friendly web interface for interacting with LangGraph `ReAct Agent` with MCP tools
- **Tool Management**: Add, remove, and configure MCP tools directly through the UI(supports Smithery JSON Format). This happens dynamically without restarting the application.
- **Streaming Responses**: See agent responses and tool calls in real-time
- **Conversation History**: Track and manage your conversation with the agent

## MCP Architecture

MCP (Model Context Protocol) consists of three main components.

1. **MCP Host**: Programs that want to access data through MCP, such as Claude Desktop, IDEs, or LangChain/LangGraph.

2. **MCP Client**: Protocol clients that maintain 1:1 connections with servers, acting as intermediaries between hosts and servers.

3. **MCP Server**: Lightweight programs that expose specific functionalities through the standardized model context protocol, serving as key data sources.

## Installation

1. Clone this repository

```bash
git clone https://github.com/Tox1cCoder/MCP-LangGraphDebugger.git
cd langgraph-mcp-agents
```

2. Create a virtual environment and install dependencies using uv

```bash
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
```

3. Create a `.env` file with your API keys(from `.env.example`)

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key(optional)
TAVILY_API_KEY=your_tavily_api_key(optional)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=your_langsmith_project
```
## Usage

1. Start the Streamlit application.

```bash
streamlit run app.py
```

2. The application will launch in your browser, displaying the main interface.

3. Use the sidebar to add and configure MCP tools

You may visit to [Smithery](https://smithery.ai/) to find useful MCP servers.
