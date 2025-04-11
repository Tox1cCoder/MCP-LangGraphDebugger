# LangGraph Agent with MCP

## Project Overview

![project architecture](./assets/architecture.png)

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
4. 
## Quick Start with Docker

You can easily run this project using Docker without setting up a local Python environment.

### Requirements (Docker Desktop)

Install Docker Desktop from the link below:

- [Install Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Run with Docker Compose

1. Navigate to the `dockers` directory

```bash
cd dockers
```

2. Create a `.env` file with your API keys in the project root directory.

```bash
cp .env.example .env
```

Enter your obtained API keys in the `.env` file.

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key
```

3. Select the Docker Compose file that matches your system architecture.

**AMD64/x86_64 Architecture (Intel/AMD Processors)**

```bash
# Run container
docker compose up -d -f docker-compose.yaml
```

**ARM64 Architecture (Apple Silicon M1/M2/M3)**

```bash
# Run container
docker compose up -d -f docker-compose-mac.yaml
```

4. Access the application in your browser at http://localhost:8585

## Install Directly from Source Code

1. Clone this repository

```bash
git clone https://github.com/Tox1cCoder/MCP-LangGraphDebugger.git
cd MCP-LangGraphDebugger
```

2. Create a virtual environment and install dependencies using uv

```bash
uv venv
uv pip install -r requirements.txt
source .venv/bin/activate  # For Windows: .venv\Scripts\activate
```

3. Create a `.env` file with your API keys (copy from `.env.example`)

```bash
cp .env.example .env
```

Enter your obtained API keys in the `.env` file.

```bash
ANTHROPIC_API_KEY=your_anthropic_api_key
OPENAI_API_KEY=your_openai_api_key(optional)
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_API_KEY=your_langsmith_api_key
LANGSMITH_PROJECT=your_langsmith_project
```

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

1. Start the Streamlit application. (The Korean version file is `app_KOR.py`.)

```bash
streamlit run app_KOR.py
```

2. The application will run in the browser and display the main interface.

3. Use the sidebar to add and configure MCP tools

Visit [Smithery](https://smithery.ai/) to find useful MCP servers.

First, select the tool you want to use.

Click the COPY button in the JSON configuration on the right.

![copy from Smithery](./assets/smithery-copy-json.png)

Paste the copied JSON string in the `Tool JSON` section.

<img src="./assets/add-tools.png" alt="tool json" style="width: auto; height: auto;">

Click the `Add Tool` button to add it to the "Registered Tools List" section.

Finally, click the "Apply" button to apply the changes to initialize the agent with the new tools.

<img src="./assets/apply-tool-configuration.png" alt="tool json" style="width: auto; height: auto;">

4. Check the agent's status.

![check status](./assets/check-status.png)

5. Interact with the ReAct agent that utilizes the configured MCP tools by asking questions in the chat interface.

![project demo](./assets/project-demo.png)
