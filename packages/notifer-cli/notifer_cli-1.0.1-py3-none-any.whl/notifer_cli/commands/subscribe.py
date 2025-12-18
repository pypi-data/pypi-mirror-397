"""Subscribe command."""
import click
import json
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.table import Table

from ..client import NotiferClient
from ..config import Config

console = Console()


@click.command()
@click.argument("topics")
@click.option("--output", "-o", type=click.Path(), help="Save messages to file (JSONL format)")
@click.option("--since", help="Only show messages since timestamp (ISO format)")
@click.option("--api-key", help="API key for authentication")
@click.option("--server", help="Override server URL")
@click.option("--json", "json_output", is_flag=True, help="Output raw JSON (no formatting)")
def subscribe(topics, output, since, api_key, server, json_output):
    """
    Subscribe to topics and receive messages in real-time.

    TOPICS can be a single topic or comma-separated list.

    \b
    Examples:
      notifer subscribe my-topic
      notifer subscribe alerts,deployments
      notifer subscribe my-topic --output messages.jsonl
      notifer subscribe my-topic --since 2025-01-01T00:00:00Z
    """
    try:
        # Load config
        config = Config.load()

        # Override with command options
        if server:
            config.server = server
        if api_key:
            config.api_key = api_key

        # Parse topics
        topic_list = [t.strip() for t in topics.split(",")]

        # Open output file if specified
        output_file = None
        if output:
            output_file = open(output, "a")

        # Subscribe to first topic (for now, multi-topic requires multiple connections)
        topic = topic_list[0]
        if len(topic_list) > 1:
            console.print(
                f"[yellow]Note:[/yellow] Subscribing to first topic only: {topic}\n"
                f"Multi-topic support coming soon!"
            )

        client = NotiferClient(config)

        if not json_output:
            console.print(
                Panel(
                    f"[cyan]Subscribed to:[/cyan] {topic}\n"
                    f"[dim]Press Ctrl+C to stop[/dim]",
                    title="Listening",
                    border_style="cyan",
                )
            )

        # Subscribe and process messages
        message_count = 0
        for message in client.subscribe(topic, since=since):
            message_count += 1

            # Save to file if specified
            if output_file:
                output_file.write(json.dumps(message) + "\n")
                output_file.flush()

            # Output message
            if json_output:
                console.print(json.dumps(message))
            else:
                # Format message nicely
                timestamp = datetime.fromisoformat(message["timestamp"].replace("Z", "+00:00"))
                formatted_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

                title_text = message.get("title", "")
                priority_text = f"P{message.get('priority', 3)}"
                tags_text = ", ".join(message.get("tags", []))

                # Priority color
                priority = message.get("priority", 3)
                if priority >= 5:
                    priority_color = "red"
                elif priority >= 4:
                    priority_color = "yellow"
                else:
                    priority_color = "blue"

                # Build display
                header = f"[{priority_color}]{priority_text}[/{priority_color}]"
                if title_text:
                    header += f" [bold]{title_text}[/bold]"
                header += f" [dim]({formatted_time})[/dim]"

                console.print(f"\n{header}")
                console.print(message["message"])

                if tags_text:
                    console.print(f"[dim]Tags: {tags_text}[/dim]")

                console.print("[dim]" + "─" * 60 + "[/dim]")

    except KeyboardInterrupt:
        if not json_output:
            console.print(
                f"\n[green]✓[/green] Received {message_count} message(s). Disconnected."
            )
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()
    finally:
        if output_file:
            output_file.close()
