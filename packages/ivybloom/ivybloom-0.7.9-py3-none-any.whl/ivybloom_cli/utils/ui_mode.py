"""
UI Mode management for CLI startup and feature toggling.

Manages the choice between basic Click UI and enhanced Clack/Charm UI,
with full backward compatibility and easy reversion.
"""

from typing import Optional, Dict, Any
from enum import Enum
from pathlib import Path
import json

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .colors import get_console, print_success, print_warning, print_error


class UIMode(str, Enum):
    """Available UI modes for CLI."""

    BASIC = "basic"  # Traditional Click prompts (backward compatible)
    ENHANCED = "enhanced"  # Clack + Rich (prettier, interactive)
    CHARM = "charm"  # Charm tools + Clack (advanced, optional)
    AUTO = "auto"  # Auto-detect based on availability


class UIConfig:
    """Manage UI mode configuration."""

    CONFIG_FILE = Path.home() / ".config" / "ivybloom" / "ui_config.json"

    # Default configuration
    DEFAULT_CONFIG = {
        "mode": UIMode.AUTO,
        "show_welcome": True,
        "use_colors": True,
        "use_progress_bars": True,
        "use_animations": False,
        "theme": "dark",
    }

    def __init__(self):
        """Initialize UI config."""
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load config from file or return defaults.

        Returns:
            Configuration dictionary
        """
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE) as f:
                    return json.load(f)
            except Exception:
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def save_config(self) -> None:
        """Save config to file."""
        self.CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(self.CONFIG_FILE, "w") as f:
            json.dump(self.config, f, indent=2, default=str)

    def get_mode(self) -> UIMode:
        """Get current UI mode.

        Returns:
            UIMode enum value
        """
        mode = self.config.get("mode", UIMode.AUTO)
        if isinstance(mode, str):
            return UIMode(mode)
        return mode

    def set_mode(self, mode: UIMode) -> None:
        """Set UI mode.

        Args:
            mode: UIMode to set
        """
        self.config["mode"] = mode.value
        self.save_config()

    def get_theme(self) -> str:
        """Get current theme.

        Returns:
            Theme name
        """
        return self.config.get("theme", "dark")

    def set_theme(self, theme: str) -> None:
        """Set theme.

        Args:
            theme: Theme name
        """
        self.config["theme"] = theme
        self.save_config()

    def is_feature_enabled(self, feature: str) -> bool:
        """Check if feature is enabled.

        Args:
            feature: Feature name

        Returns:
            True if enabled
        """
        return self.config.get(f"use_{feature}", True)

    def set_feature(self, feature: str, enabled: bool) -> None:
        """Enable/disable feature.

        Args:
            feature: Feature name
            enabled: Whether to enable
        """
        self.config[f"use_{feature}"] = enabled
        self.save_config()


class UIStartupWizard:
    """Welcome wizard for first-time UI setup."""

    def __init__(self, console: Optional[Console] = None):
        """Initialize startup wizard.

        Args:
            console: Rich Console instance
        """
        self.console = console or get_console()
        self.config = UIConfig()

    def run(self) -> None:
        """Run startup wizard if needed."""
        if not self.config.config.get("show_welcome", True):
            return

        self._show_welcome()
        mode = self._choose_ui_mode()
        self.config.set_mode(mode)
        self.config.config["show_welcome"] = False
        self.config.save_config()

        self._show_next_steps(mode)

    def _show_welcome(self) -> None:
        """Show welcome screen."""
        welcome_text = """
[bold cyan]Welcome to IvyBloom CLI![/bold cyan]

We're about to ask you to choose a UI mode.
This choice affects how you interact with the CLI.

[bold]Don't worry![/bold]
You can always change this later with:
  [cyan]ivybloom config ui-mode[/cyan]

Let's get started!
"""
        panel = Panel(
            welcome_text,
            title="🚀 First Time Setup",
            border_style="green",
        )
        self.console.print(panel)

    def _choose_ui_mode(self) -> UIMode:
        """Let user choose UI mode.

        Returns:
            Selected UIMode
        """
        self.console.print("\n[bold cyan]Select UI Mode:[/bold cyan]\n")

        options = [
            {
                "name": "BASIC (Click)",
                "description": "Traditional Click prompts - simple, reliable, backward-compatible",
                "value": UIMode.BASIC,
            },
            {
                "name": "ENHANCED (Clack + Rich)",
                "description": "Beautiful interactive prompts - recommended for most users",
                "value": UIMode.ENHANCED,
            },
            {
                "name": "AUTO (Auto-detect)",
                "description": "Use ENHANCED if available, fallback to BASIC",
                "value": UIMode.AUTO,
            },
        ]

        for i, opt in enumerate(options, 1):
            self.console.print(f"[bold]{i}[/bold]. {opt['name']}")
            self.console.print(f"   {opt['description']}\n")

        choice = click.prompt("Select mode", type=click.Choice(["1", "2", "3"]), default="3")
        return options[int(choice) - 1]["value"]

    def _show_next_steps(self, mode: UIMode) -> None:
        """Show next steps based on chosen mode.

        Args:
            mode: Chosen UIMode
        """
        if mode == UIMode.BASIC:
            message = """
[cyan]You've chosen BASIC mode.[/cyan]

You'll see traditional Click prompts.
This mode is fully backward-compatible.

[dim]To see enhanced prompts later, run:[/dim]
  [cyan]ivybloom config ui-mode enhanced[/cyan]
"""
        elif mode == UIMode.ENHANCED:
            message = """
[cyan]You've chosen ENHANCED mode.[/cyan]

You'll see beautiful interactive prompts powered by Clack.
Make sure clack is installed:
  [cyan]pip install clack clack-prompts[/cyan]

[dim]To revert to basic mode later, run:[/dim]
  [cyan]ivybloom config ui-mode basic[/cyan]
"""
        else:  # AUTO
            message = """
[cyan]You've chosen AUTO mode.[/cyan]

The CLI will use ENHANCED mode if available,
otherwise it will fall back to BASIC mode.

This is the recommended mode for most users.

[dim]To change mode later, run:[/dim]
  [cyan]ivybloom config ui-mode <basic|enhanced|charm>[/cyan]
"""

        panel = Panel(message, title="✅ Mode Selected", border_style="green")
        self.console.print(panel)


class UIModeDetector:
    """Detect UI mode capabilities and select appropriate implementation."""

    @staticmethod
    def is_clack_available() -> bool:
        """Check if Clack library is installed.

        Returns:
            True if clack is available
        """
        try:
            import clack  # noqa: F401
            return True
        except ImportError:
            return False

    @staticmethod
    def is_gum_available() -> bool:
        """Check if gum CLI tool is installed.

        Returns:
            True if gum is available
        """
        import subprocess

        try:
            subprocess.run(["gum", "--version"], capture_output=True, timeout=1)
            return True
        except Exception:
            return False

    @staticmethod
    def get_effective_mode(requested_mode: UIMode) -> UIMode:
        """Get effective UI mode based on availability.

        Args:
            requested_mode: Requested UIMode

        Returns:
            Effective UIMode
        """
        if requested_mode == UIMode.AUTO:
            if UIModeDetector.is_clack_available():
                return UIMode.ENHANCED
            return UIMode.BASIC

        if requested_mode == UIMode.CHARM:
            if not UIModeDetector.is_clack_available():
                # Fallback to enhanced if charm requested but clack unavailable
                return UIMode.ENHANCED
            return UIMode.CHARM

        if requested_mode == UIMode.ENHANCED:
            if not UIModeDetector.is_clack_available():
                return UIMode.BASIC
            return UIMode.ENHANCED

        return UIMode.BASIC

    @staticmethod
    def show_ui_capabilities() -> None:
        """Display current UI capabilities.

        Shows what UI modes are available based on installed packages.
        """
        console = get_console()

        console.print("\n[bold cyan]UI Capabilities:[/bold cyan]\n")

        capabilities = [
            ("BASIC (Click)", True),  # Always available
            ("ENHANCED (Clack)", UIModeDetector.is_clack_available()),
            ("CHARM Tools (gum)", UIModeDetector.is_gum_available()),
        ]

        for capability, available in capabilities:
            status = "[green]✓ Available[/green]" if available else "[dim]✗ Not available[/dim]"
            console.print(f"  {capability}: {status}")

        console.print()

        # Show installation hints
        if not UIModeDetector.is_clack_available():
            print_warning("Clack not installed. Install it for enhanced prompts:")
            console.print("  [cyan]pip install clack clack-prompts[/cyan]\n")

        if not UIModeDetector.is_gum_available():
            print_warning("Gum not installed. Install it for advanced selection:")
            console.print("  [cyan]brew install charmbracelet/tap/gum  # macOS[/cyan]")
            console.print("  [cyan]sudo apt install gum  # Ubuntu/Debian[/cyan]\n")


class UIContextManager:
    """Manages UI context for commands.

    Provides consistent UI behavior throughout the application.
    """

    def __init__(self):
        """Initialize UI context manager."""
        self.config = UIConfig()
        self.mode = UIModeDetector.get_effective_mode(self.config.get_mode())
        self.console = get_console()

    def get_mode(self) -> UIMode:
        """Get current UI mode.

        Returns:
            Current UIMode
        """
        return self.mode

    def use_clack(self) -> bool:
        """Should we use Clack prompts?

        Returns:
            True if should use Clack
        """
        return self.mode in [UIMode.ENHANCED, UIMode.CHARM]

    def use_charm_tools(self) -> bool:
        """Should we use Charm tools?

        Returns:
            True if should use Charm tools
        """
        return self.mode == UIMode.CHARM

    def get_prompt_builder(self):
        """Get appropriate prompt builder for current mode.

        Returns:
            Prompt builder instance (Clack or Click)
        """
        if self.use_clack():
            from .interactive_prompts import ProjectSelectionPrompt
            return ProjectSelectionPrompt(self.console)
        else:
            # Basic Click-based prompts
            return self._get_basic_prompts()

    def _get_basic_prompts(self):
        """Get basic Click-only prompts.

        Returns:
            Basic prompt provider
        """
        # TODO: Create BasicPrompts class for Click-only operation
        return None

    def show_mode_info(self) -> None:
        """Display current UI mode information."""
        mode_name = self.mode.value.upper()
        console_output = f"[cyan]UI Mode: {mode_name}[/cyan]"

        if self.mode == UIMode.AUTO:
            effective = UIModeDetector.get_effective_mode(self.mode)
            console_output += f" [dim](using {effective.value})[/dim]"

        self.console.print(console_output)

    @staticmethod
    def show_reversion_help() -> None:
        """Show help for reverting to basic mode."""
        console = get_console()
        console.print("\n[yellow]To revert to BASIC mode, run:[/yellow]")
        console.print("  [cyan]ivybloom config ui-mode basic[/cyan]")
        console.print("  [cyan]ivybloom config ui-mode --reset[/cyan]\n")

