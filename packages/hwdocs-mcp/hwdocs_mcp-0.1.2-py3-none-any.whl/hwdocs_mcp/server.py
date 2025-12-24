"""Simplified MCP Server for document processing with semtools."""

from __future__ import annotations

import asyncio
import fnmatch
import glob
import logging
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .client import (
    AuthenticationError,
    CloudApiClient,
    CloudApiError,
    QuotaExceededError,
)
from .config import Config, ServerSettings

logger = logging.getLogger(__name__)

# Global state for current workspace
_current_workspace: str | None = None


def _find_binary(name: str) -> str | None:
    """Find a binary in PATH.
    
    On Windows, .cmd wrapper scripts may not work correctly with
    asyncio.create_subprocess_exec(), so we prefer .exe files.
    """
    # First try direct lookup
    path = shutil.which(name)
    
    if sys.platform == "win32":
        # On Windows, .cmd wrappers may not work with subprocess
        # Try to find the actual .exe first
        exe_name = f"{name}.exe"
        exe_path = shutil.which(exe_name)
        if exe_path:
            return exe_path
        
        # If we found a .cmd file, try to find the .exe in npm global modules
        if path and path.lower().endswith('.cmd'):
            # Try common npm global locations
            npm_prefix = os.environ.get('npm_config_prefix', '')
            if npm_prefix:
                potential = Path(npm_prefix) / 'node_modules' / '@llamaindex' / 'semtools' / 'dist' / 'bin' / exe_name
                if potential.exists():
                    return str(potential)
            
            # Also try relative to the .cmd file location
            cmd_dir = Path(path).parent
            potential = cmd_dir / 'node_modules' / '@llamaindex' / 'semtools' / 'dist' / 'bin' / exe_name
            if potential.exists():
                return str(potential)
    
    return path


def _get_parse_cache_dir() -> Path:
    """Get the parse cache directory (~/.parse)."""
    return Path.home() / ".parse"


def _expand_paths(paths: list[str], pattern: str | None = None) -> list[str]:
    """Expand paths with glob patterns and directory support.
    
    Args:
        paths: List of file paths, directory paths, or glob patterns
        pattern: Optional glob pattern to filter files (e.g., "*.pdf")
    
    Returns:
        List of expanded file paths
    """
    expanded = []
    
    for p in paths:
        path = Path(p).expanduser().resolve()
        
        # Check if path contains glob patterns
        if '*' in p or '?' in p or '[' in p:
            # Use glob to expand
            matches = glob.glob(str(path), recursive=True)
            expanded.extend(matches)
        elif path.is_dir():
            # If it's a directory, find files
            if pattern:
                # Use pattern to filter
                for f in path.rglob(pattern):
                    if f.is_file():
                        expanded.append(str(f))
            else:
                # Get all files in directory
                for f in path.iterdir():
                    if f.is_file():
                        expanded.append(str(f))
        elif path.exists():
            expanded.append(str(path))
        else:
            logger.warning(f"Path not found: {p}")
    
    return list(set(expanded))  # Remove duplicates


def _get_parsed_files(pattern: str | None = None) -> list[str]:
    """Get list of parsed markdown files from cache directory.
    
    Args:
        pattern: Optional pattern to filter files (e.g., "*.pdf.md" or just "report")
    
    Returns:
        List of parsed markdown file paths
    """
    cache_dir = _get_parse_cache_dir()
    if not cache_dir.exists():
        return []
    
    files = []
    for f in cache_dir.iterdir():
        if f.is_file() and f.suffix == '.md':
            if pattern:
                # Check if pattern matches filename
                if fnmatch.fnmatch(f.name.lower(), f"*{pattern.lower()}*"):
                    files.append(str(f))
            else:
                files.append(str(f))
    
    return sorted(files)


def create_server() -> Server:
    """Create and configure the MCP server."""
    global _current_workspace
    
    server = Server("hwdocs")
    config = Config.load()
    settings = ServerSettings()

    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List available tools."""
        tools = [
            Tool(
                name="parse_documents",
                description=(
                    "Parse documents (PDF, DOCX, PPTX, etc.) into searchable markdown using LlamaIndex Cloud. "
                    "This operation consumes API quota. Returns paths to the parsed markdown files. "
                    "The parsed files are cached locally for future searches. "
                    "Supports directories and glob patterns (e.g., '*.pdf', 'docs/*.docx')."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "List of file paths, directory paths, or glob patterns to parse. "
                                "Examples: ['report.pdf'], ['./docs'], ['*.pdf'], ['docs/**/*.docx']"
                            ),
                        },
                        "pattern": {
                            "type": "string",
                            "description": (
                                "Optional glob pattern to filter files when parsing directories. "
                                "Examples: '*.pdf', '*.docx', '*.pptx'"
                            ),
                        },
                    },
                    "required": ["files"],
                },
            ),
            Tool(
                name="search_documents",
                description=(
                    "Perform semantic keyword search across documents using local embeddings. "
                    "This is a FREE local operation - no quota used. "
                    "Works best with keywords or comma-separated terms. "
                    "Supports directories and glob patterns. "
                    "Use with parsed markdown files from parse_documents."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (keywords or comma-separated terms work best)",
                        },
                        "files": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": (
                                "List of files, directories, or glob patterns to search. "
                                "Examples: ['~/.parse'], ['~/.parse/*.md'], ['./docs']"
                            ),
                        },
                        "pattern": {
                            "type": "string",
                            "description": "Optional glob pattern to filter files (e.g., '*.md')",
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 3)",
                            "default": 3,
                        },
                        "n_lines": {
                            "type": "integer",
                            "description": "Context lines before/after match (default: 5)",
                            "default": 5,
                        },
                        "max_distance": {
                            "type": "number",
                            "description": "Return all results with distance below this threshold (0.0+, lower = more similar)",
                        },
                        "ignore_case": {
                            "type": "boolean",
                            "description": "Case-insensitive search (default: true, recommended)",
                            "default": True,
                        },
                    },
                    "required": ["query", "files"],
                },
            ),
            Tool(
                name="search_parsed",
                description=(
                    "Search all previously parsed documents in the cache (~/.parse). "
                    "This is a convenient shortcut that automatically searches all parsed markdown files. "
                    "FREE local operation - no quota used. "
                    "Use this after parsing documents with parse_documents."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query (keywords or comma-separated terms work best)",
                        },
                        "filter": {
                            "type": "string",
                            "description": (
                                "Optional filter to narrow down which parsed files to search. "
                                "Matches against filename. Example: 'report' matches 'report.pdf.md'"
                            ),
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 3)",
                            "default": 3,
                        },
                        "n_lines": {
                            "type": "integer",
                            "description": "Context lines before/after match (default: 5)",
                            "default": 5,
                        },
                        "max_distance": {
                            "type": "number",
                            "description": "Return all results with distance below this threshold (0.0+, lower = more similar)",
                        },
                        "ignore_case": {
                            "type": "boolean",
                            "description": "Case-insensitive search (default: true, recommended)",
                            "default": True,
                        },
                    },
                    "required": ["query"],
                },
            ),
            Tool(
                name="list_parsed",
                description=(
                    "List all previously parsed documents in the cache (~/.parse). "
                    "Use this to see what documents are available for searching."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "filter": {
                            "type": "string",
                            "description": "Optional filter to narrow down results. Matches against filename.",
                        },
                    },
                },
            ),
            Tool(
                name="manage_workspace",
                description=(
                    "Manage semtools workspaces for caching embeddings. "
                    "Use workspaces when performing repeated searches over the same files - "
                    "embeddings are cached for much faster subsequent searches. "
                    "Actions: 'use' (create/select), 'status' (show info), 'prune' (clean up). "
                    "After using 'use', subsequent search commands will automatically use the workspace."
                ),
                inputSchema={
                    "type": "object",
                    "properties": {
                        "action": {
                            "type": "string",
                            "enum": ["use", "status", "prune"],
                            "description": "Action to perform: use (create/select workspace), status (show current workspace), prune (clean up stale files)",
                        },
                        "name": {
                            "type": "string",
                            "description": "Workspace name (required for 'use' action)",
                        },
                    },
                    "required": ["action"],
                },
            ),
            Tool(
                name="get_quota",
                description="Check your remaining document parsing quota for the current billing period.",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
        ]

        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
        """Handle tool calls."""
        try:
            if name == "parse_documents":
                return await _handle_parse_documents(arguments, config)
            elif name == "search_documents":
                return await _handle_search_documents(arguments)
            elif name == "search_parsed":
                return await _handle_search_parsed(arguments)
            elif name == "list_parsed":
                return await _handle_list_parsed(arguments)
            elif name == "manage_workspace":
                return await _handle_manage_workspace(arguments)
            elif name == "get_quota":
                return await _handle_get_quota(config)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
        except Exception as e:
            logger.exception(f"Error handling tool {name}")
            return [TextContent(type="text", text=f"Error: {e}")]

    return server


async def _handle_parse_documents(
    arguments: dict[str, Any],
    config: Config,
) -> list[TextContent]:
    """Handle parse_documents tool - executes semtools parse command."""
    files = arguments.get("files", [])
    pattern = arguments.get("pattern")

    if not files:
        return [TextContent(type="text", text="Error: files parameter is required")]

    # Find parse binary
    parse_bin = _find_binary("parse")
    if not parse_bin:
        return [TextContent(
            type="text",
            text="Error: 'parse' binary not found. Install semtools: npm install -g @llamaindex/semtools"
        )]

    # Expand paths with glob and directory support
    expanded_files = _expand_paths(files, pattern)
    
    if not expanded_files:
        return [TextContent(type="text", text="Error: No valid files found matching the criteria")]

    # Filter to only parseable file types
    parseable_extensions = {'.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', '.html', '.htm', '.txt', '.md', '.rtf'}
    valid_files = [f for f in expanded_files if Path(f).suffix.lower() in parseable_extensions]
    
    if not valid_files:
        return [TextContent(
            type="text", 
            text=f"Error: No parseable files found. Found {len(expanded_files)} files but none with supported extensions: {parseable_extensions}"
        )]

    # Check quota if cloud access is configured
    if config.has_cloud_access():
        try:
            async with CloudApiClient(config) as client:
                quota = await client.get_quota()
                if quota.remaining_pages < 1:
                    return [TextContent(
                        type="text",
                        text=f"Quota exceeded. Used {quota.used_pages}/{quota.monthly_limit} pages. Resets: {quota.resets_at}"
                    )]
        except CloudApiError as e:
            logger.warning(f"Could not check quota: {e}")
            # Continue anyway - the parse command might still work

    # Execute parse command
    try:
        args = [parse_bin] + valid_files

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            return [TextContent(type="text", text=f"Parse failed: {error_msg}")]

        output = stdout.decode("utf-8", errors="replace").strip()

        # Count pages parsed (rough estimate for quota tracking)
        parsed_files = [line for line in output.split("\n") if line.strip()]

        # Try to deduct quota after successful parse
        if config.has_cloud_access() and parsed_files:
            try:
                async with CloudApiClient(config) as client:
                    # Estimate pages - this is approximate
                    estimated_pages = len(parsed_files) * 5  # rough estimate
                    await client.deduct_quota(estimated_pages)
            except CloudApiError as e:
                logger.warning(f"Could not deduct quota: {e}")

        result = f"## Parsed {len(parsed_files)} file(s)\n\n"
        result += "Output markdown files:\n"
        for pf in parsed_files:
            result += f"- {pf}\n"
        result += "\n### Next Steps\n"
        result += "- Use `search_parsed` to search all parsed files\n"
        result += "- Use `search_documents` with specific files to search\n"
        result += "- Use `list_parsed` to see all cached parsed files"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Parse error: {e}")]


async def _handle_search_documents(
    arguments: dict[str, Any],
) -> list[TextContent]:
    """Handle search_documents tool - executes semtools search command."""
    global _current_workspace
    
    query = arguments.get("query", "")
    files = arguments.get("files", [])
    pattern = arguments.get("pattern")
    top_k = arguments.get("top_k", 3)
    n_lines = arguments.get("n_lines", 5)
    max_distance = arguments.get("max_distance")
    ignore_case = arguments.get("ignore_case", True)

    if not query:
        return [TextContent(type="text", text="Error: query is required")]

    if not files:
        return [TextContent(type="text", text="Error: files parameter is required")]

    # Find search binary
    search_bin = _find_binary("search")
    if not search_bin:
        return [TextContent(
            type="text",
            text="Error: 'search' binary not found. Install semtools: npm install -g @llamaindex/semtools"
        )]

    # Expand paths with glob and directory support
    expanded_files = _expand_paths(files, pattern)
    
    if not expanded_files:
        return [TextContent(type="text", text="Error: No valid files found matching the criteria")]

    # Build command
    args = [search_bin, query] + expanded_files
    args.extend(["--top-k", str(top_k)])
    args.extend(["--n-lines", str(n_lines)])

    if max_distance is not None:
        args.extend(["--max-distance", str(max_distance)])

    if ignore_case:
        args.append("--ignore-case")

    # Execute search command
    try:
        env = os.environ.copy()
        
        # Apply current workspace if set
        if _current_workspace:
            env["SEMTOOLS_WORKSPACE"] = _current_workspace

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            return [TextContent(type="text", text=f"Search failed: {error_msg}")]

        output = stdout.decode("utf-8", errors="replace").strip()

        if not output:
            return [TextContent(type="text", text=f"No results found for: {query}")]

        result = f"## Search Results for: {query}\n\n"
        if _current_workspace:
            result += f"*Using workspace: {_current_workspace}*\n\n"
        result += "```\n"
        result += output
        result += "\n```"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Search error: {e}")]


async def _handle_search_parsed(
    arguments: dict[str, Any],
) -> list[TextContent]:
    """Handle search_parsed tool - search all parsed files in cache."""
    global _current_workspace
    
    query = arguments.get("query", "")
    filter_pattern = arguments.get("filter")
    top_k = arguments.get("top_k", 3)
    n_lines = arguments.get("n_lines", 5)
    max_distance = arguments.get("max_distance")
    ignore_case = arguments.get("ignore_case", True)

    if not query:
        return [TextContent(type="text", text="Error: query is required")]

    # Get parsed files
    parsed_files = _get_parsed_files(filter_pattern)
    
    if not parsed_files:
        cache_dir = _get_parse_cache_dir()
        if filter_pattern:
            return [TextContent(
                type="text", 
                text=f"No parsed files found matching filter '{filter_pattern}' in {cache_dir}. Use parse_documents first."
            )]
        return [TextContent(
            type="text", 
            text=f"No parsed files found in {cache_dir}. Use parse_documents to parse documents first."
        )]

    # Find search binary
    search_bin = _find_binary("search")
    if not search_bin:
        return [TextContent(
            type="text",
            text="Error: 'search' binary not found. Install semtools: npm install -g @llamaindex/semtools"
        )]

    # Build command
    args = [search_bin, query] + parsed_files
    args.extend(["--top-k", str(top_k)])
    args.extend(["--n-lines", str(n_lines)])

    if max_distance is not None:
        args.extend(["--max-distance", str(max_distance)])

    if ignore_case:
        args.append("--ignore-case")

    # Execute search command
    try:
        env = os.environ.copy()
        
        # Apply current workspace if set
        if _current_workspace:
            env["SEMTOOLS_WORKSPACE"] = _current_workspace

        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            return [TextContent(type="text", text=f"Search failed: {error_msg}")]

        output = stdout.decode("utf-8", errors="replace").strip()

        if not output:
            return [TextContent(type="text", text=f"No results found for: {query}")]

        result = f"## Search Results for: {query}\n\n"
        result += f"*Searched {len(parsed_files)} parsed file(s)*"
        if filter_pattern:
            result += f" *(filter: {filter_pattern})*"
        if _current_workspace:
            result += f" *[workspace: {_current_workspace}]*"
        result += "\n\n```\n"
        result += output
        result += "\n```"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Search error: {e}")]


async def _handle_list_parsed(
    arguments: dict[str, Any],
) -> list[TextContent]:
    """Handle list_parsed tool - list all parsed files in cache."""
    filter_pattern = arguments.get("filter")
    
    parsed_files = _get_parsed_files(filter_pattern)
    cache_dir = _get_parse_cache_dir()
    
    if not parsed_files:
        if filter_pattern:
            return [TextContent(
                type="text",
                text=f"## Parsed Files\n\nNo files matching '{filter_pattern}' found in {cache_dir}."
            )]
        return [TextContent(
            type="text",
            text=f"## Parsed Files\n\nNo parsed files found in {cache_dir}.\n\nUse `parse_documents` to parse documents first."
        )]
    
    result = f"## Parsed Files ({len(parsed_files)} total)\n\n"
    result += f"Cache directory: `{cache_dir}`\n\n"
    
    if filter_pattern:
        result += f"*Filter: {filter_pattern}*\n\n"
    
    for f in parsed_files:
        filename = Path(f).name
        # Show original filename (remove .md suffix to show source file)
        original = filename[:-3] if filename.endswith('.md') else filename
        result += f"- `{original}` → `{filename}`\n"
    
    result += "\n### Usage\n"
    result += "- Use `search_parsed` to search these files\n"
    result += "- Use `search_documents` with specific file paths for targeted search"
    
    return [TextContent(type="text", text=result)]


async def _handle_manage_workspace(
    arguments: dict[str, Any],
) -> list[TextContent]:
    """Handle manage_workspace tool - executes semtools workspace command."""
    global _current_workspace
    
    action = arguments.get("action", "")
    name = arguments.get("name")

    if not action:
        return [TextContent(type="text", text="Error: action is required")]

    if action not in ["use", "status", "prune"]:
        return [TextContent(type="text", text=f"Error: Invalid action '{action}'. Use: use, status, or prune")]

    if action == "use" and not name:
        return [TextContent(type="text", text="Error: 'name' is required for 'use' action")]

    # Find workspace binary
    workspace_bin = _find_binary("workspace")
    if not workspace_bin:
        return [TextContent(
            type="text",
            text="Error: 'workspace' binary not found. Install semtools: npm install -g @llamaindex/semtools"
        )]

    # Build command
    args = [workspace_bin, action]
    if name and action == "use":
        args.append(name)

    # Execute workspace command
    try:
        env = os.environ.copy()
        if _current_workspace:
            env["SEMTOOLS_WORKSPACE"] = _current_workspace
            
        proc = await asyncio.create_subprocess_exec(
            *args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            error_msg = stderr.decode("utf-8", errors="replace").strip()
            return [TextContent(type="text", text=f"Workspace command failed: {error_msg}")]

        output = stdout.decode("utf-8", errors="replace").strip()

        result = f"## Workspace {action.capitalize()}\n\n"
        result += output

        if action == "use":
            # Store the workspace for future search commands
            _current_workspace = name
            result += f"\n\n✅ **Workspace '{name}' is now active.** "
            result += "All subsequent search commands will use this workspace for caching."

        if action == "status" and _current_workspace:
            result += f"\n\n*Current MCP session workspace: {_current_workspace}*"

        return [TextContent(type="text", text=result)]

    except Exception as e:
        return [TextContent(type="text", text=f"Workspace error: {e}")]


async def _handle_get_quota(config: Config) -> list[TextContent]:
    """Handle get_quota tool."""
    if not config.has_cloud_access():
        return [TextContent(
            type="text",
            text=(
                "## Quota Status\n\n"
                "No API token configured.\n\n"
                "Run 'hwdocs login' to authenticate and enable quota tracking."
            ),
        )]

    try:
        async with CloudApiClient(config) as client:
            quota = await client.get_quota()
            return [TextContent(
                type="text",
                text=(
                    f"## Quota Status\n\n"
                    f"- **Plan:** {quota.plan}\n"
                    f"- **Used:** {quota.used_pages} / {quota.monthly_limit} pages\n"
                    f"- **Remaining:** {quota.remaining_pages} pages\n"
                    f"- **Resets:** {quota.resets_at}\n"
                ),
            )]
    except AuthenticationError as e:
        return [TextContent(
            type="text",
            text=f"## Authentication Error\n\n{e}\n\nRun 'hwdocs login' to re-authenticate.",
        )]
    except CloudApiError as e:
        return [TextContent(type="text", text=f"## API Error\n\n{e}")]


def main() -> None:
    """Run the MCP server."""
    server = create_server()

    async def run():
        async with stdio_server() as (read_stream, write_stream):
            await server.run(read_stream, write_stream, server.create_initialization_options())

    asyncio.run(run())


if __name__ == "__main__":
    main()
