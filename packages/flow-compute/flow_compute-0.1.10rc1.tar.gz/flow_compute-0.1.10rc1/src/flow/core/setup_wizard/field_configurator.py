"""Field configuration logic for the setup wizard.

This module extracts and focuses the complex logic of configuring
individual fields, including dynamic choices and validation.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import click
from rich.console import Console

from flow.cli.commands._init_components.setup_components import select_from_options
from flow.cli.utils.theme_manager import theme_manager
from flow.core.setup_adapters import ConfigField, FieldType, ProviderSetupAdapter
from flow.core.setup_wizard.prompter import confirm_with_escape, prompt_text_with_escape
from flow.sdk.helpers.masking import mask_strict_last4


class FieldConfigResult(dict):
    """Typed result container for field configuration."""

    @property
    def value(self) -> Any:  # type: ignore[override]
        return self.get("value")

    @property
    def display_value(self) -> str | None:  # type: ignore[override]
        return self.get("display_value")


def configure_field(
    *,
    console: Console,
    adapter: ProviderSetupAdapter,
    field_name: str,
    context: dict[str, Any],
    current_config: dict[str, Any],
    coerce_fn: Callable[[Any, Any], Any],
    status_header: str | None = None,
    shown_empty_choice_hint: set[str] | None = None,
) -> FieldConfigResult | None:
    """Configure a single field and return a result or None if cancelled."""
    fields = {f.name: f for f in adapter.get_configuration_fields()}
    field = fields[field_name]
    display_name = field.display_name or field.name.replace("_", " ").title()

    # Render header for non-choice fields (TEXT, PASSWORD, BOOLEAN, LINK)
    # CHOICE fields use InteractiveSelector, which has its own full-screen TUI with
    # breadcrumbs and renders help_text via the extra_header_html parameter.
    if field.field_type != FieldType.CHOICE:
        console.clear()
        _render_field_header(
            console,
            display_name,
            help_text=field.help_text,
        )

    # Value collection
    if field.field_type == FieldType.LINK:
        res = _handle_link_field(
            console, adapter, field, field_name, context, current_config, display_name
        )
        return res
    elif field.field_type == FieldType.CHOICE:
        value = _handle_choice_field(
            console,
            adapter,
            field_name,
            field,
            context,
            current_config,
            status_header,
            shown_empty_choice_hint,
        )
        if value is _CANCELLED:
            return None
    elif field.field_type == FieldType.PASSWORD:
        value = prompt_text_with_escape(display_name, is_password=True)
        if value is None:
            return None
    elif field.field_type == FieldType.BOOLEAN:
        confirm = confirm_with_escape(f"\n{display_name}", default=bool(field.default))
        if confirm is None:
            return None
        value = confirm
    else:  # TEXT
        value = prompt_text_with_escape(display_name, is_password=False, default=field.default)
        if value is None:
            return None

    # Validate
    validation_result = adapter.validate_field(
        field_name, str(value), {**context, **current_config}
    )

    if validation_result.is_valid:
        processed = (
            validation_result.processed_value
            if hasattr(validation_result, "processed_value")
            else None
        )
        final_value = coerce_fn(field, processed if processed is not None else value)
        # Determine display value
        if validation_result.display_value:
            display_val = validation_result.display_value
        elif field.mask_display:
            display_val = mask_strict_last4(str(final_value))
        else:
            display_val = str(final_value)
        success_color = theme_manager.get_color("success")
        console.print(f"[{success_color}]✓[/{success_color}] {display_name}: {display_val}")
        return FieldConfigResult(value=final_value, display_value=display_val)
    else:
        console.print(f"[error]{validation_result.message}[/error]")
        try_again = confirm_with_escape("Try again?", default=True)
        if try_again:
            return configure_field(
                console=console,
                adapter=adapter,
                field_name=field_name,
                context=context,
                current_config=current_config,
                coerce_fn=coerce_fn,
                status_header=status_header,
                shown_empty_choice_hint=shown_empty_choice_hint,
            )
        return None


_CANCELLED = object()


def _render_field_header(
    console: Console,
    display_name: str,
    help_text: str | None = None,
) -> None:
    """Render the standard field configuration header."""
    brand_prefix = "Flow Setup"
    console.print(f"\n[bold]{brand_prefix} › Configuration › {display_name}[/bold]")
    console.print("─" * 50)
    console.print("[dim]ESC to go back • Ctrl+C to exit[/dim]")

    if help_text:
        console.print(f"[dim]{help_text}[/dim]")


def _handle_choice_field(
    console: Console,
    adapter: ProviderSetupAdapter,
    field_name: str,
    field: ConfigField,
    context: dict[str, Any],
    current_config: dict[str, Any],
    status_header: str | None,
    shown_empty_choice_hint: set[str] | None,
):
    # Dynamic choices
    if field.dynamic_choices:
        choice_strings = adapter.get_dynamic_choices(field_name, {**context, **current_config})
        if not choice_strings:
            hint = field.empty_choices_hint
            depends_on = field.depends_on or []
            missing = [d for d in depends_on if not (context.get(d) or current_config.get(d))]
            if (
                hint
                and shown_empty_choice_hint is not None
                and field_name not in shown_empty_choice_hint
            ):
                try:
                    from rich.panel import Panel as _Panel

                    warn_color = theme_manager.get_color("warning")
                    if missing:
                        missing_str = ", ".join(m.replace("_", " ").title() for m in missing)
                        text = f"{hint} (missing: {missing_str})."
                    else:
                        text = hint
                    console.print(_Panel(text, border_style=warn_color))
                except Exception:  # noqa: BLE001
                    if hint:
                        console.print(f"\n[warning]{hint}[/warning]")
                try:
                    shown_empty_choice_hint.add(field_name)  # type: ignore[union-attr]
                except Exception:  # noqa: BLE001
                    pass
            else:
                if (
                    shown_empty_choice_hint is not None
                    and field_name not in shown_empty_choice_hint
                ):
                    try:
                        from rich.panel import Panel as _Panel

                        warn_color = theme_manager.get_color("warning")
                        console.print(
                            _Panel(
                                "No options available. Skipping this field.",
                                border_style=warn_color,
                            )
                        )
                    except Exception:  # noqa: BLE001
                        console.print(
                            "\n[warning]No options available. Skipping this field.[/warning]"
                        )
                    try:
                        shown_empty_choice_hint.add(field_name)  # type: ignore[union-attr]
                    except Exception:  # noqa: BLE001
                        pass
            return _CANCELLED

        # Convert to dictionaries for intelligent selection
        is_ssh_key_selection = field_name == "default_ssh_key"
        choices = []
        for choice_str in choice_strings:
            if "|" in choice_str:
                parts = choice_str.split("|")
                if len(parts) >= 4 and is_ssh_key_selection:
                    id_part, name_part, created_at, fingerprint = (
                        parts[0],
                        parts[1],
                        parts[2],
                        parts[3],
                    )
                    created_display = ""
                    if created_at and created_at.strip():
                        try:
                            clean_date = created_at.replace("Z", "+00:00").split("T")[0]
                            if len(clean_date) >= 10:
                                created_display = clean_date[:10]
                            else:
                                from datetime import datetime as _dt

                                dt = _dt.fromisoformat(created_at.replace("Z", "+00:00"))
                                created_display = dt.strftime("%Y-%m-%d")
                        except Exception:  # noqa: BLE001
                            created_display = ""
                    choices.append(
                        {
                            "name": name_part,
                            "id": id_part,
                            "display": name_part,
                            "created_at": created_display,
                            "fingerprint": fingerprint,
                        }
                    )
                else:
                    id_part = parts[0]
                    name_part = parts[1] if len(parts) > 1 else parts[0]
                    choices.append({"name": name_part, "id": id_part, "display": name_part})
            elif "(" in choice_str and choice_str.endswith(")"):
                name_part = choice_str.split("(")[0].strip()
                id_part = choice_str.split("(")[-1].rstrip(")")
                choices.append({"name": name_part, "id": id_part, "display": choice_str})
            else:
                choices.append({"name": choice_str, "id": choice_str, "display": choice_str})

        # Build header
        header_parts: list[str] = []
        if status_header:
            header_parts.append(status_header)
        if field.help_text:
            header_parts.append(field.help_text)

        selected = select_from_options(
            console=console,
            options=choices,
            name_key="display",
            id_key="id",
            title=f"Select {field.display_name or field.name.replace('_', ' ').title()}",
            show_ssh_table=is_ssh_key_selection,
            extra_header_html=("\n\n".join(header_parts) if header_parts else None),
            breadcrumbs=[
                "Flow Setup",
                "Configuration",
                (field.display_name or field.name.replace("_", " ").title()),
            ],
            preferred_viewport_size=5,
        )
        if selected:
            return selected["id"]
        return _CANCELLED

    # Static choices
    choice_strings = field.choices or []
    choices = [{"name": choice, "id": choice} for choice in choice_strings]
    header_parts: list[str] = []
    if status_header:
        header_parts.append(status_header)
    if field.help_text:
        header_parts.append(field.help_text)
    selected = select_from_options(
        console=console,
        options=choices,
        name_key="name",
        id_key="id",
        title=f"Select {field.display_name or field.name.replace('_', ' ').title()}",
        extra_header_html=("\n\n".join(header_parts) if header_parts else None),
        breadcrumbs=[
            "Flow Setup",
            "Configuration",
            field.display_name or field.name.replace("_", " ").title(),
        ],
        preferred_viewport_size=5,
    )
    if selected:
        return selected["id"]
    return _CANCELLED


def _handle_link_field(
    console: Console,
    adapter: ProviderSetupAdapter,
    field: ConfigField,
    field_name: str,
    context: dict[str, Any],
    current_config: dict[str, Any],
    display_name: str,
) -> FieldConfigResult | None:
    """Generic link field handler.

    Opens a browser to an external URL for configuration, then re-validates
    the field after the user confirms completion.
    """
    # Extract options
    options = field.options or {}
    url_provider = options.get("url_provider")
    prompt_text = options.get("prompt_text", "Opening your browser to configure this field...")
    fallback_text = options.get(
        "fallback_text",
        "There was an issue generating the link to setup this field. Please try again or contact support if the problem persists.",
    )
    wait_text = options.get("wait_text", "Press [bold]Enter[/bold] to continue.")
    launch_browser = options.get("launch_browser", True)

    # Obtain setup URL from provider, passing merged context so it has access to dependencies
    setup_url = None
    if url_provider and callable(url_provider):
        merged_context = {**context, **current_config}
        setup_url = url_provider(merged_context)

    if setup_url:
        console.print(f"\n{prompt_text}")
        console.print(
            f"[dim]If your browser doesn't open, use this link:[/dim] [accent]{setup_url}[/accent]"
        )
        # Best-effort open in the default browser
        if launch_browser:
            click.launch(setup_url)
    else:
        console.print(f"\n{fallback_text}")

    # Prompt user to continue after configuring in browser
    console.print(f"\n{wait_text}")
    input()

    # Re-validate field
    validation = adapter.validate_field(field_name, "", {**context, **current_config})
    if validation.is_valid:
        success_color = theme_manager.get_color("success")
        console.print(f"[{success_color}]✓[/{success_color}] {display_name} configured")
        # Return a sentinel value; the field is informational
        return FieldConfigResult(
            value="configured", display_value=validation.display_value or "Configured"
        )

    console.print(f"[warning]{validation.message}[/warning]")
    try_again = confirm_with_escape("Try again?", default=True)
    if try_again:
        return _handle_link_field(
            console, adapter, field, field_name, context, current_config, display_name
        )
    return None
