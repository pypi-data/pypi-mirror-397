"""Base configuration class with common functionality."""


class BaseConfig:
    """Base configuration class with common functionality."""

    def keys(self) -> list[str]:
        """Get all non-private configuration keys."""
        return [attr for attr in dir(self) if not attr.startswith("_") and not callable(getattr(self, attr))]
