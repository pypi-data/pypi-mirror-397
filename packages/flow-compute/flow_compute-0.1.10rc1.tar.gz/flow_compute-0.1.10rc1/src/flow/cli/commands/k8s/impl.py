"""Kubernetes cluster management implementation.

Lazily imported by commands.py to improve CLI startup time, can import things normally.
"""

from __future__ import annotations

import asyncio
import logging
import os
import subprocess
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

import click
from rich.console import Console

import flow.sdk.factory as sdk_factory
from flow.adapters.providers.builtin.mithril.bindings.api.kubernetes_clusters import (
    get_kubernetes_cluster_v2_kubernetes_clusters_cluster_fid_get as get_k8s_cluster,
)
from flow.adapters.providers.builtin.mithril.bindings.api.kubernetes_clusters import (
    get_kubernetes_clusters_v2_kubernetes_clusters_get as get_k8s_clusters,
)
from flow.adapters.providers.builtin.mithril.bindings.api.ssh_keys import (
    get_ssh_keys_v2_ssh_keys_get as get_ssh_keys,
)
from flow.adapters.providers.builtin.mithril.bindings.client import AuthenticatedClient
from flow.adapters.providers.builtin.mithril.bindings.models.http_validation_error import (
    HTTPValidationError,
)
from flow.adapters.providers.builtin.mithril.bindings.models.kubernetes_cluster_model import (
    KubernetesClusterModel,
)
from flow.adapters.providers.builtin.mithril.bindings.models.kubernetes_cluster_model_status import (
    KubernetesClusterModelStatus,
)
from flow.adapters.providers.builtin.mithril.bindings.models.new_ssh_key_model import (
    NewSshKeyModel,
)
from flow.adapters.providers.builtin.mithril.domain.models import PlatformSSHKey
from flow.cli.commands.k8s._kubeconfig import (
    check_kubeconfig_conflict,
    create_backup,
    fetch_remote_kubeconfig,
    load_local_kubeconfig,
    merge_kubeconfigs,
    rewrite_kubeconfig,
    save_kubeconfig,
    show_kubeconfig_diff,
    validate_kubeconfig,
)
from flow.cli.ui.formatters.shared_task import TaskFormatter
from flow.cli.ui.presentation.animated_progress import AnimatedEllipsisProgress
from flow.cli.ui.presentation.table_styles import create_flow_table, wrap_table_in_panel
from flow.cli.ui.presentation.time_formatter import TimeFormatter
from flow.cli.utils.error_handling import render_auth_required_message
from flow.cli.utils.json_output import error_json, print_json
from flow.cli.utils.ssh_helpers import build_ssh_argv, ssh_command_string
from flow.cli.utils.theme_manager import theme_manager as _tm
from flow.core.utils.ssh_key import (
    discover_local_ssh_keys,
    match_local_key_to_platform,
    md5_fingerprint_from_public_key,
)
from flow.errors import AuthenticationError

logger = logging.getLogger(__name__)


@contextmanager
def _handle_errors(console: Console, output_json: bool):
    try:
        yield
    except AuthenticationError:
        if output_json:
            print_json(error_json("Authentication required"))
            sys.exit(1)
        render_auth_required_message(console, output_json=False)
        raise click.exceptions.Exit(1)
    except Exception as e:
        logger.debug(f"Error in k8s command: {e}", exc_info=True)
        if output_json:
            print_json(error_json(str(e)))
            sys.exit(1)
        raise click.ClickException(str(e)) from e


def _format_http_validation_error(error: HTTPValidationError) -> str:
    error_msg = "Validation error from API"
    if error.detail:
        details = [f"{err.loc}: {err.msg}" for err in error.detail]
        if details:
            error_msg = f"Validation error: {', '.join(details)}"
    return error_msg


def _get_api_client() -> tuple[str, str, str]:
    """Get authenticated API client details.

    Returns:
        Tuple of (api_url, token, project_id)

    Raises:
        AuthenticationError: If unable to authenticate
    """
    flow = sdk_factory.create_client(auto_init=True)
    provider = flow.provider
    project_id = provider.project_id
    api_url = provider.api_url

    mithril_config = getattr(provider.ctx, "config", None)
    if not mithril_config:
        raise AuthenticationError("Unable to get Mithril configuration")

    token = mithril_config.auth_token
    if not token:
        raise AuthenticationError("No authentication token found")

    return api_url, token, project_id


def _is_cluster_fid(identifier: str) -> bool:
    """Check if identifier is a cluster FID (starts with 'clust_').

    Args:
        identifier: String to check

    Returns:
        True if identifier is a cluster FID, False otherwise
    """
    return identifier.startswith("clust_")


async def _resolve_cluster_and_ssh_keys(
    cluster_name_or_fid: str,
    api_client: AuthenticatedClient,
    project_id: str,
    console: Console,
) -> tuple[KubernetesClusterModel, list[NewSshKeyModel]]:
    """Resolve cluster and SSH keys by FID or name.

    Args:
        cluster_name_or_fid: Cluster name or FID (starting with 'clust_')
        api_client: Authenticated API client
        project_id: Project ID
        console: Console for progress display

    Returns:
        Tuple of (cluster, ssh_keys)

    Raises:
        click.ClickException: If cluster not found or API errors occur
    """
    if _is_cluster_fid(cluster_name_or_fid):
        cluster_fid = cluster_name_or_fid

        with AnimatedEllipsisProgress(
            console, f"Loading cluster {cluster_fid}", start_immediately=True
        ):
            cluster_response, ssh_keys_response = await asyncio.gather(
                get_k8s_cluster.asyncio(client=api_client, cluster_fid=cluster_fid),
                get_ssh_keys.asyncio(client=api_client, project=project_id),
            )

        if cluster_response is None:
            raise click.ClickException(f"Cluster '{cluster_fid}' not found")
        elif isinstance(cluster_response, HTTPValidationError):
            raise click.ClickException(_format_http_validation_error(cluster_response))

        if ssh_keys_response is None:
            raise click.ClickException("Failed to fetch SSH keys from API")
        elif isinstance(ssh_keys_response, HTTPValidationError):
            raise click.ClickException(_format_http_validation_error(ssh_keys_response))

        return cluster_response, ssh_keys_response
    else:
        cluster_name = cluster_name_or_fid

        with AnimatedEllipsisProgress(
            console, f"Searching for cluster '{cluster_name}'", start_immediately=True
        ):
            clusters_response, ssh_keys_response = await asyncio.gather(
                get_k8s_clusters.asyncio(client=api_client, project=project_id),
                get_ssh_keys.asyncio(client=api_client, project=project_id),
            )

        if clusters_response is None:
            raise click.ClickException("Failed to fetch Kubernetes clusters from API")
        elif isinstance(clusters_response, HTTPValidationError):
            raise click.ClickException(_format_http_validation_error(clusters_response))

        if ssh_keys_response is None:
            raise click.ClickException("Failed to fetch SSH keys from API")
        elif isinstance(ssh_keys_response, HTTPValidationError):
            raise click.ClickException(_format_http_validation_error(ssh_keys_response))

        matching_clusters = [c for c in clusters_response if c.name == cluster_name]

        if not matching_clusters:
            raise click.ClickException(
                f"Cluster '{cluster_name}' not found. Use 'flow k8s list' to see available clusters."
            )
        elif len(matching_clusters) > 1:
            fids = ", ".join(c.fid for c in matching_clusters)
            raise click.ClickException(
                f"Multiple clusters with name '{cluster_name}' found. Use FID instead: {fids}"
            )

        return matching_clusters[0], ssh_keys_response


def _map_ssh_key_names(
    ssh_key_fids: list[str], ssh_keys: list[NewSshKeyModel], max_display: int = 2
) -> str:
    """Map SSH key FIDs to human-readable names.

    Args:
        ssh_key_fids: List of SSH key FIDs from cluster
        ssh_keys: List of NewSshKeyModel objects
        max_display: Maximum number of key names to display before truncating

    Returns:
        Formatted string with key names, e.g., "key1, key2, ... (5 total)"
    """
    if not ssh_key_fids:
        return "[dim]None[/dim]"

    fid_to_name = {key.fid: key.name for key in ssh_keys}
    key_names = [fid_to_name.get(fid, fid) for fid in ssh_key_fids]

    total_count = len(key_names)
    if total_count <= max_display:
        return ", ".join(key_names)

    displayed_names = ", ".join(key_names[:max_display])
    return f"{displayed_names}, ... ({total_count} total)"


def _get_k8s_status_priority(cluster: KubernetesClusterModel) -> int:
    match cluster.status:
        case KubernetesClusterModelStatus.AVAILABLE:
            return 0
        case KubernetesClusterModelStatus.PENDING:
            return 1
        case KubernetesClusterModelStatus.TERMINATED:
            return 2


T = TypeVar("T")


def _get_k8s_created_timestamp(cluster: KubernetesClusterModel, default: T) -> datetime | T:
    try:
        return datetime.fromisoformat(cluster.created_at.replace("Z", "+00:00"))
    except ValueError:
        return default


def _sort_and_filter_clusters(
    clusters: list[KubernetesClusterModel], show_all: bool = False
) -> list[KubernetesClusterModel]:
    # TODO(ilia): Have k8s listing api support server-side sorting.
    if not show_all:
        clusters = [c for c in clusters if c.status != KubernetesClusterModelStatus.TERMINATED]

    return sorted(
        clusters,
        key=lambda c: (
            _get_k8s_status_priority(c),
            -_get_k8s_created_timestamp(c, default=datetime.min.replace(tzinfo=None)).timestamp(),
        ),
    )


def _render_k8s_clusters_table(
    clusters: list[KubernetesClusterModel],
    verbose: bool,
    console: Console,
    ssh_keys: list[NewSshKeyModel],
) -> None:
    table = create_flow_table(show_borders=False, expand=False)
    table.add_column("#", style="white", width=4, header_style="bold white", justify="right")
    table.add_column("Name", style="white", width=24, header_style="bold white", justify="left")
    table.add_column("Region", style="white", width=16, header_style="bold white", justify="left")
    table.add_column("Status", style="white", width=12, header_style="bold white", justify="left")
    table.add_column("Created", style="white", width=20, header_style="bold white", justify="left")

    if verbose:
        table.add_column(
            "Instances", style="white", width=10, header_style="bold white", justify="right"
        )
        table.add_column(
            "SSH Keys", style="white", width=30, header_style="bold white", justify="left"
        )

    for idx, cluster in enumerate(clusters, start=1):
        created_dt = _get_k8s_created_timestamp(cluster, default=None)

        row = [
            str(idx),
            cluster.name,
            cluster.region,
            TaskFormatter.format_status_with_color(cluster.status.value),
            TimeFormatter.format_time_ago(created_dt),
        ]

        if verbose:
            instance_count = len(cluster.instances) if cluster.instances else 0
            ssh_key_names = _map_ssh_key_names(cluster.ssh_keys or [], ssh_keys)

            row.extend(
                [
                    str(instance_count),
                    ssh_key_names,
                ]
            )

        table.add_row(*row)

    wrap_table_in_panel(table, "Kubernetes Clusters", console)


async def list_clusters(verbose: bool, output_json: bool, show_all: bool) -> None:
    """List Kubernetes clusters in the current project."""
    console = _tm.create_console()

    with _handle_errors(console, output_json):
        api_url, token, project_id = _get_api_client()
        api_client = AuthenticatedClient(base_url=api_url, token=token)

        with AnimatedEllipsisProgress(
            console, "Loading Kubernetes clusters", start_immediately=True
        ):
            clusters_response, ssh_keys_response = await asyncio.gather(
                get_k8s_clusters.asyncio(client=api_client, project=project_id),
                get_ssh_keys.asyncio(client=api_client, project=project_id),
            )

        if clusters_response is None:
            raise click.ClickException("Failed to fetch Kubernetes clusters from API")
        elif isinstance(clusters_response, HTTPValidationError):
            raise click.ClickException(_format_http_validation_error(clusters_response))

        if ssh_keys_response is None:
            raise click.ClickException("Failed to fetch SSH keys from API")
        elif isinstance(ssh_keys_response, HTTPValidationError):
            raise click.ClickException(_format_http_validation_error(ssh_keys_response))

        clusters = clusters_response
        ssh_keys = ssh_keys_response

        if output_json:
            output: list[dict[str, Any]] = []
            for cluster in clusters:
                output.append(cluster.to_dict())
            print_json(output)
            return

        if not clusters:
            console.print("\n[dim]No Kubernetes clusters found in this project.[/dim]")
            console.print("[dim]Tip: Create clusters via the Mithril platform.[/dim]\n")
            return

        sorted_clusters = _sort_and_filter_clusters(clusters, show_all)

        _render_k8s_clusters_table(sorted_clusters, verbose, console, ssh_keys)

        console.print(
            f"\n[dim]Total: {len(sorted_clusters)} cluster{'s' if len(sorted_clusters) != 1 else ''}[/dim]"
        )


def _render_cluster_details(
    cluster: KubernetesClusterModel, console: Console, ssh_keys: list[NewSshKeyModel]
) -> None:
    table = create_flow_table(show_borders=True, expand=False)
    table.add_column("Property", style="accent", width=20, header_style="bold white")
    table.add_column("Value", style="white", width=60, header_style="bold white")

    created_dt = _get_k8s_created_timestamp(cluster, default=None)

    table.add_row("FID", cluster.fid)
    table.add_row("Name", cluster.name)
    table.add_row("Region", cluster.region)
    table.add_row("Status", TaskFormatter.format_status_with_color(cluster.status.value))
    table.add_row("Created", TimeFormatter.format_time_ago(created_dt) if created_dt else "Unknown")
    table.add_row("Kubernetes Host", cluster.kube_host or "[dim]Not available[/dim]")

    instance_count = len(cluster.instances) if cluster.instances else 0
    table.add_row("Instances", str(instance_count))

    ssh_key_names = _map_ssh_key_names(cluster.ssh_keys or [], ssh_keys, max_display=3)
    table.add_row("SSH Keys", ssh_key_names)

    wrap_table_in_panel(table, f"Cluster: {cluster.name}", console)

    if cluster.join_command:
        console.print("\n[bold]Join Command:[/bold]")
        console.print(f"[dim]{cluster.join_command}[/dim]\n")
    else:
        console.print("\n[dim]Join command not available[/dim]\n")


async def cluster_info(cluster_name_or_fid: str, output_json: bool) -> None:
    """Show detailed information about a Kubernetes cluster."""
    console = _tm.create_console()

    with _handle_errors(console, output_json):
        api_url, token, project_id = _get_api_client()
        api_client = AuthenticatedClient(base_url=api_url, token=token)

        cluster, ssh_keys = await _resolve_cluster_and_ssh_keys(
            cluster_name_or_fid, api_client, project_id, console
        )

        if output_json:
            output = cluster.to_dict()
            print_json(output)
            return
        else:
            _render_cluster_details(cluster, console, ssh_keys)


def _find_ssh_key_for_cluster(
    cluster: KubernetesClusterModel, ssh_keys: list[NewSshKeyModel]
) -> Path | None:
    """Resolve local SSH key matching cluster's configured keys.

    Args:
        cluster: Cluster model with ssh_keys list
        ssh_keys: List of platform SSH keys from API

    Returns:
        Path to matching local private key, or None if not found
    """
    if not cluster.ssh_keys:
        return None

    local_keys = discover_local_ssh_keys()
    if not local_keys:
        return None

    platform_keys = []
    for key in ssh_keys:
        fingerprint = md5_fingerprint_from_public_key(key.public_key) or ""
        platform_keys.append(
            PlatformSSHKey(
                fid=key.fid,
                name=key.name,
                public_key=key.public_key,
                fingerprint=fingerprint,
                created_at=key.created_at,
                required=key.required,
            )
        )

    for local_key in local_keys:
        platform_key_id = match_local_key_to_platform(
            local_key.private_key_path, platform_keys, match_by_name=True
        )
        if platform_key_id and platform_key_id in cluster.ssh_keys:
            return local_key.private_key_path

    return None


def _get_ssh_key_path(
    identity_file: str | None,
    cluster: KubernetesClusterModel,
    ssh_keys: list[NewSshKeyModel],
) -> Path:
    """Get SSH key path from identity file or resolve from cluster keys.

    Args:
        identity_file: Optional explicit SSH key path
        cluster: Cluster object
        ssh_keys: List of SSH keys from the API

    Returns:
        Path to SSH key

    Raises:
        click.ClickException: If no matching SSH key found
    """
    if identity_file:
        return Path(identity_file)

    ssh_key_path = _find_ssh_key_for_cluster(cluster, ssh_keys)
    if not ssh_key_path:
        raise click.ClickException(
            f"No matching SSH key found for cluster '{cluster.name}'. "
            "Use -i to specify a key explicitly."
        )

    return ssh_key_path


async def cluster_ssh(
    cluster_name_or_fid: str,
    remote_cmd: tuple[str, ...],
    show: bool,
    identity_file: str | None = None,
) -> None:
    """SSH into a Kubernetes cluster control node."""
    console = _tm.create_console()

    with _handle_errors(console, False):
        api_url, token, project_id = _get_api_client()
        api_client = AuthenticatedClient(base_url=api_url, token=token)

        cluster, ssh_keys = await _resolve_cluster_and_ssh_keys(
            cluster_name_or_fid, api_client, project_id, console
        )

        if not cluster.kube_host:
            raise click.ClickException(
                f"Cluster '{cluster.name}' does not have an SSH endpoint available. "
                "The cluster may still be initializing."
            )

        ssh_key_path = _get_ssh_key_path(identity_file, cluster, ssh_keys)

        remote_command_list = list(remote_cmd) if remote_cmd else None
        ssh_argv = build_ssh_argv(
            user="ubuntu",
            host=cluster.kube_host,
            port=22,
            key_path=str(ssh_key_path),
            extra_ssh_args=None,
            remote_command=remote_command_list,
        )

        if show:
            console.print(ssh_command_string(ssh_argv))
            return

        try:
            if not remote_cmd:
                os.execvp(ssh_argv[0], ssh_argv)
            else:
                subprocess.run(ssh_argv, check=False)
        except Exception as e:
            raise click.ClickException(f"SSH connection failed: {e}") from e


async def update_kubeconfig(
    cluster_name_or_fid: str,
    identity_file: str | None,
    yes: bool,
    no_backup: bool,
    skip_validation: bool,
) -> None:
    """Update local kubeconfig with cluster credentials.

    Args:
        cluster_name_or_fid: Cluster name or FID
        identity_file: Optional SSH key path override
        yes: Skip confirmation prompts
        no_backup: Skip backup of existing config
        skip_validation: Skip kubectl connectivity test
    """
    console = _tm.create_console()

    with _handle_errors(console, False):
        api_url, token, project_id = _get_api_client()
        api_client = AuthenticatedClient(base_url=api_url, token=token)

        cluster, ssh_keys = await _resolve_cluster_and_ssh_keys(
            cluster_name_or_fid, api_client, project_id, console
        )

        ssh_key_path = _get_ssh_key_path(identity_file, cluster, ssh_keys)

        context_name = f"mithril:{cluster.name}"

        with AnimatedEllipsisProgress(console, "Downloading kubeconfig from cluster"):
            remote_config = fetch_remote_kubeconfig(cluster, ssh_key_path)

        modified_config = rewrite_kubeconfig(remote_config, cluster)

        kubeconfig_path = Path.home() / ".kube" / "config"
        local_config = load_local_kubeconfig(kubeconfig_path)

        if not yes:
            conflict = check_kubeconfig_conflict(local_config, modified_config, context_name)
            if conflict:
                old_entries, new_entries = conflict
                show_kubeconfig_diff(console, context_name, old_entries, new_entries)
                console.print()

                if not click.confirm(
                    f"Overwrite existing '{context_name}' entries?", default=False
                ):
                    console.print("[dim]Operation cancelled[/dim]")
                    return

        # Backup existing config.
        if not no_backup and kubeconfig_path.exists():
            backup_path = create_backup(kubeconfig_path)
            console.print(f"[dim]Backup created: {backup_path}[/dim]")

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            save_kubeconfig(tmp_path, modified_config)

        try:
            merged_config = merge_kubeconfigs(kubeconfig_path, tmp_path, context_name)
            save_kubeconfig(kubeconfig_path, merged_config)
        finally:
            tmp_path.unlink(missing_ok=True)

        console.print(f"[green]✓ Kubeconfig updated for cluster '{cluster.name}'[/green]")
        console.print(f"[dim]Context: {context_name}[/dim]")

        if not skip_validation:
            with AnimatedEllipsisProgress(console, "Validating connectivity"):
                validate_kubeconfig(context_name)
                console.print("[green]✓ Connection validated[/green]")

        # Show next steps.
        console.print("\n[bold]Test the connection:[/bold]")
        console.print("  kubectl get nodes")
        console.print("  kubectl get pods --all-namespaces")
