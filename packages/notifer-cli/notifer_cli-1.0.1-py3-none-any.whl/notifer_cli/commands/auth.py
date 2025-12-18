"""Authentication commands."""
import click
from rich.console import Console
from rich.panel import Panel
from getpass import getpass

from ..client import NotiferClient
from ..config import Config

console = Console()


@click.command()
@click.argument("email", required=False)
@click.option("--server", help="Override server URL")
def login(email, server):
    """
    Login with email and password.

    Stores JWT tokens in ~/.notifer.yaml for future requests.

    \b
    Examples:
      notifer login user@example.com
      notifer login  # Will prompt for email
    """
    try:
        # Load config
        config = Config.load()
        if server:
            config.server = server

        # Get email if not provided
        if not email:
            email = click.prompt("Email")

        # Get password (hidden input)
        password = getpass("Password: ")

        # Login
        client = NotiferClient(config)
        result = client.login(email, password)

        # Save tokens to config
        config.save()

        console.print(
            Panel(
                f"[green]✓[/green] Logged in as [cyan]{result['user']['email']}[/cyan]\n\n"
                f"Username: {result['user']['username']}\n"
                f"Tier: {result['user']['subscription_tier']}\n"
                f"Tokens saved to: {Config.config_path()}",
                title="Login Successful",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]✗ Login failed:[/red] {str(e)}", style="red")
        raise click.Abort()


@click.command()
def logout():
    """
    Logout and clear stored credentials.

    Removes tokens from ~/.notifer.yaml
    """
    try:
        config = Config.load()

        # Clear auth data
        config.email = None
        config.access_token = None
        config.refresh_token = None
        config.api_key = None
        config.save()

        console.print(
            Panel(
                "[green]✓[/green] Logged out successfully\n\n"
                "All credentials cleared from config file.",
                title="Logout",
                border_style="green",
            )
        )

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()
