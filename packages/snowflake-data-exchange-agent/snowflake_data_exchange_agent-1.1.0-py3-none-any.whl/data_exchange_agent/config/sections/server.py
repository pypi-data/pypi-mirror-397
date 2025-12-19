from data_exchange_agent.config.sections.base_section_config import BaseSectionConfig


class ServerConfig(BaseSectionConfig):
    """Configuration class for server host and port settings."""

    def __init__(self, host: str | None = None, port: int | None = None):
        """
        Initialize server configuration.

        Args:
            host: Host address to bind to (None = Not configured)
            port: Port number to bind to (None = Not configured)

        """
        super().__init__()
        self.host = host
        self.port = port

    def _custom_validation(self) -> str | None:
        """
        Validate server configuration.

        Returns:
            str | None: Error message string or None on success.

        """
        if self.host is not None:
            if not isinstance(self.host, str):
                return f"Host must be a string, got {type(self.host).__name__}."

        if self.port is not None:
            if not isinstance(self.port, int):
                return f"Port must be an integer, got {type(self.port).__name__}."
            if not (1 <= self.port <= 65535):
                return "Port must be between 1 and 65535."

        return None

    def __repr__(self) -> str:
        """Return string representation of server configuration."""
        return f"ServerConfig(host='{self.host}', port={self.port})"
