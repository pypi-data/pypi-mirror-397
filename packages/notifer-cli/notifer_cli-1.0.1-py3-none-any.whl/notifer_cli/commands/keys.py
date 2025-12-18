"""API keys management commands."""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm

from ..client import NotiferClient
from ..config import Config

console = Console()


@click.group()
def keys():
    """Manage API keys for programmatic access."""
    pass


@keys.command("list")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
def list_keys(api_key, server):
    """List all API keys."""
    try:
        config = Config.load()
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        client = NotiferClient(config)
        keys_data = client.list_api_keys()

        if not keys_data:
            console.print("[yellow]No API keys found[/yellow]")
            return

        # Create table
        table = Table(title="API Keys", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Prefix", style="dim")
        table.add_column("Scopes", style="green")
        table.add_column("Requests", justify="right")
        table.add_column("Status", justify="center")
        table.add_column("Created")
        table.add_column("Last Used")

        for key in keys_data:
            scopes_str = ", ".join(key["scopes"][:3])
            if len(key["scopes"]) > 3:
                scopes_str += f" +{len(key['scopes']) - 3} more"

            status = "[green]✓ Active[/green]" if key["is_active"] else "[red]✗ Revoked[/red]"
            last_used = key["last_used"] or "[dim]Never[/dim]"

            table.add_row(
                key["name"],
                key["key_prefix"],
                scopes_str,
                str(key["request_count"]),
                status,
                key["created_at"][:10],
                last_used[:10] if key["last_used"] else last_used,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()


@keys.command("create")
@click.argument("name")
@click.option("--description", "-d", help="Key description")
@click.option("--scopes", "-s", default="*", help="Comma-separated scopes (default: *)")
@click.option("--expires", help="Expiration date (ISO format)")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
def create_key(name, description, scopes, expires, api_key, server):
    """
    Create a new API key.

    \b
    Examples:
      notifer keys create "CI/CD Pipeline"
      notifer keys create "Monitoring" --scopes publish,subscribe
      notifer keys create "Read Only" --scopes topics:read,subscribe
    """
    try:
        config = Config.load()
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        # Parse scopes
        scope_list = [s.strip() for s in scopes.split(",")] if scopes != "*" else ["*"]

        client = NotiferClient(config)
        result = client.create_api_key(
            name=name,
            description=description,
            scopes=scope_list,
            expires_at=expires,
        )

        # Show the key (only shown once!)
        console.print(
            Panel(
                f"[yellow]⚠ IMPORTANT: Save this key now - it won't be shown again![/yellow]\n\n"
                f"[bold green]{result['key']}[/bold green]\n\n"
                f"Name: {result['name']}\n"
                f"Scopes: {', '.join(result['scopes'])}\n"
                f"Created: {result['created_at'][:19]}",
                title="API Key Created",
                border_style="green",
            )
        )

        # Offer to save to config
        if Confirm.ask("\nSave this key to config file?", default=False):
            config.api_key = result["key"]
            config.save()
            console.print("[green]✓[/green] Key saved to ~/.notifer.yaml")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()


@keys.command("revoke")
@click.argument("key_id")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
def revoke_key(key_id, api_key, server):
    """Revoke an API key (keeps for audit)."""
    try:
        config = Config.load()
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        if not Confirm.ask(f"Revoke API key {key_id}?", default=False):
            console.print("Cancelled")
            return

        client = NotiferClient(config)
        client.revoke_api_key(key_id)

        console.print(f"[green]✓[/green] API key revoked: {key_id}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()


@keys.command("delete")
@click.argument("key_id")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
def delete_key(key_id, api_key, server):
    """Permanently delete an API key."""
    try:
        config = Config.load()
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        if not Confirm.ask(
            f"[red]Permanently delete[/red] API key {key_id}? This cannot be undone!",
            default=False,
        ):
            console.print("Cancelled")
            return

        client = NotiferClient(config)
        client.delete_api_key(key_id)

        console.print(f"[green]✓[/green] API key deleted: {key_id}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()
