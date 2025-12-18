"""Local provider initialization and configuration implementation."""

from flow.protocols.provider_init import ProviderInitProtocol as IProviderInit


class LocalInit(IProviderInit):
    """Local provider initialization interface implementation.

    Handles configuration for running tasks locally, primarily
    used for development and testing.
    """

    def __init__(self):
        """Initialize local provider init.

        Local provider doesn't need HTTP client since it runs locally.
        """
        pass

    def list_projects(self) -> list[dict[str, str]]:
        """List projects for local provider.

        Local provider doesn't have projects concept, returns empty list.

        Returns:
            Empty list - projects not applicable for local execution
        """
        return []

    def list_ssh_keys(self, project_id: str | None = None) -> list[dict[str, str]]:
        """List SSH keys for local provider.

        Local provider doesn't use SSH keys since tasks run locally.

        Args:
            project_id: Ignored for local provider

        Returns:
            Empty list - SSH keys not applicable for local execution
        """
        return []
