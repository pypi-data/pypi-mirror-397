# -*- coding: utf-8 -*-
"""
MCP Stdio Server for Motion Database Retrieval.

Provides two tools:
- search_motions: Search motions by text using vector similarity
- get_motion_frames: Get VPD frame data by motion ID
"""
import asyncio
import json
from typing import Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from .db import motion_db


# Create MCP server instance
server = Server("motion-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="search_motions",
            description="Search motions by text description using vector similarity. Returns matching motions with similarity scores.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Text query to search for (e.g., 'walking', 'jumping', 'dancing')"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return (default: 5)",
                        "default": 5,
                        "minimum": 1,
                        "maximum": 20
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_motion_frames",
            description="Get VPD frame data for a motion by ID. Returns bone transformation data for each frame.",
            inputSchema={
                "type": "object",
                "properties": {
                    "motion_id": {
                        "type": "string",
                        "description": "UUID of the motion to get frames for"
                    },
                    "start_frame": {
                        "type": "integer",
                        "description": "Start frame index (inclusive, optional)",
                        "minimum": 0
                    },
                    "end_frame": {
                        "type": "integer",
                        "description": "End frame index (inclusive, optional)",
                        "minimum": 0
                    },
                    "format": {
                        "type": "string",
                        "enum": ["json", "vpd"],
                        "description": "Output format: 'json' for raw data, 'vpd' for VPD text format (default: json)",
                        "default": "json"
                    }
                },
                "required": ["motion_id"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls."""
    
    if name == "search_motions":
        query = arguments.get("query", "")
        top_k = arguments.get("top_k", 5)
        
        if not query:
            return [TextContent(type="text", text="Error: query is required")]
        
        try:
            results = await motion_db.search_motions(query, top_k)
            
            if not results:
                return [TextContent(type="text", text="No motions found matching the query.")]
            
            # Format results
            output = f"Found {len(results)} motion(s) matching '{query}':\n\n"
            for i, m in enumerate(results, 1):
                output += f"{i}. **{m['name']}** (ID: {m['id']})\n"
                output += f"   - Description: {m['description'] or 'N/A'}\n"
                output += f"   - Frames: {m['total_frames']} ({m['duration_seconds']:.2f}s)\n"
                output += f"   - Similarity: {m['similarity']:.4f}\n\n"
            
            return [TextContent(type="text", text=output)]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error searching motions: {str(e)}")]
    
    elif name == "get_motion_frames":
        motion_id = arguments.get("motion_id", "")
        start_frame = arguments.get("start_frame")
        end_frame = arguments.get("end_frame")
        output_format = arguments.get("format", "json")
        
        if not motion_id:
            return [TextContent(type="text", text="Error: motion_id is required")]
        
        try:
            # Get motion metadata first
            motion = await motion_db.get_motion_by_id(motion_id)
            if not motion:
                return [TextContent(type="text", text=f"Motion not found: {motion_id}")]
            
            # Get frames
            frames = await motion_db.get_frames(motion_id, start_frame, end_frame)
            
            if not frames:
                return [TextContent(type="text", text=f"No frames found for motion: {motion_id}")]
            
            if output_format == "vpd":
                # Return VPD format for each frame
                output = f"# Motion: {motion['name']}\n"
                output += f"# Frames: {len(frames)}\n\n"
                
                for frame in frames:
                    output += f"--- Frame {frame['frame_index']} ---\n"
                    output += motion_db.frame_to_vpd(frame['bone_data'], motion['name'])
                    output += "\n"
                
                return [TextContent(type="text", text=output)]
            else:
                # Return JSON format
                result = {
                    "motion": motion,
                    "frame_count": len(frames),
                    "frames": frames
                }
                return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
            
        except Exception as e:
            return [TextContent(type="text", text=f"Error getting frames: {str(e)}")]
    
    else:
        return [TextContent(type="text", text=f"Unknown tool: {name}")]


async def run_server():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


def main():
    """Entry point for the MCP server."""
    asyncio.run(run_server())


if __name__ == "__main__":
    main()
