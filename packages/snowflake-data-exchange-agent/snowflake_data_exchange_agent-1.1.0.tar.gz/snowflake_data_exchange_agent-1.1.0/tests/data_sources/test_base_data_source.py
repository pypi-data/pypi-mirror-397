"""
Comprehensive test suite for the BaseDataSource abstract class.

This test class validates the abstract interface contract and ensures proper
behavior of implementations.
"""

import unittest

from abc import ABC

from data_exchange_agent.data_sources.base import BaseDataSource


class TestBaseDataSource(unittest.TestCase):
    """
    Test suite for the BaseDataSource abstract class.

    Validates that BaseDataSource is correctly defined as an abstract class
    with the expected abstract properties and methods.
    """

    def test_base_data_source_is_abstract(self):
        """Test that BaseDataSource is an abstract class."""
        self.assertTrue(issubclass(BaseDataSource, ABC))

    def test_cannot_instantiate_base_data_source(self):
        """Test that BaseDataSource cannot be instantiated directly."""
        with self.assertRaises(TypeError) as context:
            BaseDataSource()

        error_message = str(context.exception)
        self.assertIn("abstract", error_message.lower())

    def test_has_statement_abstract_property(self):
        """Test that BaseDataSource has statement abstract property."""
        # Check that statement is defined as an abstract property
        self.assertTrue(hasattr(BaseDataSource, "statement"))
        self.assertTrue(
            isinstance(getattr(type(BaseDataSource), "statement", None), property)
            or hasattr(BaseDataSource.statement, "fget")
        )

    def test_has_results_folder_path_abstract_property(self):
        """Test that BaseDataSource has results_folder_path abstract property."""
        self.assertTrue(hasattr(BaseDataSource, "results_folder_path"))
        self.assertTrue(
            isinstance(getattr(type(BaseDataSource), "results_folder_path", None), property)
            or hasattr(BaseDataSource.results_folder_path, "fget")
        )

    def test_has_base_file_name_abstract_property(self):
        """Test that BaseDataSource has base_file_name abstract property."""
        self.assertTrue(hasattr(BaseDataSource, "base_file_name"))
        self.assertTrue(
            isinstance(getattr(type(BaseDataSource), "base_file_name", None), property)
            or hasattr(BaseDataSource.base_file_name, "fget")
        )

    def test_has_export_data_abstract_method(self):
        """Test that BaseDataSource has export_data abstract method."""
        self.assertTrue(hasattr(BaseDataSource, "export_data"))
        self.assertTrue(callable(getattr(BaseDataSource, "export_data", None)))


class ConcreteDataSource(BaseDataSource):
    """A concrete implementation of BaseDataSource for testing."""

    def __init__(self, statement: str, results_folder_path: str, base_file_name: str):
        self._statement = statement
        self._results_folder_path = results_folder_path
        self._base_file_name = base_file_name

    @property
    def statement(self) -> str:
        return self._statement

    @property
    def results_folder_path(self) -> str:
        return self._results_folder_path

    @property
    def base_file_name(self) -> str:
        return self._base_file_name

    def export_data(self) -> bool:
        return True


class TestConcreteDataSourceImplementation(unittest.TestCase):
    """
    Test suite for concrete implementations of BaseDataSource.

    Validates that a concrete implementation of BaseDataSource works correctly.
    """

    def test_concrete_implementation_can_be_instantiated(self):
        """Test that a concrete implementation can be instantiated."""
        data_source = ConcreteDataSource(
            statement="SELECT * FROM users",
            results_folder_path="/tmp/results",
            base_file_name="result",
        )
        self.assertIsInstance(data_source, BaseDataSource)

    def test_statement_property_returns_correct_value(self):
        """Test that statement property returns the correct value."""
        statement = "SELECT * FROM users"
        data_source = ConcreteDataSource(
            statement=statement,
            results_folder_path="/tmp/results",
            base_file_name="result",
        )
        self.assertEqual(data_source.statement, statement)

    def test_results_folder_path_property_returns_correct_value(self):
        """Test that results_folder_path property returns the correct value."""
        results_folder_path = "/tmp/custom/path"
        data_source = ConcreteDataSource(
            statement="SELECT * FROM users",
            results_folder_path=results_folder_path,
            base_file_name="result",
        )
        self.assertEqual(data_source.results_folder_path, results_folder_path)

    def test_base_file_name_property_returns_correct_value(self):
        """Test that base_file_name property returns the correct value."""
        base_file_name = "custom_result"
        data_source = ConcreteDataSource(
            statement="SELECT * FROM users",
            results_folder_path="/tmp/results",
            base_file_name=base_file_name,
        )
        self.assertEqual(data_source.base_file_name, base_file_name)

    def test_export_data_method_returns_bool(self):
        """Test that export_data method returns a boolean."""
        data_source = ConcreteDataSource(
            statement="SELECT * FROM users",
            results_folder_path="/tmp/results",
            base_file_name="result",
        )
        result = data_source.export_data()
        self.assertIsInstance(result, bool)
        self.assertTrue(result)


class IncompleteDataSource(BaseDataSource):
    """An incomplete implementation missing some abstract methods for testing."""

    @property
    def statement(self) -> str:
        return "SELECT * FROM users"

    @property
    def results_folder_path(self) -> str:
        return "/tmp/results"

    # Missing base_file_name property and export_data method


class TestIncompleteImplementation(unittest.TestCase):
    """
    Test suite for incomplete implementations of BaseDataSource.

    Validates that incomplete implementations cannot be instantiated.
    """

    def test_incomplete_implementation_cannot_be_instantiated(self):
        """Test that incomplete implementation cannot be instantiated."""
        with self.assertRaises(TypeError) as context:
            IncompleteDataSource()

        error_message = str(context.exception)
        # Should mention that abstract methods are not implemented
        self.assertIn("abstract", error_message.lower())


if __name__ == "__main__":
    unittest.main()
