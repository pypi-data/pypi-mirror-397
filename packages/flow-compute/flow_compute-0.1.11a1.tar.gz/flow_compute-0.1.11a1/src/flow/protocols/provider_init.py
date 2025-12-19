"""Provider initialization interface.

This module defines the interface for provider initialization and configuration,
separate from the main provider runtime interface.
"""

from typing import Protocol


class ProviderInitProtocol(Protocol):
    """Provider initialization and configuration interface.

    Defines provider-specific initialization capabilities and enables the CLI
    to gather configuration without hard-coding provider logic. This abstraction
    allows new providers to be added without modifying the CLI commands.
    """

    def get_setup_instructions(self) -> list[str]:
        """Get human-readable setup instructions for this provider.

        Returns:
            List of setup instruction strings for display to users.
        """
        ...

    def test_connection(self, config: dict[str, str]) -> tuple[bool, str]:
        """Test connection to provider with given configuration.

        Args:
            config: Configuration dictionary to test

        Returns:
            Tuple of (is_connected, status_message).
        """
        ...


# Backward compatibility alias
IProviderInit = ProviderInitProtocol
