"""Data source registry for dynamic class registration."""

from data_exchange_agent.data_sources.base import BaseDataSource
from data_exchange_agent.utils.base_registry import BaseRegistry


class DataSourceRegistry(BaseRegistry[BaseDataSource]):
    """Registry for data source classes implementations."""

    _registry_type_name = "data source"
