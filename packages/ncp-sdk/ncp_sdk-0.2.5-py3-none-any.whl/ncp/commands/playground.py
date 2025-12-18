"""Interactive playground command for testing agents."""

import asyncio
from datetime import datetime
import json
import re
from pathlib import Path

import click
import toml
import urllib3
import websockets
from prompt_toolkit import PromptSession
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..utils import get_platform_and_key, find_project_root, get_playground_config

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def create_key_bindings():
    """Create custom key bindings for the prompt.

    - Enter: Submit message
    - Meta+Enter (Alt+Enter or Esc,Enter): Insert newline (multi-line mode)
    """
    kb = KeyBindings()

    @kb.add('enter')
    def _(event):
        """Submit on Enter."""
        event.current_buffer.validate_and_handle()

    @kb.add('escape', 'enter')  # Meta+Enter (Alt+Enter or Esc then Enter)
    def _(event):
        """Insert newline on Meta+Enter."""
        event.current_buffer.insert_text('\n')

    return kb


async def run_websocket_chat(
    agent: str,
    platform_url: str,
    api_key: str,
    show_tools: bool = False,
    logs: str = None
):
    """Run WebSocket chat with agent.

    Args:
        agent: Agent name
        platform_url: Platform URL
        api_key: API key for authentication
        show_tools: Whether to show tool calls and results
        logs: Log level for tool execution logs (DEBUG, INFO, WARNING, ERROR)
    """
    # Define log level hierarchy for filtering
    log_levels = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}
    log_threshold = log_levels.get(logs, None) if logs else None
    # Convert HTTP URL to WebSocket URL
    ws_url = platform_url.replace("https://", "wss://").replace("http://", "ws://")
    ws_url = f"{ws_url}/api/v1/sdk_agents/playground/chat/ws"

    conversation_id = None
    max_retries = 3
    retry_count = 0
    first_connection = True  # Track if this is the first connection
    pending_message = None  # Track message that needs response after reconnect

    # Disable SSL verification for development
    import ssl
    ssl_context = ssl.SSLContext()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    # Outer reconnection loop - handles connection failures transparently
    while retry_count < max_retries:
        try:
            # Enable keep-alive pings to prevent idle timeout
            # Pings are automatic and don't interfere with agent execution
            async with websockets.connect(
                ws_url,
                ssl=ssl_context,
                ping_interval=20,  # Send ping every 20 seconds
                ping_timeout=10    # Consider dead if no pong in 10 seconds
            ) as websocket:
                # Reset retry count on successful connection
                retry_count = 0

                # Authenticate
                auth_message = {
                    "type": "auth",
                    "token": f"Bearer {api_key}"
                }
                await websocket.send(json.dumps(auth_message))

                # Wait for auth response
                auth_response = await websocket.recv()
                auth_data = json.loads(auth_response)

                if auth_data.get("type") == "error":
                    click.echo(f"❌ Authentication failed: {auth_data.get('error')}", err=True)
                    return

                if auth_data.get("type") == "auth" and auth_data.get("status") == "ok":
                    # Only update first_connection flag, no message display
                    if first_connection:
                        first_connection = False

                # Create prompt session with enhanced input features
                # Multi-line mode is always enabled
                completer = WordCompleter(
                    ['/exit', '/help', '/reset', '/clear'],
                    ignore_case=True,
                    sentence=True
                )
                session = PromptSession(
                    history=InMemoryHistory(),
                    completer=completer,
                    key_bindings=create_key_bindings(),
                    multiline=True,
                    prompt_continuation='... '
                )

                # Main chat loop
                while True:
                    # Check if we have a pending message from before disconnect
                    is_resend = False
                    if pending_message:
                        user_input = pending_message
                        pending_message = None
                        is_resend = True
                        # Don't prompt for input, just resend the message
                    else:
                        # Get user input with enhanced editing features
                        try:
                            user_input = await session.prompt_async("You> ")
                        except (KeyboardInterrupt, EOFError):
                            click.echo()
                            click.echo("👋 Goodbye!")
                            return

                        if not user_input.strip():
                            continue

                    # Handle special commands
                    if user_input.strip().lower() == "/exit":
                        click.echo("👋 Goodbye!")
                        return  # Exit completely
                    elif user_input.strip().lower() == "/help":
                        click.echo()
                        click.echo("Available commands:")
                        click.echo("  /help   - Show this help message")
                        click.echo("  /exit   - Exit playground")
                        click.echo("  /reset  - Reset conversation history")
                        click.echo("  /clear  - Clear screen")
                        click.echo()
                        click.echo("Keybindings:")
                        click.echo("  ↑/↓            - Navigate command history")
                        click.echo("  ←/→            - Move cursor within input line")
                        click.echo("  Enter          - Submit message")
                        click.echo("  Alt+Enter      - Insert new line (multi-line input)")
                        click.echo("  Esc then Enter - Insert new line (alternative)")
                        click.echo("  Tab            - Auto-complete commands")
                        click.echo("  Ctrl+C         - Exit playground")
                        click.echo()
                        continue
                    elif user_input.strip().lower() == "/reset":
                        conversation_id = None
                        click.echo("🔄 Conversation reset")
                        click.echo()
                        continue
                    elif user_input.strip().lower() == "/clear":
                        click.clear()
                        click.echo("🎮 NCP Agent Playground")
                        click.echo()
                        continue

                    # Send chat message
                    chat_message = {
                        "type": "chat",
                        "agent_name": agent,
                        "message": user_input,
                    }

                    # Only send conversation_history if we don't have a conversation_id
                    # If we have a conversation_id, the platform will load history from DB
                    if conversation_id:
                        chat_message["conversation_id"] = conversation_id
                    else:
                        chat_message["conversation_history"] = []

                    await websocket.send(json.dumps(chat_message))

                    # Track this message in case we need to resend after reconnect
                    pending_message = user_input

                    # Display response header (only if not a resend - already shown)
                    if not is_resend:
                        click.echo()
                        click.echo("Agent> ", nl=False)

                    # Receive and display streaming response
                    agent_response = ""
                    tool_calls = []
                    log_entries = []  # Buffer for tool execution logs
                    current_tool = None  # Track current tool for Rich panel display

                    while True:
                        try:
                            response_data = await websocket.recv()
                            event = json.loads(response_data)
                            event_type = event.get("type")

                            if event_type == "text":
                                text_chunk = event.get("content", "")
                                agent_response += text_chunk

                                # Filter out Llama bracket notation (will be shown as formatted tool calls)
                                # Pattern matches: [func_name(args), func_name2(args), ...]
                                # Only if the entire chunk is ONLY the bracket notation
                                stripped = text_chunk.strip()
                                is_tool_call_notation = bool(re.match(r'^\[\w+\([^)]*\)(,\s*\w+\([^)]*\))*\]$', stripped))

                                if not is_tool_call_notation:
                                    # Display normal text immediately for streaming
                                    click.echo(text_chunk, nl=False)

                            elif event_type == "tool_call":
                                tool_data = event.get("data", {})
                                tool_calls.append(tool_data)

                                if show_tools:
                                    # Store current tool for Rich panel display when result arrives
                                    current_tool = {
                                        "name": tool_data.get("name", "unknown"),
                                        "arguments": tool_data.get("arguments", {})
                                    }

                            elif event_type == "tool_result":
                                if show_tools and current_tool:
                                    click.echo()  # Spacing before panel

                                    # Create Rich console for formatted output
                                    console = Console()
                                    panel_content = Text()

                                    # Tool name with icon
                                    panel_content.append(f"🔧 {current_tool['name']}\n", style="bold cyan")

                                    # Arguments
                                    args = current_tool['arguments']
                                    if args:
                                        args_str = ", ".join([f"{k}={repr(v)}" for k, v in args.items()])
                                        panel_content.append(f"Arguments: {args_str}\n", style="dim white")

                                    # Result or error
                                    result = event.get("tool_result")
                                    error = event.get("error")

                                    if error:
                                        panel_content.append(f"❌ Error: {error}", style="bold red")
                                    else:
                                        result_str = str(result) if result else "Success"
                                        if len(result_str) > 150:
                                            result_str = result_str[:150] + "..."
                                        panel_content.append(f"✓ Result: {result_str}", style="green")

                                    # Display panel
                                    panel = Panel(
                                        panel_content,
                                        title=f"[bold cyan]Tool: {current_tool['name']}[/bold cyan]",
                                        border_style="cyan" if not error else "red",
                                        padding=(0, 1)
                                    )
                                    console.print(panel)
                                    click.echo()  # Spacing after panel

                                    # Clear current tool
                                    current_tool = None

                            elif event_type == "conversation_id":
                                # Store conversation ID for subsequent messages
                                conversation_id = event.get("conversation_id")
                                # Platform will manage conversation history using this ID

                            elif event_type == "tool_log":
                                # Handle tool execution logs
                                if log_threshold is not None:
                                    log_level = event.get("level", "INFO").upper()
                                    log_message = event.get("message", "")
                                    tool_name = event.get("tool_name", "unknown")
                                    timestamp = event.get("timestamp", "")

                                    # Filter based on log level threshold
                                    if log_levels.get(log_level, 1) >= log_threshold:
                                        # Parse timestamp or use current time
                                        if timestamp:
                                            try:
                                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                                time_str = dt.strftime("%H:%M:%S")
                                            except:
                                                time_str = datetime.now().strftime("%H:%M:%S")
                                        else:
                                            time_str = datetime.now().strftime("%H:%M:%S")

                                        # Store log entry for later display
                                        log_entries.append({
                                            "time": time_str,
                                            "level": log_level,
                                            "tool": tool_name,
                                            "message": log_message
                                        })

                            elif event_type == "done":
                                # Execution complete
                                # SDK doesn't need the full history - platform manages it
                                pending_message = None  # Clear pending message - response received successfully
                                break

                            elif event_type == "error":
                                # Display error
                                click.echo()
                                error_msg = event.get("error", "Unknown error")
                                click.echo(f"\n❌ Error: {error_msg}", err=True)
                                pending_message = None  # Clear pending message - don't retry errors
                                break

                        except json.JSONDecodeError as e:
                            click.echo(f"\n❌ Failed to parse response: {str(e)}", err=True)
                            pending_message = None  # Clear pending message - don't retry parse errors
                            break

                    # Display tool execution logs if any were captured
                    if log_entries:
                        click.echo()  # Add spacing after agent response
                        click.echo()  # Add extra spacing before logs panel

                        # Create Rich console for formatted output
                        console = Console()

                        # Build log content with color coding
                        log_text = Text()
                        for entry in log_entries:
                            # Color based on log level
                            if entry["level"] == "DEBUG":
                                color = "dim white"
                                icon = "🔍"
                            elif entry["level"] == "INFO":
                                color = "cyan"
                                icon = "ℹ️ "
                            elif entry["level"] == "WARNING":
                                color = "yellow"
                                icon = "⚠️ "
                            elif entry["level"] == "ERROR":
                                color = "red"
                                icon = "❌"
                            else:
                                color = "white"
                                icon = "  "

                            # Format: [HH:MM:SS] [LEVEL] tool_name: message
                            log_line = f"[{entry['time']}] {icon} {entry['level']:7} {entry['tool']:15} {entry['message']}\n"
                            log_text.append(log_line, style=color)

                        # Display in a Rich Panel
                        panel = Panel(
                            log_text,
                            title="[bold cyan]Tool Execution Logs[/bold cyan]",
                            border_style="cyan",
                            padding=(0, 1)
                        )
                        console.print(panel)

                    # New line after response
                    click.echo()
                    click.echo()

        except (websockets.exceptions.ConnectionClosed, websockets.exceptions.WebSocketException) as e:
            # Connection lost - retry silently
            retry_count += 1
            if retry_count < max_retries:
                # Exponential backoff: 1s, 2s, 4s
                await asyncio.sleep(2 ** (retry_count - 1))
                # Loop will retry connection automatically
                continue
            else:
                # All retries failed
                click.echo(f"\n❌ WebSocket error: {str(e)}", err=True)
                return

        except Exception as e:
            # Other errors - don't retry
            click.echo(f"\n❌ Error: {str(e)}", err=True)
            return


def run_playground(
    agent: str = None,
    platform: str = None,
    api_key: str = None,
    local: bool = False,
    show_tools: bool = False,
    logs: str = None
):
    """Run interactive playground for testing agents.

    Args:
        agent: Agent name or path to agent package
        platform: Platform URL (optional if stored in config)
        api_key: API key (optional if stored in config)
        local: Run agent locally instead of on platform
        show_tools: Show tool calls and results (default: False)
        logs: Log level for tool execution logs (DEBUG, INFO, WARNING, ERROR)
    """
    click.echo("NCP Agent Playground")
    click.echo()

    # Load playground configuration from ncp.toml
    config = get_playground_config()

    # Command-line flags override config file settings
    if not show_tools:
        show_tools = config.get("show_tools", False)

    # Load logs config from ncp.toml if not provided via CLI
    if logs is None:
        logs_config = config.get("logs")
        if logs_config:
            # Normalize to uppercase (case-insensitive support)
            logs = logs_config.upper()
            valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR"]
            if logs not in valid_levels:
                click.echo(f"⚠️  Invalid log level in ncp.toml: {logs_config}. Ignoring.", err=True)
                logs = None

    # Determine what to run
    if agent:
        # Specific agent provided
        agent_path = Path(agent)
        if agent_path.exists() and agent_path.suffix == ".ncp":
            click.echo(f"Loading agent from package: {agent}")
        else:
            click.echo(f"Agent: {agent}")
    else:
        # Try to find agent in current project
        project_root = find_project_root()
        if project_root is None:
            click.echo("❌ No agent specified and no ncp.toml found in current directory", err=True)
            click.echo("   Either provide --agent or run from within a project directory", err=True)
            raise click.Abort()

        # Read project name from ncp.toml
        toml_file = project_root / "ncp.toml"
        try:
            config = toml.load(toml_file)
            project_name = config.get("project", {}).get("name")
            if not project_name:
                click.echo("❌ Project name not found in ncp.toml [project] section", err=True)
                raise click.Abort()
        except Exception as e:
            click.echo(f"❌ Error reading ncp.toml: {e}", err=True)
            raise click.Abort()

        click.echo(f"Agent: {project_name}")
        agent = project_name

    if local:
        click.echo("Mode: Local execution")
        click.echo()
        click.echo("⚠️  Local execution not yet implemented")
        click.echo("   Agent will be tested on the platform")
        click.echo()
    else:
        # Get platform credentials
        try:
            platform_url, api_key_to_use = get_platform_and_key(platform, api_key)
            click.echo(f"Platform: {platform_url}")
        except click.UsageError as e:
            click.echo(f"❌ {e}", err=True)
            raise click.Abort()

    click.echo()
    click.echo("─" * 60)
    click.echo()

    # Run WebSocket chat
    try:
        asyncio.run(run_websocket_chat(agent, platform_url, api_key_to_use, show_tools, logs))
    except (KeyboardInterrupt, EOFError):
        click.echo()
        click.echo("👋 Goodbye!")
        click.echo()
