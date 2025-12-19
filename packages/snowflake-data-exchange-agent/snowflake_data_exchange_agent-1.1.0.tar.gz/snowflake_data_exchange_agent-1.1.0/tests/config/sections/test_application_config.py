"""
Unit tests for ApplicationConfig class.

This module tests the ApplicationConfig which manages application-level
settings like workers, task fetch interval, and debug mode.
"""

import unittest

from data_exchange_agent.config.sections.application import ApplicationConfig


class TestApplicationConfig(unittest.TestCase):
    """Test suite for ApplicationConfig class."""

    def test_initialization_with_all_none(self):
        """Test ApplicationConfig initialization with all None values."""
        config = ApplicationConfig()

        self.assertIsNone(config.workers)
        self.assertIsNone(config.task_fetch_interval)
        self.assertIsNone(config.debug_mode)

    def test_initialization_with_values(self):
        """Test ApplicationConfig initialization with actual values."""
        config = ApplicationConfig(workers=8, task_fetch_interval=60, debug_mode=True)

        self.assertEqual(config.workers, 8)
        self.assertEqual(config.task_fetch_interval, 60)
        self.assertTrue(config.debug_mode)

    def test_initialization_with_partial_values(self):
        """Test ApplicationConfig initialization with some None values."""
        config = ApplicationConfig(workers=4, task_fetch_interval=None, debug_mode=False)

        self.assertEqual(config.workers, 4)
        self.assertIsNone(config.task_fetch_interval)
        self.assertFalse(config.debug_mode)

    def test_valid_workers_value(self):
        """Test ApplicationConfig with valid workers value."""
        config = ApplicationConfig(workers=10)

        self.assertEqual(config.workers, 10)

    def test_workers_minimum_boundary(self):
        """Test workers at minimum valid boundary (1)."""
        config = ApplicationConfig(workers=1)

        self.assertEqual(config.workers, 1)

    def test_workers_maximum_boundary(self):
        """Test workers at maximum valid boundary (100)."""
        config = ApplicationConfig(workers=100)

        self.assertEqual(config.workers, 100)

    def test_workers_below_minimum_raises_error(self):
        """Test that workers below 1 raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(workers=0)

        self.assertIn("Workers must be at least 1", str(context.exception))

    def test_workers_negative_raises_error(self):
        """Test that negative workers raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(workers=-5)

        self.assertIn("Workers must be at least 1", str(context.exception))

    def test_workers_above_maximum_raises_error(self):
        """Test that workers above 100 raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(workers=101)

        self.assertIn("Workers cannot exceed 100", str(context.exception))

    def test_workers_invalid_type_raises_error(self):
        """Test that non-integer workers raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(workers="not_an_int")

        self.assertIn("Workers must be an integer", str(context.exception))

    def test_workers_float_raises_error(self):
        """Test that float workers raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(workers=5.5)

        self.assertIn("Workers must be an integer", str(context.exception))

    def test_valid_task_fetch_interval(self):
        """Test ApplicationConfig with valid task_fetch_interval."""
        config = ApplicationConfig(task_fetch_interval=120)

        self.assertEqual(config.task_fetch_interval, 120)

    def test_task_fetch_interval_minimum_boundary(self):
        """Test task_fetch_interval at minimum valid boundary (1)."""
        config = ApplicationConfig(task_fetch_interval=1)

        self.assertEqual(config.task_fetch_interval, 1)

    def test_task_fetch_interval_below_minimum_raises_error(self):
        """Test that task_fetch_interval below 1 raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(task_fetch_interval=0)

        self.assertIn("Task fetch interval must be at least 1 second", str(context.exception))

    def test_task_fetch_interval_negative_raises_error(self):
        """Test that negative task_fetch_interval raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(task_fetch_interval=-10)

        self.assertIn("Task fetch interval must be at least 1 second", str(context.exception))

    def test_task_fetch_interval_invalid_type_raises_error(self):
        """Test that non-integer task_fetch_interval raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(task_fetch_interval="not_an_int")

        self.assertIn("Task fetch interval must be an integer", str(context.exception))

    def test_task_fetch_interval_float_raises_error(self):
        """Test that float task_fetch_interval raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(task_fetch_interval=30.5)

        self.assertIn("Task fetch interval must be an integer", str(context.exception))

    def test_valid_debug_mode_true(self):
        """Test ApplicationConfig with debug_mode=True."""
        config = ApplicationConfig(debug_mode=True)

        self.assertTrue(config.debug_mode)

    def test_valid_debug_mode_false(self):
        """Test ApplicationConfig with debug_mode=False."""
        config = ApplicationConfig(debug_mode=False)

        self.assertFalse(config.debug_mode)

    def test_debug_mode_invalid_type_raises_error(self):
        """Test that non-boolean debug_mode raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(debug_mode="not_a_bool")

        self.assertIn("Debug mode must be a boolean", str(context.exception))

    def test_debug_mode_integer_raises_error(self):
        """Test that integer debug_mode raises ValueError."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(debug_mode=1)

        self.assertIn("Debug mode must be a boolean", str(context.exception))

    def test_multiple_valid_parameters(self):
        """Test ApplicationConfig with multiple valid parameters."""
        config = ApplicationConfig(workers=25, task_fetch_interval=90, debug_mode=True)

        self.assertEqual(config.workers, 25)
        self.assertEqual(config.task_fetch_interval, 90)
        self.assertTrue(config.debug_mode)

    def test_repr(self):
        """Test string representation of ApplicationConfig."""
        config = ApplicationConfig(workers=4, task_fetch_interval=120, debug_mode=False)

        repr_str = repr(config)

        self.assertIn("ApplicationConfig", repr_str)
        self.assertIn("workers=4", repr_str)
        self.assertIn("task_fetch_interval=120", repr_str)
        self.assertIn("debug_mode=False", repr_str)

    def test_repr_with_none_values(self):
        """Test repr with None values."""
        config = ApplicationConfig(workers=None, task_fetch_interval=None, debug_mode=None)

        repr_str = repr(config)

        self.assertIn("ApplicationConfig", repr_str)
        self.assertIn("workers=None", repr_str)
        self.assertIn("task_fetch_interval=None", repr_str)
        self.assertIn("debug_mode=None", repr_str)

    def test_getitem_access(self):
        """Test dictionary-style access via __getitem__."""
        config = ApplicationConfig(workers=8, task_fetch_interval=60, debug_mode=True)

        self.assertEqual(config["workers"], 8)
        self.assertEqual(config["task_fetch_interval"], 60)
        self.assertTrue(config["debug_mode"])

    def test_getitem_with_missing_attribute(self):
        """Test __getitem__ raises KeyError for missing attributes."""
        config = ApplicationConfig()

        with self.assertRaises(KeyError):
            _ = config["nonexistent"]

    def test_inherits_from_base_section_config(self):
        """Test that ApplicationConfig inherits from BaseConfig."""
        from data_exchange_agent.config.sections.base_section_config import BaseSectionConfig

        config = ApplicationConfig()

        self.assertIsInstance(config, BaseSectionConfig)

    def test_none_values_pass_validation(self):
        """Test that None values don't trigger validation errors."""
        # This should not raise any errors
        config = ApplicationConfig(workers=None, task_fetch_interval=None, debug_mode=None)

        self.assertIsNone(config.workers)
        self.assertIsNone(config.task_fetch_interval)
        self.assertIsNone(config.debug_mode)


class TestApplicationConfigEdgeCases(unittest.TestCase):
    """Test edge cases for ApplicationConfig."""

    def test_workers_with_zero(self):
        """Test workers value of exactly 0."""
        with self.assertRaises(ValueError) as context:
            ApplicationConfig(workers=0)

        self.assertIn("Workers must be at least 1", str(context.exception))

    def test_workers_large_valid_value(self):
        """Test workers with large valid value."""
        config = ApplicationConfig(workers=99)

        self.assertEqual(config.workers, 99)

    def test_task_fetch_interval_large_value(self):
        """Test task_fetch_interval with very large value."""
        config = ApplicationConfig(task_fetch_interval=86400)  # 24 hours

        self.assertEqual(config.task_fetch_interval, 86400)

    def test_multiple_invalid_parameters(self):
        """Test that first invalid parameter is reported."""
        with self.assertRaises(ValueError):
            ApplicationConfig(workers=-1, task_fetch_interval=-1, debug_mode="invalid")

    def test_attribute_modification_after_creation(self):
        """Test that attributes can be modified after creation."""
        config = ApplicationConfig(workers=4)

        # Modify the attribute (note: this bypasses validation)
        config.workers = 8

        self.assertEqual(config.workers, 8)


if __name__ == "__main__":
    unittest.main()
