import re

from abc import ABC, abstractmethod

from data_exchange_agent.config.sections.connections.base import BaseConnectionConfig


class BaseJDBCConnectionConfig(BaseConnectionConfig, ABC):
    """Configuration base class for JDBC connection settings."""

    # Matches DNS-valid characters (letters, numbers, hyphens, dots)
    _HOST_DNS_PATTERN = re.compile(r"^[a-zA-Z0-9_\-\.]+$")
    # Matches IPv4 format (does not validate ranges)
    _HOST_IP_PATTERN = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")

    _required_fields = ["driver_name", "username", "password", "database", "host", "port", "url"]

    def __init__(
        self,
        driver_name: str,
        username: str,
        password: str,
        database: str,
        host: str,
        port: int,
        **extra_options: str | int | float | bool,
    ) -> None:
        """
        Initialize a JDBC connection configuration.

        Args:
            driver_name: Driver name
            username: Database username
            password: Database password
            database: Database name
            host: Database host address
            port: Database port number
            **extra_options: Extra options to add to the JDBC connection URL as key-value pairs

        """
        super().__init__()
        self.driver_name = driver_name
        self.username = username
        self.password = password
        self.database = database
        self.host = host
        self.port = port
        self.extra_options = extra_options
        self.url = self.build_url()

    @abstractmethod
    def build_url(self) -> str:
        """Build the JDBC connection URL."""
        pass

    def _repr_fields(self) -> str:
        """Get string representation of fields (for use in __repr__)."""
        extra_options_masked = {
            key: "***" if key == "password" else self._mask_sensitive_data(value)
            for key, value in self.extra_options.items()
        }
        return (
            f"driver_name='{self.driver_name}', "
            f"username='{self.username}', "
            f"password='***', "
            f"host='{self.host}', "
            f"port={self.port}, "
            f"database='{self.database}', "
            f"extra_options={extra_options_masked}, "
            f"url='***'"
        )

    def __repr__(self) -> str:
        """Return string representation of a JDBC connection configuration."""
        class_name = self.__class__.__name__
        return f"{class_name}({self._repr_fields()})"

    def _custom_validation(self) -> str | None:
        """
        Validate the JDBC connection configuration.

        Returns:
            str | None: Error message string or None on success.

        """
        validation_error = super()._custom_validation()
        if validation_error:
            return validation_error

        host_error = self._validate_host()
        if host_error:
            return host_error

        if not isinstance(self.port, int):
            return f"Port must be an integer, got {type(self.port).__name__}."
        if not (1 <= self.port <= 65535):
            return "Port must be between 1 and 65535."

        extra_options_error = self._validate_extra_options()
        if extra_options_error:
            return extra_options_error

        return None

    def _validate_host(self) -> str | None:
        if not (1 <= len(self.host) <= 255):
            return "Hostname length must be between 1 and 255 characters."

        # This checks if it contains only valid DNS characters and dots.
        if not self._HOST_DNS_PATTERN.fullmatch(self.host):
            return "Hostname contains invalid characters. Must only contain letters, numbers, hyphens, and dots."

        # Check for IP address format (simple check)
        if self._HOST_IP_PATTERN.fullmatch(self.host):
            return None  # It's a valid IPv4 format

        # If not an IP, treat as a DNS name and check common pitfalls

        # No leading or trailing dots
        if self.host.startswith(".") or self.host.endswith("."):
            return "DNS name cannot start or end with a dot."

        # Check for empty labels (e.g., "host..name")
        if ".." in self.host:
            return "DNS name cannot contain adjacent dots (empty label)."

        # Check for hyphens at start/end of any label (part between dots)
        labels = self.host.split(".")
        for label in labels:
            if label.startswith("-") or label.endswith("-"):
                return "Labels (parts between dots) cannot start or end with a hyphen."

        return None

    def _validate_extra_options(self) -> str | None:
        if not isinstance(self.extra_options, dict):
            return f"Extra options must be a dictionary, got {type(self.extra_options).__name__}."
        for key, value in self.extra_options.items():
            # validate key
            if not isinstance(key, str):
                return f"Extra option keys must be strings, got {type(key).__name__}."
            key_error = self._validate_required_field(key, "Extra option key")
            if key_error:
                return f"Extra option key error: {key_error}"

            # validate value
            value_error = self._validate_required_field(value, f"Extra option '{key}'")
            if value_error:
                return f"Extra option '{key}' value error: {value_error}"

        return None
