"""Base registry for dynamic class registration."""

from abc import ABC
from typing import Generic, TypeVar


T = TypeVar("T")


class BaseRegistry(ABC, Generic[T]):
    """Base registry for configuration classes."""

    _registry: dict[str, type[T]] = {}
    _registry_type_name: str = "item"  # Override in subclasses

    def __init_subclass__(cls, **kwargs):
        """Initialize subclass with its own registry."""
        super().__init_subclass__(**kwargs)
        cls._registry = {}

    @classmethod
    def register(cls, name: str, config_class: type[T]) -> None:
        """
        Register a configuration class.

        Args:
            name: The configuration type name
            config_class: The configuration class to register

        """
        cls._registry[name] = config_class

    @classmethod
    def get(cls, name: str) -> type[T]:
        """
        Get a registered configuration class.

        Args:
            name: The configuration type name

        Returns:
            The registered configuration class

        Raises:
            KeyError: If the configuration type is not registered

        """
        if name not in cls._registry:
            available = ", ".join(cls._registry.keys()) if cls._registry else "none"
            raise KeyError(
                f"{cls._registry_type_name.capitalize()} type '{name}' not registered. Available types: {available}"
            )
        return cls._registry[name]

    @classmethod
    def create(cls, name: str, **kwargs) -> T:
        """
        Create an instance of a registered configuration.

        Args:
            name: The configuration type name
            **kwargs: Arguments to pass to the configuration class constructor

        Returns:
            An instance of the configuration class

        """
        config_class = cls.get(name)
        return config_class(**kwargs)

    @classmethod
    def list_types(cls) -> list[str]:
        """Return list of registered configuration types."""
        return list(cls._registry.keys())

    @classmethod
    def is_registered(cls, name: str) -> bool:
        """Check if a configuration type is registered."""
        return name in cls._registry
