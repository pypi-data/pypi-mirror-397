# Motion MCP Server

MCP Stdio Server for Motion Database Retrieval.

## Features

- **search_motions**: Search motions by text using vector similarity
- **get_motion_frames**: Get VPD frame data by motion ID

## Installation

```bash
# Using uvx (recommended for deployment)
uvx motion-mcp

# Or install locally
pip install -e .
motion-mcp
```

## Configuration

Create `.env` file with:

```env
POSTGRES_HOST=your-neon-host.neon.tech
POSTGRES_PORT=5432
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password
POSTGRES_DB=your_db
DASHSCOPE_API_KEY=your_dashscope_key
```

## Usage with Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "motion-mcp": {
      "command": "uvx",
      "args": ["motion-mcp"]
    }
  }
}
```
