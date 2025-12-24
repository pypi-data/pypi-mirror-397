"""
Interactive UI components for banner, help, and breadcrumbs.

Provides system info display and visual elements for the interactive menu.
"""

import sys
import os
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from claux import __version__
from claux.i18n import get_language, t
from claux.ui.industrial_theme import (
    IndustrialIcons as Icons,
    get_industrial_box,
    CLAUX_LOGO_INDUSTRIAL,
    NOTHING_THEME,
)

# Fix Windows console encoding
if os.name == "nt":
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleOutputCP(65001)  # UTF-8
    except Exception:
        pass

console = Console(force_terminal=True, legacy_windows=False, theme=NOTHING_THEME)


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


def show_banner(context, force=False):
    """Display context-aware welcome banner with project status."""
    # Import _banner_shown from interactive.py to maintain state
    from claux.commands import interactive

    if interactive._banner_shown and not force:
        return

    interactive._banner_shown = True

    # Get system info (for Python version and language)
    info = get_system_info()

    # Build status line based on context
    current_dir = context.git_root if context.git_root else Path.cwd()

    # Build banner content with ASCII art logo
    banner_lines = []

    # ASCII art logo with version
    logo_lines = CLAUX_LOGO_INDUSTRIAL.strip().split('\n')
    if len(logo_lines) > 0:
        logo_lines[0] += f"  v{__version__}"
    banner_lines.extend(logo_lines)
    banner_lines.append(t('cli.interactive.banner_subtitle'))
    banner_lines.append("")  # Empty line

    # Project path
    banner_lines.append(f"{Icons.PATH} {current_dir}")

    # Status line - show only when there are problems
    if context.is_git and context.has_claux:
        # Everything OK - no status needed (UNIX philosophy: silence is golden)
        pass
    elif context.is_git:
        # Git OK but Claux not installed - show warning
        status = f"{Icons.WARNING} Claux not installed"
        banner_lines.append(f"[yellow]{status}[/yellow]")
    else:
        # Not a git repository - show warning
        status = f"{Icons.WARNING} Not a git repository - limited functionality"
        banner_lines.append(f"[yellow]{status}[/yellow]")

    # MCP and Profile info (always show when Claux installed)
    if context.is_git and context.has_claux:
        mcp_str = context.mcp_config or "none"
        profile_str = context.agent_profile or "none"
        banner_lines.append(f"[dim]{Icons.MCP} MCP: {mcp_str}   {Icons.PROFILE} Profile: {profile_str}[/dim]")

    # System info line (Python, Language)
    sys_info = f"{Icons.LANGUAGE} Python {info['python']}   {Icons.LOCALE} {info['language'].upper()}"
    banner_lines.append(f"[dim]{sys_info}[/dim]")

    banner_panel = Panel(
        "\n".join(banner_lines),
        box=get_industrial_box(),
        border_style="primary",
        padding=(1, 2)
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
    breadcrumb.append(f"{Icons.PATH} ", style="")

    parts = path.split(" > ")
    for i, part in enumerate(parts):
        if i > 0:
            breadcrumb.append(" -> ", style="dim cyan")
        breadcrumb.append(part, style="bold cyan" if i == len(parts) - 1 else "dim")

    console.print(breadcrumb)
    console.print()
