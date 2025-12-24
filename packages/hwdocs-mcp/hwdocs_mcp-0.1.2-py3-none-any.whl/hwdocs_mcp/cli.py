"""CLI commands for hwdocs-mcp - authentication and status only."""

from __future__ import annotations

import argparse
import asyncio
import sys

from .client import CloudApiClient, CloudApiError
from .config import Config, get_config_path


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="hwdocs",
        description="Document processing authentication CLI",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Login command
    login_parser = subparsers.add_parser("login", help="Authenticate with the cloud API")
    login_parser.add_argument(
        "--token",
        type=str,
        help="API token (if not provided, shows manual instructions)",
    )

    # Logout command
    subparsers.add_parser("logout", help="Remove stored authentication")

    # Status command
    subparsers.add_parser("status", help="Show current status and quota")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        print("\n## Quick Start")
        print("1. Get your API token from the dashboard")
        print("2. Run: hwdocs login --token YOUR_TOKEN")
        print("3. Use the MCP tools in your editor (Cursor, VS Code, etc.)")
        sys.exit(0)

    if args.command == "login":
        cmd_login(args.token)
    elif args.command == "logout":
        cmd_logout()
    elif args.command == "status":
        asyncio.run(cmd_status())
    else:
        parser.print_help()


def cmd_login(token: str | None = None) -> None:
    """Handle login command."""
    config = Config.load()

    if token:
        config.api_token = token
        config.save()
        print("Token saved successfully")
        print("\nYou can now use the MCP tools:")
        print("  - parse_documents: Parse PDFs into searchable markdown")
        print("  - search_documents: Semantic search across documents")
        print("  - manage_workspace: Cache embeddings for faster searches")
        print("  - get_quota: Check your parsing quota")
        return

    print("To configure authentication:")
    print(f"  1. Get your API token from the dashboard")
    print(f"  2. Run: hwdocs login --token YOUR_TOKEN")
    print(f"\nAlternatively, edit {get_config_path()} directly:")
    print('  {"api_token": "YOUR_TOKEN"}')


def cmd_logout() -> None:
    """Handle logout command."""
    config = Config.load()
    if config.api_token:
        config.api_token = None
        config.save()
        print("Logged out successfully")
    else:
        print("Not logged in")


async def cmd_status() -> None:
    """Handle status command."""
    config = Config.load()

    print("## hwdocs Status\n")

    # Configuration
    print(f"Config file: {get_config_path()}")
    print(f"API base: {config.api_base}")
    print()

    # Authentication and quota
    if config.has_cloud_access():
        print("Authentication: logged in")
        try:
            async with CloudApiClient(config) as client:
                quota = await client.get_quota()
                print(f"Plan: {quota.plan}")
                print(f"Quota: {quota.used_pages}/{quota.monthly_limit} pages used")
                print(f"Remaining: {quota.remaining_pages} pages")
                print(f"Resets: {quota.resets_at}")
        except CloudApiError as e:
            print(f"Quota check failed: {e}")
    else:
        print("Authentication: not logged in")
        print("  Run 'hwdocs login --token YOUR_TOKEN' to enable cloud features")

    print()
    print("## Available MCP Tools")
    print("  - parse_documents: Parse documents (uses quota)")
    print("  - search_documents: Semantic search (free)")
    print("  - manage_workspace: Workspace management (free)")
    print("  - get_quota: Check quota status")


if __name__ == "__main__":
    main()
