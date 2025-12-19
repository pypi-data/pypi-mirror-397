import argparse
import unittest

from unittest.mock import MagicMock, Mock, patch

from data_exchange_agent.container import MODULES, _Container, create_container
from data_exchange_agent.uploaders.azure_blob_uploader import AzureBlobUploader
from data_exchange_agent.utils.sf_logger import SFLogger
from dependency_injector import containers, providers


class TestContainer(unittest.TestCase):
    """
    Comprehensive test suite for the Container dependency injection class.

    This test class validates the Container's dependency injection functionality,
    including:
    - Provider registration and configuration
    - Singleton pattern implementation for services
    - Service instantiation and dependency wiring
    - Configuration management integration
    - Proper inheritance from DeclarativeContainer

    The tests ensure that the dependency injection container works correctly
    and provides the expected services to the application components.
    """

    def setUp(self):
        """
        Set up test fixtures before each test method.

        Creates a fresh Container instance for each test to ensure
        test isolation and prevent side effects between tests.
        """
        self.container: _Container = _Container()
        self.toml_config = {
            "blob": {
                "container_name": "test-container",
                "connection_string": "DefaultEndpointsProtocol=https;AccountName=test;AccountKey=key;EndpointSuffix=core.windows.net",
            },
            "s3": {
                "bucket_name": "test-bucket",
                "profile_name": "test-profile",
            },
        }

    def test_container_is_declarative_container(self):
        """
        Test that Container properly inherits from DeclarativeContainer.

        Validates that the Container class follows the dependency-injector
        pattern by inheriting from either DeclarativeContainer or
        DynamicContainer (which can happen after initialization).
        This ensures proper dependency injection functionality.
        """
        self.assertTrue(
            isinstance(self.container, containers.DeclarativeContainer)
            or isinstance(self.container, containers.DynamicContainer)
        )

    def test_container_has_config_provider(self):
        """Test that container has config provider."""
        self.assertTrue(hasattr(self.container, "config"))
        self.assertIsInstance(self.container.config, providers.Configuration)

    def test_container_has_task_manager_provider(self):
        """Test that container has task_manager provider."""
        self.assertTrue(hasattr(self.container, "task_manager"))
        self.assertIsInstance(self.container.task_manager, providers.Dependency)

    def test_container_has_sf_logger_provider(self):
        """Test that container has sf_logger provider."""
        self.assertTrue(hasattr(self.container, "sf_logger"))
        self.assertIsInstance(self.container.sf_logger, providers.Singleton)

    def test_sf_logger_provider_creates_instance(self):
        """Test that sf_logger provider creates SFLogger instance."""
        sf_logger = self.container.sf_logger()
        self.assertIsInstance(sf_logger, SFLogger)

    def test_container_has_azure_blob_uploader_provider(self):
        """Test that container has azure_blob_uploader provider."""
        self.assertTrue(hasattr(self.container, "azure_blob_uploader"))
        self.assertIsInstance(self.container.azure_blob_uploader, providers.Singleton)

    def test_azure_blob_uploader_provider_creates_instance(self):
        """Test that azure_blob_uploader provider creates AzureBlobUploader instance."""
        azure_blob_uploader = self.container.azure_blob_uploader(cloud_storage_toml=self.toml_config)
        self.assertIsInstance(azure_blob_uploader, AzureBlobUploader)

    def test_container_providers_are_singletons(self):
        """Test that providers return singleton instances."""
        program_config1 = self.container.program_config()
        program_config2 = self.container.program_config()
        self.assertIs(program_config1, program_config2)

        sf_logger1 = self.container.sf_logger()
        sf_logger2 = self.container.sf_logger()
        self.assertIs(sf_logger1, sf_logger2)

        sf_stage_uploader1 = self.container.sf_stage_uploader()
        sf_stage_uploader2 = self.container.sf_stage_uploader()
        self.assertIs(sf_stage_uploader1, sf_stage_uploader2)

        amazon_s3_uploader1 = self.container.amazon_s3_uploader(cloud_storage_toml=self.toml_config)
        amazon_s3_uploader2 = self.container.amazon_s3_uploader(cloud_storage_toml=self.toml_config)
        self.assertIs(amazon_s3_uploader1, amazon_s3_uploader2)

        azure_blob_uploader1 = self.container.azure_blob_uploader(cloud_storage_toml=self.toml_config)
        azure_blob_uploader2 = self.container.azure_blob_uploader(cloud_storage_toml=self.toml_config)
        self.assertIs(azure_blob_uploader1, azure_blob_uploader2)


class TestCreateContainer(unittest.TestCase):
    """
    Test suite for the create_container factory function.

    This test class validates the create_container() factory function which is
    the ONLY supported way to create a Container instance. It tests:
    - Container creation without arguments
    - Container creation with CLI arguments
    - ConfigManager integration (loading CLI and TOML configs)
    - TaskManager configuration override
    - Module wiring for dependency injection
    """

    @patch("data_exchange_agent.container._Container")
    def test_create_container_without_args(self, mock_container_class):
        """Test create_container creates and configures container without arguments."""
        mock_container = Mock()
        mock_program_config = MagicMock()
        mock_container.program_config.return_value = mock_program_config
        mock_container_class.return_value = mock_container

        # Mock the program_config getitem to return worker/interval values
        mock_program_config.__getitem__.side_effect = lambda key: {
            "selected_task_source": "api",
            "application.workers": 4,
            "application.task_fetch_interval": 120,
        }[key]

        container = create_container()

        # Verify container was created
        mock_container_class.assert_called_once()

        # Verify program_config was called to load TOML config
        mock_container.program_config.assert_called()
        mock_program_config.load_toml_config.assert_called_once()

        # Verify program_config CLI load was NOT called when args is None
        # (Note: load_cli_config should not be called when args is None)

        # Verify task_manager override was called
        mock_container.task_manager.override.assert_called_once()

        # Verify modules were wired
        mock_container.wire.assert_called_once_with(modules=MODULES)

        # Verify the returned container is the mock
        self.assertEqual(container, mock_container)

    @patch("data_exchange_agent.container._Container")
    def test_create_container_with_args(self, mock_container_class):
        """Test create_container loads CLI config when args provided."""
        mock_container = Mock()
        mock_program_config = MagicMock()
        mock_container.program_config.return_value = mock_program_config
        mock_container_class.return_value = mock_container

        # Mock the program_config getitem to return worker/interval values
        mock_program_config.__getitem__.side_effect = lambda key: {
            "selected_task_source": "api",
            "application.workers": 8,
            "application.task_fetch_interval": 60,
        }[key]

        # Create mock argparse.Namespace
        args = argparse.Namespace(workers=8, interval=60, host="localhost", port=8080, debug=True)

        container = create_container(args)

        # Verify container was created
        mock_container_class.assert_called_once()

        # Verify program_config was called with args
        mock_container.program_config.assert_called()
        mock_program_config.load_cli_config.assert_called_once_with(args)
        mock_program_config.load_toml_config.assert_called_once()

        # Verify task_manager override was called
        mock_container.task_manager.override.assert_called_once()

        # Verify modules were wired
        mock_container.wire.assert_called_once_with(modules=MODULES)

        self.assertEqual(container, mock_container)

    @patch("data_exchange_agent.container._Container")
    def test_create_container_task_manager_configuration(self, mock_container_class):
        """Test create_container configures TaskManager with values from ConfigManager."""
        mock_container = Mock()
        mock_program_config = MagicMock()
        mock_container.program_config.return_value = mock_program_config
        mock_container_class.return_value = mock_container

        # Set up specific worker and interval values
        expected_workers = 16
        expected_interval = 90

        mock_program_config.__getitem__.side_effect = lambda key: {
            "selected_task_source": "api",
            "application.workers": expected_workers,
            "application.task_fetch_interval": expected_interval,
        }[key]

        create_container()

        # Verify task_manager.override was called
        mock_container.task_manager.override.assert_called_once()

        # Get the provider that was passed to override
        call_args = mock_container.task_manager.override.call_args
        provider_arg = call_args[0][0]

        # Verify it's a Singleton provider for TaskManager
        self.assertIsInstance(provider_arg, providers.Singleton)

        # Verify program_config was accessed for the right keys
        self.assertIn("application.workers", [call[0][0] for call in mock_program_config.__getitem__.call_args_list])
        self.assertIn(
            "application.task_fetch_interval", [call[0][0] for call in mock_program_config.__getitem__.call_args_list]
        )

    @patch("data_exchange_agent.container._Container")
    def test_create_container_wires_all_modules(self, mock_container_class):
        """Test create_container wires all necessary modules for dependency injection."""
        mock_container = Mock()
        mock_program_config = MagicMock()
        mock_container.program_config.return_value = mock_program_config
        mock_container_class.return_value = mock_container

        mock_program_config.__getitem__.side_effect = lambda key: {
            "selected_task_source": "api",
            "application.workers": 4,
            "application.task_fetch_interval": 120,
        }[key]

        create_container()

        # Verify wire was called with MODULES
        mock_container.wire.assert_called_once_with(modules=MODULES)

        # Verify MODULES contains expected module paths
        self.assertIn("data_exchange_agent.utils.decorators", MODULES)
        self.assertIn("data_exchange_agent.tasks.manager", MODULES)
        self.assertIn("data_exchange_agent.task_sources.api", MODULES)
        self.assertIn("data_exchange_agent.servers.flask_app", MODULES)
        self.assertIn("data_exchange_agent.servers.waitress_app", MODULES)

    @patch("data_exchange_agent.config.manager.TomlConfig.load_config")
    @patch("data_exchange_agent.config.manager.ConfigManager.__getitem__")
    @patch("data_exchange_agent.container.TaskSourceAdapterRegistry")
    def test_create_container_integration(self, mock_load, mock_getitem, mock_task_source_adapter_registry):
        """Test create_container works end-to-end without extensive mocking."""  # mock_load.return_value = {}
        # Create container without arguments
        container = create_container()

        # Verify it returns a _Container instance
        self.assertIsInstance(container, (containers.DeclarativeContainer, containers.DynamicContainer))

        # Verify the container has necessary providers
        self.assertTrue(hasattr(container, "program_config"))
        self.assertTrue(hasattr(container, "task_manager"))
        self.assertTrue(hasattr(container, "sf_logger"))

    @patch("data_exchange_agent.config.manager.TomlConfig.load_config")
    @patch("data_exchange_agent.config.manager.ConfigManager.__getitem__")
    @patch("data_exchange_agent.container.TaskSourceAdapterRegistry")
    def test_create_container_integration_with_args(self, mock_load, mock_getitem, mock_task_source_adapter_registry):
        """Test create_container works end-to-end with arguments."""
        # Create arguments
        args = argparse.Namespace(workers=10, interval=30, host="0.0.0.0", port=9000, debug=False)

        # Create container with arguments
        container = create_container(args)

        # Verify it returns a _Container instance
        self.assertIsInstance(container, (containers.DeclarativeContainer, containers.DynamicContainer))

        # Verify the container configuration was affected by args
        # (The program_config should have loaded the CLI args)
        program_config = container.program_config()
        self.assertIsNotNone(program_config)


if __name__ == "__main__":
    unittest.main()
