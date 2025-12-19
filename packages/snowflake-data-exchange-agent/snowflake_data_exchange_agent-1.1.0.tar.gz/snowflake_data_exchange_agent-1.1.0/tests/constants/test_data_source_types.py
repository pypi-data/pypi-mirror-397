"""
Comprehensive test suite for the DataSourceType enum.

This test class validates the DataSourceType enumeration used for
categorizing different types of data sources.
"""

import unittest

from enum import Enum

from data_exchange_agent.constants.data_source_types import DataSourceType


class TestDataSourceType(unittest.TestCase):
    """
    Test suite for the DataSourceType enum.

    Validates that DataSourceType is correctly defined with all expected
    values and proper string representation.
    """

    def test_data_source_type_is_enum(self):
        """Test that DataSourceType is an Enum."""
        self.assertTrue(issubclass(DataSourceType, Enum))

    def test_data_source_type_is_str_enum(self):
        """Test that DataSourceType is a string enum."""
        self.assertTrue(issubclass(DataSourceType, str))

    def test_jdbc_type_exists(self):
        """Test that JDBC type exists."""
        self.assertTrue(hasattr(DataSourceType, "JDBC"))
        self.assertEqual(DataSourceType.JDBC.value, "jdbc")

    def test_str_representation(self):
        """Test string representation of enum values."""
        self.assertEqual(str(DataSourceType.JDBC), "jdbc")

    def test_enum_can_be_compared_to_string(self):
        """Test that enum values can be compared to strings."""
        self.assertEqual(DataSourceType.JDBC, "jdbc")

    def test_enum_in_string_context(self):
        """Test that enum works correctly in string contexts."""
        result = f"Data source type: {DataSourceType.JDBC}"
        self.assertEqual(result, "Data source type: jdbc")

    def test_enum_from_value(self):
        """Test creating enum from string value."""
        result = DataSourceType("jdbc")
        self.assertEqual(result, DataSourceType.JDBC)

    def test_enum_from_invalid_value_raises_error(self):
        """Test that invalid value raises ValueError."""
        with self.assertRaises(ValueError):
            DataSourceType("invalid")

    def test_all_enum_values_are_lowercase(self):
        """Test that all enum values are lowercase strings."""
        for data_source_type in DataSourceType:
            self.assertEqual(data_source_type.value, data_source_type.value.lower())

    def test_enum_is_hashable(self):
        """Test that enum values are hashable and can be used in sets/dicts."""
        enum_set = {DataSourceType.JDBC}
        self.assertIn(DataSourceType.JDBC, enum_set)

        enum_dict = {DataSourceType.JDBC: "test"}
        self.assertEqual(enum_dict[DataSourceType.JDBC], "test")

    def test_enum_iteration(self):
        """Test that enum can be iterated."""
        types = list(DataSourceType)
        self.assertIn(DataSourceType.JDBC, types)

    def test_enum_member_count(self):
        """Test the number of enum members."""
        # Currently only JDBC is defined
        types = list(DataSourceType)
        self.assertGreaterEqual(len(types), 1)

    def test_enum_equality(self):
        """Test enum equality comparisons."""
        self.assertEqual(DataSourceType.JDBC, DataSourceType.JDBC)
        self.assertEqual(DataSourceType.JDBC, "jdbc")

    def test_enum_identity(self):
        """Test enum identity (same object)."""
        a = DataSourceType.JDBC
        b = DataSourceType.JDBC
        self.assertIs(a, b)

    def test_enum_name_property(self):
        """Test enum name property."""
        self.assertEqual(DataSourceType.JDBC.name, "JDBC")

    def test_enum_value_property(self):
        """Test enum value property."""
        self.assertEqual(DataSourceType.JDBC.value, "jdbc")


if __name__ == "__main__":
    unittest.main()
