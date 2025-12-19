"""Connection registry for dynamic class registration."""

from data_exchange_agent.config.sections.connections.base import BaseConnectionConfig
from data_exchange_agent.utils.base_registry import BaseRegistry


class ConnectionRegistry(BaseRegistry[BaseConnectionConfig]):
    """Registry for connection configuration classes."""

    _registry_type_name = "connection"
