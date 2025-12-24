"""CLI for kef configuration manager."""

from pathlib import Path

import click
from rich.console import Console
from rich.syntax import Syntax
from rich.tree import Tree

from .config import ConfigManager

console = Console()


@click.group()
@click.version_option()
def cli():
    """kef - Kaggle Efficient Framework configuration manager."""
    pass


@cli.command()
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
def completion(shell: str):
    """Generate completion script for the specified shell.

    To enable completion, add the following to your shell profile:

    (zsh)  eval "$(_KEF_COMPLETE=zsh_source kef)"

    (bash) eval "$(_KEF_COMPLETE=bash_source kef)"

    (fish) _KEF_COMPLETE=fish_source kef | source
    """
    if shell == "fish":
        click.echo("_KEF_COMPLETE=fish_source kef | source")
    else:
        click.echo(f'eval "$(_{"KEF"}_COMPLETE={shell}_source kef)"')


@cli.command()
@click.argument("key", required=False)
@click.option("--resolve/--no-resolve", default=True, help="Resolve OmegaConf interpolations.")
def view(key: str | None, resolve: bool):
    """View the merged configuration.

    If KEY is provided, only that part of the configuration is shown.
    Supports dot notation (e.g., unity_catalog.server).
    """
    try:
        manager = ConfigManager()
        manager.load()

        if key:
            value = manager.get(key)
            if value is None:
                console.print(f"[red]Key '{key}' not found in configuration.[/red]")
                return

            # If it's a sub-config, convert to YAML
            from omegaconf import DictConfig, OmegaConf

            if isinstance(value, DictConfig):
                content = OmegaConf.to_yaml(value, resolve=resolve)
                syntax = Syntax(content, "yaml", theme="monokai", background_color="default")
                console.print(syntax)
            else:
                console.print(value)
        else:
            content = manager.to_yaml()
            syntax = Syntax(content, "yaml", theme="monokai", background_color="default")
            console.print(syntax)

    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred:[/red] {e}")


@cli.command()
def info():
    """Show information about the configuration sources."""
    try:
        manager = ConfigManager()
        manager.discover()

        tree = Tree("[bold blue]kef Configuration Info[/bold blue]")

        tree.add(f"Working Directory: [cyan]{Path.cwd()}[/cyan]")

        if manager.base_config_path:
            tree.add(f"Base Config (Repo Root): [green]{manager.base_config_path}[/green]")
        else:
            tree.add("Base Config (Repo Root): [red]Not found[/red]")

        if manager.project_config_path:
            tree.add(f"Project Config: [green]{manager.project_config_path}[/green]")
        else:
            tree.add("Project Config: [red]Not found[/red]")

        console.print(tree)

    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")


if __name__ == "__main__":
    cli()
