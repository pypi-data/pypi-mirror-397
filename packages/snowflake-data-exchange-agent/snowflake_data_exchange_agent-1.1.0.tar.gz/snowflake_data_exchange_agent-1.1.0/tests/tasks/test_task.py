"""
Tests for the Task class.

This module tests the Task dataclass to ensure it maintains
its expected attributes and behavior.
"""

import unittest
from dataclasses import FrozenInstanceError

from data_exchange_agent.tasks.task import Task


class TestTask(unittest.TestCase):
    """Test Task dataclass."""

    def setUp(self):
        """Set up test fixtures."""
        self.valid_task_data = {
            "id": "task-001",
            "engine": "snowflake",
            "database": "test_db",
            "schema": "public",
            "statement": "SELECT * FROM test_table",
            "source_type": "snowflake_stored_procedure",
            "upload_type": "s3",
            "upload_path": "s3://bucket/path/to/data",
        }

    def test_task_creation(self):
        """Test that a Task can be created with valid data."""
        task = Task(**self.valid_task_data)

        self.assertEqual(task.id, "task-001")
        self.assertEqual(task.engine, "snowflake")
        self.assertEqual(task.database, "test_db")
        self.assertEqual(task.schema, "public")
        self.assertEqual(task.statement, "SELECT * FROM test_table")
        self.assertEqual(task.source_type, "snowflake_stored_procedure")
        self.assertEqual(task.upload_type, "s3")
        self.assertEqual(task.upload_path, "s3://bucket/path/to/data")

    def test_task_frozen(self):
        """Test that Task is frozen and cannot be modified after creation."""
        task = Task(**self.valid_task_data)

        with self.assertRaises(FrozenInstanceError):
            task.id = "new-id"

        with self.assertRaises(FrozenInstanceError):
            task.engine = "postgres"

        with self.assertRaises(FrozenInstanceError):
            task.statement = "SELECT 1"

    def test_task_to_dict(self):
        """Test that to_dict returns a dictionary with all task attributes."""
        task = Task(**self.valid_task_data)
        task_dict = task.to_dict()

        self.assertIsInstance(task_dict, dict)
        self.assertEqual(task_dict, self.valid_task_data)

    def test_task_to_dict_contains_all_fields(self):
        """Test that to_dict contains all expected fields."""
        task = Task(**self.valid_task_data)
        task_dict = task.to_dict()

        expected_keys = {"id", "engine", "database", "schema", "statement", "source_type", "upload_type", "upload_path"}
        self.assertEqual(set(task_dict.keys()), expected_keys)

    def test_task_equality(self):
        """Test that two tasks with same data are equal."""
        task1 = Task(**self.valid_task_data)
        task2 = Task(**self.valid_task_data)

        self.assertEqual(task1, task2)

    def test_task_inequality(self):
        """Test that two tasks with different data are not equal."""
        task1 = Task(**self.valid_task_data)

        different_data = self.valid_task_data.copy()
        different_data["id"] = "task-002"
        task2 = Task(**different_data)

        self.assertNotEqual(task1, task2)

    def test_task_hash(self):
        """Test that Task is hashable (due to frozen=True)."""
        task = Task(**self.valid_task_data)

        # Should not raise an error
        hash_value = hash(task)
        self.assertIsInstance(hash_value, int)

    def test_task_can_be_used_in_set(self):
        """Test that Task can be added to a set."""
        task1 = Task(**self.valid_task_data)
        task2 = Task(**self.valid_task_data)

        different_data = self.valid_task_data.copy()
        different_data["id"] = "task-002"
        task3 = Task(**different_data)

        task_set = {task1, task2, task3}
        # task1 and task2 are identical, so set should only have 2 items
        self.assertEqual(len(task_set), 2)

    def test_task_can_be_used_as_dict_key(self):
        """Test that Task can be used as a dictionary key."""
        task = Task(**self.valid_task_data)

        task_dict = {task: "some_value"}
        self.assertEqual(task_dict[task], "some_value")

    def test_task_with_empty_strings(self):
        """Test Task creation with empty string values."""
        empty_data = {
            "id": "",
            "engine": "",
            "database": "",
            "schema": "",
            "statement": "",
            "source_type": "",
            "upload_type": "",
            "upload_path": "",
        }
        task = Task(**empty_data)

        self.assertEqual(task.id, "")
        self.assertEqual(task.engine, "")
        self.assertEqual(task.statement, "")

    def test_task_with_special_characters(self):
        """Test Task with special characters in fields."""
        special_data = self.valid_task_data.copy()
        special_data["statement"] = "SELECT * FROM table WHERE name = 'O''Brien' AND age > 30"
        special_data["upload_path"] = "s3://bucket/path/with spaces/and-dashes_underscores"

        task = Task(**special_data)

        self.assertEqual(task.statement, "SELECT * FROM table WHERE name = 'O''Brien' AND age > 30")
        self.assertEqual(task.upload_path, "s3://bucket/path/with spaces/and-dashes_underscores")

    def test_task_with_long_statement(self):
        """Test Task with a long SQL statement."""
        long_statement = """
        WITH cte AS (
            SELECT
                id,
                name,
                department,
                salary,
                ROW_NUMBER() OVER (PARTITION BY department ORDER BY salary DESC) as rn
            FROM employees
            WHERE status = 'active'
        )
        SELECT
            department,
            AVG(salary) as avg_salary,
            COUNT(*) as employee_count
        FROM cte
        WHERE rn <= 10
        GROUP BY department
        ORDER BY avg_salary DESC
        """

        task_data = self.valid_task_data.copy()
        task_data["statement"] = long_statement

        task = Task(**task_data)
        self.assertEqual(task.statement, long_statement)

    def test_task_repr(self):
        """Test Task string representation."""
        task = Task(**self.valid_task_data)
        task_repr = repr(task)

        self.assertIn("Task", task_repr)
        self.assertIn("task-001", task_repr)

    def test_task_different_engines(self):
        """Test Task with different database engines."""
        engines = ["snowflake", "postgres", "mysql", "sqlserver", "oracle"]

        for engine in engines:
            task_data = self.valid_task_data.copy()
            task_data["engine"] = engine
            task_data["id"] = f"task-{engine}"

            task = Task(**task_data)
            self.assertEqual(task.engine, engine)

    def test_task_different_upload_types(self):
        """Test Task with different upload types."""
        upload_configs = [
            ("s3", "s3://bucket/path"),
            ("azure", "azure://container/path"),
            ("gcs", "gs://bucket/path"),
            ("local", "/local/path/to/file"),
            ("snowflake_stage", "@my_stage/path"),
        ]

        for upload_type, upload_path in upload_configs:
            task_data = self.valid_task_data.copy()
            task_data["upload_type"] = upload_type
            task_data["upload_path"] = upload_path
            task_data["id"] = f"task-{upload_type}"

            task = Task(**task_data)
            self.assertEqual(task.upload_type, upload_type)
            self.assertEqual(task.upload_path, upload_path)

    def test_task_missing_required_field_raises_error(self):
        """Test that creating a Task without required fields raises TypeError."""
        incomplete_data = {
            "id": "task-001",
            "engine": "snowflake",
            # Missing other required fields
        }

        with self.assertRaises(TypeError):
            Task(**incomplete_data)

    def test_task_with_extra_fields_raises_error(self):
        """Test that creating a Task with extra fields raises TypeError."""
        extra_data = self.valid_task_data.copy()
        extra_data["extra_field"] = "extra_value"

        with self.assertRaises(TypeError):
            Task(**extra_data)

    def test_task_to_dict_immutability(self):
        """Test that modifying the dict from to_dict doesn't affect the Task."""
        task = Task(**self.valid_task_data)
        task_dict = task.to_dict()

        # Modify the returned dictionary
        task_dict["id"] = "modified-id"

        # Original task should remain unchanged
        self.assertEqual(task.id, "task-001")

    def test_multiple_tasks_independence(self):
        """Test that multiple Task instances are independent."""
        task1 = Task(**self.valid_task_data)

        task2_data = self.valid_task_data.copy()
        task2_data["id"] = "task-002"
        task2_data["statement"] = "SELECT 1"
        task2 = Task(**task2_data)

        # Verify both tasks maintain their own data
        self.assertEqual(task1.id, "task-001")
        self.assertEqual(task2.id, "task-002")
        self.assertEqual(task1.statement, "SELECT * FROM test_table")
        self.assertEqual(task2.statement, "SELECT 1")

    def test_task_with_unicode_characters(self):
        """Test Task with unicode characters."""
        unicode_data = self.valid_task_data.copy()
        unicode_data["statement"] = "SELECT * FROM users WHERE name = '日本語' OR city = 'São Paulo'"
        unicode_data["database"] = "测试数据库"

        task = Task(**unicode_data)

        self.assertEqual(task.statement, "SELECT * FROM users WHERE name = '日本語' OR city = 'São Paulo'")
        self.assertEqual(task.database, "测试数据库")

    def test_task_field_types(self):
        """Test that all Task fields accept string values."""
        task = Task(**self.valid_task_data)

        self.assertIsInstance(task.id, str)
        self.assertIsInstance(task.engine, str)
        self.assertIsInstance(task.database, str)
        self.assertIsInstance(task.schema, str)
        self.assertIsInstance(task.statement, str)
        self.assertIsInstance(task.source_type, str)
        self.assertIsInstance(task.upload_type, str)
        self.assertIsInstance(task.upload_path, str)


if __name__ == "__main__":
    unittest.main()
