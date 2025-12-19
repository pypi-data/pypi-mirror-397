"""
Data source implementations for various database systems.

This package contains modules for connecting to and extracting data from
different database engines, handling JDBC connections, and data export utilities.
"""

from data_exchange_agent.constants.data_source_types import DataSourceType
from data_exchange_agent.data_sources.base import BaseDataSource
from data_exchange_agent.data_sources.data_source_registry import DataSourceRegistry
from data_exchange_agent.data_sources.jdbc_data_source import JDBCDataSource


# Register data source types
DataSourceRegistry.register(DataSourceType.JDBC, JDBCDataSource)

__all__ = ["BaseDataSource", "DataSourceRegistry", "JDBCDataSource"]
