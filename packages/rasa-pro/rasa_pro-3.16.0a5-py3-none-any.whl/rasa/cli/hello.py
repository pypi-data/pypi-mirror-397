"""CLI command for starting the Rasa Hello builder service."""

import argparse
import base64
import json
import os
import threading
import time
import urllib.parse
import webbrowser
from typing import Any, Dict, List

from rasa.cli import SubParsersAction
from rasa.shared.utils.cli import print_info, print_success, print_warning

LOCAL_RASA_MCP_SERVER_NAME = "Local Rasa"
# Port is hardcoded because the frontend is compiled with this port
BUILDER_SERVICE_PORT = 5050


def add_subparser(
    subparsers: SubParsersAction, parents: List[argparse.ArgumentParser]
) -> None:
    """Add the hello subparser.

    Args:
        subparsers: Subparser we are going to attach to.
        parents: Parent parsers, needed to ensure tree structure in argparse.
    """
    hello_parser = subparsers.add_parser(
        "hello",
        parents=parents,
        help="(Experimental) Start the Rasa Hello builder service with MCP support.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    hello_parser.add_argument(
        "--mcp-port",
        type=int,
        default=5051,
        help="Port for the MCP server.",
    )
    hello_parser.add_argument(
        "--no-browser",
        action="store_true",
        help="Don't open a browser window after server starts.",
    )
    hello_parser.set_defaults(func=run)


def _print_experimental_warning() -> None:
    """Print a warning that this command is experimental."""
    print_warning(
        "\n"
        "⚠️  EXPERIMENTAL FEATURE ⚠️\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "The 'rasa hello' command is experimental and may change or be removed\n"
        "in future versions. Use at your own risk.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )


def _mcp_server_url(mcp_host: str, mcp_port: int) -> str:
    """Get the MCP server URL."""
    return f"http://{mcp_host}:{mcp_port}/mcp"


def _mcp_server_config(mcp_host: str, mcp_port: int) -> Dict[str, Any]:
    """Get the MCP server configuration."""
    return {
        "url": _mcp_server_url(mcp_host, mcp_port),
    }


def _generate_cursor_deeplink(mcp_host: str, mcp_port: int) -> str:
    """Generate a Cursor deeplink for one-click MCP server installation.

    Args:
        mcp_host: The MCP server host.
        mcp_port: The MCP server port.

    Returns:
        The Cursor deeplink URL.
    """
    config = _mcp_server_config(mcp_host, mcp_port)
    config_json = json.dumps(config)
    config_base64 = base64.b64encode(config_json.encode()).decode()
    server_name = urllib.parse.quote(LOCAL_RASA_MCP_SERVER_NAME)
    return f"cursor://anysphere.cursor-deeplink/mcp/install?name={server_name}&config={config_base64}"


def _print_mcp_instructions(mcp_host: str, mcp_port: int) -> None:
    """Print instructions for using the MCP server in Cursor.

    Args:
        mcp_host: The MCP server host.
        mcp_port: The MCP server port.
    """
    config = _mcp_server_config(mcp_host, mcp_port)
    deeplink = _generate_cursor_deeplink(mcp_host, mcp_port)

    print_info(
        "\n"
        "🔌 MCP Server Instructions for Cursor\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        "\n"
        "Option 1: One-click install (paste this link in your browser):\n"
        f"  {deeplink}\n"
        "\n"
        "Option 2: Manual configuration\n"
        "Add the following to ~/.cursor/mcp.json (or .cursor/mcp.json in project):\n"
        "\n"
        "{\n"
        '  "mcpServers": {\n'
        f'    "{LOCAL_RASA_MCP_SERVER_NAME}": {json.dumps(config)}\n'
        "  }\n"
        "}\n"
        "\n"
        "After installing:\n"
        "1. Activate the MCP server in Cursor's settings. IMPORTANT: if you restart "
        "`rasa hello`, you will need to reactivate the MCP server.\n"
        "2. The Rasa tools will be available in Cursor's AI assistant\n"
        "3. You can ask the assistant to help you build and modify your Rasa bot\n"
        "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )


def _open_browser_delayed(url: str, delay: float = 2.0) -> None:
    """Open a browser window after a delay.

    Args:
        url: The URL to open.
        delay: Delay in seconds before opening the browser.
    """
    time.sleep(delay)
    webbrowser.open(url)


def run(args: argparse.Namespace) -> None:
    """Run the Rasa Hello builder service.

    Args:
        args: The CLI arguments.
    """
    # Print experimental warning
    _print_experimental_warning()

    # Set environment variables for the builder service
    os.environ["SERVER_PORT"] = str(BUILDER_SERVICE_PORT)
    os.environ["MCP_SERVER_PORT"] = str(args.mcp_port)
    # This can only be run with the agent sdk copilot enabled, since that is
    # providing the MCP server
    os.environ["USE_AGENT_SDK_COPILOT"] = "true"
    # Disable authentication for local development with rasa hello
    os.environ["RASA_BUILDER_DISABLE_AUTH"] = "true"

    # Use current working directory as project directory
    project_dir = os.getcwd()

    # Print MCP instructions
    mcp_host = os.environ.get("MCP_SERVER_HOST", "127.0.0.1")
    _print_mcp_instructions(mcp_host, args.mcp_port)

    # Print startup info
    frontend_url = f"http://localhost:{BUILDER_SERVICE_PORT}"
    print_success(
        f"\n"
        f"🚀 Starting Rasa Hello Builder Service\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"  Frontend:      {frontend_url}\n"
        f"  MCP Server:    {_mcp_server_url(mcp_host, args.mcp_port)}\n"
        f"  Project Dir:   {project_dir}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )

    # Open browser in a background thread after server starts
    if not args.no_browser:
        browser_thread = threading.Thread(
            target=_open_browser_delayed,
            args=(frontend_url, 3.0),
            daemon=True,
        )
        browser_thread.start()
        print_info("Browser will open automatically in a few seconds...\n")

    # Import and run the builder main
    from rasa.builder.main import main as builder_main

    builder_main(project_folder=project_dir)
