"""
CLI Commands for nostromo.

Provides the main entry points:
- nostromo: Launch TUI
- nostromo configure: Setup wizard
- nostromo rotate: Key rotation
- nostromo status: Show configuration
"""

import getpass
import sys
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from nostromo_core.theme import (
    DISPLAY_NAME,
    HEADER_COMPACT,
    PRIMARY,
    SYSTEM_NAME,
)
from nostromo_core.theme.errors import NostromoError, format_error

from nostromo_cli.config import get_config_manager
from nostromo_cli.secrets import PROVIDERS, Provider, get_secrets_manager

# Create Typer app
app = typer.Typer(
    name="nostromo",
    help=f"{SYSTEM_NAME} - Terminal Interface",
    add_completion=False,
    rich_markup_mode="rich",
)

# Rich console for styled output
console = Console()


def print_header() -> None:
    """Print the MOTHER header."""
    console.print(HEADER_COMPACT, style=f"bold {PRIMARY}")


def print_error(message: str) -> None:
    """Print a themed error message."""
    console.print(f"\n*** {SYSTEM_NAME} ALERT ***", style="bold red")
    console.print(message, style="red")


def print_success(message: str) -> None:
    """Print a success message."""
    console.print(f"\n✓ {message}", style=f"bold {PRIMARY}")


@app.command()
def main(
    config_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--config-dir",
            "-c",
            help="Override configuration directory",
        ),
    ] = None,
    providers_config: Annotated[
        Optional[Path],
        typer.Option(
            "--llm-config",
            help="Override providers.toml path",
        ),
    ] = None,
    user_config: Annotated[
        Optional[Path],
        typer.Option(
            "--user-config",
            help="Override user.toml path",
        ),
    ] = None,
    session: Annotated[
        Optional[str],
        typer.Option(
            "--session",
            "-s",
            help="Session ID to use or resume",
        ),
    ] = None,
) -> None:
    """
    Launch the MU-TH-UR 6000 interface.

    Full-screen terminal chat interface with Aliens aesthetic.
    """
    # Initialize config manager with overrides
    config = get_config_manager(config_dir, providers_config, user_config)

    # Ensure configs exist
    config.ensure_configs_exist()

    # Check if any provider is configured
    secrets = get_secrets_manager()
    configured = secrets.list_configured_providers()

    if not configured:
        print_header()
        print_error(format_error(NostromoError.NO_AUTH))
        console.print("\nRun [bold]nostromo configure[/] to set up your API keys.\n")
        raise typer.Exit(1)

    # Check if active provider has a key
    active_provider = config.get_active_provider()
    if active_provider not in configured:
        print_header()
        print_error(
            format_error(NostromoError.KEY_MISSING, provider=active_provider.upper())
        )
        console.print(
            f"\nRun [bold]nostromo configure --provider {active_provider}[/] to configure it.\n"
        )
        raise typer.Exit(1)

    # Launch TUI
    from nostromo_cli.app import NostromoApp

    tui_app = NostromoApp(config=config, session_id=session)
    tui_app.run()


@app.command()
def configure(
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="Configure specific provider (anthropic, openai)",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Force reconfiguration even if already set",
        ),
    ] = False,
) -> None:
    """
    Configure API keys and settings.

    Interactive setup wizard for first-time configuration
    or updating existing settings.
    """
    print_header()
    console.print(f"\n*** {SYSTEM_NAME} CONFIGURATION PROTOCOL ***\n", style=f"bold {PRIMARY}")

    config = get_config_manager()
    config.ensure_configs_exist()

    secrets = get_secrets_manager()

    # Show storage type
    console.print(f"STORAGE: {secrets.get_storage_type()}\n", style="dim")

    providers_to_configure: list[Provider] = []

    if provider:
        if provider.lower() not in PROVIDERS:
            print_error(format_error(NostromoError.INVALID_PROVIDER, provider=provider.upper()))
            raise typer.Exit(1)
        providers_to_configure = [provider.lower()]  # type: ignore
    else:
        providers_to_configure = list(PROVIDERS)

    for prov in providers_to_configure:
        existing = secrets.get_key(prov)

        if existing and not force:
            masked = existing[:8] + "..." + existing[-4:] if len(existing) > 12 else "****"
            console.print(f"[bold]{prov.upper()}[/]: CONFIGURED ({masked})")

            if not typer.confirm("Reconfigure?", default=False):
                continue

        console.print(f"\n[bold]{prov.upper()} API KEY CONFIGURATION[/]")
        console.print("─" * 40)

        while True:
            api_key = getpass.getpass(f"ENTER {prov.upper()} API KEY: ")

            if not api_key.strip():
                if provider:
                    # Specific provider requested, require input
                    console.print("KEY CANNOT BE EMPTY.", style="red")
                    continue
                else:
                    # Full wizard, allow skip
                    console.print("SKIPPED.", style="dim")
                    break

            confirm = getpass.getpass("CONFIRM API KEY: ")

            if api_key != confirm:
                console.print("KEYS DO NOT MATCH. RETRY.", style="red")
                continue

            try:
                secrets.store_key(prov, api_key)
                print_success(f"{prov.upper()} KEY STORED IN SECURE VAULT")
            except Exception as e:
                print_error(f"FAILED TO STORE KEY: {e}")
                raise typer.Exit(1)

            break

    # Set active provider if only one is configured
    configured = secrets.list_configured_providers()
    if len(configured) == 1:
        config.set_active_provider(configured[0])
        console.print(f"\nACTIVE PROVIDER SET TO: [bold]{configured[0].upper()}[/]")
    elif len(configured) > 1:
        console.print(f"\nCONFIGURED PROVIDERS: {', '.join(p.upper() for p in configured)}")
        console.print(f"ACTIVE PROVIDER: [bold]{config.get_active_provider().upper()}[/]")
        console.print(
            "\nTo change active provider, edit [bold]~/.config/nostromo/providers.toml[/]"
        )

    console.print(f"\n{SYSTEM_NAME} CONFIGURATION COMPLETE.\n", style=f"bold {PRIMARY}")


@app.command()
def rotate(
    provider: Annotated[
        Optional[str],
        typer.Option(
            "--provider",
            "-p",
            help="Provider to rotate key for",
        ),
    ] = None,
    all_keys: Annotated[
        bool,
        typer.Option(
            "--all",
            "-a",
            help="Rotate all configured keys",
        ),
    ] = False,
) -> None:
    """
    Rotate API keys.

    Replace existing API keys with new ones.
    """
    print_header()
    console.print(f"\n*** {SYSTEM_NAME} KEY ROTATION PROTOCOL ***\n", style=f"bold {PRIMARY}")

    secrets = get_secrets_manager()
    configured = secrets.list_configured_providers()

    if not configured:
        print_error(format_error(NostromoError.NO_AUTH))
        raise typer.Exit(1)

    providers_to_rotate: list[Provider] = []

    if all_keys:
        providers_to_rotate = configured
    elif provider:
        if provider.lower() not in PROVIDERS:
            print_error(format_error(NostromoError.INVALID_PROVIDER, provider=provider.upper()))
            raise typer.Exit(1)
        if provider.lower() not in configured:
            print_error(
                format_error(NostromoError.KEY_MISSING, provider=provider.upper())
            )
            raise typer.Exit(1)
        providers_to_rotate = [provider.lower()]  # type: ignore
    else:
        print_error("SPECIFY --provider OR --all")
        raise typer.Exit(1)

    for prov in providers_to_rotate:
        console.print(f"\n[bold]{prov.upper()} KEY ROTATION[/]")
        console.print("─" * 40)

        existing = secrets.get_key(prov)
        if existing:
            masked = existing[:8] + "..." if len(existing) > 8 else "****"
            console.print(f"CURRENT KEY: {masked}")

        while True:
            new_key = getpass.getpass(f"ENTER NEW {prov.upper()} API KEY: ")

            if not new_key.strip():
                console.print(format_error(NostromoError.KEY_ROTATION_ABORT), style="yellow")
                break

            confirm = getpass.getpass("CONFIRM NEW KEY: ")

            if new_key != confirm:
                console.print("KEYS DO NOT MATCH. RETRY.", style="red")
                continue

            try:
                secrets.rotate_key(prov, new_key)
                print_success(format_error(NostromoError.KEY_ROTATION_SUCCESS, provider=prov.upper()))
            except Exception as e:
                print_error(f"ROTATION FAILED: {e}")
                console.print(format_error(NostromoError.KEY_ROTATION_ABORT), style="yellow")

            break

    console.print(f"\n{SYSTEM_NAME} KEY ROTATION COMPLETE.\n", style=f"bold {PRIMARY}")


@app.command()
def status() -> None:
    """
    Show configuration status.

    Display configured providers, active settings, and storage info.
    """
    print_header()
    console.print(f"\n*** {SYSTEM_NAME} STATUS REPORT ***\n", style=f"bold {PRIMARY}")

    config = get_config_manager()
    secrets = get_secrets_manager()

    # Storage info
    console.print(f"STORAGE TYPE: {secrets.get_storage_type()}")
    console.print(f"CONFIG DIR: ~/.config/nostromo/")
    console.print(f"DATA DIR: ~/.local/share/nostromo/")
    console.print()

    # Provider status table
    table = Table(title="PROVIDER STATUS", style=PRIMARY)
    table.add_column("PROVIDER", style="bold")
    table.add_column("STATUS")
    table.add_column("MODEL")
    table.add_column("ACTIVE")

    configured = secrets.list_configured_providers()
    active = config.get_active_provider() if config.providers_exists() else None

    for prov in PROVIDERS:
        status = "[green]CONFIGURED[/]" if prov in configured else "[red]NOT CONFIGURED[/]"
        model = ""
        is_active = ""

        if prov in configured:
            try:
                prov_config = config.get_provider_config(prov)
                model = prov_config.model
            except Exception:
                model = "N/A"

        if prov == active:
            is_active = "[bold green]◉ ACTIVE[/]"

        table.add_row(prov.upper(), status, model, is_active)

    console.print(table)

    # User config summary
    console.print()
    try:
        user_config = config.get_user_config()
        console.print("[bold]USER PREFERENCES:[/]")
        console.print(f"  TYPING EFFECT: {'ENABLED' if user_config.typing_effect else 'DISABLED'}")
        console.print(f"  TYPING SPEED: {user_config.typing_speed} CHARS/SEC")
        console.print(f"  HISTORY: {'ENABLED' if user_config.history_enabled else 'DISABLED'}")
    except Exception:
        console.print("[dim]USER CONFIG: NOT FOUND[/]")

    console.print(f"\n{DISPLAY_NAME} READY.\n", style=f"bold {PRIMARY}")


@app.command()
def version() -> None:
    """Show version information."""
    from nostromo_cli import __version__

    console.print(f"{SYSTEM_NAME} INTERFACE", style=f"bold {PRIMARY}")
    console.print(f"VERSION: {__version__}")


if __name__ == "__main__":
    app()
