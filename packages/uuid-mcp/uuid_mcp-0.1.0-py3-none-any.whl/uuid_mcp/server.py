#!/usr/bin/env python3
"""
Simple MCP server that provides a UUID generation tool.
"""
import asyncio
import uuid
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Create the MCP server instance
server = Server("uuid-generator")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="generate_uuid",
            description="Generate a random UUID (version 4)",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    if name == "generate_uuid":
        generated_uuid = str(uuid.uuid4())
        return [
            TextContent(
                type="text",
                text=generated_uuid
            )
        ]
    else:
        raise ValueError(f"Unknown tool: {name}")

def main():
    """Run the MCP server."""
    asyncio.run(_main())

async def _main():
    """Internal async main function."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    main()

