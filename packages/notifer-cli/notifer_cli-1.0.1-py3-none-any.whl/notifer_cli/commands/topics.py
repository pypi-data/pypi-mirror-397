"""Topics management commands."""
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Confirm

from ..client import NotiferClient
from ..config import Config

console = Console()


@click.group()
def topics():
    """Manage topics."""
    pass


@topics.command("list")
@click.option("--mine", is_flag=True, help="Show only your topics")
@click.option("--limit", "-l", type=int, default=50, help="Number of topics to show")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
def list_topics(mine, limit, api_key, server):
    """List topics."""
    try:
        config = Config.load()
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        client = NotiferClient(config)
        topics_data = client.my_topics(limit=limit) if mine else client.list_topics(limit=limit)

        if not topics_data:
            console.print("[yellow]No topics found[/yellow]")
            return

        # Create table
        table = Table(title="Topics", show_header=True, header_style="bold cyan")
        table.add_column("Name", style="cyan")
        table.add_column("Access", justify="center")
        table.add_column("Messages", justify="right")
        table.add_column("Subscribers", justify="right")
        table.add_column("Description")

        for topic in topics_data:
            access_level = topic.get("access_level", "public")
            if access_level == "private":
                access_badge = "[red]🔒 Private[/red]"
            elif access_level == "protected":
                access_badge = "[yellow]🔐 Protected[/yellow]"
            else:
                access_badge = "[green]🌍 Public[/green]"

            description = topic.get("description", "") or "[dim]No description[/dim]"
            if len(description) > 40:
                description = description[:37] + "..."

            table.add_row(
                topic["name"],
                access_badge,
                str(topic.get("message_count", 0)),
                str(topic.get("subscriber_count", 0)),
                description,
            )

        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()


@topics.command("get")
@click.argument("name")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
def get_topic(name, api_key, server):
    """Get topic details."""
    try:
        config = Config.load()
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        client = NotiferClient(config)
        topic = client.get_topic(name)

        # Format access level
        access_level = topic.get("access_level", "public")
        if access_level == "private":
            access_badge = "[red]🔒 Private[/red]"
        elif access_level == "protected":
            access_badge = "[yellow]🔐 Protected[/yellow]"
        else:
            access_badge = "[green]🌍 Public[/green]"

        # Build info panel
        info = (
            f"[bold]Name:[/bold] {topic['name']}\n"
            f"[bold]Access:[/bold] {access_badge}\n"
            f"[bold]Discoverable:[/bold] {'Yes' if topic.get('is_discoverable') else 'No'}\n"
            f"[bold]Messages:[/bold] {topic.get('message_count', 0)}\n"
            f"[bold]Subscribers:[/bold] {topic.get('subscriber_count', 0)}\n"
            f"[bold]Created:[/bold] {topic.get('created_at', 'N/A')[:19]}\n"
        )

        if topic.get("description"):
            info += f"\n[bold]Description:[/bold]\n{topic['description']}"

        console.print(Panel(info, title=f"Topic: {name}", border_style="cyan"))

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()


@topics.command("create")
@click.argument("name")
@click.option("--description", "-d", help="Topic description")
@click.option("--private", is_flag=True, help="Make topic private")
@click.option("--no-discover", is_flag=True, help="Hide from discovery")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
def create_topic(name, description, private, no_discover, api_key, server):
    """
    Create a new topic.

    \b
    Examples:
      notifer topics create my-topic
      notifer topics create alerts --description "System alerts"
      notifer topics create private-topic --private
    """
    try:
        config = Config.load()
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        client = NotiferClient(config)
        result = client.create_topic(
            name=name,
            description=description,
            is_private=private,
            is_discoverable=not no_discover,
        )

        console.print(
            Panel(
                f"[green]✓[/green] Topic created: [cyan]{result['name']}[/cyan]\n\n"
                f"ID: {result['id']}\n"
                f"Access: {result['access_level']}\n"
                f"Discoverable: {result.get('is_discoverable', True)}",
                title="Created",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()


@topics.command("delete")
@click.argument("topic_id")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
def delete_topic(topic_id, api_key, server):
    """Permanently delete a topic."""
    try:
        config = Config.load()
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        if not Confirm.ask(
            f"[red]Permanently delete[/red] topic {topic_id}? This cannot be undone!",
            default=False,
        ):
            console.print("Cancelled")
            return

        client = NotiferClient(config)
        client.delete_topic(topic_id)

        console.print(f"[green]✓[/green] Topic deleted: {topic_id}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()
