"""
Interactive menu system for Claux CLI.

Provides a rich, user-friendly terminal interface.
"""

import sys
import os
import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from claux import __version__
from claux.i18n import get_language, t
from claux.core.user_config import get_config

# Fix Windows console encoding
if os.name == "nt":
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except Exception:
        pass

app = typer.Typer(help="Interactive mode")
console = Console(force_terminal=True, legacy_windows=False)

# Global flag to show banner only once
_banner_shown = False


def get_system_info():
    """Get system status information."""
    try:
        from claux.core.mcp import get_active_config
        from claux.core.profiles import get_active_profile

        mcp_config = get_active_config()
        profile = get_active_profile()
        py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        return {
            "python": py_version,
            "mcp": mcp_config or "none",
            "profile": profile or "none",
            "language": get_language(),
        }
    except Exception:
        return {
            "python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "mcp": "none",
            "profile": "none",
            "language": get_language(),
        }


def show_banner(force=False):
    """Display welcome banner with system info (only once by default)."""
    global _banner_shown

    if _banner_shown and not force:
        return

    _banner_shown = True

    # Get system info
    info = get_system_info()

    # Info bar
    info_line = f"🐍 Python {info['python']}  *  🔌 MCP: {info['mcp']}  *  🤖 Profile: {info['profile']}  *  🌍 {info['language'].upper()}"

    banner_panel = Panel(
        f"[bold cyan]🎼 {t('cli.interactive.banner_title')}[/bold cyan] [bold white]v{__version__}[/bold white]\n"
        f"[dim italic]{t('cli.interactive.banner_subtitle')}[/dim italic]\n\n"
        f"[dim]{info_line}[/dim]",
        border_style="bold cyan",
        padding=(1, 2),
    )

    console.print()
    console.print(banner_panel)
    console.print()


def show_help_footer():
    """Show compact help footer with keyboard shortcuts."""
    console.print("[dim]Keys: ↑↓ navigate | ↵ select | q quit | h help | Ctrl+C exit[/dim]\n")


def show_breadcrumbs(path: str):
    """Show navigation breadcrumbs."""
    breadcrumb = Text()
    breadcrumb.append("┌─ ", style="dim cyan")
    breadcrumb.append("📍 ", style="")

    parts = path.split(" > ")
    for i, part in enumerate(parts):
        if i > 0:
            breadcrumb.append(" -> ", style="dim cyan")
        breadcrumb.append(part, style="bold cyan" if i == len(parts) - 1 else "dim")

    console.print(breadcrumb)
    console.print()


def main_menu():
    """Show main interactive menu."""
    console.clear()
    show_banner()
    console.print(f"[bold cyan]{t('cli.interactive.menu_title')}[/bold cyan]\n")
    show_help_footer()

    # Group choices by category for better organization
    choices = [
        # Setup & Quick Start
        Choice(value="wizard", name=f"🧙  {t('cli.interactive.menu_wizard')}"),
        Separator(),
        # Launch
        Choice(value="launch", name=f"🚀  {t('cli.interactive.menu_launch')}"),
        Separator(),
        # Configuration
        Choice(value="mcp", name=f"🔌  {t('cli.interactive.menu_mcp')}"),
        Choice(value="agents", name=f"🤖  {t('cli.interactive.menu_agents')}"),
        Choice(value="config", name=f"⚙️  {t('cli.interactive.menu_config')}"),
        Choice(value="lang", name=f"🌍  {t('cli.interactive.menu_lang')}"),
        Separator(),
        # Tools & Utilities
        Choice(value="bookmarks", name=f"📚  {t('cli.interactive.menu_bookmarks')}"),
        Choice(value="doctor", name=f"🩺  {t('cli.interactive.menu_doctor')}"),
        Choice(value="history", name=f"📜  {t('cli.interactive.menu_history')}"),
        Separator(),
        # Help & Exit
        Choice(value="help", name=f"❓  {t('cli.interactive.menu_help')}"),
        Choice(value="exit", name=f"🚪  {t('cli.interactive.menu_exit')} (q)"),
    ]

    try:
        action = inquirer.select(
            message=t("cli.interactive.select_option"),
            choices=choices,
            default="wizard",
            pointer=">",
        ).execute()

        # Handle keyboard shortcuts
        if action == "q":
            action = "exit"

    except KeyboardInterrupt:
        return "exit"
    except Exception:
        # Fallback for Cygwin and other incompatible terminals
        console.print(f"[yellow]!  {t('cli.interactive.unsupported_terminal')}[/yellow]")
        console.print(f"[dim]{t('cli.interactive.try_different_terminal')}[/dim]\n")
        console.print(f"{t('cli.interactive.available_commands')}")
        console.print("  claux wizard    - Run setup wizard")
        console.print("  claux mcp       - Manage MCP configurations")
        console.print("  claux agents    - Manage agent profiles")
        console.print("  claux lang      - Change language")
        console.print("  claux --help    - Show all commands\n")
        return "exit"

    return action


def mcp_menu():
    """MCP configuration submenu."""
    from claux.core.mcp import list_configs, get_active_config

    console.clear()
    console.print(
        f"[bold cyan]{t('cli.interactive.mcp_title')}[/bold cyan] [dim]({t('cli.interactive.mcp_breadcrumb')})[/dim]\n"
    )
    show_help_footer()

    configs = list_configs()
    current = get_active_config()

    if not configs:
        console.print(f"[yellow]{t('cli.interactive.mcp_no_configs')}[/yellow]")
        console.print(f"[dim]{t('cli.interactive.mcp_invalid_directory')}[/dim]\n")
        typer.pause(t("cli.common.press_enter"))
        return

    # Create compact table
    table = Table(
        show_header=True,
        header_style="bold white",
        border_style="dim",
        padding=(0, 1),
    )
    table.add_column("", style="green", width=3)  # Status indicator
    table.add_column(t("cli.interactive.mcp_name"), style="cyan")
    table.add_column(t("cli.interactive.mcp_tokens"), style="yellow", justify="right")
    table.add_column(t("cli.interactive.mcp_description"), style="dim")

    config_details = {
        "base": ("~600", t("cli.interactive.mcp_base_desc")),
        "full": ("~5000", t("cli.interactive.mcp_full_desc")),
    }

    for config_name in configs:
        indicator = "[*]" if config_name == current else "[ ]"
        tokens, desc = config_details.get(config_name, ("?", t("cli.interactive.mcp_custom_desc")))
        table.add_row(indicator, config_name, tokens, desc)

    console.print(table)
    console.print()

    choices = []
    for c in configs:
        prefix = "[*] " if c == current else "    "
        choices.append(Choice(value=c, name=f"{prefix}{c}"))

    choices.append(Separator())
    choices.append(Choice(value="back", name=t("cli.interactive.back")))

    selection = inquirer.select(
        message=t("cli.interactive.mcp_select"),
        choices=choices,
        default=current if current else configs[0],
        pointer=">",
    ).execute()

    if selection == "back" or selection == "b":
        return

    # Switch MCP config
    from claux.core.mcp import switch_config

    switch_config(selection)

    console.print(f"\n[green]✓[/green] {t('cli.interactive.mcp_switched', config=selection)}")
    console.print(f"[yellow]![/yellow] {t('cli.interactive.mcp_restart')}\n")

    typer.pause(t("cli.common.press_enter"))


def agent_profiles_menu():
    """Agent profiles submenu."""
    from claux.core.profiles import list_profiles, get_active_profile

    console.clear()
    console.print(
        f"[bold cyan]{t('cli.interactive.agents_title')}[/bold cyan] [dim]({t('cli.interactive.agents_breadcrumb')})[/dim]\n"
    )
    show_help_footer()

    profiles = list_profiles()
    current = get_active_profile()

    if not profiles:
        console.print(f"[yellow]{t('cli.interactive.agents_no_profiles')}[/yellow]")
        console.print(f"[dim]{t('cli.interactive.mcp_invalid_directory')}[/dim]\n")
        typer.pause(t("cli.common.press_enter"))
        return

    # Create compact table
    table = Table(
        show_header=True,
        header_style="bold white",
        border_style="dim",
        padding=(0, 1),
    )
    table.add_column("", style="green", width=3)
    table.add_column(t("cli.interactive.agents_profile"), style="cyan")
    table.add_column(t("cli.interactive.agents_agents"), style="blue", justify="right")
    table.add_column(t("cli.interactive.agents_savings"), style="yellow", justify="right")
    table.add_column(t("cli.interactive.agents_description"), style="dim")

    profile_info = {
        "base": ("8", "82%", t("cli.interactive.agents_minimal")),
        "nextjs-full": ("28", "22%", t("cli.interactive.agents_nextjs_full")),
        "health-all": ("15", "56%", t("cli.interactive.agents_health_all")),
        "development": ("12", "67%", t("cli.interactive.agents_development")),
    }

    for profile in profiles:
        indicator = "[*]" if profile == current else "[ ]"
        agents, savings, desc = profile_info.get(
            profile, ("?", "?", t("cli.interactive.agents_custom"))
        )
        table.add_row(indicator, profile, agents, savings, desc)

    console.print(table)
    console.print()

    choices = []
    for p in profiles:
        prefix = "[*] " if p == current else "    "
        choices.append(Choice(value=p, name=f"{prefix}{p}"))

    choices.append(Separator())
    choices.append(Choice(value="back", name=t("cli.interactive.back")))

    selection = inquirer.select(
        message=t("cli.interactive.agents_select"),
        choices=choices,
        default=current if current else profiles[0],
        pointer=">",
    ).execute()

    if selection == "back" or selection == "b":
        return

    # Activate profile
    from claux.core.profiles import activate_profile

    activate_profile(selection)

    agents, savings, _ = profile_info.get(selection, ("?", "?", ""))
    console.print(f"\n[green]✓[/green] {t('cli.interactive.agents_activated', profile=selection)}")
    console.print(
        f"[dim]  {t('cli.interactive.agents_info', agents=agents, savings=savings)}[/dim]"
    )
    console.print(f"[yellow]![/yellow] {t('cli.interactive.mcp_restart')}\n")

    typer.pause(t("cli.common.press_enter"))


def language_menu():
    """Language settings submenu."""
    from claux.i18n import get_available_languages, set_language, get_language

    console.clear()
    console.print(
        f"[bold cyan]{t('cli.interactive.lang_title')}[/bold cyan] [dim]({t('cli.interactive.lang_breadcrumb')})[/dim]\n"
    )
    show_help_footer()

    langs = get_available_languages()
    current = get_language()

    lang_names = {
        "en": "English",
        "ru": "Russian (Русский)",
    }

    console.print(f"[dim]{t('cli.interactive.lang_select_prompt')}[/dim]\n")

    choices = []
    for lang in langs:
        prefix = "[*] " if lang == current else "    "
        choices.append(Choice(value=lang, name=f"{prefix}{lang_names.get(lang, lang)}"))

    choices.append(Separator())
    choices.append(Choice(value="back", name=t("cli.interactive.back")))

    selection = inquirer.select(
        message=t("cli.interactive.lang_select"),
        choices=choices,
        default=current,
        pointer=">",
    ).execute()

    if selection == "back" or selection == "b":
        return

    set_language(selection)

    # Reset banner flag so it shows with new language
    global _banner_shown
    _banner_shown = False

    console.print(
        f"\n[green]✓[/green] {t('cli.interactive.lang_switched', lang=lang_names.get(selection, selection))}"
    )
    console.print(f"[dim]  {t('cli.interactive.lang_env_note', lang=selection)}[/dim]")
    console.print(f"[dim]  {t('cli.interactive.lang_apply_next')}[/dim]\n")

    typer.pause(t("cli.common.press_enter"))


def config_menu():
    """Configuration menu."""
    config = get_config()

    console.clear()
    console.print(
        f"[bold cyan]{t('cli.interactive.config_title')}[/bold cyan] [dim]({t('cli.interactive.config_breadcrumb')})[/dim]\n"
    )
    show_help_footer()

    console.print(f"[dim]{t('cli.interactive.config_manage')}[/dim]\n")

    # Show current Claude Code behavior
    exit_after_close = config.get("claude.exit_after_close", True)
    behavior_text = (
        t("cli.interactive.config_claude_exit_enabled")
        if exit_after_close
        else t("cli.interactive.config_claude_exit_disabled")
    )
    console.print(f"[dim]Current: {behavior_text}[/dim]\n")

    choices = [
        Choice(value="view", name=t("cli.interactive.config_view")),
        Choice(value="toggle_claude", name=t("cli.interactive.config_toggle_claude_exit")),
        Choice(value="reset", name=t("cli.interactive.config_reset")),
        Separator(),
        Choice(value="back", name=t("cli.interactive.back")),
    ]

    selection = inquirer.select(
        message=t("cli.interactive.config_select"),
        choices=choices,
        pointer=">",
    ).execute()

    if selection == "back" or selection == "b":
        return
    elif selection == "view":
        import yaml

        console.print()
        console.print(f"[bold]{t('cli.interactive.config_current')}[/bold]\n")
        console.print(yaml.dump(config.load(), default_flow_style=False))
    elif selection == "toggle_claude":
        # Toggle the setting
        new_value = not exit_after_close
        config.set("claude.exit_after_close", new_value)

        behavior = (
            t("cli.interactive.config_claude_exit_enabled")
            if new_value
            else t("cli.interactive.config_claude_exit_disabled")
        )
        console.print(
            f"\n[green]✓[/green] {t('cli.interactive.config_claude_exit_changed', behavior=behavior)}"
        )
    elif selection == "reset":
        confirm = inquirer.confirm(
            message=t("cli.interactive.config_reset_confirm"),
            default=False,
        ).execute()
        if confirm:
            config.reset()
            console.print(f"\n[green]✓[/green] {t('cli.interactive.config_reset_success')}")

    console.print()
    typer.pause(t("cli.common.press_enter"))


def launch_claude_code():
    """Launch Claude Code with current configuration.

    Returns:
        str: "exit_all" if should exit claux after Claude Code closes, None otherwise
    """
    import shutil
    import subprocess
    from claux.core.mcp import get_active_config
    from claux.core.profiles import get_active_profile

    console.clear()
    console.print(
        f"[bold cyan]{t('cli.interactive.launch_title')}[/bold cyan] [dim]({t('cli.interactive.launch_breadcrumb')})[/dim]\n"
    )
    show_help_footer()

    # Check if claude command exists
    claude_path = shutil.which("claude")
    if not claude_path:
        console.print(f"[red]✗[/red] {t('cli.interactive.launch_not_found')}")
        console.print(f"[dim]{t('cli.interactive.launch_install_hint')}[/dim]\n")
        typer.pause(t("cli.common.press_enter"))
        return None

    # Get current configuration
    mcp_config = get_active_config() or "none"
    profile = get_active_profile() or "all agents"

    # Show current configuration
    console.print(f"[bold]{t('cli.interactive.launch_current_config')}[/bold]\n")

    config_table = Table(
        show_header=False,
        border_style="dim",
        padding=(0, 1),
    )
    config_table.add_column(style="cyan", width=20)
    config_table.add_column(style="white")

    config_table.add_row("🔌 MCP Config:", f"[yellow]{mcp_config}[/yellow]")
    config_table.add_row("🤖 Agent Profile:", f"[green]{profile}[/green]")
    config_table.add_row("📍 Directory:", f"[dim]{os.getcwd()}[/dim]")
    config_table.add_row("🛠️  Claude CLI:", f"[dim]{claude_path}[/dim]")

    console.print(config_table)
    console.print()

    # Confirm launch
    try:
        confirm = inquirer.confirm(
            message=t("cli.interactive.launch_confirm"),
            default=True,
        ).execute()

        if not confirm:
            return None

        console.print(f"\n[cyan]{t('cli.interactive.launch_starting')}[/cyan]")
        console.print()

        # Launch Claude Code
        try:
            # Check user preference for exit behavior
            config = get_config()
            exit_after_close = config.get("claude.exit_after_close", True)

            # On Windows, use the current console
            if os.name == "nt":
                subprocess.run([claude_path], check=False)
                # After Claude Code exits, check if should exit claux too
                if exit_after_close:
                    return "exit_all"
                else:
                    return None
            else:
                # On Unix-like systems
                if exit_after_close:
                    # Replace the current process completely
                    os.execvp(claude_path, [claude_path])
                else:
                    # Run as subprocess to return to menu
                    subprocess.run([claude_path], check=False)
                    return None
        except Exception as e:
            console.print(f"\n[red]✗[/red] {t('cli.interactive.launch_error', error=str(e))}\n")
            typer.pause(t("cli.common.press_enter"))
            return None

    except KeyboardInterrupt:
        console.print()
        return None


@app.command()
def menu():
    """Launch interactive menu."""
    while True:
        action = main_menu()

        if action == "exit":
            console.print(f"\n[bold cyan]{t('cli.interactive.goodbye')}[/bold cyan]\n")
            break
        elif action == "wizard":
            from claux.commands.wizard import setup

            setup(search_dir=None, max_depth=2, auto_yes=False)
        elif action == "mcp":
            mcp_menu()
        elif action == "agents":
            agent_profiles_menu()
        elif action == "launch":
            result = launch_claude_code()
            if result == "exit_all":
                console.print(f"\n[bold cyan]{t('cli.interactive.goodbye')}[/bold cyan]\n")
                break
        elif action == "lang":
            language_menu()
        elif action == "config":
            config_menu()
        elif action == "bookmarks":
            console.print(f"\n[yellow]{t('cli.interactive.feature_soon')}[/yellow]\n")
            typer.pause()
        elif action == "doctor":
            console.print(f"\n[yellow]{t('cli.interactive.feature_soon')}[/yellow]\n")
            typer.pause()
        elif action == "history":
            console.print(f"\n[yellow]{t('cli.interactive.feature_soon')}[/yellow]\n")
            typer.pause()
        elif action == "help":
            console.print(f"\n[bold]Help:[/bold] {t('cli.interactive.help_visit')}\n")
            typer.pause()


if __name__ == "__main__":
    app()
