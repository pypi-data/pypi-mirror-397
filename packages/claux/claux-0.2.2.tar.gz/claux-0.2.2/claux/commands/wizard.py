"""
Setup wizard for Claude Code Orchestrator Kit.

Interactive setup with auto-discovery of projects and intelligent configuration.
"""

import typer
from pathlib import Path
from typing import List, Dict, Any, Optional
from enum import Enum

from claux.ui import Console
from claux.commands.init import get_orchestrator_install_path
import shutil


app = typer.Typer(help="Interactive setup wizard")


class ProjectType(str, Enum):
    """Detected project types."""

    PYTHON = "python"
    NODEJS = "nodejs"
    NEXTJS = "nextjs"
    REACT = "react"
    DJANGO = "django"
    FASTAPI = "fastapi"
    UNKNOWN = "unknown"


def detect_project_type(project_path: Path) -> ProjectType:
    """
    Detect project type based on files present.

    Args:
        project_path: Path to project directory.

    Returns:
        Detected ProjectType.
    """
    # Check for Next.js
    if (
        (project_path / "next.config.js").exists()
        or (project_path / "next.config.ts").exists()
        or (project_path / "next.config.mjs").exists()
    ):
        return ProjectType.NEXTJS

    # Check for React (package.json with react dependency)
    package_json = project_path / "package.json"
    if package_json.exists():
        try:
            import json

            with open(package_json) as f:
                data = json.load(f)
                deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                if "react" in deps:
                    return ProjectType.REACT
                if "next" in deps:
                    return ProjectType.NEXTJS
        except Exception:
            pass

    # Check for Django
    if (project_path / "manage.py").exists():
        manage_py = project_path / "manage.py"
        if manage_py.exists():
            content = manage_py.read_text()
            if "django" in content.lower():
                return ProjectType.DJANGO

    # Check for FastAPI
    requirements = project_path / "requirements.txt"
    if requirements.exists():
        content = requirements.read_text()
        if "fastapi" in content.lower():
            return ProjectType.FASTAPI

    pyproject = project_path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if "fastapi" in content.lower():
            return ProjectType.FASTAPI

    # Check for Python (generic)
    if (
        (project_path / "setup.py").exists()
        or (project_path / "pyproject.toml").exists()
        or (project_path / "requirements.txt").exists()
        or list(project_path.glob("*.py"))
    ):
        return ProjectType.PYTHON

    # Check for Node.js (generic)
    if (project_path / "package.json").exists():
        return ProjectType.NODEJS

    return ProjectType.UNKNOWN


def recommend_mcp_config(project_type: ProjectType) -> str:
    """
    Recommend MCP configuration based on project type.

    Args:
        project_type: Detected project type.

    Returns:
        Recommended MCP config name (e.g., "base", "frontend", "supabase").
    """
    recommendations = {
        ProjectType.NEXTJS: "frontend",
        ProjectType.REACT: "frontend",
        ProjectType.DJANGO: "supabase",
        ProjectType.FASTAPI: "supabase",
        ProjectType.PYTHON: "base",
        ProjectType.NODEJS: "base",
        ProjectType.UNKNOWN: "base",
    }
    return recommendations.get(project_type, "base")


def find_projects_in_directory(
    search_dir: Path, max_depth: int = 3, exclude_dirs: Optional[List[str]] = None
) -> List[Dict[str, Any]]:
    """
    Find all git repositories in directory tree.

    Args:
        search_dir: Directory to search.
        max_depth: Maximum depth to search.
        exclude_dirs: Directory names to exclude (e.g., ["node_modules", ".venv"]).

    Returns:
        List of project dicts with keys: path, name, type, has_orchestrator.
    """
    if exclude_dirs is None:
        exclude_dirs = [
            "node_modules",
            ".venv",
            "venv",
            ".git",
            "__pycache__",
            "dist",
            "build",
            ".next",
            "target",
            ".cache",
            ".pytest_cache",
        ]

    projects = []

    def search_recursive(current_dir: Path, current_depth: int):
        if current_depth > max_depth:
            return

        # Check if current directory is a git repo
        if (current_dir / ".git").exists():
            project_type = detect_project_type(current_dir)
            has_orchestrator = (current_dir / ".claude").exists()

            projects.append(
                {
                    "path": current_dir,
                    "name": current_dir.name,
                    "type": project_type,
                    "has_orchestrator": has_orchestrator,
                    "recommended_mcp": recommend_mcp_config(project_type),
                }
            )
            # Don't search deeper if we found a git repo
            return

        # Search subdirectories
        try:
            for item in current_dir.iterdir():
                if item.is_dir() and item.name not in exclude_dirs:
                    search_recursive(item, current_depth + 1)
        except PermissionError:
            pass

    search_recursive(search_dir, 0)
    return projects


@app.command()
def setup(
    search_dir: Optional[Path] = typer.Option(
        None,
        "--search-dir",
        "-s",
        help="Directory to search for projects (default: ~/PycharmProjects, ~/projects, ~/Documents)",
    ),
    max_depth: int = typer.Option(
        2, "--max-depth", "-d", help="Maximum depth to search for projects"
    ),
    auto_yes: bool = typer.Option(
        False, "--yes", "-y", help="Automatically answer yes to all prompts"
    ),
):
    """
    Interactive setup wizard with auto-discovery of projects.

    Finds all git repositories in common project directories and offers
    to install orchestrator with recommended configuration for each.

    Examples:
        # Search in default locations
        claux wizard setup

        # Search in specific directory
        claux wizard setup -s ~/my-projects

        # Auto-accept all (useful for CI)
        claux wizard setup -y
    """
    Console.print()
    Console.print_header("🧙 Claude Code Orchestrator - Setup Wizard")
    Console.print()
    Console.print("This wizard will:", style="dim")
    Console.print("  1. Find all your git projects", style="dim")
    Console.print("  2. Detect project types", style="dim")
    Console.print("  3. Recommend optimal configurations", style="dim")
    Console.print("  4. Install and configure orchestrator", style="dim")
    Console.print()

    # Determine search directories
    if search_dir:
        search_dirs = [Path(search_dir)]
    else:
        home = Path.home()
        search_dirs = [
            home / "PycharmProjects",
            home / "projects",
            home / "Documents",
            home / "dev",
            home / "code",
            Path.cwd(),
        ]
        # Only use directories that exist
        search_dirs = [d for d in search_dirs if d.exists()]

    if not search_dirs:
        Console.print_error("No search directories found!")
        raise typer.Exit(1)

    Console.print_info(f"Searching for projects in {len(search_dirs)} location(s)...")
    for d in search_dirs:
        Console.print(f"  * {d}", style="dim")
    Console.print()

    # Find all projects
    all_projects = []
    for search_dir in search_dirs:
        Console.print(f"📂 Scanning {search_dir}...", style="dim")
        projects = find_projects_in_directory(search_dir, max_depth=max_depth)
        all_projects.extend(projects)

    if not all_projects:
        Console.print_warning("No git projects found!")
        Console.print()
        Console.print("Try:", style="dim")
        Console.print("  * Increase search depth: --max-depth 3", style="dim")
        Console.print("  * Specify directory: --search-dir /path/to/projects", style="dim")
        Console.print("  * Or use direct init: claux init /path/to/project", style="dim")
        raise typer.Exit(0)

    Console.print()
    Console.print_success(f"Found {len(all_projects)} project(s)!")
    Console.print()

    # Display projects table
    Console.print_subheader("Projects found:")
    Console.print()

    for i, project in enumerate(all_projects, 1):
        status = "[*] Installed" if project["has_orchestrator"] else "[ ] Not installed"
        status_style = "green" if project["has_orchestrator"] else "yellow"

        type_display = project["type"].value.capitalize()
        Console.print(
            f"  [{i}] {project['name']:<30} "
            f"[dim]{type_display:<12}[/dim] "
            f"[{status_style}]{status}[/{status_style}]"
        )

    Console.print()

    # Ask which projects to setup
    if not auto_yes:
        Console.print_prompt("Which projects would you like to setup?")
        Console.print("  Enter numbers (e.g., '1,3,5' or '1-3' or 'all'):", style="dim")
        choice = typer.prompt("", default="all")
    else:
        choice = "all"

    # Parse selection
    selected_indices = set()
    if choice.lower() == "all":
        selected_indices = set(range(len(all_projects)))
    else:
        for part in choice.split(","):
            part = part.strip()
            if "-" in part:
                # Range (e.g., "1-3")
                start, end = part.split("-")
                start_idx = int(start.strip()) - 1
                end_idx = int(end.strip()) - 1
                selected_indices.update(range(start_idx, end_idx + 1))
            else:
                # Single number
                selected_indices.add(int(part) - 1)

    selected_projects = [
        all_projects[i] for i in sorted(selected_indices) if 0 <= i < len(all_projects)
    ]

    if not selected_projects:
        Console.print_warning("No projects selected. Exiting.")
        raise typer.Exit(0)

    Console.print()
    Console.print_info(f"Installing orchestrator in {len(selected_projects)} project(s)...")
    Console.print()

    # Get orchestrator source
    try:
        install_root = get_orchestrator_install_path()
        source_claude_dir = install_root / ".claude"
    except FileNotFoundError as e:
        Console.print_error(str(e))
        raise typer.Exit(1)

    # Install in each selected project
    success_count = 0
    for project in selected_projects:
        project_path = project["path"]
        project_name = project["name"]

        Console.print(f"📦 {project_name}", style="bold")

        # Skip if already installed (unless force)
        if project["has_orchestrator"]:
            Console.print("  ⊙ Already installed, skipping", style="yellow")
            Console.print()
            continue

        try:
            # Copy .claude directory
            target_claude_dir = project_path / ".claude"
            shutil.copytree(source_claude_dir, target_claude_dir)

            # Update .gitignore
            gitignore_path = project_path / ".gitignore"
            gitignore_entries = [
                ".tmp/",
                ".claude/settings.local.json",
                ".claude/.active-agent-profile",
                ".claude/backups/",
            ]

            if gitignore_path.exists():
                existing_content = gitignore_path.read_text(encoding="utf-8")
                new_entries = [e for e in gitignore_entries if e not in existing_content]

                if new_entries:
                    with open(gitignore_path, "a", encoding="utf-8") as f:
                        f.write("\n# Claude Code Orchestrator\n")
                        f.write("\n".join(new_entries))
                        f.write("\n")
            else:
                with open(gitignore_path, "w", encoding="utf-8") as f:
                    f.write("# Claude Code Orchestrator\n")
                    f.write("\n".join(gitignore_entries))
                    f.write("\n")

            Console.print("  [*] Installed", style="green")
            Console.print(f"  [*] Detected: {project['type'].value}", style="dim")
            Console.print(f"  [*] Recommended MCP: {project['recommended_mcp']}", style="dim")
            success_count += 1

        except Exception as e:
            Console.print(f"  [X] Failed: {e}", style="red")

        Console.print()

    # Summary
    Console.print()
    Console.print_success(
        f"[*] Setup complete! Installed in {success_count}/{len(selected_projects)} project(s)"
    )
    Console.print()

    # Next steps
    Console.print_subheader("Next steps:")
    Console.print("  1. Navigate to each project", style="dim")
    Console.print("  2. Activate profile: [code]claux agents activate base[/code]", style="dim")
    Console.print("  3. Configure MCP: [code]claux mcp switch <config>[/code]", style="dim")
    Console.print("  4. Restart Claude Code", style="dim")
    Console.print()
    Console.print("For project-specific MCP recommendations, see the output above.", style="dim")
    Console.print()
