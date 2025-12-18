"""
MCP CLI Commands for PraisonAIWP

Commands to run and manage the MCP server.
"""

import os
import json
import click
from rich.console import Console

console = Console()


@click.group()
def mcp():
    """MCP (Model Context Protocol) server commands."""
    pass


@mcp.command()
@click.option('--transport', '-t', default='stdio',
              type=click.Choice(['stdio', 'streamable-http']),
              help='Transport type for the MCP server')
@click.option('--host', default='localhost', help='Host for HTTP transport')
@click.option('--port', default=8000, help='Port for HTTP transport')
@click.option('--server', '-s', default=None, help='WordPress server name from config')
def run(transport, host, port, server):
    """
    Run the MCP server.

    Examples:
        praisonaiwp mcp run                    # Run with stdio (default)
        praisonaiwp mcp run -t streamable-http # Run with HTTP transport
        praisonaiwp mcp run --server production # Use specific WordPress server
    """
    try:
        from praisonaiwp.mcp.server import run_server, MCP_AVAILABLE

        if not MCP_AVAILABLE:
            console.print("[red]Error:[/red] MCP SDK is not installed.")
            console.print("Install it with: [cyan]pip install praisonaiwp[mcp][/cyan]")
            raise click.Abort()

        # Set server environment variable if specified
        if server:
            os.environ['PRAISONAIWP_SERVER'] = server

        console.print(f"[green]Starting MCP server...[/green]")
        console.print(f"Transport: [cyan]{transport}[/cyan]")

        if transport == 'streamable-http':
            console.print(f"URL: [cyan]http://{host}:{port}/mcp[/cyan]")

        run_server(transport=transport)

    except ImportError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("Install MCP with: [cyan]pip install praisonaiwp[mcp][/cyan]")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@mcp.command()
@click.option('--name', '-n', default='praisonaiwp', help='Server name in config')
@click.option('--server', '-s', default=None, help='WordPress server name from config')
def install(name, server):
    """
    Install MCP server in Claude Desktop.

    This generates the configuration needed to add PraisonAIWP
    to Claude Desktop's MCP servers.

    Examples:
        praisonaiwp mcp install
        praisonaiwp mcp install --name "My WordPress"
    """
    import sys
    import shutil

    # Find the praisonaiwp executable
    praisonaiwp_path = shutil.which('praisonaiwp')
    if not praisonaiwp_path:
        # Fallback to python -m
        praisonaiwp_path = sys.executable
        args = ["-m", "praisonaiwp", "mcp", "run"]
    else:
        args = ["mcp", "run"]

    # Build configuration
    config = {
        "mcpServers": {
            name: {
                "command": praisonaiwp_path,
                "args": args,
            }
        }
    }

    if server:
        config["mcpServers"][name]["env"] = {
            "PRAISONAIWP_SERVER": server
        }

    # Determine config file path
    if sys.platform == 'darwin':
        config_path = os.path.expanduser(
            "~/Library/Application Support/Claude/claude_desktop_config.json"
        )
    elif sys.platform == 'win32':
        config_path = os.path.join(
            os.environ.get('APPDATA', ''),
            'Claude',
            'claude_desktop_config.json'
        )
    else:
        config_path = os.path.expanduser("~/.config/claude/claude_desktop_config.json")

    console.print("\n[bold]Claude Desktop MCP Configuration[/bold]\n")
    console.print(f"Add this to: [cyan]{config_path}[/cyan]\n")
    console.print("[yellow]Configuration:[/yellow]")
    console.print(json.dumps(config, indent=2))

    console.print("\n[bold]Or merge with existing config:[/bold]")
    console.print(f"""
1. Open {config_path}
2. Add the following to the "mcpServers" object:

[cyan]"{name}": {json.dumps(config["mcpServers"][name], indent=2)}[/cyan]

3. Restart Claude Desktop
""")


@mcp.command()
@click.option('--server', '-s', default=None, help='WordPress server name from config')
def dev(server):
    """
    Run MCP server in development mode with inspector.

    This starts the MCP Inspector for testing and debugging.

    Examples:
        praisonaiwp mcp dev
        praisonaiwp mcp dev --server staging
    """
    import subprocess
    import sys

    try:
        from praisonaiwp.mcp.server import MCP_AVAILABLE

        if not MCP_AVAILABLE:
            console.print("[red]Error:[/red] MCP SDK is not installed.")
            console.print("Install it with: [cyan]pip install praisonaiwp[mcp][/cyan]")
            raise click.Abort()

        console.print("[green]Starting MCP development server with inspector...[/green]")
        console.print("Open the inspector at: [cyan]http://localhost:5173[/cyan]")

        # Set server environment variable if specified
        env = os.environ.copy()
        if server:
            env['PRAISONAIWP_SERVER'] = server

        # Run mcp dev command
        cmd = [sys.executable, "-m", "mcp", "dev", "-m", "praisonaiwp.mcp.server"]
        subprocess.run(cmd, env=env)

    except ImportError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()
    except FileNotFoundError:
        console.print("[red]Error:[/red] MCP CLI not found.")
        console.print("Install it with: [cyan]pip install 'mcp[cli]'[/cyan]")
        raise click.Abort()


@mcp.command()
def info():
    """
    Show MCP server information and available tools.
    """
    try:
        from praisonaiwp.mcp.server import MCP_AVAILABLE

        console.print("\n[bold]PraisonAIWP MCP Server[/bold]\n")

        if MCP_AVAILABLE:
            console.print("[green]✓[/green] MCP SDK is installed")
        else:
            console.print("[red]✗[/red] MCP SDK is not installed")
            console.print("  Install with: [cyan]pip install praisonaiwp[mcp][/cyan]")
            return

        console.print("\n[bold]Available Tools:[/bold]")
        tools = [
            ("create_post", "Create a new WordPress post"),
            ("update_post", "Update an existing post"),
            ("delete_post", "Delete a post"),
            ("get_post", "Get post details"),
            ("list_posts", "List posts with filters"),
            ("find_text", "Find text in posts"),
            ("list_categories", "List all categories"),
            ("set_post_categories", "Set post categories"),
            ("create_term", "Create a new term"),
            ("list_users", "List WordPress users"),
            ("create_user", "Create a new user"),
            ("get_user", "Get user details"),
            ("list_plugins", "List installed plugins"),
            ("activate_plugin", "Activate a plugin"),
            ("deactivate_plugin", "Deactivate a plugin"),
            ("list_themes", "List installed themes"),
            ("activate_theme", "Activate a theme"),
            ("import_media", "Import media file"),
            ("flush_cache", "Flush WordPress cache"),
            ("get_core_version", "Get WordPress version"),
            ("db_query", "Execute database query"),
            ("search_replace", "Search and replace in database"),
            ("wp_cli", "Execute any WP-CLI command"),
        ]

        for name, desc in tools:
            console.print(f"  • [cyan]{name}[/cyan] - {desc}")

        console.print("\n[bold]Available Resources:[/bold]")
        resources = [
            ("wordpress://info", "WordPress installation info"),
            ("wordpress://posts/{post_id}", "Get specific post"),
            ("wordpress://posts", "List of recent posts"),
            ("wordpress://categories", "All categories"),
            ("wordpress://users", "All users"),
            ("wordpress://plugins", "Installed plugins"),
            ("wordpress://themes", "Installed themes"),
            ("wordpress://config", "Server configuration"),
        ]

        for uri, desc in resources:
            console.print(f"  • [cyan]{uri}[/cyan] - {desc}")

        console.print("\n[bold]Available Prompts:[/bold]")
        prompts = [
            ("create_blog_post_prompt", "Template for creating blog posts"),
            ("update_content_prompt", "Template for updating content"),
            ("bulk_update_prompt", "Template for bulk operations"),
            ("seo_optimize_prompt", "Template for SEO optimization"),
        ]

        for name, desc in prompts:
            console.print(f"  • [cyan]{name}[/cyan] - {desc}")

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
