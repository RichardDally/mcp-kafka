import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run_client():
    # 1. Define the command to start the server over stdio
    # This acts identically to an LLM host launching the server process
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "mcp-kafka", "start-server"]
    )

    print(f"Connecting to MCP Server via: {server_params.command} {' '.join(server_params.args)}...")

    # 2. Connect to the server's standard input and output
    async with stdio_client(server_params) as (read, write):
        # 3. Create a session and initialize the protocol handshakes
        async with ClientSession(read, write) as session:
            await session.initialize()
            print("Successfully initialized Client Session!\n")
            
            # 4. Ask the server what tools it has available
            print("--- Discovering Tools ---")
            tools_response = await session.list_tools()
            for tool in tools_response.tools:
                print(f"Discovered tool: '{tool.name}' -> {tool.description}")
            print("\n")
            
            # 5. Programmatically call the `get_usage_metrics` tool
            print("--- Calling get_usage_metrics ---")
            result1 = await session.call_tool("get_usage_metrics", arguments={})
            # result.content is a list of content blocks (text, image, etc). We want the text block.
            for content_block in result1.content:
                if content_block.type == "text":
                    print(f"Result: {content_block.text}\n")
            
            # 6. Programmatically call the `count_action` tool with arguments
            print("--- Calling count_action with action_name='play' ---")
            result2 = await session.call_tool("count_action", arguments={"action_name": "play"})
            for content_block in result2.content:
                if content_block.type == "text":
                    print(f"Result: {content_block.text}\n")
