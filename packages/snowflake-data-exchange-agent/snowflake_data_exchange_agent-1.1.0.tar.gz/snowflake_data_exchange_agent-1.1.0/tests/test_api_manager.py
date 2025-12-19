import unittest

from unittest.mock import ANY, MagicMock, Mock, patch

import requests

from data_exchange_agent import custom_exceptions
from data_exchange_agent.task_sources.api import APITaskSourceAdapter


class TestAPIManager(unittest.TestCase):
    """
    Comprehensive test suite for the APIManager class.

    This test class validates the functionality of the APIManager, including:
    - API key loading from TOML configuration files
    - Task retrieval from remote API endpoints
    - Task status updates via API calls
    - Error handling for network failures and invalid responses
    - Proper authentication header management

    The tests use mocking to isolate the APIManager from external dependencies
    and ensure reliable, fast test execution.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates a mock APIManager instance with a test API key to avoid
        file system dependencies during testing. This ensures consistent
        test behavior regardless of the presence of configuration files.
        """
        # Note: api_manager is created in individual tests with proper mocking
        mock_task_source = Mock()
        mock_task_source.key = "test_api_key"
        self.mock_program_config = MagicMock()
        self.mock_program_config.__getitem__.return_value = mock_task_source

    def test_api_key_success(self):
        """
        Test successful API key loading from TOML configuration file.

        Verifies that when a valid TOML configuration file exists with the
        proper structure (api_configuration.key), the APIManager correctly
        loads and stores the API key for subsequent use in API requests.
        """
        mock_task_source = Mock()
        mock_task_source.key = "test_api_key_from_file"

        # Make ConfigManager["task_source"] return the mock object
        mock_program_config = MagicMock()
        mock_program_config.__getitem__.return_value = mock_task_source

        api_manager = APITaskSourceAdapter(program_config=mock_program_config)

        self.assertEqual(api_manager.api_key, "test_api_key_from_file")

        mock_program_config.__getitem__.assert_called_with("task_source")

    def test_api_key_not_found(self):
        """Test API key loading when api_configuration section is missing."""
        mock_program_config = MagicMock()
        mock_program_config.__getitem__.side_effect = KeyError("task_source.key")

        with self.assertRaises(custom_exceptions.ConfigurationError) as context:
            _ = APITaskSourceAdapter(program_config=mock_program_config)

        self.assertIn("API task source configuration is missing or incomplete", str(context.exception))

    def test_api_key_missing_key_field(self):
        """Test API key loading when key field is missing."""
        mock_program_config = MagicMock()
        mock_program_config.__getitem__.side_effect = AttributeError("task_source.key")

        with self.assertRaises(custom_exceptions.ConfigurationError) as context:
            _ = APITaskSourceAdapter(program_config=mock_program_config)

        self.assertIn("API task source configuration is missing or incomplete", str(context.exception))

    @patch("data_exchange_agent.task_sources.api.requests.get")
    def test_get_tasks_success(self, mock_get):
        """
        Test successful task retrieval from the remote API endpoint.

        Validates that the APIManager correctly:
        - Makes GET requests to the tasks endpoint with proper parameters
        - Includes authentication headers with the API key
        - Returns the JSON response data when the request succeeds
        - Handles the expected response format with task lists

        Args:
            mock_get: Mock for the requests.get function
            mock_program_config: Mock for the program config

        """
        api_manager = APITaskSourceAdapter(program_config=self.mock_program_config)

        # Mock the HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tasks": [{"id": 1, "name": "task1"}, {"id": 2, "name": "task2"}]}
        mock_get.return_value = mock_response

        # Call the method under test
        result = api_manager.get_tasks()

        # Verify the request was made correctly
        mock_get.assert_called_once_with(
            "http://127.0.0.1:5000/tasks?agent_id=1&group_id=1",
            headers={"Authorization": "Bearer test_api_key"},
            timeout=ANY,
        )

        # Verify the result
        expected_result = [{"id": 1, "name": "task1"}, {"id": 2, "name": "task2"}]
        self.assertEqual(result, expected_result)

    @patch("data_exchange_agent.task_sources.api.requests.get")
    def test_get_tasks_failure(self, mock_get):
        """Test task retrieval failure from API."""
        api_manager = APITaskSourceAdapter(program_config=self.mock_program_config)

        # Mock failed HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404")
        mock_get.return_value = mock_response

        with self.assertRaises(Exception) as context:
            api_manager.get_tasks()

        self.assertEqual(str(context.exception), "404")

    @patch("data_exchange_agent.task_sources.api.requests.put")
    def test_complete_task_success(self, mock_put):
        """Test successful task update."""
        api_manager = APITaskSourceAdapter(program_config=self.mock_program_config)

        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"message": "Task updated successfully"}
        mock_put.return_value = mock_response

        api_manager.complete_task("123")

        mock_put.assert_called_once_with(
            "http://127.0.0.1:5000/tasks/123/complete",
            headers={"Authorization": "Bearer test_api_key"},
            timeout=ANY,
        )

    @patch("data_exchange_agent.task_sources.api.requests.put")
    def test_complete_task_failure(self, mock_put):
        """Test task update failure."""
        api_manager = APITaskSourceAdapter(program_config=self.mock_program_config)

        # Mock failed HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
        mock_put.return_value = mock_response

        with self.assertRaises(requests.exceptions.HTTPError) as context:
            api_manager.complete_task("123")

        self.assertEqual(str(context.exception), "500")

    @patch("data_exchange_agent.task_sources.api.requests.get")
    def test_get_tasks_with_network_error(self, mock_get):
        """Test get_tasks with network error."""
        api_manager = APITaskSourceAdapter(program_config=self.mock_program_config)

        # Mock network error
        mock_get.side_effect = requests.RequestException("Network error")

        with self.assertRaises(requests.RequestException):
            api_manager.get_tasks()

    @patch("data_exchange_agent.task_sources.api.requests.put")
    def test_complete_task_with_network_error(self, mock_put):
        """Test complete_task with network error."""
        api_manager = APITaskSourceAdapter(program_config=self.mock_program_config)

        # Mock network error
        mock_put.side_effect = requests.RequestException("Network error")

        with self.assertRaises(requests.RequestException) as context:
            api_manager.complete_task("123")

        self.assertEqual(str(context.exception), "Network error")

    def test_api_manager_initialization(self):
        """Test APIManager initialization."""
        mock_program_config = MagicMock()
        api_manager = APITaskSourceAdapter(program_config=mock_program_config)

        mock_program_config.__getitem__.assert_called_once_with("task_source")

        self.assertTrue(hasattr(api_manager, "api_key"))


if __name__ == "__main__":
    unittest.main()
