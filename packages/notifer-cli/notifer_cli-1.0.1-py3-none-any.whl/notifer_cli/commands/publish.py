"""Publish command."""
import click
from rich.console import Console
from rich.panel import Panel

from ..client import NotiferClient
from ..config import Config

console = Console()


@click.command()
@click.argument("topic")
@click.argument("message")
@click.option("--title", "-t", help="Message title")
@click.option("--priority", "-p", type=int, default=3, help="Priority (1-5, default: 3)")
@click.option("--tags", help="Comma-separated tags")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
def publish(topic, message, title, priority, tags, api_key, server):
    """
    Publish a message to a topic.

    \b
    Examples:
      notifer publish my-topic "Hello World!"
      notifer publish alerts "Server down!" --priority 5 --tags urgent,server
      notifer publish deploy "# Success\\n\\n**Deployed** v1.2.3" --title "Deploy"
    """
    try:
        # Load config
        config = Config.load()

        # Override with command options
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        # Parse tags
        tag_list = tags.split(",") if tags else []

        # Create client and publish
        client = NotiferClient(config)
        result = client.publish(
            topic=topic,
            message=message,
            title=title,
            priority=priority,
            tags=tag_list,
        )

        # Success message
        console.print(
            Panel(
                f"[green]✓[/green] Message published to [cyan]{topic}[/cyan]\n\n"
                f"ID: {result['id']}\n"
                f"Timestamp: {result['timestamp']}\n"
                f"Priority: {result['priority']}",
                title="Published",
                border_style="green",
            )
        )

    except Exception as e:
        # Try to get detailed error message from response
        error_msg = str(e)
        if hasattr(e, 'response') and e.response is not None:
            try:
                detail = e.response.json().get('detail', error_msg)
                error_msg = detail
            except Exception:
                pass
        console.print(f"[red]✗ Error:[/red] {error_msg}", style="red")
        raise click.Abort()
