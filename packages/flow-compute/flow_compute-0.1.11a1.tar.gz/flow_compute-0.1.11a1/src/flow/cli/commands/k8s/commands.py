"""Entrypoints for `flow k8s ...` commands."""

from __future__ import annotations

import asyncio

import click

from flow.cli.app import OrderedDYMGroup
from flow.cli.commands.base import BaseCommand
from flow.cli.utils.error_handling import cli_error_guard
from flow.cli.utils.theme_manager import theme_manager as _tm


@click.command()
@click.option("--verbose", "-v", is_flag=True, help="Show detailed cluster information")
@click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
@click.option(
    "--all", "show_all", is_flag=True, help="Show all clusters, including terminated ones"
)
def list_clusters(verbose: bool, output_json: bool, show_all: bool) -> None:
    """List Kubernetes clusters in the current project.

    \b
    Examples:
      flow k8s list                # Simple table view
      flow k8s list --verbose      # Detailed view with instance/SSH key counts
      flow k8s list --json         # JSON output for automation
    """
    from .impl import list_clusters as list_clusters_impl

    asyncio.run(list_clusters_impl(verbose, output_json, show_all))


@click.command()
@click.argument("cluster_name_or_fid")
@click.option("--json", "output_json", is_flag=True, help="Output JSON for automation")
def cluster_info(cluster_name_or_fid: str, output_json: bool) -> None:
    """Show detailed information about a Kubernetes cluster.

    CLUSTER_NAME_OR_FID can be either a cluster name or FID (starting with 'clust_').

    \b
    Examples:
      flow k8s info my-cluster      # Lookup by name
      flow k8s info clust_abc123    # Lookup by FID
      flow k8s info my-cluster --json
    """
    from .impl import cluster_info as cluster_info_impl

    asyncio.run(cluster_info_impl(cluster_name_or_fid, output_json))


@click.command()
@click.argument("cluster_name_or_fid")
@click.argument("remote_cmd", nargs=-1)
@click.option("--show", is_flag=True, help="Display SSH command without executing")
@click.option(
    "-i",
    "--identity",
    "identity_file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="SSH private key file to use (like ssh -i)",
)
def ssh(
    cluster_name_or_fid: str, remote_cmd: tuple[str, ...], show: bool, identity_file: str | None
) -> None:
    """SSH into Kubernetes cluster control node.

    CLUSTER_NAME_OR_FID can be either a cluster name or FID (starting with 'clust_').

    \b
    Examples:
      flow k8s ssh my-cluster                         # Interactive SSH session
      flow k8s ssh clust_abc123 -- kubectl get nodes  # Run remote command
      flow k8s ssh my-cluster --show                  # Display SSH command
      flow k8s ssh my-cluster -i ~/.ssh/my_key        # Use specific SSH key
    """
    from .impl import cluster_ssh as cluster_ssh_impl

    asyncio.run(cluster_ssh_impl(cluster_name_or_fid, remote_cmd, show, identity_file))


@click.command()
@click.argument("cluster_name_or_fid")
@click.option(
    "-i",
    "--identity",
    "identity_file",
    type=click.Path(exists=True, dir_okay=False, resolve_path=True),
    help="SSH private key file to use (like ssh -i)",
)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation prompts")
@click.option("--no-backup", is_flag=True, help="Skip backup of existing kubeconfig")
@click.option("--skip-validation", is_flag=True, help="Skip kubectl connectivity test")
def update_kubeconfig(
    cluster_name_or_fid: str,
    identity_file: str | None,
    yes: bool,
    no_backup: bool,
    skip_validation: bool,
) -> None:
    """Fetch k8s cluster credentials and update local kubeconfig.

    CLUSTER_NAME_OR_FID can be either a cluster name or FID (starting with 'clust_').

    \b
    This command:
      - Downloads kubeconfig from the cluster control node
      - Renames entries to 'mithril:{CLUSTER_NAME}' to avoid conflicts
      - Merges with your local ~/.kube/config
      - Sets the new context as current
      - Validates connectivity

    \b
    Examples:
      flow k8s update-kubeconfig my-cluster           # Update kubeconfig
      flow k8s update-kubeconfig clust_abc123 -y      # Skip prompts
      flow k8s update-kubeconfig my-cluster -i ~/.ssh/my_key
    """
    from .impl import update_kubeconfig as update_kubeconfig_impl

    asyncio.run(
        update_kubeconfig_impl(cluster_name_or_fid, identity_file, yes, no_backup, skip_validation)
    )


class K8sCommand(BaseCommand):
    """Kubernetes cluster management command."""

    @property
    def name(self) -> str:
        """Command name."""
        return "k8s"

    @property
    def help(self) -> str:
        """Command help text."""
        return "Manage Kubernetes clusters"

    def get_command(self) -> click.Command:
        """Return the k8s command group."""

        @click.group(name="k8s", cls=OrderedDYMGroup, invoke_without_command=True)
        @cli_error_guard(self)
        def k8s_group():
            """Manage Kubernetes clusters.

            \b
            Examples:
              flow k8s list                # List all clusters
              flow k8s list --verbose      # Detailed view
              flow k8s list --json         # JSON output
              flow k8s info my-cluster     # Show cluster details

            Run 'flow k8s list' to see all available Kubernetes clusters.
            """
            ctx = click.get_current_context()

            if ctx.invoked_subcommand is None:
                console = _tm.create_console()

                console.print("\n[bold]Kubernetes Cluster Management[/bold]\n")
                console.print("[dim]Available commands:[/dim]")
                console.print("  [accent]flow k8s list[/accent]         # List all clusters")
                console.print("  [accent]flow k8s list -v[/accent]      # Detailed view")
                console.print("  [accent]flow k8s list --json[/accent]  # JSON output")
                console.print("  [accent]flow k8s info <name>[/accent]  # Show cluster details")
                console.print(
                    "  [accent]flow k8s ssh <name>[/accent]   # SSH into cluster control node"
                )
                console.print()

        k8s_group.add_command(list_clusters, name="list")
        k8s_group.add_command(cluster_info, name="info")
        k8s_group.add_command(ssh, name="ssh")
        k8s_group.add_command(update_kubeconfig, name="update-kubeconfig")

        return k8s_group


command = K8sCommand()
