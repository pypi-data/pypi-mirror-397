"""Main CLI entry point."""
import click
from rich.console import Console

from .commands import publish, subscribe, keys, topics, config, auth

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="notifer")
@click.pass_context
def cli(ctx):
    """
    Notifer CLI - Simple pub-sub notifications from the command line.

    Send and receive notifications, manage API keys, and configure topics.

    \b
    Examples:
      # Publish a message
      notifer publish my-topic "Hello World!"

      # Subscribe to messages
      notifer subscribe my-topic

      # Manage API keys
      notifer keys create "CI/CD" --scopes publish

    For more help on a specific command:
      notifer <command> --help
    """
    ctx.ensure_object(dict)


# Register command groups
cli.add_command(publish.publish)
cli.add_command(subscribe.subscribe)
cli.add_command(keys.keys)
cli.add_command(topics.topics)
cli.add_command(config.config)
cli.add_command(auth.login)
cli.add_command(auth.logout)


if __name__ == "__main__":
    cli()
