"""Orchestration for the Generic Setup Wizard.

This class coordinates rendering, input, validation, and field configuration
using the modular helpers in this package.
"""

from __future__ import annotations

import os
import signal
import sys
from typing import Any

import click
from rich.console import Console

from flow.cli.ui.components.renderer import style as _pt_style
from flow.cli.utils.theme_manager import theme_manager
from flow.core.setup_adapters import FieldType, ProviderSetupAdapter
from flow.core.setup_wizard.field_configurator import configure_field
from flow.core.setup_wizard.menu_selector import interactive_menu_select
from flow.core.setup_wizard.ui_renderer import UIRenderer


class GenericSetupWizard:
    """Generic setup wizard that works with any provider adapter."""

    @staticmethod
    def _coerce_to_type(field, value):
        if field.field_type == FieldType.BOOLEAN:
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.lower() in ("true", "yes", "1", "on")
            return bool(value)
        return value

    def __init__(self, console: Console, adapter: ProviderSetupAdapter):
        self.console = console
        self.adapter = adapter
        self.ui = UIRenderer(console)
        self.config: dict[str, Any] = {}
        self._config_dirty = False
        # Cache validation results to avoid re-validating unchanged values during menu re-renders
        self._validation_cache: dict[tuple[str, str], Any] = {}

    def run(self) -> bool:
        """Run the setup wizard flow."""

        # Keyboard interrupt handler
        def keyboard_interrupt_handler(signum, frame):
            self.console.print("\n\n[warning]Setup cancelled[/warning]")
            try:
                os.system("stty sane 2>/dev/null || true")
            except Exception:  # noqa: BLE001
                pass
            sys.exit(0)

        old_handler = signal.signal(signal.SIGINT, keyboard_interrupt_handler)
        try:
            self.ui.render_welcome(self.adapter)

            # Load existing configuration into self.config
            self.config = self.adapter.detect_existing_config()

            # Render the status panel only once. If configuration is incomplete,
            # the configuration loop will render (and re-render) the status as
            # needed. For a fully-configured environment, show the status here
            # before presenting the completion actions. This avoids duplicate
            # status/SSH panels in typical interactive flows.
            if self._is_fully_configured():
                proceed = self._handle_fully_configured()
                if not proceed:
                    return False
                try:
                    if self._config_dirty and not self.adapter.save_configuration(self.config):
                        self.console.print("\n[error]Failed to save configuration[/error]")
                        return False
                    return True
                except Exception:  # noqa: BLE001
                    return True
            else:
                # Let the configuration loop own status rendering to prevent
                # duplicating the status/SSH panels.
                if not self._configure_missing_items():
                    return False

                if not self.adapter.save_configuration(self.config):
                    self.console.print("\n[error]Failed to save configuration[/error]")
                    return False
                if self._verify_configuration(self.config):
                    self.ui.render_completion(self.adapter)
                    return True
                else:
                    self.console.print(
                        "\n[warning]Setup completed but verification failed. Check your settings.[/warning]"
                    )
                    return False
        finally:
            signal.signal(signal.SIGINT, old_handler)

    def _is_fully_configured(self) -> bool:
        fields = self.adapter.get_configuration_fields()
        required_fields = [f for f in fields if f.required]
        return all(self._is_field_effectively_configured(f) for f in required_fields)

    def _is_field_effectively_configured(self, field) -> bool:
        value = self.config.get(field.name)
        name = field.name
        if field.field_type == FieldType.LINK:
            # Check dependencies first
            if field.depends_on:
                for dep in field.depends_on:
                    dep_value = self.config.get(dep)
                    if not dep_value:
                        return False
            # LINK fields are validated via adapter even if there's no stored value
            validation_result = self.adapter.validate_field(name, str(value or ""), self.config)
            return validation_result.is_valid

        if not value:
            return False

        if name == "api_key":
            v = str(value)
            if v.startswith("YOUR_"):
                return False
            return v.startswith("fkey_") and len(v) >= 20
        if name == "project":
            v = str(value).strip()
            if v.startswith("YOUR_"):
                return False
            return len(v) > 0
        if name == "default_ssh_key":
            v = str(value).strip()
            return v == "_auto_" or v.startswith("sshkey_")
        return True

    def _handle_fully_configured(self) -> bool:
        from flow.cli.ui.presentation.visual_constants import get_status_display
        from flow.cli.utils.theme_manager import theme_manager

        self.console.print(
            f"\n{get_status_display('configured', 'All required components are configured', icon_style='check')}"
        )
        menu_options = [
            ("verify", "Verify and finish (recommended)", ""),
            ("reconfig", "Change configuration", ""),
            ("exit", "Exit now (skip verification)", ""),
        ]
        self.console.print()
        brand_prefix = "Flow Setup"
        action = interactive_menu_select(
            options=menu_options,
            title="What would you like to do?",
            default_index=0,
            extra_header_html=None,
            breadcrumbs=[brand_prefix, "Complete"],
        )
        # If selection couldn't be obtained (non-interactive/EOF), default to verify
        if action is None:
            action = "verify"
        if action == "verify":
            success, error = self.adapter.verify_configuration(self.config)
            if success:
                success_color = theme_manager.get_color("success")
                self.console.print(
                    f"\n[{success_color}]✓ Configuration verified successfully![/{success_color}]"
                )
                return True
            else:
                self.console.print(f"\n[warning]Verification failed: {error}[/warning]")
                return self._configure_missing_items()
        elif action == "reconfig":
            return self._configure_missing_items()
        elif action == "exit":
            missing = [
                f.name
                for f in self.adapter.get_configuration_fields()
                if f.required and not self._is_field_effectively_configured(f)
            ]
            if missing:
                self.console.print(
                    f"\n[warning]Warning: Required items not configured: {', '.join(missing)}[/warning]"
                )
                from flow.core.setup_wizard.prompter import confirm_with_escape

                exit_anyway = confirm_with_escape("Exit anyway?", default=False)
                if not exit_anyway:
                    return False
            self.console.print("\n[dim]Exiting without verification.[/dim]")
            return True
        return True

    def _configure_missing_items(self) -> bool:
        fields = self.adapter.get_configuration_fields()
        # Always add a spacer before the selector so returning to the menu
        # after a change doesn't butt up against the panels.
        self._shown_empty_choice_hint: set[str] = set()
        while True:
            self.console.clear()

            menu_options = []
            choice_map: dict[str, str] = {}
            choice_num = 1
            for field in fields:
                existing_value = self.config.get(field.name)
                field_title = field.display_name or field.name.replace("_", " ").title()

                # Auto-configure CHOICE fields if only one option (except SSH keys since we always want that selection to be explicit)
                if (
                    field.field_type == FieldType.CHOICE
                    and field.dynamic_choices
                    and not existing_value
                    and field.name != "default_ssh_key"
                ):
                    # Check if dependencies are satisfied first
                    depends_on = field.depends_on or []
                    missing_deps = [d for d in depends_on if not self.config.get(d)]
                    if not missing_deps:
                        # Only auto-configure if all dependencies are satisfied
                        choices = self.adapter.get_dynamic_choices(field.name, self.config)
                        if len(choices) == 1:
                            # Auto-configure with the single available choice
                            single_choice = choices[0]
                            # Extract ID from formatted choice string (format: "id|name|..." or just "id")
                            choice_id = (
                                single_choice.split("|")[0]
                                if "|" in single_choice
                                else single_choice
                            )
                            validation_result = self.adapter.validate_field(
                                field.name, choice_id, self.config
                            )
                            if validation_result.is_valid:
                                coerced_value = self._coerce_to_type(field, choice_id)
                                self.config[field.name] = coerced_value
                                self._config_dirty = True
                                # Update existing_value so it shows as configured in menu
                                existing_value = coerced_value

                # Get current field status for inline display
                status_text = ""
                dim_color = theme_manager.get_color("muted")
                # For billing, validate even when there is no stored value so status reflects reality
                if field.name == "billing" and not existing_value:
                    validation_result = self._get_validation_result("billing", "", self.config)
                    if validation_result.is_valid and validation_result.display_value:
                        status_text = " " + _pt_style(
                            f"[{validation_result.display_value}]",
                            fg=theme_manager.get_color("success"),
                        )
                    else:
                        status_text = " " + _pt_style("[Not configured]", fg=dim_color)
                elif existing_value:
                    # Get current validation result to display status
                    validation_result = self._get_validation_result(
                        field.name, str(existing_value), self.config
                    )
                    if validation_result.is_valid and validation_result.display_value:
                        status_text = " " + _pt_style(
                            f"[{validation_result.display_value}]",
                            fg=theme_manager.get_color("success"),
                        )
                    elif not validation_result.is_valid:
                        status_text = " " + _pt_style(
                            "[Invalid]", fg=theme_manager.get_color("error")
                        )
                else:
                    status_text = " " + _pt_style("[Not configured]", fg=dim_color)

                if existing_value:
                    display_text = f"[{choice_num}] Configure {field_title}{status_text}"
                    description = ""
                else:
                    display_text = f"[{choice_num}] Configure {field_title}{status_text}"
                    depends_on = field.depends_on or []
                    missing = [d for d in depends_on if not self.config.get(d)]
                    if missing:
                        # Look up display names for missing dependencies
                        fields_by_name = {f.name: f for f in fields}
                        missing_display_names = []
                        for m in missing:
                            dep_field = fields_by_name.get(m)
                            if dep_field and dep_field.display_name:
                                missing_display_names.append(dep_field.display_name)
                            else:
                                missing_display_names.append(m.replace("_", " ").title())
                        description = f"Requires: {', '.join(missing_display_names)}"
                        # If dependencies are missing, "Requires: ..." implies not configured.
                        # Only show "[Not configured]" when there is no dependency description.
                        dim_color = theme_manager.get_color("muted")
                        plain_status = _pt_style("[Not configured]", fg=dim_color)
                        combined_desc = description if description else plain_status
                        menu_options.append(
                            (
                                f"disabled_{choice_num}",
                                f"[{choice_num}] Configure {field_title}",
                                combined_desc,
                            )
                        )
                        choice_num += 1
                        continue
                    else:
                        description = ""
                menu_options.append((str(choice_num), display_text, description))
                choice_map[str(choice_num)] = field.name
                choice_num += 1

            menu_options.append(("done", f"[{choice_num}] Done (save and exit)", ""))
            # Print a spacer line before the menu every time to keep
            # consistent padding between status panels and the selector.
            self.console.print()

            try:
                default_index = 0
                first_missing_menu_index = None
                for _idx, field in enumerate(fields):
                    if not self._is_field_effectively_configured(field):
                        chosen_key = None
                        for k, v in choice_map.items():
                            if v == field.name:
                                chosen_key = k
                                break
                        if chosen_key is not None:
                            for mi, (val, _t, _d) in enumerate(menu_options):
                                if val == chosen_key:
                                    first_missing_menu_index = mi
                                    break
                        break
                if first_missing_menu_index is not None:
                    default_index = first_missing_menu_index
                else:
                    default_index = len(menu_options) - 1

                # Ensure default index doesn't land on a disabled item
                while default_index < len(menu_options) and menu_options[default_index][
                    0
                ].startswith("disabled_"):
                    default_index += 1
                # If all items below are disabled, try going up
                if default_index >= len(menu_options):
                    default_index = 0
                    while default_index < len(menu_options) and menu_options[default_index][
                        0
                    ].startswith("disabled_"):
                        default_index += 1
            except Exception:  # noqa: BLE001
                default_index = 0

            brand_prefix = "Flow Setup"
            choice = interactive_menu_select(
                options=menu_options,
                title="Configuration Menu",
                default_index=default_index,
                extra_header_html=None,
                breadcrumbs=[brand_prefix, "Configuration"],
            )

            # If selection couldn't be obtained (non-interactive/EOF), fall back to Done
            if choice is None:
                choice = "done"
            if choice == "done":
                required_fields = [f for f in fields if f.required]
                # Check which required fields are not configured
                missing = [
                    (f.display_name or f.name.replace("_", " ").title())
                    for f in required_fields
                    if not self._is_field_effectively_configured(f)
                ]
                if missing:
                    self.console.print(
                        f"\n[warning]Warning: Required items not configured: {', '.join(missing)}[/warning]"
                    )
                    exit_anyway = click.confirm("Exit anyway?", default=False)
                    if not exit_anyway:
                        continue
                return True

            field_name = choice_map.get(choice)
            if field_name:
                result = configure_field(
                    console=self.console,
                    adapter=self.adapter,
                    field_name=field_name,
                    context=self.config,
                    current_config=self.config,
                    coerce_fn=self._coerce_to_type,
                    status_header=None,
                    shown_empty_choice_hint=self._shown_empty_choice_hint,
                )
                if result:
                    self.config[field_name] = result.value
                    self._config_dirty = True

                    # Clear dependent fields when a field they depend on changes
                    # Derive fields to clear from the depends_on relationship in ConfigFields
                    fields_to_clear = [
                        f.name for f in fields if f.depends_on and field_name in f.depends_on
                    ]
                    for field_to_clear in fields_to_clear:
                        self.config.pop(field_to_clear, None)
                    # Invalidate cached validation results for the changed field and its dependents
                    self._invalidate_validation_cache_for_fields([field_name] + fields_to_clear)

    def _verify_configuration(self, config: dict[str, Any]) -> bool:
        from rich.progress import Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

        from flow.cli.ui.presentation.visual_constants import format_text
        from flow.cli.utils.theme_manager import theme_manager
        from flow.core.setup_wizard.ui_renderer import AnimatedDots

        self.console.print(f"\n{format_text('title', 'Verifying Configuration')}")
        self.console.print("─" * 50)

        import time as _time

        start_time = _time.time()
        dots = AnimatedDots()
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TimeElapsedColumn(),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("Connecting to API...", total=None)
            try:
                progress.update(task, description=f"Connecting to API{dots.next()}")
                _time.sleep(0.5)
                progress.update(task, description=f"Testing configuration{dots.next()}")
                success, error = self.adapter.verify_configuration(config)
                elapsed = _time.time() - start_time
                if success:
                    success_color = theme_manager.get_color("success")
                    progress.update(
                        task,
                        description=f"[{success_color}]✓ Configuration verified! ({elapsed:.1f}s)[/{success_color}]",
                    )
                    return True
                else:
                    progress.update(
                        task, description=f"[error]✗ Verification failed ({elapsed:.1f}s)[/error]"
                    )
                    self.console.print(f"\n[error]Error:[/error] {error}")
                    return False
            except Exception as e:  # noqa: BLE001
                elapsed = _time.time() - start_time
                progress.update(
                    task, description=f"[error]✗ Verification failed ({elapsed:.1f}s)[/error]"
                )
                self.console.print(f"\n[error]Error:[/error] {e}")
                return False

    def _get_validation_result(self, field_name: str, value: str, context: dict[str, Any]):
        """Return cached validation result if value and dependencies haven't changed.

        The cache key includes the values of any declared dependencies for the field
        (e.g., api_key for billing), so changing a dependency triggers re-validation.
        """
        # Build dependency-aware cache key
        fields_by_name = {f.name: f for f in self.adapter.get_configuration_fields()}
        field = fields_by_name.get(field_name)
        depends_on = field.depends_on if field and field.depends_on else []
        dep_items = tuple(sorted((dep, str(context.get(dep, ""))) for dep in depends_on))
        cache_key = (field_name, value, dep_items)

        if cache_key in self._validation_cache:
            return self._validation_cache[cache_key]
        result = self.adapter.validate_field(field_name, value, context)
        self._validation_cache[cache_key] = result
        return result

    def _invalidate_validation_cache_for_fields(self, field_names: list[str]) -> None:
        """Remove cached validation entries for the given fields."""
        field_names_set = set(field_names)
        keys_to_delete = [k for k in self._validation_cache.keys() if k[0] in field_names_set]
        for k in keys_to_delete:
            del self._validation_cache[k]
