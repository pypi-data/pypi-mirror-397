#!/usr/bin/env python3
"""
MCP Server for OpenAI Agents SDK Documentation
Provides tools for querying and exploring OpenAI Agents SDK documentation.
"""

import asyncio
import json
from typing import Optional
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
import mcp.server.stdio

# Import our documentation functions
from .documentation import (
    load_or_refresh_index,
    get_documentation_for_feature,
    fetch_documentation_content,
    DOCS_INDEX_FILE
)

# Initialize the MCP server
server = Server("openai-agents-sdk-docs")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools for the MCP server."""
    return [
        Tool(
            name="list_documentation_topics",
            description=(
                "Get a complete list of all available documentation topics/modules "
                "from the OpenAI Agents SDK. Returns a JSON object mapping topic names "
                "to their documentation URLs. This is useful for discovering what "
                "documentation is available."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "force_refresh": {
                        "type": "boolean",
                        "description": "Force refresh the index from the website (default: false)",
                        "default": False
                    }
                },
                "required": []
            }
        ),
        Tool(
            name="get_documentation",
            description=(
                "Search for and retrieve documentation for a specific feature, module, "
                "or topic from the OpenAI Agents SDK. Uses AI to intelligently match "
                "your query to the most relevant documentation page. Accepts natural "
                "language queries like 'handoffs', 'how to stream responses', or "
                "'tracing agents'. Returns the matched topic, URL, and full documentation content."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": (
                            "The feature, module, or topic you want documentation for. "
                            "Can be a simple name like 'handoffs' or a natural language "
                            "question like 'how do I trace my agent'"
                        )
                    },
                    "include_content": {
                        "type": "boolean",
                        "description": "Whether to include the full documentation content (default: true)",
                        "default": True
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool calls from the MCP client."""
    
    if name == "list_documentation_topics":
        # Get the documentation index
        force_refresh = arguments.get("force_refresh", False)
        
        try:
            doc_map = load_or_refresh_index(force_refresh=force_refresh)
            
            # Format the response
            response_text = f"Found {len(doc_map)} documentation topics:\n\n"
            response_text += json.dumps(doc_map, indent=2, ensure_ascii=False)
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            error_msg = f"Error loading documentation index: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    elif name == "get_documentation":
        query = arguments.get("query")
        include_content = arguments.get("include_content", True)
        
        if not query:
            return [TextContent(type="text", text="Error: 'query' parameter is required")]
        
        try:
            # Find the matching documentation
            topic, url = get_documentation_for_feature(query)
            
            if not topic or not url:
                # Provide suggestions
                doc_map = load_or_refresh_index()
                suggestions = list(doc_map.keys())[:10]
                
                response_text = f"No matching documentation found for '{query}'.\n\n"
                response_text += "Here are some available topics:\n"
                for suggestion in suggestions:
                    response_text += f"  - {suggestion}\n"
                
                return [TextContent(type="text", text=response_text)]
            
            # Build response
            response_text = f"✓ Found: {topic}\n"
            response_text += f"URL: {url}\n\n"
            
            # Fetch content if requested
            if include_content:
                content = fetch_documentation_content(url)
                if content:
                    response_text += "=" * 80 + "\n"
                    response_text += "DOCUMENTATION CONTENT:\n"
                    response_text += "=" * 80 + "\n\n"
                    response_text += content
                else:
                    response_text += "Warning: Could not fetch documentation content."
            
            return [TextContent(type="text", text=response_text)]
            
        except Exception as e:
            error_msg = f"Error retrieving documentation: {str(e)}"
            return [TextContent(type="text", text=error_msg)]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


def start_server():
    """Start the MCP server (entry point for package)."""
    asyncio.run(main())


async def main():
    """Run the MCP server."""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    start_server()
