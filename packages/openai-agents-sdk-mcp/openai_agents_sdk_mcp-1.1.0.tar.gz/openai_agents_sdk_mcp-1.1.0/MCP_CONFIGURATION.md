# MCP Configuration Examples

This document provides example configurations for various MCP clients.

> **Important**: This tool requires an OpenAI API key to function. The key is used for intelligent documentation matching via GPT-4o-mini. Make sure to include it in your configuration.

## Prerequisites

1. **Get an OpenAI API key**: 
   - Sign up at [OpenAI Platform](https://platform.openai.com/)
   - Generate an API key from the [API keys page](https://platform.openai.com/api-keys)
   
2. **Install the package**:
   ```bash
   pip install openai-agents-sdk-mcp
   ```

## Claude Desktop Configuration

Add this to your Claude Desktop configuration file:

### macOS
Location: `~/Library/Application Support/Claude/claude_desktop_config.json`

### Windows
Location: `%APPDATA%/Claude/claude_desktop_config.json`

### Configuration

```json
{
  "mcpServers": {
    "openai-agents-sdk-docs": {
      "command": "/absolute/path/to/openai-agent-sdk-mcp/.venv/bin/python",
      "args": [
        "/absolute/path/to/openai-agent-sdk-mcp/server.py"
      ],
      "env": {
        "OPENAI_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

**Important**: 
- Replace `/absolute/path/to/` with the actual absolute path to your installation
- **Replace `sk-your-api-key-here` with your actual OpenAI API key** - the tool will not work without it

### Quick Path Setup

To get the absolute path:

```bash
cd /path/to/openai-agent-sdk-mcp
pwd  # Copy this path
```

Then use:
- Python: `<path-from-pwd>/.venv/bin/python`
- Server: `<path-from-pwd>/server.py`

## VS Code / Cursor Configuration

For VS Code or Cursor using MCP, add to your workspace settings:

```json
{
  "mcp.servers": {
    "openai-agents-sdk-docs": {
      "command": "/absolute/path/to/.venv/bin/python",
      "args": ["/absolute/path/to/server.py"],
      "env": {
        "OPENAI_API_KEY": "sk-your-api-key-here"
      }
    }
  }
}
```

## Environment Variable Setup

Instead of hardcoding the API key in the config, you can:

1. Set it in your system environment:
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

2. Use it in config:
   ```json
   {
     "mcpServers": {
       "openai-agents-sdk-docs": {
         "command": "/path/to/.venv/bin/python",
         "args": ["/path/to/server.py"]
       }
     }
   }
   ```

The server will automatically load from `.env` file or system environment.

## Testing Your Configuration

After configuration, restart your MCP client (Claude Desktop, VS Code, etc.) and verify:

1. The server appears in the MCP tools list
2. You can call `list_documentation_topics`
3. You can query documentation with `get_documentation`

## Example Usage in Claude

Once configured, you can ask Claude:

- "List all available OpenAI Agents SDK documentation topics"
- "Get documentation for handoffs"
- "How do I use streaming in OpenAI Agents?"
- "Show me documentation about guardrails"

Claude will use the MCP tools to fetch and provide the documentation.
