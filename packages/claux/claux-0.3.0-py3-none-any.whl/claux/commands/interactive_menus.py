"""
Interactive menu components for MCP, agents, language, and configuration.

Provides submenu handlers for different configuration areas.
"""

import typer
from InquirerPy import inquirer
from InquirerPy.base.control import Choice
from InquirerPy.separator import Separator
from rich.console import Console
from rich.table import Table

from claux.i18n import t
from claux.core.user_config import get_config
from claux.ui.industrial_theme import (
    IndustrialIcons as Icons,
    format_status,
    format_number,
    NOTHING_THEME,
)

console = Console(force_terminal=True, legacy_windows=False, theme=NOTHING_THEME)


def mcp_menu():
    """MCP configuration submenu."""
    from claux.core.mcp import list_configs, get_active_config

    console.clear()
    console.print(
        f"[bold cyan]{t('cli.interactive.mcp_title')}[/bold cyan] [dim]({t('cli.interactive.mcp_breadcrumb')})[/dim]\n"
    )
    from claux.commands.interactive_ui import show_help_footer
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
        "base": (format_number(600), t("cli.interactive.mcp_base_desc")),
        "full": (format_number(5000, abbreviated=True), t("cli.interactive.mcp_full_desc")),
    }

    for config_name in configs:
        indicator = format_status(config_name == current)
        tokens, desc = config_details.get(config_name, ("?", t("cli.interactive.mcp_custom_desc")))
        table.add_row(indicator, config_name, tokens, desc)

    console.print(table)
    console.print()

    choices = []
    for c in configs:
        prefix = f"{Icons.ACTIVE} " if c == current else f"{Icons.INACTIVE} "
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
    from claux.commands.interactive_ui import show_help_footer
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
        indicator = format_status(profile == current)
        agents, savings, desc = profile_info.get(
            profile, ("?", "?", t("cli.interactive.agents_custom"))
        )
        table.add_row(indicator, profile, agents, savings, desc)

    console.print(table)
    console.print()

    choices = []
    for p in profiles:
        prefix = f"{Icons.ACTIVE} " if p == current else f"{Icons.INACTIVE} "
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
    from claux.commands.interactive_ui import show_help_footer
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
        prefix = f"{Icons.ACTIVE} " if lang == current else f"{Icons.INACTIVE} "
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
    from claux.commands import interactive
    interactive._banner_shown = False

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
    from claux.commands.interactive_ui import show_help_footer
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
