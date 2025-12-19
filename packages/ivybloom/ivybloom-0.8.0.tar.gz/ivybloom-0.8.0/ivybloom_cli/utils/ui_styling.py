"""
UI/UX styling and theming utilities for IvyBloom CLI project linking.

Integrates Click, Rich, Clack, and optional Charm tools for beautiful,
accessible terminal interfaces.
"""

from typing import List, Dict, Any, Optional, Callable
from enum import Enum
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style
from rich.progress import Progress, BarColumn, SpinnerColumn, TextColumn
from rich.align import Align
from rich.columns import Columns


class Theme(str, Enum):
    """Available color themes for CLI output."""

    LIGHT = "light"
    DARK = "dark"
    OCEAN = "ocean"
    FOREST = "forest"
    CUSTOM = "custom"


class ClickColors:
    """Click-compatible ANSI color utilities."""

    # Standard colors for Click commands
    SUCCESS = "green"
    WARNING = "yellow"
    ERROR = "red"
    INFO = "cyan"
    DEBUG = "blue"
    HIGHLIGHT = "magenta"

    # Rich style equivalents for consistency
    @staticmethod
    def get_style(color_name: str) -> str:
        """Get Rich style string from color name."""
        return f"bold {color_name}" if color_name != "magenta" else "bold magenta"


class RichTheme:
    """Rich console theming for project linking commands."""

    # Color palette
    PRIMARY = "cyan"
    SUCCESS = "green"
    WARNING = "yellow"
    ERROR = "red"
    INFO = "blue"
    ACCENT = "magenta"

    # Status indicators
    STATUS_ICONS = {
        "synced": "✅",
        "syncing": "⏳",
        "dirty": "🔄",
        "error": "❌",
        "new": "✨",
        "conflict": "⚠️ ",
    }

    # Change type icons
    CHANGE_ICONS = {
        "added": "✨",
        "modified": "🔄",
        "deleted": "🗑️ ",
        "conflict": "⚠️ ",
    }

    @staticmethod
    def get_status_display(status: str, text: str = "") -> str:
        """Get Rich markup for status display."""
        icon = RichTheme.STATUS_ICONS.get(status, "•")
        text_content = text or status.upper()

        status_styles = {
            "synced": f"[bold green]{icon} {text_content}[/bold green]",
            "syncing": f"[bold blue]{icon} {text_content}[/bold blue]",
            "dirty": f"[bold yellow]{icon} {text_content}[/bold yellow]",
            "error": f"[bold red]{icon} {text_content}[/bold red]",
            "new": f"[bold cyan]{icon} {text_content}[/bold cyan]",
            "conflict": f"[bold magenta]{icon} {text_content}[/bold magenta]",
        }

        return status_styles.get(status, f"[cyan]{icon} {text_content}[/cyan]")

    @staticmethod
    def get_change_display(change_type: str, resource_id: str) -> str:
        """Get Rich markup for change display."""
        icon = RichTheme.CHANGE_ICONS.get(change_type, "•")
        return f"  {icon} [cyan]{resource_id}[/cyan]"


class ClackPromptBuilder:
    """Builder for creating consistent Clack prompts with styling."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize prompt builder.

        Args:
            console: Rich Console instance for styling
        """
        self.console = console or Console()

    def build_select_prompt(
        self,
        title: str,
        choices: List[Dict[str, str]],
        description: Optional[str] = None,
        hint: Optional[str] = None,
    ) -> str:
        """Build and run a select prompt with Clack.

        Args:
            title: Prompt title
            choices: List of choice dicts with 'name' and 'value' keys
            description: Optional description text
            hint: Optional hint text (e.g., "use arrow keys")

        Returns:
            Selected value from choices

        Raises:
            ImportError: If Clack not installed
        """
        try:
            from clack.prompts import select
        except ImportError:
            raise ImportError(
                "Clack not installed. Install with: pip install clack clack-prompts"
            )

        # Format choices for Clack
        clack_choices = [{"label": c["name"], "value": c["value"]} for c in choices]

        result = select(message=title, choices=clack_choices)

        return result

    def build_confirm_prompt(
        self,
        title: str,
        default: bool = True,
        description: Optional[str] = None,
    ) -> bool:
        """Build and run a confirm prompt with Clack.

        Args:
            title: Prompt title
            default: Default value (Y/N)
            description: Optional description

        Returns:
            User's yes/no choice

        Raises:
            ImportError: If Clack not installed
        """
        try:
            from clack.prompts import confirm
        except ImportError:
            raise ImportError(
                "Clack not installed. Install with: pip install clack clack-prompts"
            )

        result = confirm(message=title, default=default)
        return result

    def build_text_prompt(
        self,
        title: str,
        default: Optional[str] = None,
        placeholder: Optional[str] = None,
        validate: Optional[Callable[[str], bool]] = None,
    ) -> Dict[str, Any]:
        """Build a text input prompt with styling.

        Args:
            title: Prompt title
            default: Default value
            placeholder: Placeholder text
            validate: Optional validation function

        Returns:
            Dict with prompt configuration
        """
        prompt_config = {
            "type": "text",
            "name": "input",
            "message": f"[bold cyan]{title}[/bold cyan]",
        }

        if default:
            prompt_config["default"] = default

        if placeholder:
            prompt_config["placeholder"] = placeholder

        if validate:
            prompt_config["validate"] = validate

        return prompt_config

    def build_checkbox_prompt(
        self,
        title: str,
        choices: List[Dict[str, str]],
        min_selected: int = 1,
    ) -> Dict[str, Any]:
        """Build a checkbox (multi-select) prompt with styling.

        Args:
            title: Prompt title
            choices: List of choice dicts
            min_selected: Minimum selections required

        Returns:
            Dict with prompt configuration
        """
        return {
            "type": "checkbox",
            "name": "selected",
            "message": f"[bold cyan]{title}[/bold cyan]",
            "choices": choices,
            "min_selected": min_selected,
        }


class ProgressIndicator:
    """Rich progress bar utilities for sync operations."""

    @staticmethod
    def create_sync_progress() -> Progress:
        """Create a progress bar for sync operations.

        Returns:
            Configured Rich Progress instance
        """
        return Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        )

    @staticmethod
    def create_download_progress() -> Progress:
        """Create a progress bar for file downloads.

        Returns:
            Configured Rich Progress instance
        """
        from rich.progress import DownloadColumn, TransferSpeedColumn, TimeRemainingColumn

        return Progress(
            TextColumn("[progress.description]{task.description}"),
            DownloadColumn(),
            BarColumn(),
            TransferSpeedColumn(),
            TimeRemainingColumn(),
        )


class TableBuilder:
    """Builder for creating consistent Rich tables."""

    @staticmethod
    def create_projects_table() -> Table:
        """Create table for project list display.

        Returns:
            Configured Rich Table
        """
        table = Table(title="📁 Your Projects", show_header=True, header_style="bold cyan")
        table.add_column("Project ID", style="cyan", width=15)
        table.add_column("Name", style="bold")
        table.add_column("Description", style="dim")
        table.add_column("Jobs", style="green", justify="right")
        table.add_column("Last Activity", style="dim")
        return table

    @staticmethod
    def create_sync_status_table() -> Table:
        """Create table for sync status display.

        Returns:
            Configured Rich Table
        """
        table = Table(title="Sync Status", show_header=True, header_style="bold cyan")
        table.add_column("Item", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Time", style="dim")
        return table

    @staticmethod
    def create_changes_table() -> Table:
        """Create table for displaying changes.

        Returns:
            Configured Rich Table
        """
        table = Table(title="Changes", show_header=True, header_style="bold cyan")
        table.add_column("Type", style="yellow", width=10)
        table.add_column("Resource", style="cyan")
        table.add_column("Details", style="dim")
        return table


class PanelBuilder:
    """Builder for creating consistent Rich panels."""

    @staticmethod
    def create_info_panel(title: str, content: str) -> Panel:
        """Create an info panel.

        Args:
            title: Panel title
            content: Panel content (can include Rich markup)

        Returns:
            Configured Rich Panel
        """
        return Panel(
            content,
            title=title,
            border_style="blue",
            expand=False,
        )

    @staticmethod
    def create_success_panel(title: str, content: str) -> Panel:
        """Create a success panel.

        Args:
            title: Panel title
            content: Panel content

        Returns:
            Configured Rich Panel
        """
        return Panel(
            f"[green]{content}[/green]",
            title=f"✅ {title}",
            border_style="green",
            expand=False,
        )

    @staticmethod
    def create_error_panel(title: str, content: str) -> Panel:
        """Create an error panel.

        Args:
            title: Panel title
            content: Panel content

        Returns:
            Configured Rich Panel
        """
        return Panel(
            f"[red]{content}[/red]",
            title=f"❌ {title}",
            border_style="red",
            expand=False,
        )

    @staticmethod
    def create_conflict_panel(
        resource_id: str,
        local_version: Dict[str, Any],
        remote_version: Dict[str, Any],
    ) -> Panel:
        """Create a conflict resolution panel.

        Args:
            resource_id: ID of conflicting resource
            local_version: Local version details
            remote_version: Remote version details

        Returns:
            Configured Rich Panel
        """
        content = f"""
[bold cyan]Resource:[/bold cyan] {resource_id}

[bold yellow]Local Version:[/bold yellow]
  Modified: {local_version.get('modified', 'N/A')}
  Size: {local_version.get('size', 'N/A')}

[bold cyan]Remote Version:[/bold cyan]
  Modified: {remote_version.get('modified', 'N/A')}
  Size: {remote_version.get('size', 'N/A')}
"""
        return Panel(
            content,
            title="⚠️  Conflict Detected",
            border_style="magenta",
        )


# Stubs for future Charm tools integration
class CharmToolsIntegration:
    """Integration with Charm tools (gum, glow, lipgloss).

    This is a stub for future implementation when Charm tools are installed.
    Charm tools are Go-based CLI tools that complement Python CLI libraries.
    """

    @staticmethod
    def is_gum_available() -> bool:
        """Check if gum (Charm tool) is installed.

        Returns:
            True if gum is available, False otherwise
        """
        # TODO: Implement gum availability check
        return False

    @staticmethod
    def select_with_gum(
        title: str,
        choices: List[str],
        multi_select: bool = False,
    ) -> Optional[str]:
        """Use gum for advanced project selection with filtering.

        Args:
            title: Selection prompt title
            choices: List of choices
            multi_select: Whether to allow multiple selections

        Returns:
            Selected choice or None if cancelled

        Note:
            This is a stub. Requires gum CLI to be installed.
            Gum provides fuzzy search, filtering, and better UX than Clack alone.
        """
        # TODO: Implement gum subprocess call
        # subprocess.run(['gum', 'choose'] + choices)
        return None

    @staticmethod
    def display_markdown_with_glow(markdown_content: str) -> None:
        """Display markdown content using glow (Charm tool).

        Args:
            markdown_content: Markdown text to display

        Note:
            This is a stub. Requires glow CLI to be installed.
            Glow provides beautiful markdown rendering in terminal.
        """
        # TODO: Implement glow subprocess call
        # subprocess.run(['glow'], input=markdown_content, text=True)
        pass

    @staticmethod
    def style_with_lipgloss(text: str, style: str) -> str:
        """Apply lipgloss styling to text (Charm tool).

        Args:
            text: Text to style
            style: Style specification

        Returns:
            Styled text

        Note:
            This is a stub. Lipgloss is more powerful than Rich for advanced styling.
            Would require Python wrapper or subprocess calls.
        """
        # TODO: Implement lipgloss styling
        return text


# Stubs for future TUI integration
class TUIIntegration:
    """Integration with Textual for TUI dashboard.

    This is a stub for future implementation of interactive TUI components.
    """

    @staticmethod
    def create_sync_dashboard() -> None:
        """Create an interactive TUI dashboard for sync operations.

        Note:
            This is a stub for future implementation.
            Would use Textual framework for real-time sync monitoring.
        """
        # TODO: Implement Textual-based TUI dashboard
        # from textual.app import ComposeResult
        # from textual.containers import Container
        # from textual.widgets import Static
        pass

    @staticmethod
    def show_live_job_updates(project_id: str) -> None:
        """Display live job updates in TUI.

        Args:
            project_id: Project to monitor

        Note:
            This is a stub for future implementation.
        """
        # TODO: Implement live job display in TUI
        pass


# Color/theme configuration
class StyleConfig:
    """Configuration for CLI styling and themes."""

    # Default theme
    CURRENT_THEME = Theme.DARK

    # Theme-specific color palettes
    PALETTES = {
        Theme.DARK: {
            "primary": "cyan",
            "success": "green",
            "warning": "yellow",
            "error": "red",
            "accent": "magenta",
        },
        Theme.LIGHT: {
            "primary": "blue",
            "success": "green",
            "warning": "orange1",
            "error": "red",
            "accent": "purple",
        },
        Theme.OCEAN: {
            "primary": "deep_sky_blue1",
            "success": "sea_green1",
            "warning": "gold1",
            "error": "red",
            "accent": "light_sea_green",
        },
        Theme.FOREST: {
            "primary": "green",
            "success": "light_green",
            "warning": "yellow",
            "error": "red",
            "accent": "lime",
        },
    }

    @staticmethod
    def get_palette(theme: Theme = Theme.DARK) -> Dict[str, str]:
        """Get color palette for theme.

        Args:
            theme: Theme to get palette for

        Returns:
            Dictionary of color names
        """
        return StyleConfig.PALETTES.get(theme, StyleConfig.PALETTES[Theme.DARK])

    @staticmethod
    def apply_theme(theme: Theme) -> None:
        """Apply theme globally.

        Args:
            theme: Theme to apply
        """
        StyleConfig.CURRENT_THEME = theme

