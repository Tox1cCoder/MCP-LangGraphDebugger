# LangGraph Agent with MCP

## MCP Architecture

MCP (Model Context Protocol) consists of three main components.

1. **MCP Host**: Programs that want to access data through MCP, such as Claude Desktop, IDEs, or LangChain/LangGraph.

2. **MCP Client**: Protocol clients that maintain 1:1 connections with servers, acting as intermediaries between hosts and servers.

3. **MCP Server**: Lightweight programs that expose specific functionalities through the standardized model context protocol, serving as key data sources.
