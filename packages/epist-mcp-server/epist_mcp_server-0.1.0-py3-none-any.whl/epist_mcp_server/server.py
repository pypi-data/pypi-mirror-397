import asyncio
import logging
import os
from typing import Any

import httpx
from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mcp_server")

# Configuration
API_URL = os.getenv("EPIST_API_URL", "https://epist-api-920152096400.us-central1.run.app/api/v1")
API_KEY = os.getenv("EPIST_API_KEY")

if not API_KEY:
    logger.warning("EPIST_API_KEY environment variable not set. Some tools may fail.")

# Initialize MCP Server
app = Server("epist")


async def make_request(method: str, endpoint: str, json: dict | None = None, params: dict | None = None) -> Any:
    """Helper to make authenticated API requests."""
    headers = {"X-API-Key": API_KEY or "", "Content-Type": "application/json"}

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method, f"{API_URL}{endpoint}", json=json, params=params, headers=headers, timeout=30.0
        )
        response.raise_for_status()
        return response.json()


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """List available tools."""
    return [
        types.Tool(
            name="ingest_audio",
            description="Ingest an audio file from a URL for processing (transcription + embedding).",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL of the audio file"},
                    "language": {"type": "string", "description": "Language code (default: en)", "default": "en"},
                    "rag_enabled": {"type": "boolean", "description": "Enable RAG indexing", "default": True},
                },
                "required": ["url"],
            },
        ),
        types.Tool(
            name="search_knowledge_base",
            description="Semantically search the transcribed audio knowledge base.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 5},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="get_transcription_status",
            description="Check the status of an ingestion task.",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_id": {"type": "string", "description": "ID returned by ingest_audio"},
                },
                "required": ["audio_id"],
            },
        ),
        types.Tool(
            name="get_transcript",
            description="Get the full transcript of a processed audio file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "audio_id": {"type": "string", "description": "ID of the audio file"},
                },
                "required": ["audio_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool execution."""
    try:
        if name == "ingest_audio":
            url = arguments.get("url")
            language = arguments.get("language", "en")
            rag_enabled = arguments.get("rag_enabled", True)

            response = await make_request(
                "POST",
                "/audio/transcribe_url",
                json={"audio_url": url, "language": language, "rag_enabled": rag_enabled},
            )

            return [
                types.TextContent(
                    type="text", text=f"Ingestion started. Audio ID: {response['id']}. Status: {response['status']}"
                )
            ]

        elif name == "search_knowledge_base":
            query = arguments.get("query")
            limit = arguments.get("limit", 5)

            results = await make_request("POST", "/search/", json={"query": query, "limit": limit})

            if not results:
                return [types.TextContent(type="text", text="No results found.")]

            # Format results
            formatted_results = []
            for r in results:
                score_pct = f"{r['score'] * 100:.1f}%"
                time_range = (
                    f"{int(r['start'] // 60)}:{int(r['start'] % 60):02d}-{int(r['end'] // 60)}:{int(r['end'] % 60):02d}"
                )
                formatted_results.append(f"- [{score_pct}] ({time_range}): {r['text']}")

            return [types.TextContent(type="text", text="\n".join(formatted_results))]

        elif name == "get_transcription_status":
            audio_id = arguments.get("audio_id")
            response = await make_request("GET", f"/audio/{audio_id}")
            return [types.TextContent(type="text", text=f"Status: {response['status']}")]

        elif name == "get_transcript":
            audio_id = arguments.get("audio_id")
            transcript = await make_request("GET", f"/audio/{audio_id}/transcript")

            # Format transcript (simple text dump)
            full_text = transcript.get("text", "")
            return [types.TextContent(type="text", text=full_text)]

        raise ValueError(f"Unknown tool: {name}")

    except httpx.HTTPStatusError as e:
        logger.error(f"API Error: {e.response.text}")
        return [types.TextContent(type="text", text=f"API Error: {e.response.status_code} - {e.response.text}")]
    except Exception as e:
        logger.error(f"Error executing tool {name}: {e}")
        return [types.TextContent(type="text", text=f"Error: {e!s}")]


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """List available resources."""
    # Since we don't have a direct "list all audio" endpoint optimized for this,
    # we return a static template or empty list.
    # In a real scenario, we might fetch the most recent audio files.
    return [
        types.Resource(
            uri="transcript://template",
            name="Transcript Template",
            description="Template for accessing transcripts. Use transcript://{audio_id}",
            mimeType="text/plain",
        )
    ]


@app.read_resource()
async def read_resource(uri: Any) -> str | bytes:
    """Read a specific resource."""
    # Parse URI: transcript://{audio_id}
    uri_str = str(uri)
    if not uri_str.startswith("transcript://"):
        raise ValueError(f"Unknown resource scheme: {uri_str}")

    audio_id = uri_str.replace("transcript://", "")

    try:
        # Fetch status first to ensure it exists, or directly fetch transcript
        # We'll directly fetch the transcript to be efficient
        transcript = await make_request("GET", f"/audio/{audio_id}/transcript")
        return transcript.get("text", "")
    except httpx.HTTPStatusError as e:
        raise ValueError(f"Could not fetch transcript for {audio_id}: {e.response.text}")
    except Exception as e:
        raise ValueError(f"Error reading resource {uri_str}: {e}")


async def run():
    # Run the server using stdin/stdout streams
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


def main():
    """Synchronous entry point for the console script."""
    asyncio.run(run())


if __name__ == "__main__":
    main()
