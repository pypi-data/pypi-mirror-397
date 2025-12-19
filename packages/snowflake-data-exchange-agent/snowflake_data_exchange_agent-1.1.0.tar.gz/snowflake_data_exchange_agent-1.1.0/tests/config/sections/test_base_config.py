"""
Unit tests for BaseConfig class.

This module tests the BaseConfig metaclass and base functionality
that all configuration classes inherit.
"""

import unittest

from data_exchange_agent.config.sections.base_section_config import BaseSectionConfig


class TestValidatingMeta(unittest.TestCase):
    """Test suite for ValidatingMeta metaclass."""

    def test_creates_instances(self):
        """Test that ValidatingMeta allows instance creation."""

        class TestConfig(BaseSectionConfig):
            def _custom_validation(self):
                return None

        config = TestConfig()
        self.assertIsInstance(config, TestConfig)

    def test_calls_validation_on_instantiation(self):
        """Test that validation is called during instantiation."""
        validation_called = []

        class TestConfig(BaseSectionConfig):
            def _custom_validation(self):
                validation_called.append(True)
                return None

        TestConfig()
        self.assertTrue(validation_called)

    def test_raises_error_on_validation_failure(self):
        """Test that validation errors raise ValueError."""

        class TestConfig(BaseSectionConfig):
            def _custom_validation(self):
                return "Validation error"

        with self.assertRaises(ValueError) as context:
            TestConfig()

        self.assertIn("Validation error", str(context.exception))

    def test_validates_required_fields_before_custom(self):
        """Test that required fields are validated before custom validation."""

        class TestConfig(BaseSectionConfig):
            _required_fields = ["field1"]

            def _custom_validation(self):
                return "Custom validation"

        # Should fail on required field first
        with self.assertRaises(ValueError) as context:
            TestConfig()

        self.assertIn("field1 is required but not set", str(context.exception))


class TestBaseConfig(unittest.TestCase):
    """Test suite for BaseConfig class."""

    def test_is_abstract(self):
        """Test that BaseConfig cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            BaseSectionConfig()

    def test_requires_custom_validation_implementation(self):
        """Test that subclasses must implement _custom_validation."""

        class IncompleteConfig(BaseSectionConfig):
            pass

        # Should fail because _custom_validation is abstract
        with self.assertRaises(TypeError):
            IncompleteConfig()

    def test_has_required_fields_attribute(self):
        """Test that BaseConfig has _required_fields attribute."""
        self.assertTrue(hasattr(BaseSectionConfig, "_required_fields"))
        self.assertIsInstance(BaseSectionConfig._required_fields, list)

    def test_default_required_fields_is_empty(self):
        """Test that default _required_fields is empty list."""
        self.assertEqual(BaseSectionConfig._required_fields, [])

    def test_getitem_with_valid_attribute(self):
        """Test __getitem__ with a valid attribute."""

        class TestConfig(BaseSectionConfig):
            def __init__(self):
                super().__init__()
                self.test_attr = "test_value"

            def _custom_validation(self):
                return None

        config = TestConfig()
        self.assertEqual(config["test_attr"], "test_value")

    def test_getitem_with_missing_attribute_raises_keyerror(self):
        """Test __getitem__ raises KeyError for missing attributes."""

        class TestConfig(BaseSectionConfig):
            def _custom_validation(self):
                return None

        config = TestConfig()

        with self.assertRaises(KeyError) as context:
            _ = config["nonexistent"]

        self.assertIn("'nonexistent' not found in configuration", str(context.exception))

    def test_getitem_with_private_attribute_raises_keyerror(self):
        """Test __getitem__ raises KeyError for private attributes."""

        class TestConfig(BaseSectionConfig):
            def __init__(self):
                super().__init__()
                self._private = "private_value"

            def _custom_validation(self):
                return None

        config = TestConfig()

        with self.assertRaises(KeyError) as context:
            _ = config["_private"]

        self.assertIn("Private attributes cannot be accessed via indexing", str(context.exception))


class TestBaseConfigRequiredFields(unittest.TestCase):
    """Test suite for required fields validation in BaseConfig."""

    def test_required_field_not_set_raises_error(self):
        """Test that missing required field raises ValueError."""

        class TestConfig(BaseSectionConfig):
            _required_fields = ["required_field"]

            def _custom_validation(self):
                return None

        with self.assertRaises(ValueError) as context:
            TestConfig()

        self.assertIn("required_field is required but not set", str(context.exception))

    def test_required_field_with_value_passes(self):
        """Test that required field with value passes validation."""

        class TestConfig(BaseSectionConfig):
            _required_fields = ["required_field"]

            def __init__(self):
                super().__init__()
                self.required_field = "value"

            def _custom_validation(self):
                return None

        config = TestConfig()
        self.assertEqual(config.required_field, "value")

    def test_required_field_none_raises_error(self):
        """Test that required field with None raises ValueError."""

        class TestConfig(BaseSectionConfig):
            _required_fields = ["required_field"]

            def __init__(self):
                super().__init__()
                self.required_field = None

            def _custom_validation(self):
                return None

        with self.assertRaises(ValueError) as context:
            TestConfig()

        self.assertIn("required_field value cannot be None", str(context.exception))

    def test_required_field_empty_string_raises_error(self):
        """Test that required field with empty string raises ValueError."""

        class TestConfig(BaseSectionConfig):
            _required_fields = ["required_field"]

            def __init__(self):
                super().__init__()
                self.required_field = ""

            def _custom_validation(self):
                return None

        with self.assertRaises(ValueError) as context:
            TestConfig()

        self.assertIn("required_field value cannot be empty", str(context.exception))

    def test_required_field_whitespace_only_raises_error(self):
        """Test that required field with only whitespace raises ValueError."""

        class TestConfig(BaseSectionConfig):
            _required_fields = ["required_field"]

            def __init__(self):
                super().__init__()
                self.required_field = "   "

            def _custom_validation(self):
                return None

        with self.assertRaises(ValueError) as context:
            TestConfig()

        self.assertIn("required_field value cannot contain only whitespace", str(context.exception))

    def test_required_field_integer_passes(self):
        """Test that required field with integer value passes."""

        class TestConfig(BaseSectionConfig):
            _required_fields = ["required_field"]

            def __init__(self):
                super().__init__()
                self.required_field = 42

            def _custom_validation(self):
                return None

        config = TestConfig()
        self.assertEqual(config.required_field, 42)

    def test_multiple_required_fields(self):
        """Test multiple required fields."""

        class TestConfig(BaseSectionConfig):
            _required_fields = ["field1", "field2", "field3"]

            def __init__(self):
                super().__init__()
                self.field1 = "value1"
                self.field2 = "value2"
                self.field3 = "value3"

            def _custom_validation(self):
                return None

        config = TestConfig()
        self.assertEqual(config.field1, "value1")
        self.assertEqual(config.field2, "value2")
        self.assertEqual(config.field3, "value3")

    def test_multiple_required_fields_first_missing_reported(self):
        """Test that first missing required field is reported."""

        class TestConfig(BaseSectionConfig):
            _required_fields = ["field1", "field2", "field3"]

            def __init__(self):
                super().__init__()

            def _custom_validation(self):
                return None

        with self.assertRaises(ValueError) as context:
            TestConfig()

        # Should report field1 as it's checked first
        self.assertIn("field1 is required but not set", str(context.exception))


class TestBaseConfigCustomValidation(unittest.TestCase):
    """Test suite for custom validation in BaseConfig."""

    def test_custom_validation_called(self):
        """Test that _custom_validation is called."""
        validation_called = []

        class TestConfig(BaseSectionConfig):
            def _custom_validation(self):
                validation_called.append(True)
                return None

        TestConfig()
        self.assertTrue(validation_called)

    def test_custom_validation_error_raises_valueerror(self):
        """Test that custom validation error raises ValueError."""

        class TestConfig(BaseSectionConfig):
            def _custom_validation(self):
                return "Custom error message"

        with self.assertRaises(ValueError) as context:
            TestConfig()

        self.assertIn("Custom error message", str(context.exception))

    def test_custom_validation_none_allows_instantiation(self):
        """Test that returning None from custom validation allows instantiation."""

        class TestConfig(BaseSectionConfig):
            def _custom_validation(self):
                return None

        config = TestConfig()
        self.assertIsNotNone(config)

    def test_custom_validation_can_access_attributes(self):
        """Test that custom validation can access instance attributes."""

        class TestConfig(BaseSectionConfig):
            def __init__(self):
                super().__init__()
                self.value = 10

            def _custom_validation(self):
                if self.value > 5:
                    return "Value too large"
                return None

        with self.assertRaises(ValueError) as context:
            TestConfig()

        self.assertIn("Value too large", str(context.exception))


class TestBaseConfigInheritance(unittest.TestCase):
    """Test suite for BaseConfig inheritance behavior."""

    def test_subclass_can_extend_required_fields(self):
        """Test that subclasses can extend _required_fields."""

        class ParentConfig(BaseSectionConfig):
            _required_fields = ["parent_field"]

            def __init__(self):
                super().__init__()
                self.parent_field = "value"

            def _custom_validation(self):
                return None

        class ChildConfig(ParentConfig):
            _required_fields = ParentConfig._required_fields + ["child_field"]

            def __init__(self):
                super().__init__()
                self.child_field = "child_value"

        config = ChildConfig()
        self.assertEqual(config.parent_field, "value")
        self.assertEqual(config.child_field, "child_value")

    def test_subclass_inherits_getitem(self):
        """Test that subclasses inherit __getitem__ functionality."""

        class ParentConfig(BaseSectionConfig):
            def _custom_validation(self):
                return None

        class ChildConfig(ParentConfig):
            def __init__(self):
                super().__init__()
                self.test_attr = "test"

        config = ChildConfig()
        self.assertEqual(config["test_attr"], "test")


if __name__ == "__main__":
    unittest.main()
