"""Kubeconfig management utilities for k8s commands."""

from __future__ import annotations

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import urlparse, urlunparse

import yaml
from rich.console import Console

from flow.cli.utils.ssh_helpers import build_ssh_argv

if TYPE_CHECKING:
    from flow.adapters.providers.builtin.mithril.bindings.models.kubernetes_cluster_model import (
        KubernetesClusterModel,
    )

KubeConfig = dict[str, Any]


def fetch_remote_kubeconfig(cluster: KubernetesClusterModel, ssh_key_path: Path) -> KubeConfig:
    """Fetch kubeconfig from remote cluster via SSH.

    Args:
        cluster: Cluster object with kube_host
        ssh_key_path: Path to SSH private key

    Returns:
        Parsed kubeconfig dictionary

    Raises:
        RuntimeError: If SSH fails
        TypeError: If kubeconfig is not a dictionary
        ValueError: If YAML is invalid
    """
    ssh_argv = build_ssh_argv(
        user="ubuntu",
        host=cluster.kube_host,
        port=22,
        key_path=str(ssh_key_path),
        extra_ssh_args=None,
        remote_command=["cat", "~/.kube/config"],
    )

    try:
        result = subprocess.run(ssh_argv, capture_output=True, text=True, check=True, timeout=30)
        config = yaml.safe_load(result.stdout)
        if not isinstance(config, dict):
            raise TypeError("Remote kubeconfig is not a valid YAML dictionary")
        return config
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Failed to fetch kubeconfig via SSH: {e.stderr or e.stdout}") from e
    except yaml.YAMLError as e:
        raise ValueError(f"Remote kubeconfig is not valid YAML: {e}") from e


def replace_server_url(url: str, new_host: str) -> str:
    """Replace host in server URL while preserving scheme and port.

    Args:
        url: Original server URL (e.g., https://127.0.0.1:6443)
        new_host: New host to use (e.g., 10.20.30.40)

    Returns:
        Modified URL with new host
    """
    parsed = urlparse(url)
    # Replace host, preserve port if present.
    if parsed.port:
        new_netloc = f"{new_host}:{parsed.port}"
    else:
        new_netloc = new_host

    return urlunparse((parsed.scheme, new_netloc, parsed.path, "", "", ""))


def rewrite_kubeconfig(config: KubeConfig, cluster: KubernetesClusterModel) -> KubeConfig:
    """Rewrite local kubeconfig from a remote cluster

    Replace local IPs with internet-facing IP address and rename context, server, and user entries.

    Args:
        config: Original kubeconfig dictionary
        cluster: Cluster object with name and kube_host

    Returns:
        Modified kubeconfig with renamed entries and replaced IPs
    """
    modified = config.copy()
    context_name = f"mithril:{cluster.name}"

    # Replace server URLs in clusters
    if "clusters" in modified:
        for cluster_entry in modified["clusters"]:
            if "cluster" in cluster_entry and "server" in cluster_entry["cluster"]:
                cluster_entry["cluster"]["server"] = replace_server_url(
                    cluster_entry["cluster"]["server"], cluster.kube_host
                )
            # Rename cluster
            cluster_entry["name"] = context_name

    # Rename contexts
    if "contexts" in modified:
        for context_entry in modified["contexts"]:
            context_entry["name"] = context_name
            if "context" in context_entry:
                context_entry["context"]["cluster"] = context_name
                context_entry["context"]["user"] = context_name

    # Rename users
    if "users" in modified:
        for user_entry in modified["users"]:
            user_entry["name"] = context_name

    # Update current-context
    modified["current-context"] = context_name

    return modified


def load_local_kubeconfig(path: Path) -> KubeConfig | None:
    if not path.exists():
        return None

    with path.open("r") as f:
        return yaml.safe_load(f)


def check_kubeconfig_conflict(
    local_config: KubeConfig | None, new_config: KubeConfig, context_name: str
) -> tuple[dict[str, Any], dict[str, Any]] | None:
    """Check if context exists locally and differs from new config.

    Args:
        local_config: Local kubeconfig dictionary (or None if doesn't exist)
        new_config: New kubeconfig dictionary to merge
        context_name: Name of the context to check

    Returns:
        Tuple of (old_entries, new_entries) if entries exist and differ, None otherwise
    """
    if not local_config:
        return None

    ENTRY_TYPES = [
        ("context", "contexts"),
        ("cluster", "clusters"),
        ("user", "users"),
    ]

    old_entries = {}
    for entry_key, config_key in ENTRY_TYPES:
        for entry in local_config.get(config_key, []):
            if entry.get("name") == context_name:
                old_entries[entry_key] = entry
                break

    if not old_entries:
        return None

    new_entries = {}
    for entry_key, config_key in ENTRY_TYPES:
        for entry in new_config.get(config_key, []):
            if entry.get("name") == context_name:
                new_entries[entry_key] = entry
                break

    # Check if entries actually differ
    for entry_key, _ in ENTRY_TYPES:
        if old_entries.get(entry_key) != new_entries.get(entry_key):
            return (old_entries, new_entries)

    return None


def show_kubeconfig_diff(
    console: Console, context_name: str, old_entries: dict[str, Any], new_entries: dict[str, Any]
) -> None:
    """Show diff between old and new kubeconfig entries.

    Args:
        console: Rich console for output
        context_name: Name of the context being updated
        old_entries: Existing entries from local config
        new_entries: New entries from remote config
    """
    console.print(f"\n[yellow]Existing kubeconfig entries for '{context_name}':[/yellow]")

    for entry_type in ["cluster", "context", "user"]:
        if entry_type in old_entries:
            console.print(f"\n[dim]# Old {entry_type}:[/dim]")
            old_yaml = yaml.safe_dump(old_entries[entry_type], default_flow_style=False)
            for line in old_yaml.splitlines():
                console.print(f"[red]- {line}[/red]")

    console.print("\n[green]New kubeconfig entries:[/green]")

    for entry_type in ["cluster", "context", "user"]:
        if entry_type in new_entries:
            console.print(f"\n[dim]# New {entry_type}:[/dim]")
            new_yaml = yaml.safe_dump(new_entries[entry_type], default_flow_style=False)
            for line in new_yaml.splitlines():
                console.print(f"[green]+ {line}[/green]")


def create_backup(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.parent / f"{path.name}.backup.{timestamp}"
    shutil.copy2(path, backup_path)
    return backup_path


def merge_kubeconfigs(
    local_kubeconfig_path: Path, remote_kubeconfig_path: Path, context_name: str
) -> KubeConfig:
    """Merge remote kubeconfig into local using kubectl config view --flatten.

    Args:
        local_kubeconfig_path: Path to local kubeconfig file
        remote_kubeconfig_path: Path to remote kubeconfig file
        context_name: Name of the context being added (for setting current-context)

    Returns:
        Merged kubeconfig dictionary

    Raises:
        RuntimeError: If kubectl merge fails
        TypeError: If kubectl returns non-dictionary YAML
        ValueError: If kubectl returns invalid YAML
        FileNotFoundError: If kubectl is not installed
    """
    # Use kubectl's native merge with KUBECONFIG env var
    # Leftmost file takes precedence, so put remote first
    kubeconfig_env = f"{remote_kubeconfig_path}:{local_kubeconfig_path}"

    try:
        result = subprocess.run(
            ["kubectl", "config", "view", "--flatten"],
            env={**os.environ, "KUBECONFIG": kubeconfig_env},
            capture_output=True,
            text=True,
            check=True,
            timeout=10,
        )
        merged = yaml.safe_load(result.stdout)
        if not isinstance(merged, dict):
            raise TypeError("kubectl config view returned invalid YAML")

        # Set current-context to the new context
        merged["current-context"] = context_name

        return merged
    except FileNotFoundError as e:
        raise FileNotFoundError("kubectl command not found. Please install kubectl.") from e
    except subprocess.CalledProcessError as e:
        raise RuntimeError(
            f"Failed to merge kubeconfigs with kubectl: {e.stderr or e.stdout}"
        ) from e
    except yaml.YAMLError as e:
        raise ValueError(f"kubectl returned invalid YAML: {e}") from e


def save_kubeconfig(path: Path, config: KubeConfig) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w") as f:
        yaml.safe_dump(config, f, default_flow_style=False, sort_keys=False)


def validate_kubeconfig(context_name: str) -> None:
    """Validate kubeconfig by testing kubectl connectivity.

    Args:
        context_name: Name of the context to test

    Raises:
        RuntimeError: If validation fails, with command and output details
    """
    cmd = ["kubectl", "version", "--context", context_name, "--request-timeout=5s"]

    try:
        subprocess.run(
            cmd,
            capture_output=True,
            check=True,
            text=True,
            timeout=10,
        )
    except subprocess.CalledProcessError as e:
        cmd_str = " ".join(cmd)
        output = e.stderr or e.stdout or "(no output)"
        raise RuntimeError(
            f"Failed to validate kubeconfig.\nCommand: {cmd_str}\nOutput: {output}"
        ) from e
