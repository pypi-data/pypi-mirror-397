"""Abstract base class for all data source implementations."""

from abc import ABC, abstractmethod


class BaseDataSource(ABC):
    """
    Base data source implementation.

    This class provides a base implementation for all data source implementations.
    It defines the interface for exporting data from the data source.
    """

    @property
    @abstractmethod
    def statement(self) -> str:
        """The statement to execute."""
        pass

    @property
    @abstractmethod
    def results_folder_path(self) -> str:
        """The path to the results folder."""
        pass

    @property
    @abstractmethod
    def base_file_name(self) -> str:
        """The base file name."""
        pass

    @abstractmethod
    def export_data(self) -> bool:
        """
        Export data to the results folder from the data source.

        Returns:
            bool: True if the data was exported successfully, False otherwise

        """
        pass
