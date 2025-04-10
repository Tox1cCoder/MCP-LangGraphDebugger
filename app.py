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

async def cleanup_mcp_client():
    """
    Safely terminate the existing MCP client.

    Properly releases resources if an existing client exists.
    """
    if "mcp_client" in st.session_state and st.session_state.mcp_client is not None:
        try:

            await st.session_state.mcp_client.__aexit__(None, None, None)
            st.session_state.mcp_client = None
        except Exception as e:
            import traceback

def print_message():
    """
    Display chat history on screen.

    Distinguishes between user and assistant messages on screen,
    and displays tool call information within the assistant message container.
    """
    i = 0
    while i < len(st.session_state.history):
        message = st.session_state.history[i]

        if message["role"] == "user":
            st.chat_message("user").markdown(message["content"])
            i += 1
        elif message["role"] == "assistant":
            with st.chat_message("assistant"):
                st.markdown(message["content"])

                if (
                    i + 1 < len(st.session_state.history)
                    and st.session_state.history[i + 1]["role"] == "assistant_tool"
                ):
                    with st.expander("🔧 Tool Call Information", expanded=False):
                        st.markdown(st.session_state.history[i + 1]["content"])
                    i += 2
                else:
                    i += 1
        else:
            i += 1

def get_streaming_callback(text_placeholder, tool_placeholder):
    """
    Create a streaming callback function.

    Parameters:
        text_placeholder: Streamlit component to display text responses
        tool_placeholder: Streamlit component to display tool call information

    Returns:
        callback_func: Streaming callback function
        accumulated_text: List to store accumulated text responses
        accumulated_tool: List to store accumulated tool call information
    """
    accumulated_text = []
    accumulated_tool = []

    def callback_func(message: dict):
            nonlocal accumulated_text, accumulated_tool
            message_content = message.get("content", None)
    
            if isinstance(message_content, AIMessageChunk):
                content = message_content.content
                if isinstance(content, list) and len(content) > 0:
                    message_chunk = content[0]
                    if message_chunk["type"] == "text":
                        accumulated_text.append(message_chunk["text"])
                        text_placeholder.markdown("".join(accumulated_text))
                    elif message_chunk["type"] == "tool_use":
                        if "partial_json" in message_chunk:
                            accumulated_tool.append(message_chunk["partial_json"])
                        else:
                            tool_call_chunks = message_content.tool_call_chunks
                            tool_call_chunk = tool_call_chunks[0]
                            accumulated_tool.append(
                                "\n```json\n" + str(tool_call_chunk) + "\n```\n"
                            )
                        with tool_placeholder.expander(
                            "🔧 Tool Call Information", expanded=True
                        ):
                            st.markdown("".join(accumulated_tool))
            elif isinstance(message_content, ToolMessage):
                accumulated_tool.append(
                    "\n```json\n" + str(message_content.content) + "\n```\n"
                )
                with tool_placeholder.expander("🔧 Tool Call Information", expanded=True):
                    st.markdown("".join(accumulated_tool))
            return None
    
        return callback_func, accumulated_text, accumulated_tool

async def process_query(query, text_placeholder, tool_placeholder, timeout_seconds=60):
    """
    Process user questions and generate responses.

    Parameters:
        query: Text of the question entered by the user
        text_placeholder: Streamlit component to display text responses
        tool_placeholder: Streamlit component to display tool call information
        timeout_seconds: Response generation time limit (seconds)

    Returns:
        response: Agent's response object
        final_text: Final text response
        final_tool: Final tool call information
    """
    try:
        if st.session_state.agent:
            streaming_callback, accumulated_text_obj, accumulated_tool_obj = (
                get_streaming_callback(text_placeholder, tool_placeholder)
            )
            try:
                response = await asyncio.wait_for(
                    astream_graph(
                        st.session_state.agent,
                        {"messages": [HumanMessage(content=query)]},
                        callback=streaming_callback,
                        config=RunnableConfig(
                            recursion_limit=100, thread_id=st.session_state.thread_id
                        ),
                    ),
                    timeout=timeout_seconds,
                )
            except asyncio.TimeoutError:
                error_msg = f"⏱️ Request time exceeded {timeout_seconds} seconds. Please try again later."
                return {"error": error_msg}, error_msg, ""

            final_text = "".join(accumulated_text_obj)
            final_tool = "".join(accumulated_tool_obj)
            return response, final_text, final_tool
        else:
            return (
                {"error": "🚫 Agent has not been initialized."},
                "🚫 Agent has not been initialized.",
                "",
            )
    except Exception as e:
        import traceback

        error_msg = f"❌ Error occurred during query processing: {str(e)}\n{traceback.format_exc()}"
        return {"error": error_msg}, error_msg, ""


async def initialize_session(mcp_config=None):
    """
    Initialize MCP session and agent.

    Parameters:
        mcp_config: MCP tool configuration (JSON). Use default settings if None

    Returns:
        bool: Initialization success status
    """
    try:
        with st.spinner("🔄 Connecting to MCP server..."):
            await cleanup_mcp_client()

            if mcp_config is None:
                mcp_config = {
                    "weather": {
                        "command": "python",
                        "args": ["./mcp_server_local.py"],
                        "transport": "stdio",
                    },
                }
            client = MultiServerMCPClient(mcp_config)
            await client.__aenter__()
            tools = client.get_tools()
            st.session_state.tool_count = len(tools)
            st.session_state.mcp_client = client

            model = ChatAnthropic(
                model="claude-3-7-sonnet-latest", temperature=0.1, max_tokens=20000
            )
            agent = create_react_agent(
                model,
                tools,
                checkpointer=MemorySaver(),
                prompt="Use your tools to answer the question. Answer in English.",
            )
            st.session_state.agent = agent
            st.session_state.session_initialized = True
            return True
    except Exception as e:
        st.error(f"❌ Error during initialization: {str(e)}")
        import traceback

        st.error(traceback.format_exc())
        return False


with st.sidebar.expander("Add MCP Tools", expanded=False):
    default_config = """{
  "weather": {
    "command": "python",
    "args": ["./mcp_server_local.py"],
    "transport": "stdio"
  }
}"""
    if "pending_mcp_config" not in st.session_state:
        try:
            st.session_state.pending_mcp_config = json.loads(
                st.session_state.get("mcp_config_text", default_config)
            )
        except Exception as e:
            st.error(f"Failed to set initial pending config: {e}")

    st.subheader("Add Individual Tool")
    st.markdown(
        """
    Enter **one tool** in JSON format:
    
    ```json
    {
      "tool_name": {
        "command": "execution_command",
        "args": ["arg1", "arg2", ...],
        "transport": "stdio"
      }
    }
    ```    
    ⚠️ **Important**: JSON must be wrapped in curly braces (`{}`).
    """
    )

    example_json = {
        "github": {
            "command": "npx",
            "args": [
                "-y",
                "@smithery/cli@latest",
                "run",
                "@smithery-ai/github",
                "--config",
                '{"githubPersonalAccessToken":"your_token_here"}',
            ],
            "transport": "stdio",
        }
    }

    default_text = json.dumps(example_json, indent=2, ensure_ascii=False)

    new_tool_json = st.text_area(
        "Tool JSON",
        default_text,
        height=250,
    )

    if st.button(
        "Add Tool",
        type="primary",
        key="add_tool_button",
        use_container_width=True,
    ):
        try:
            if not new_tool_json.strip().startswith(
                "{"
            ) or not new_tool_json.strip().endswith("}"):
                st.error("JSON must start and end with curly braces ({}).")
                st.markdown('Correct format: `{ "tool_name": { ... } }`')
            else:
                parsed_tool = json.loads(new_tool_json)

                if "mcpServers" in parsed_tool:
                    parsed_tool = parsed_tool["mcpServers"]
                    st.info("'mcpServers' format detected. Converting automatically.")

                if len(parsed_tool) == 0:
                    st.error("Please enter at least one tool.")
                else:
                    success_tools = []
                    for tool_name, tool_config in parsed_tool.items():
                        if "url" in tool_config:
                            tool_config["transport"] = "sse"
                            st.info(
                                f"URL detected in '{tool_name}' tool, setting transport to 'sse'."
                            )
                        elif "transport" not in tool_config:
                            tool_config["transport"] = "stdio"

                        if "command" not in tool_config and "url" not in tool_config:
                            st.error(
                                f"'{tool_name}' tool configuration requires either 'command' or 'url' field."
                            )
                        elif "command" in tool_config and "args" not in tool_config:
                            st.error(
                                f"'{tool_name}' tool configuration requires 'args' field."
                            )
                        elif "command" in tool_config and not isinstance(
                            tool_config["args"], list
                        ):
                            st.error(
                                f"'args' field in '{tool_name}' tool must be an array ([]) format."
                            )
                        else:
                            st.session_state.pending_mcp_config[tool_name] = tool_config
                            success_tools.append(tool_name)

                    if success_tools:
                        if len(success_tools) == 1:
                            st.success(
                                f"{success_tools[0]} tool has been added. Press 'Apply' button to apply changes."
                            )
                        else:
                            tool_names = ", ".join(success_tools)
                            st.success(
                                f"Total {len(success_tools)} tools ({tool_names}) have been added. Press 'Apply' button to apply changes."
                            )
        except json.JSONDecodeError as e:
            st.error(f"JSON parsing error: {e}")
            st.markdown(
                f"""
            **How to fix**:
            1. Check that your JSON format is correct.
            2. All keys must be wrapped in double quotes (").
            3. String values must also be wrapped in double quotes (").
            4. When using double quotes within a string, they must be escaped (\\").
            """
            )
        except Exception as e:
            st.error(f"Error occurred: {e}")

    st.divider()

    st.subheader("Current Tool Settings (Read-only)")
    st.code(
        json.dumps(st.session_state.pending_mcp_config, indent=2, ensure_ascii=False)
    )
