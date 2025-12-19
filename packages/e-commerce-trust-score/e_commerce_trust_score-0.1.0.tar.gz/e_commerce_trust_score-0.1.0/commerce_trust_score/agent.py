"""Trust score agent core logic."""

import json
from typing import Optional

from claude_agent_sdk import (
    ClaudeAgentOptions,
    ClaudeSDKClient,
    AssistantMessage,
    TextBlock,
)

from .config import TRUST_AGENT_SYSTEM_PROMPT
from .tools import create_url_tools_server


async def run_trust_agent(url: str, max_turns: int = 3) -> dict:
    """
    Run the trust score agent for a given URL.
    
    Calls Claude via Claude Agent SDK, using our in-process MCP tool.
    Expects Claude to respond with a JSON object as text.
    
    Args:
        url: The URL to analyze
        max_turns: Maximum number of conversation turns (default: 3)
        
    Returns:
        dict: Trust score analysis result with score, label, factors, and explanations
        
    Raises:
        RuntimeError: If the agent response cannot be parsed as JSON
    """
    # Create the URL tools server
    url_tools_server = create_url_tools_server()
    
    # Configure the agent to use our MCP server + tool
    options = ClaudeAgentOptions(
        system_prompt=TRUST_AGENT_SYSTEM_PROMPT,
        # Register MCP servers: one named "url-tools"
        mcp_servers={"url-tools": url_tools_server},
        # Allow exactly this tool: mcp__<server_name>__<tool_name>
        allowed_tools=["mcp__url-tools__inspect_url"],
        max_turns=max_turns,  # enough for tool call + reasoning + final answer
    )

    assistant_text = ""

    async with ClaudeSDKClient(options=options) as client:
        # Ask the agent to compute a trust score for this URL
        await client.query(
            f"Given this product URL: {url}\n"
            f"Call the inspect_url tool, then follow the instructions."
        )

        # Stream back the response and accumulate Assistant text blocks
        async for msg in client.receive_response():
            if isinstance(msg, AssistantMessage):
                for block in msg.content:
                    if isinstance(block, TextBlock):
                        assistant_text += block.text

    # Parse the JSON that Claude returns
    # Sometimes Claude wraps JSON in markdown code blocks despite instructions
    text_to_parse = assistant_text.strip()
    
    # Try to extract JSON from markdown code blocks if present
    if "```" in text_to_parse:
        # Find the start and end of the code block
        start_idx = text_to_parse.find("```")
        # Skip past the opening fence and optional language identifier (e.g., ```json)
        first_newline = text_to_parse.find("\n", start_idx)
        if first_newline != -1:
            start_idx = first_newline + 1
        else:
            start_idx = start_idx + 3  # Skip just ```
        
        # Find the closing fence
        end_idx = text_to_parse.find("```", start_idx)
        if end_idx != -1:
            text_to_parse = text_to_parse[start_idx:end_idx].strip()
        else:
            # No closing fence, take everything after opening
            text_to_parse = text_to_parse[start_idx:].strip()
    
    # If still no JSON structure found, try to extract just the JSON object
    if not text_to_parse.startswith("{"):
        # Try to find the first { and last }
        json_start = text_to_parse.find("{")
        json_end = text_to_parse.rfind("}")
        if json_start != -1 and json_end != -1 and json_end > json_start:
            text_to_parse = text_to_parse[json_start:json_end + 1]
    
    try:
        data = json.loads(text_to_parse)
    except json.JSONDecodeError as e:
        # Print the actual response for debugging
        print(f"ERROR: Could not parse JSON from Claude response.")
        print(f"Raw response ({len(assistant_text)} chars):")
        print(f"---START---")
        print(assistant_text)
        print(f"---END---")
        print(f"Attempted to parse ({len(text_to_parse)} chars):")
        print(f"---PARSE START---")
        print(text_to_parse)
        print(f"---PARSE END---")
        raise RuntimeError(
            f"Failed to parse JSON from Claude response. "
            f"Response was {len(assistant_text)} characters. "
            f"First 200 chars: {assistant_text[:200]}"
        ) from e

    return data

