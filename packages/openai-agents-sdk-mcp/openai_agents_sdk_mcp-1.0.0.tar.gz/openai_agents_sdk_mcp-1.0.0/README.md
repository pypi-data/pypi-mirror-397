# OpenAI Agents SDK MCP Tool

A Model Context Protocol (MCP) server that provides documentation for the OpenAI Agents SDK by extracting and indexing content from the official documentation website: https://openai.github.io/openai-agents-python/

This package can be installed as a Python library and used with any MCP-compatible LLM client (Claude Desktop, VS Code, Cursor, etc.).

## Installation

### From PyPI (Recommended)

```bash
pip install openai-agents-sdk-mcp
```

### From Source

```bash
git clone https://github.com/gavinz0228/openai-agents-sdk-mcp.git
cd openai-agents-sdk-mcp
pip install -e .
```

See [INSTALLATION.md](INSTALLATION.md) for detailed installation instructions.

## Overview

This project provides both a standalone CLI tool and an MCP server that allows LLMs to access and query the OpenAI Agents SDK documentation intelligently.

## Quick Start (MCP Server)

1. **Install the package**:
   ```bash
   pip install openai-agents-sdk-mcp
   ```

2. **Set up API key**:
   ```bash
   export OPENAI_API_KEY="sk-your-api-key-here"
   ```

3. **Configure your MCP client** (e.g., Claude Desktop):
   ```json
   {
     "mcpServers": {
       "openai-agents-sdk-docs": {
         "command": "openai-agents-sdk-mcp",
         "env": {
           "OPENAI_API_KEY": "sk-your-api-key-here"
         }
       }
     }
   }
   ```

4. **Start using it** - Ask your LLM:
   - "List all OpenAI Agents SDK documentation topics"
   - "Get documentation for handoffs"
   - "How do I use streaming in OpenAI Agents?"

See [INSTALLATION.md](INSTALLATION.md) and [MCP_CONFIGURATION.md](MCP_CONFIGURATION.md) for detailed setup instructions.

## Features

### 1. **MCP Server** (Primary Interface)
Exposes two tools for LLMs:

- **`list_documentation_topics`**: Get a complete list of all available documentation topics with their URLs
- **`get_documentation`**: Search for and retrieve documentation using natural language queries

### 2. **Automatic Documentation Indexing**
- Fetches and parses the OpenAI Agents SDK documentation website
- Extracts all navigation links and topics
- Creates a structured JSON map of topics to URLs
- Saves to `docs_index.json` for quick access

### 2. **Smart Index Management**
The tool automatically manages the documentation index with intelligent caching:

- **Missing Index Detection**: Automatically fetches fresh index if `docs_index.json` doesn't exist
- **Staleness Check**: Refreshes index if older than 1 day (configurable)
- **Link Validation**: Verifies all documentation links are working
- **Broken Link Recovery**: Automatically re-fetches index if any links are broken

### 3. **AI-Powered Feature Search**
Uses OpenAI's GPT-4o-mini to intelligently match user queries to documentation:

- Accepts natural language queries (e.g., "how do I trace my agent")
- Finds the closest matching documentation topic
- Fetches and displays relevant documentation content
- Works with fuzzy matching and conversational queries

## Installation

1. **Clone the repository**:
```bash
git clone https://github.com/gavinz0228/openai-agents-sdk-mcp.git
cd openai-agents-sdk-mcp
```

2. **Install the package**:
```bash
pip install -e .
```

3. **Configure API key**:
Create a `.env` file in your working directory:
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

Or set as environment variable:
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
```

See [INSTALLATION.md](INSTALLATION.md) for more installation options.

## Usage

### MCP Server (Recommended)

The MCP server allows LLMs to access the documentation through standardized tool calls.

#### Start the Server

```bash
openai-agents-sdk-mcp
```

Or if running from source:
```bash
python -m openai_agents_sdk_mcp.server
```

#### Configure MCP Client

Add to your MCP client configuration (e.g., Claude Desktop's config):

```json
{
  "mcpServers": {
    "openai-agents-sdk-docs": {
      "command": "openai-agents-sdk-mcp"
    }
  }
}
```

Or use the absolute path if installed in a virtual environment:

```json
{
  "mcpServers": {
    "openai-agents-sdk-docs": {
      "command": "/path/to/.venv/bin/openai-agents-sdk-mcp"
    }
  }
}
```

#### Available MCP Tools

**`list_documentation_topics`**
- Lists all available documentation topics
- Optional parameter: `force_refresh` (boolean) - Force refresh the index

Example:
```json
{
  "name": "list_documentation_topics",
  "arguments": {
    "force_refresh": false
  }
}
```

**`get_documentation`**
- Search and retrieve documentation for a specific feature
- Parameters:
  - `query` (string, required) - Feature name or natural language question
  - `include_content` (boolean, optional) - Whether to include full content (default: true)

Example:
```json
{
  "name": "get_documentation",
  "arguments": {
    "query": "handoffs",
    "include_content": true
  }
}
```

#### Test the Server

```bash
python test_mcp.py
```

### Command Line Interface

Use the CLI tool for quick documentation queries:

```bash
# List all documentation topics
openai-agents-docs

# Search for specific documentation
openai-agents-docs "handoffs"
openai-agents-docs "streaming"
openai-agents-docs "how to use guardrails"
```

### As a Python Library

```python
from openai_agents_sdk_mcp import (
    load_or_refresh_index,
    get_documentation_for_feature
)

# Load documentation index
doc_map = load_or_refresh_index()
print(f"Found {len(doc_map)} topics")

# Find documentation for a feature
topic, url = get_documentation_for_feature("handoffs")
if topic:
    print(f"Topic: {topic}")
    print(f"URL: {url}")
```

### Standalone CLI Tool (Legacy)

If running from source without installation:

#### Generate/Refresh Documentation Index

```bash
python openai_agents_sdk_mcp.py
```

This will:
- Fetch the latest documentation structure
- Extract all topics and links
- Save to `docs_index.json`
- Display all available topics

#### Search for Documentation

```bash
python openai_agents_sdk_mcp.py "feature name or query"
```

**Examples**:
```bash
# Simple feature name
python openai_agents_sdk_mcp.py "handoffs"

# Natural language query
python openai_agents_sdk_mcp.py "how do I stream responses"

# Topic search
python openai_agents_sdk_mcp.py "tracing and debugging"

# Multiple words
python openai_agents_sdk_mcp.py "realtime voice"
```

The tool will:
1. Load or refresh the documentation index (if stale)
2. Use AI to find the best matching topic
3. Display the matched topic and URL
4. Fetch and show a preview of the documentation content

## How It Works

### Index Management

```python
# The index is automatically managed:
# 1. Checks if docs_index.json exists
if not exists:
    fetch_fresh_index()

# 2. Checks if index is older than 1 day
if age > 1_day:
    fetch_fresh_index()

# 3. Validates all links are working
if broken_links_found:
    fetch_fresh_index()
```

### AI-Powered Matching

The tool uses OpenAI's GPT-4o-mini to match user queries to documentation topics:

1. Loads all available topics from the index
2. Sends user query + topic list to the LLM
3. LLM identifies the most relevant topic
4. Returns the matching topic and URL

This provides intelligent matching even for:
- Typos and misspellings
- Natural language questions
- Partial or fuzzy matches
- Related concepts

## Configuration

### Constants (in `openai_agents_sdk_mcp.py`)

```python
DOCS_INDEX_FILE = "docs_index.json"  # Index file name
INDEX_MAX_AGE_DAYS = 1               # Maximum age before refresh
```

### Environment Variables

- `OPENAI_API_KEY` - Required for AI-powered search functionality

## Files

- `server.py` - MCP server implementation
- `openai_agents_sdk_mcp.py` - Core functionality and CLI tool
- `test_mcp.py` - Test script for the MCP server
- `mcp_config.json` - Example MCP client configuration
- `docs_index.json` - Cached documentation index (auto-generated)
- `requirements.txt` - Python dependencies
- `.env` - Environment variables (create this)
- `.gitignore` - Git ignore rules (protects API key)

## Dependencies

- `requests` - HTTP requests for fetching web pages
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser
- `openai` - OpenAI API client for AI-powered search
- `python-dotenv` - Environment variable management
- `mcp` - Model Context Protocol SDK

## Example Output

### Index Generation
```
Fetching OpenAI Agents SDK documentation index...
Fetching fresh documentation index...
Index refreshed with 80 topics and saved to 'docs_index.json'.

Found 80 documentation topics/features:
...
```

### Feature Search
```
Searching for documentation on: handoffs

Loaded existing index with 80 topics.
Verifying documentation links...
  ✓ All links are valid
✓ Found matching topic: Handoffs
  URL: https://openai.github.io/openai-agents-python/handoffs/

Fetching documentation content...
================================================================================
Handoffs - OpenAI Agents SDK
...
```

## License

This project is designed to work with the OpenAI Agents SDK documentation. Please refer to OpenAI's terms of service for API usage.
