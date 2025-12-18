"""MCP server for mai-tai AI agent collaboration platform."""

import asyncio
import json
import queue
import sys
import threading
import time
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from .backend import MaiTaiBackend, MaiTaiBackendError, create_backend
from .config import get_config

# Create FastMCP server
mcp = FastMCP(
    name="mai-tai-mcp",
    instructions="""
mai-tai lets you collaborate with humans like a coworker on Slack. Keep it friendly and natural!

## Two Ways to Communicate

### `ask_human` - Ask a Question and Wait (BLOCKING)

Use this whenever you have a question. **Humans appreciate being asked** - it keeps them in the
loop and builds trust. Don't be shy about asking! The tool will wait for their response so you
can continue with the right information.

**Ask about:**
- Decisions: "Hey, should I use Redis or PostgreSQL for the cache? I'm leaning toward Redis but wanted your input."
- Missing info: "I need the API key for the payment service - where can I find it?"
- Approval: "I'm about to delete 50 unused files. Cool to proceed?"
- Clarification: "The spec says 'make it fast' - what latency are we targeting?"
- Anything you're unsure about - when in doubt, just ask!

### `send_message` - Quick Update, No Response Needed (NON-BLOCKING)

Use this for status updates and FYIs. You send the message and keep working - no waiting.

**Send updates like:**
- "Starting the database migration now..."
- "Build passed! Deploying to staging."
- "Heads up: found 12 deprecated dependencies, I'll update them next."

## When You Finish a Task

**Always check in with the human!** Send a message or ask what's next:
- "All done with the auth refactor! What should I tackle next?"
- "Finished setting up the CI pipeline. Ready for the next task when you are!"
- "Migration complete, all tests passing. What's the next priority?"

This keeps the collaboration flowing naturally, like working with a teammate.

## Quick Decision Guide

```
Do I have a question or need input?  →  ask_human (wait for answer)
Just sharing status or an FYI?       →  send_message (fire and forget)
Just finished a task?                →  ask_human what to work on next!
```

## 🍹 Mai-Tai Mode - When the Human Steps Away

If the human says **"mai-tai mode"** (or "I'm stepping away", "going AFK", etc.):

1. **They're away** - Don't expect responses in the current chat
2. **Keep working** - Continue on your tasks autonomously
3. **Route ALL questions through `ask_human`** - They'll respond via mai-tai when back
4. **Use 30-minute timeouts** - Set `timeout_seconds=1800` since they may be away a while
5. **Batch non-urgent questions** - Group smaller questions together if possible
6. **Send progress updates** - Use `send_message` to keep them in the loop

When they return ("I'm back", "exit mai-tai mode"), resume normal conversation.

This lets you keep making progress while they grab lunch, take meetings, or step away.
They stay informed and can respond on their own schedule - async collaboration at its best!

## Tips

- **Acknowledge, then work** - When you get a task, send a quick "Got it, working on X!" so the human knows you received it, then do the work
- **Use markdown** - Messages support full markdown including **bold**, `code`, and code blocks:
  ```python
  def example():
      return "syntax highlighted!"
  ```
- **Be conversational** - Write like you're messaging a coworker, not filing a report
- **Ask early, ask often** - Humans prefer being asked over being surprised
- **Give context** - Include what you found, what you tried, what options you see
- **Use channels** - Create topic-specific channels to keep conversations organized
""",
)

# Global backend client (initialized on first use)
_backend: Optional[MaiTaiBackend] = None


def get_backend() -> MaiTaiBackend:
    """Get or create the backend client instance."""
    global _backend
    if _backend is None:
        try:
            config = get_config()
            _backend = create_backend(config)
            _backend.connect()
        except Exception as e:
            raise MaiTaiBackendError(0, f"Failed to initialize mai-tai backend: {e}") from e
    return _backend


# ============================================================================
# HTTP Polling for Response Detection
# ============================================================================


def _wait_for_response_polling(
    backend: "MaiTaiBackend",
    channel_id: str,
    after_message_id: str,
    timeout_seconds: int,
    poll_interval: float = 3.0,
) -> dict[str, Any] | None:
    """
    Wait for a human response using HTTP polling.

    Simple and reliable - polls for new messages every few seconds.
    Returns the response message or None on timeout.

    Args:
        backend: The backend client instance
        channel_id: Channel to poll for messages
        after_message_id: Only look for messages after this ID (the question we sent)
        timeout_seconds: How long to wait before timing out
        poll_interval: How often to poll (default: 3 seconds)
    """
    start_time = time.time()

    while time.time() - start_time < timeout_seconds:
        try:
            # Get messages after the question we sent
            result = backend.get_messages(channel_id, limit=10, after=after_message_id)
            messages = result.get("messages", [])

            # Look for a user response
            for msg in messages:
                if msg.get("sender_type") == "user":
                    return {
                        "content": msg.get("content", ""),
                        "sender_id": msg.get("sender_id"),
                        "created_at": msg.get("created_at"),
                    }

            # No response yet, wait before polling again
            time.sleep(poll_interval)

        except Exception as e:
            print(f"Polling error: {e}", file=sys.stderr)
            time.sleep(poll_interval)

    return None  # Timeout


# ============================================================================
# Primary Tool - Ask Human
# ============================================================================


@mcp.tool()
def ask_human(
    question: str,
    channel_name: Optional[str] = None,
    wait_for_response: bool = True,
    timeout_seconds: int = 300,
) -> dict[str, Any]:
    """Ask a human for help, clarification, or a decision.

    This is the primary tool for escalating questions to humans. Use this when:
    - You need information you don't have access to
    - You need a decision or approval
    - You're unsure about requirements
    - You encounter an error you can't resolve

    Args:
        question: The question to ask the human (be clear and specific)
        channel_name: Optional channel name. If not provided, uses "agent-questions"
        wait_for_response: Whether to wait for a human response (default: True)
        timeout_seconds: How long to wait for a response (default: 300 = 5 minutes)

    Returns:
        Dictionary with the human's response or timeout status
    """
    backend = get_backend()
    channel_name = channel_name or "agent-questions"

    # Find or create the channel
    channels = backend.list_channels()
    channel = next((c for c in channels if c["name"] == channel_name), None)

    if not channel:
        channel = backend.create_channel(channel_name, "chat")

    channel_id = channel["id"]

    # Send the question
    message = backend.send_message(
        channel_id=channel_id,
        content=question,
        sender_type="agent",
        metadata={"type": "question", "awaiting_response": wait_for_response},
    )

    if not wait_for_response:
        return {
            "status": "sent",
            "message_id": message["id"],
            "channel": channel_name,
            "note": "Question sent. Check back later for response.",
        }

    # Wait for response using HTTP polling (simple and reliable)
    response = _wait_for_response_polling(
        backend=backend,
        channel_id=channel_id,
        after_message_id=message["id"],
        timeout_seconds=timeout_seconds,
        poll_interval=3.0,  # Check every 3 seconds
    )

    if response:
        return {
            "status": "answered",
            "response": response["content"],
            "channel": channel_name,
        }

    return {
        "status": "timeout",
        "channel": channel_name,
        "note": f"No response after {timeout_seconds} seconds. Human may respond later.",
    }


# ============================================================================
# Channel Management Tools
# ============================================================================


@mcp.tool()
def list_channels() -> dict[str, Any]:
    """List all channels in the mai-tai project.

    Returns:
        Dictionary with 'channels' key containing list of all channels
    """
    backend = get_backend()
    channels = backend.list_channels()
    return {
        "channels": channels,
        "count": len(channels),
        "project": backend.project_name,
    }


@mcp.tool()
def create_channel(name: str, channel_type: str = "chat") -> dict[str, Any]:
    """Create a new channel for communication.

    Args:
        name: Channel name (e.g., 'feature-discussion', 'bug-reports')
        channel_type: Type of channel - 'chat' or 'notification' (default: 'chat')

    Returns:
        Created channel details with id and name
    """
    backend = get_backend()
    return backend.create_channel(name, channel_type)


@mcp.tool()
def get_channel(channel_id: str) -> dict[str, Any]:
    """Get details about a specific channel.

    Args:
        channel_id: The channel's unique identifier

    Returns:
        Channel details including id, name, type, and message count
    """
    backend = get_backend()
    return backend.get_channel(channel_id)


# ============================================================================
# Message Tools
# ============================================================================


@mcp.tool()
def send_message(
    channel_id: str,
    content: str,
    metadata: Optional[dict[str, Any]] = None,
) -> dict[str, Any]:
    """Send a message to a channel.

    Use this for general communication. For questions that need human responses,
    prefer using ask_human() instead.

    Args:
        channel_id: The channel to send to
        content: Message content (markdown supported)
        metadata: Optional metadata dict (e.g., {"type": "status_update"})

    Returns:
        Sent message details with id and timestamp
    """
    backend = get_backend()
    return backend.send_message(
        channel_id=channel_id,
        content=content,
        sender_type="agent",
        metadata=metadata,
    )


@mcp.tool()
def get_messages(
    channel_id: str,
    limit: int = 50,
    after: Optional[str] = None,
) -> dict[str, Any]:
    """Get messages from a channel.

    Args:
        channel_id: The channel to read from
        limit: Maximum number of messages to return (default: 50)
        after: Only return messages after this message ID (for pagination)

    Returns:
        Dictionary with 'messages' list and pagination info
    """
    backend = get_backend()
    return backend.get_messages(channel_id, limit=limit, after=after)


# ============================================================================
# Utility Tools
# ============================================================================


@mcp.tool()
def get_project_info() -> dict[str, Any]:
    """Get information about the connected mai-tai project.

    Returns:
        Project details including id, name, and connection status
    """
    backend = get_backend()
    return {
        "project_id": backend.project_id,
        "project_name": backend.project_name,
        "server_url": backend.config.server_url,
        "status": "connected",
    }


# ============================================================================
# Main Entry Point
# ============================================================================


def main() -> None:
    """Main entry point for the MCP server."""
    try:
        # Run the server with stdio transport
        mcp.run(transport="stdio")
    except KeyboardInterrupt:
        print("\nShutting down mai-tai-mcp server...", file=sys.stderr)
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
