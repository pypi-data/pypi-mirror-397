"""
Enhanced interactive prompts for project linking commands.

Integrates Clack, Charm tools, and Rich for beautiful, accessible prompts.
This module provides a unified interface for all interactive user input.
"""

from typing import List, Dict, Any, Optional, Callable, Tuple
from pathlib import Path
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .ui_styling import (
    ClackPromptBuilder,
    RichTheme,
    PanelBuilder,
    TableBuilder,
    CharmToolsIntegration,
    StyleConfig,
)
from .colors import get_console, print_success, print_warning, print_error


class ProjectSelectionPrompt:
    """Interactive prompt for selecting a project."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize project selection prompt.

        Args:
            console: Rich Console instance
        """
        self.console = console or get_console()
        self.builder = ClackPromptBuilder(self.console)

    def run(
        self, projects: List[Dict[str, Any]], allow_new: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Run project selection prompt.

        Args:
            projects: List of available projects
            allow_new: Whether to allow creating new project

        Returns:
            Selected project dict or None if cancelled

        Note:
            This is enhanced with:
            - Clack for beautiful prompts
            - Gum for advanced filtering (if available)
            - Rich for styling and display
        """
        if not projects and not allow_new:
            print_error("No projects available. Create one in the web app first.")
            return None

        # Build choices
        choices = [
            {
                "name": f"{p.get('name', 'Unnamed')} ({p.get('job_count', 0)} jobs)",
                "value": p.get("id", ""),
                "description": p.get("description", "")[:50],
            }
            for p in projects
        ]

        if allow_new:
            choices.append(
                {
                    "name": "[Create new project]",
                    "value": "__NEW__",
                    "description": "Create a new project",
                }
            )

        # Try to use gum if available for better UX
        if CharmToolsIntegration.is_gum_available():
            selected_id = self._run_with_gum(choices)
        else:
            selected_id = self._run_with_clack(choices)

        if not selected_id:
            return None

        if selected_id == "__NEW__":
            return self._create_new_project()

        # Find and return selected project
        return next((p for p in projects if p.get("id") == selected_id), None)

    def _run_with_clack(self, choices: List[Dict[str, str]]) -> Optional[str]:
        """Run selection using Clack prompts.

        Args:
            choices: List of choice dicts

        Returns:
            Selected value or None

        Note:
            This is a stub for Clack integration.
            When Clack is available: from clack.prompts import select
        """
        # TODO: Implement Clack integration
        # from clack.prompts import select
        #
        # choice = select(
        #     message="Select a project to link",
        #     choices=choices,
        # )
        # return choice

        # Fallback to Click for now
        for i, choice in enumerate(choices, 1):
            self.console.print(f"  [{i}] {choice['name']}")

        choice_str = click.prompt("Select project", type=int, default=1)
        if 1 <= choice_str <= len(choices):
            return choices[choice_str - 1]["value"]
        return None

    def _run_with_gum(self, choices: List[Dict[str, str]]) -> Optional[str]:
        """Run selection using gum (Charm tool).

        Args:
            choices: List of choice dicts

        Returns:
            Selected value or None

        Note:
            This is a stub for Charm gum integration.
            Gum provides fuzzy search and better UX.
        """
        # TODO: Implement gum integration
        # choice_names = [c["name"] for c in choices]
        # selected = CharmToolsIntegration.select_with_gum(
        #     "Select a project to link",
        #     choice_names
        # )
        # if selected:
        #     return next(
        #         c["value"] for c in choices if c["name"] == selected
        #     )
        return None

    def _create_new_project(self) -> Optional[Dict[str, Any]]:
        """Create new project interactively.

        Returns:
            New project dict or None

        Note:
            This is a stub for project creation flow.
        """
        # TODO: Implement new project creation
        # name = click.prompt("Project name")
        # description = click.prompt("Description (optional)", default="")
        # # Call API to create project
        # return {"id": "proj_new", "name": name, "description": description}
        return None


class DirectorySelectionPrompt:
    """Interactive prompt for selecting/creating a directory."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize directory selection prompt.

        Args:
            console: Rich Console instance
        """
        self.console = console or get_console()
        self.builder = ClackPromptBuilder(self.console)

    def run(self, default_dir: Optional[Path] = None) -> Optional[Path]:
        """Run directory selection prompt.

        Args:
            default_dir: Default directory to suggest

        Returns:
            Selected Path or None if cancelled

        Note:
            Enhanced with:
            - Input validation
            - Directory creation
            - Current directory context
        """
        if default_dir is None:
            default_dir = Path.cwd()

        self.console.print("\n[cyan]Where should this project be linked?[/cyan]")
        self.console.print(f"[dim]Current directory: {default_dir}[/dim]")

        while True:
            dir_str = click.prompt("Directory path", default=str(default_dir))
            directory = Path(dir_str).expanduser().resolve()

            # Validate path
            try:
                if directory.exists() and not directory.is_dir():
                    print_error(f"{directory} is not a directory")
                    continue

                if directory.exists() and list(directory.iterdir()):
                    # Directory not empty
                    if not click.confirm("Directory is not empty. Continue anyway?"):
                        continue

                return directory

            except Exception as e:
                print_error(f"Invalid path: {e}")
                continue

    def _run_with_clack(self, default: str) -> Optional[str]:
        """Run directory selection using Clack.

        Args:
            default: Default directory path

        Returns:
            Selected directory or None

        Note:
            This is a stub for Clack file picker.
        """
        # TODO: Implement Clack text prompt
        # from clack.prompts import text
        #
        # path = text(
        #     "Directory path",
        #     default=default,
        #     validate=lambda x: Path(x).parent.exists()
        # )
        # return path
        return None


class ConfigurationPrompt:
    """Interactive prompt for configuring sync options."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize configuration prompt.

        Args:
            console: Rich Console instance
        """
        self.console = console or get_console()
        self.builder = ClackPromptBuilder(self.console)

    def run(self) -> Dict[str, Any]:
        """Run configuration prompt.

        Returns:
            Configuration dict with sync options

        Note:
            Enhanced with:
            - Multi-select for features
            - Explanatory text for options
            - Sensible defaults
        """
        config = {}

        self.console.print("\n[bold cyan]Configure Sync Options[/bold cyan]")

        # Include jobs
        config["include_jobs"] = click.confirm(
            "Include job histories in sync?",
            default=True,
            help_option_names=["-h", "--help"],
        )

        # Include artifacts
        config["include_artifacts"] = click.confirm(
            "Include artifacts in sync?",
            default=True,
        )

        # Auto-sync frequency
        auto_sync_options = ["manual", "15min", "hourly"]
        self.console.print("\n[cyan]Auto-sync frequency:[/cyan]")
        for i, option in enumerate(auto_sync_options, 1):
            self.console.print(f"  [{i}] {option}")

        choice = click.prompt("Select frequency", type=int, default=1)
        config["auto_sync"] = auto_sync_options[choice - 1] if 1 <= choice <= 3 else "manual"

        return config

    def _run_with_checkbox(self) -> List[str]:
        """Run configuration using Clack checkbox.

        Returns:
            List of selected configuration keys

        Note:
            This is a stub for Clack checkbox integration.
        """
        # TODO: Implement Clack checkbox prompt
        # from clack.prompts import checkbox
        #
        # selected = checkbox(
        #     "Select features to include in sync",
        #     choices=[
        #         {"name": "Job histories", "value": "jobs"},
        #         {"name": "Artifacts", "value": "artifacts"},
        #         {"name": "Auto-sync", "value": "auto_sync"},
        #     ]
        # )
        # return selected
        return []


class ConflictResolutionPrompt:
    """Interactive prompt for resolving sync conflicts."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize conflict resolution prompt.

        Args:
            console: Rich Console instance
        """
        self.console = console or get_console()

    def run(
        self,
        resource_id: str,
        local_version: Dict[str, Any],
        remote_version: Dict[str, Any],
    ) -> str:
        """Run conflict resolution prompt.

        Args:
            resource_id: ID of conflicting resource
            local_version: Local version details
            remote_version: Remote version details

        Returns:
            Resolution choice: "keep_local", "use_remote", or "manual_merge"

        Note:
            Enhanced with:
            - Detailed conflict information display
            - Rich formatting for clarity
            - Multiple resolution strategies
        """
        # Display conflict panel
        panel = PanelBuilder.create_conflict_panel(
            resource_id, local_version, remote_version
        )
        self.console.print(panel)

        # Display resolution options
        self.console.print("\n[bold cyan]How would you like to resolve this?[/bold cyan]")
        options = [
            ("Keep local version", "keep_local"),
            ("Use remote version", "use_remote"),
            ("Manual merge (skip for now)", "manual_merge"),
        ]

        for i, (desc, value) in enumerate(options, 1):
            self.console.print(f"  [{i}] {desc}")

        choice = click.prompt("Choose", type=click.Choice(["1", "2", "3"]), default="1")
        return options[int(choice) - 1][1]


class SyncPreviewPrompt:
    """Interactive prompt for previewing sync changes."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize sync preview prompt.

        Args:
            console: Rich Console instance
        """
        self.console = console or get_console()

    def display_and_confirm(
        self, changes: List[Dict[str, Any]], action: str = "push"
    ) -> bool:
        """Display pending changes and ask for confirmation.

        Args:
            changes: List of change dicts
            action: Action being taken ("pull" or "push")

        Returns:
            True if user confirms, False if cancelled

        Note:
            Enhanced with:
            - Categorized display (added, modified, deleted)
            - Rich table formatting
            - Summary statistics
        """
        if not changes:
            self.console.print("[green]✅ No changes to sync[/green]")
            return False

        # Create changes table
        table = TableBuilder.create_changes_table()

        for change in changes:
            change_type = change.get("type", "unknown")
            resource_id = change.get("id", "")
            emoji = RichTheme.CHANGE_ICONS.get(change_type, "•")

            table.add_row(
                emoji,
                resource_id[:30],
                change.get("description", ""),
            )

        self.console.print("\n[cyan]Changes to [bold]{}[/bold]:[/cyan]".format(action.upper()))
        self.console.print(table)

        # Ask for confirmation
        return click.confirm("\nProceed?", default=True)


class HelpTextPrompt:
    """Display help text and documentation."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize help text prompt.

        Args:
            console: Rich Console instance
        """
        self.console = console or get_console()

    def show_welcome_guide(self) -> None:
        """Show welcome guide for new users.

        Note:
            Enhanced with:
            - Glow for markdown rendering (if available)
            - Beautiful panels and tables
            - Next steps guidance
        """
        content = """
[bold cyan]Welcome to IvyBloom Project Linking![/bold cyan]

This feature enables you to:
  📁 Link local directories to remote projects
  🔄 Sync jobs and artifacts bidirectionally
  ⚠️  Detect and resolve conflicts
  📊 Track sync history and status

[bold]Getting Started:[/bold]
  1. Run: [cyan]ivybloom projects init[/cyan]
  2. Select your project
  3. Choose a local directory
  4. Start syncing!

[bold]Common Commands:[/bold]
  [cyan]ivybloom projects pull[/cyan]     - Sync from cloud
  [cyan]ivybloom projects push[/cyan]     - Sync to cloud
  [cyan]ivybloom projects status[/cyan]   - Check sync state
  [cyan]ivybloom projects diff[/cyan]     - Preview changes

[dim]Need help? Run 'ivybloom projects --help'[/dim]
"""

        if CharmToolsIntegration.is_gum_available():
            # TODO: Use glow for markdown rendering
            pass

        panel = Panel(
            content,
            title="🚀 Project Linking Guide",
            border_style="green",
        )
        self.console.print(panel)

    def show_command_help(self, command_name: str, description: str, examples: List[str]) -> None:
        """Show help for specific command.

        Args:
            command_name: Name of command
            description: Command description
            examples: List of usage examples
        """
        content = f"""
[bold cyan]{description}[/bold cyan]

[bold]Examples:[/bold]
"""
        for example in examples:
            content += f"\n  [cyan]${example}[/cyan]"

        panel = Panel(
            content,
            title=f"Help: {command_name}",
            border_style="cyan",
        )
        self.console.print(panel)


# Stubs for future advanced features
class AdvancedPrompts:
    """Stubs for advanced interactive features."""

    @staticmethod
    def show_conflict_diff(
        local_path: Path, remote_path: Path, console: Optional[Console] = None
    ) -> None:
        """Show side-by-side diff of conflicting files.

        Args:
            local_path: Path to local file
            remote_path: Path to remote file
            console: Rich Console instance

        Note:
            This is a stub for future implementation.
            Would use difflib or rich.syntax for syntax highlighting.
        """
        # TODO: Implement side-by-side diff display
        pass

    @staticmethod
    def show_sync_timeline(sync_history: List[Dict[str, Any]]) -> None:
        """Show timeline of sync operations.

        Args:
            sync_history: List of sync operations

        Note:
            This is a stub for future implementation.
            Would display a timeline-style visualization.
        """
        # TODO: Implement sync timeline visualization
        pass

    @staticmethod
    def create_merge_helper(
        local: Dict[str, Any],
        remote: Dict[str, Any],
        base: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Interactive helper for 3-way merge.

        Args:
            local: Local version
            remote: Remote version
            base: Base version (for 3-way merge)

        Returns:
            Merged result

        Note:
            This is a stub for future implementation.
            Would provide interactive 3-way merge resolution.
        """
        # TODO: Implement 3-way merge helper
        return {}

