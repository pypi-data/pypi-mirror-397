"""MCP tools for URL inspection."""

import json
from urllib.parse import urlparse

from claude_agent_sdk import tool, create_sdk_mcp_server


@tool(
    "inspect_url",
    "Inspect a URL with very simple heuristics and return a JSON string.",
    {"url": str},
)
async def inspect_url(args):
    """
    MVP tool: does NOT visit the page.
    It just parses the URL and looks for basic red flags in the hostname/path.
    You can later replace this with a Chrome Dev MCP tool that actually loads the page.
    """
    raw_url = args["url"]
    parsed = urlparse(raw_url)

    scheme = parsed.scheme.lower()
    hostname = (parsed.netloc or "").lower()
    path = (parsed.path or "").lower()

    is_https = scheme == "https"

    # Very naive suspicious keywords list for demo purposes
    suspicious_keywords = [
        "outlet",
        "clearance",
        "90off",
        "80off",
        "cheap",
        "replica",
        "copy",
        "limiteddeal",
    ]
    hits = [
        kw for kw in suspicious_keywords
        if kw in hostname or kw in path
    ]

    # Super simple scoring just inside the tool (you can move this logic to the LLM later)
    score = 0.5  # base
    if is_https:
        score += 0.2
    if hits:
        score -= 0.1 * len(hits)

    # Small penalty for very long hostnames (often scammy)
    if len(hostname) > 30:
        score -= 0.1

    score = max(0.0, min(1.0, score))

    result = {
        "url": raw_url,
        "is_https": is_https,
        "hostname": hostname,
        "path": path,
        "suspicious_keywords": hits,
        "tool_score": score,
    }

    # Claude will see this as tool output (text), and then we ask it to build the final JSON response.
    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result),
            }
        ]
    }


def create_url_tools_server():
    """Create an in-process MCP server for URL inspection tools."""
    return create_sdk_mcp_server(
        name="url-tools",
        version="0.0.1",
        tools=[inspect_url],
    )

