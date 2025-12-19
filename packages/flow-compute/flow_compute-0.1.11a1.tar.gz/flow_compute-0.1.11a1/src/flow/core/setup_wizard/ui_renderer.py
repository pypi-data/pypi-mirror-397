"""UI rendering helpers for the setup wizard.

This module focuses on presentation (Rich Panels/Tables) and avoids any API calls.
"""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel

from flow.cli.ui.presentation.visual_constants import (
    SPACING,
    format_text,
    get_colors,
    get_panel_styles,
)
from flow.cli.utils.theme_manager import theme_manager
from flow.core.setup_adapters import ProviderSetupAdapter


class AnimatedDots:
    """Minimal animated dots implementation for progress messages."""

    def __init__(self) -> None:
        self._counter = 0
        self._dots = ["", ".", "..", "..."]

    def next(self) -> str:
        dots = self._dots[self._counter % len(self._dots)]
        self._counter += 1
        return dots


class UIRenderer:
    """Handles rendering of UI components for the setup wizard."""

    def __init__(self, console: Console):
        self.console = console
        self._shown_demo_panel: bool = False

    def render_welcome(self, adapter: ProviderSetupAdapter) -> None:
        self.console.clear()
        colors = get_colors()
        panel_styles = get_panel_styles()
        title, features = adapter.get_welcome_message()
        welcome_content = (
            f"{format_text('title', 'Flow Setup')}\n\n"
            f"{format_text('muted', f'Configure your environment for GPU workloads on {adapter.get_provider_name().upper()}')}\n\n"
            f"{format_text('body', 'This wizard will:')}\n"
        )
        for feature in features:
            welcome_content += f"  [{colors['primary']}]◦[/{colors['primary']}] {feature}\n"
        self.console.print(
            Panel(
                welcome_content.rstrip(),
                title=f"{format_text('title', '❊ Flow')}",
                title_align=panel_styles["main"]["title_align"],
                border_style=panel_styles["main"]["border_style"],
                padding=panel_styles["main"]["padding"],
                width=SPACING["panel_width"],
            )
        )
        self.console.print()
        try:
            if str(adapter.get_provider_name()).lower() == "mock":
                panel = self._create_demo_mode_panel()
                self.console.print(panel)
                self.console.print()
                self._shown_demo_panel = True
        except Exception:  # noqa: BLE001
            pass

    def render_completion(self, adapter: ProviderSetupAdapter) -> None:
        self.console.print("\n" + "─" * 50)
        billing_reminder = ""
        if hasattr(adapter, "billing_not_configured") and adapter.billing_not_configured:
            link_color = theme_manager.get_color("link")
            from flow.utils.links import WebLinks

            billing_link = WebLinks.billing_settings()
            billing_reminder = (
                "\n\n[warning]Remember to configure billing to use GPU resources:[/warning]\n"
                f"[{link_color}]{billing_link}[/{link_color}]"
            )
        panel_styles = get_panel_styles()
        self.console.print(
            Panel(
                f"{format_text('success', 'Setup complete.')}\n\n"
                f"{format_text('body', 'Flow is configured and ready for GPU workloads.')}\n"
                f"{format_text('muted', 'All credentials are securely stored and verified.')}"
                f"{billing_reminder}",
                title=f"{format_text('success', '✓ Success')}",
                title_align=panel_styles["success"]["title_align"],
                border_style=panel_styles["success"]["border_style"],
                padding=panel_styles["success"]["padding"],
                width=SPACING["panel_width"],
            )
        )

    def _create_demo_mode_panel(self) -> Panel:
        from flow.utils.links import WebLinks

        colors = get_colors()
        panel_styles = get_panel_styles()
        bullet = f"[{colors['primary']}]•[/{colors['primary']}]"
        body_lines = [
            f"{bullet} [bold]Sandbox only — no real resources are created.[/bold]",
            f"{bullet} Provider: [accent]mock[/accent]",
            f"{bullet} Switch to real: [accent]flow setup --provider mithril[/accent] or [accent]flow demo stop[/accent]",
            f"{bullet} SSH access: Your [bold]default SSH key[/bold] lets you securely log in",
            f"{bullet} Manage keys: [link]{WebLinks.ssh_keys()}[/link]",
        ]
        return Panel(
            "\n".join(body_lines),
            title=f"{format_text('subtitle', 'DEMO MODE')}",
            title_align=panel_styles["info"]["title_align"],
            border_style=theme_manager.get_color("warning"),
            padding=panel_styles["info"]["padding"],
            width=SPACING["panel_width"],
        )
