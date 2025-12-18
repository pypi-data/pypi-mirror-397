"""Configuration management commands."""
import click
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import yaml

from ..config import Config

console = Console()


@click.group()
def config():
    """Manage CLI configuration."""
    pass


@config.command("init")
def init_config():
    """Initialize configuration file."""
    config_file = Config.config_path()

    if config_file.exists():
        console.print(f"[yellow]Config file already exists:[/yellow] {config_file}")
        if not click.confirm("Overwrite?", default=False):
            return

    # Create default config
    cfg = Config()
    cfg.save()

    console.print(
        Panel(
            f"[green]✓[/green] Configuration file created\n\n"
            f"Location: {config_file}\n\n"
            f"Next: Run [cyan]notifer login[/cyan] or set your API key with:\n"
            f"[cyan]notifer config set api-key YOUR_KEY[/cyan]",
            title="Config Initialized",
            border_style="green",
        )
    )


@config.command("show")
def show_config():
    """Show current configuration."""
    try:
        cfg = Config.load()
        config_data = cfg.to_dict()

        # Format as YAML for display
        yaml_output = yaml.dump(config_data, default_flow_style=False)
        syntax = Syntax(yaml_output, "yaml", theme="monokai", line_numbers=False)

        console.print(
            Panel(
                syntax,
                title=f"Configuration ({Config.config_path()})",
                border_style="cyan",
            )
        )

    except FileNotFoundError:
        console.print(
            "[yellow]No configuration file found.[/yellow]\n"
            "Run: notifer config init"
        )
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()


@config.command("set")
@click.argument("key")
@click.argument("value")
def set_config(key, value):
    """
    Set a configuration value.

    \b
    Examples:
      notifer config set api-key noti_abc123...
      notifer config set email user@example.com
    """
    try:
        cfg = Config.load()

        # Map CLI keys to config attributes
        key_mapping = {
            "api-key": "api_key",
            "api_key": "api_key",
            "email": "email",
        }

        config_key = key_mapping.get(key)
        if not config_key:
            console.print(
                f"[red]✗ Unknown config key:[/red] {key}\n"
                f"Valid keys: {', '.join(set(key_mapping.keys()))}"
            )
            raise click.Abort()

        # Set value
        setattr(cfg, config_key, value)
        cfg.save()

        console.print(f"[green]✓[/green] Set {key} = {value}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()


@config.command("get")
@click.argument("key")
def get_config(key):
    """Get a configuration value."""
    try:
        cfg = Config.load()

        key_mapping = {
            "api-key": "api_key",
            "api_key": "api_key",
            "email": "email",
        }

        config_key = key_mapping.get(key)
        if not config_key:
            console.print(f"[red]✗ Unknown config key:[/red] {key}")
            raise click.Abort()

        value = getattr(cfg, config_key, None)
        if value:
            console.print(value)
        else:
            console.print(f"[dim]{key} not set[/dim]")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="red")
        raise click.Abort()
