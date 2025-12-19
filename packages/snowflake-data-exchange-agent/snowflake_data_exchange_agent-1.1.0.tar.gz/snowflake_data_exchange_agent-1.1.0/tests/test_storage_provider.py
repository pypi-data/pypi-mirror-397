"""
Tests for StorageProvider class.

This module tests the StorageProvider class which manages different cloud storage
upload methods including Snowflake stage, Amazon S3, and Azure Blob Storage.
"""

import os
import unittest

from pathlib import Path
from unittest.mock import MagicMock, patch

from data_exchange_agent.providers.storageProvider import StorageProvider
from data_exchange_agent.uploaders.amazon_s3_uploader import AmazonS3Uploader
from data_exchange_agent.uploaders.azure_blob_uploader import AzureBlobUploader
from data_exchange_agent.uploaders.sf_stage_uploader import SFStageUploader


class TestStorageProvider(unittest.TestCase):
    """Test StorageProvider class functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_cloud_storage_toml = {
            "s3": {
                "bucket": "test-bucket",
                "region": "us-west-2",
            },
            "blob": {
                "container_name": "test-container",
                "connection_string": "test-connection-string",
            },
            "snowflake:stage": {
                "stage": "test-stage",
            },
        }

    def test_init_with_valid_upload_type_s3(self):
        """Test initialization with valid S3 upload type."""
        provider = StorageProvider("s3", self.mock_cloud_storage_toml)

        self.assertEqual(provider.upload_type, "s3")
        self.assertEqual(provider.cloud_storage_toml, self.mock_cloud_storage_toml)
        self.assertIn("s3", provider.upload_methods)
        self.assertEqual(provider.upload_methods["s3"], AmazonS3Uploader)

    def test_init_with_valid_upload_type_blob(self):
        """Test initialization with valid Azure Blob upload type."""
        provider = StorageProvider("blob", self.mock_cloud_storage_toml)

        self.assertEqual(provider.upload_type, "blob")
        self.assertEqual(provider.cloud_storage_toml, self.mock_cloud_storage_toml)
        self.assertIn("blob", provider.upload_methods)
        self.assertEqual(provider.upload_methods["blob"], AzureBlobUploader)

    def test_init_with_valid_upload_type_snowflake_stage(self):
        """Test initialization with valid Snowflake stage upload type."""
        provider = StorageProvider("snowflake:stage", self.mock_cloud_storage_toml)

        self.assertEqual(provider.upload_type, "snowflake:stage")
        self.assertEqual(provider.cloud_storage_toml, self.mock_cloud_storage_toml)
        self.assertIn("snowflake:stage", provider.upload_methods)
        self.assertEqual(provider.upload_methods["snowflake:stage"], SFStageUploader)

    def test_init_with_invalid_upload_type(self):
        """Test initialization with invalid upload type raises exception."""
        with self.assertRaises(Exception) as context:
            StorageProvider("invalid-type", self.mock_cloud_storage_toml)

        self.assertIn(
            "Cloud storage type invalid-type not found in upload methods",
            str(context.exception),
        )

    def test_upload_methods_dictionary(self):
        """Test that upload_methods contains all expected uploaders."""
        provider = StorageProvider("s3", self.mock_cloud_storage_toml)

        expected_methods = {
            "snowflake:stage": SFStageUploader,
            "s3": AmazonS3Uploader,
            "blob": AzureBlobUploader,
        }

        self.assertEqual(provider.upload_methods, expected_methods)

    @patch("data_exchange_agent.providers.storageProvider.delete_folder_file")
    @patch("os.listdir")
    def test_upload_files_with_parquet_files(self, mock_listdir, mock_delete):
        """Test upload_files with parquet files."""
        mock_listdir.return_value = ["file1.parquet", "file2.parquet.crc", "file3.txt"]

        with patch("data_exchange_agent.providers.storageProvider.AmazonS3Uploader") as mock_uploader_class:
            mock_uploader = MagicMock(spec=AmazonS3Uploader)
            mock_uploader.__enter__.return_value = mock_uploader
            mock_uploader.__exit__.return_value = False
            mock_uploader_class.return_value = mock_uploader

            provider = StorageProvider("s3", self.mock_cloud_storage_toml)
            provider.upload_files(Path("/test/source"), "/test/destination")

            # Should create uploader instances for parquet files only
            self.assertEqual(mock_uploader_class.call_count, 1)

            # Should upload parquet files only
            mock_uploader.upload_files.assert_called_once_with(
                str(Path("/test/source/file1.parquet")),
                str(Path("/test/source/file2.parquet.crc")),
                destination_path="/test/destination",
            )

            # Should delete the source folder
            mock_delete.assert_called_once_with(Path("/test/source"))

    @patch("data_exchange_agent.providers.storageProvider.delete_folder_file")
    @patch("os.listdir")
    def test_upload_files_with_no_parquet_files(self, mock_listdir, mock_delete):
        """Test upload_files with no parquet files."""
        mock_listdir.return_value = ["file1.txt", "file2.csv", "file3.json"]

        with patch("data_exchange_agent.providers.storageProvider.AmazonS3Uploader") as mock_uploader_class:
            provider = StorageProvider("s3", self.mock_cloud_storage_toml)
            provider.upload_files("/test/source", "/test/destination")

            # Should not create any uploader instances
            mock_uploader_class.assert_not_called()

            # Should still delete the source folder
            mock_delete.assert_called_once_with("/test/source")

    @patch("data_exchange_agent.providers.storageProvider.delete_folder_file")
    @patch("os.listdir")
    def test_upload_files_with_empty_directory(self, mock_listdir, mock_delete):
        """Test upload_files with empty directory."""
        mock_listdir.return_value = []

        with patch("data_exchange_agent.providers.storageProvider.AmazonS3Uploader") as mock_uploader_class:
            provider = StorageProvider("s3", self.mock_cloud_storage_toml)
            provider.upload_files("/test/source", "/test/destination")

            # Should not create any uploader instances
            mock_uploader_class.assert_not_called()

            # Should still delete the source folder
            mock_delete.assert_called_once_with("/test/source")

    @patch("data_exchange_agent.providers.storageProvider.delete_folder_file")
    @patch("os.listdir")
    def test_upload_files_with_blob_uploader(self, mock_listdir, mock_delete):
        """Test upload_files with Azure Blob uploader."""
        mock_listdir.return_value = ["data.parquet"]

        with patch("data_exchange_agent.providers.storageProvider.AzureBlobUploader") as mock_uploader_class:
            mock_uploader = MagicMock()
            mock_uploader.__enter__.return_value = mock_uploader
            mock_uploader.__exit__.return_value = False
            mock_uploader_class.return_value = mock_uploader

            provider = StorageProvider("blob", self.mock_cloud_storage_toml)
            provider.upload_files(Path("/test/source"), "/test/destination")

            mock_uploader_class.assert_called_once_with(self.mock_cloud_storage_toml)
            mock_uploader.upload_files.assert_called_once_with(
                str(Path("/test/source/data.parquet")),
                destination_path="/test/destination",
            )
            mock_delete.assert_called_once_with(Path("/test/source"))

    @patch("data_exchange_agent.providers.storageProvider.delete_folder_file")
    @patch("os.listdir")
    def test_upload_files_with_snowflake_stage_uploader(self, mock_listdir, mock_delete):
        """Test upload_files with Snowflake stage uploader."""
        mock_listdir.return_value = ["data.parquet"]

        with patch("data_exchange_agent.providers.storageProvider.SFStageUploader") as mock_uploader_class:
            mock_uploader = MagicMock()
            mock_uploader.__enter__.return_value = mock_uploader
            mock_uploader.__exit__.return_value = False
            mock_uploader_class.return_value = mock_uploader

            provider = StorageProvider("snowflake:stage", self.mock_cloud_storage_toml)
            provider.upload_files(Path("/test/source"), "/test/destination")

            mock_uploader_class.assert_called_once_with(self.mock_cloud_storage_toml)
            mock_uploader.upload_files.assert_called_once_with(
                str(Path("/test/source/data.parquet")),
                destination_path="/test/destination",
            )
            mock_delete.assert_called_once_with(Path("/test/source"))

    @patch("data_exchange_agent.providers.storageProvider.delete_folder_file")
    @patch("os.listdir")
    def test_upload_files_path_joining(self, mock_listdir, mock_delete):
        """Test that file paths are correctly joined."""
        mock_listdir.return_value = ["test.parquet"]

        with patch("data_exchange_agent.providers.storageProvider.AmazonS3Uploader") as mock_uploader_class:
            mock_uploader = MagicMock()
            mock_uploader.__enter__.return_value = mock_uploader
            mock_uploader.__exit__.return_value = False
            mock_uploader_class.return_value = mock_uploader

            provider = StorageProvider("s3", self.mock_cloud_storage_toml)
            provider.upload_files("/source/folder", destination_path="/dest/path")

            # Verify the correct path is passed to upload_file
            expected_file_path = os.path.join("/source/folder", "test.parquet")
            mock_uploader.upload_files.assert_called_once_with(expected_file_path, destination_path="/dest/path")

    @patch("data_exchange_agent.providers.storageProvider.delete_folder_file")
    @patch("os.listdir")
    def test_upload_files_multiple_parquet_files(self, mock_listdir, mock_delete):
        """Test upload_files with multiple parquet files creates separate uploader instances."""
        mock_listdir.return_value = [
            "file1.parquet",
            "file2.parquet",
            "file3.parquet.crc",
        ]

        with patch("data_exchange_agent.providers.storageProvider.AmazonS3Uploader") as mock_uploader_class:
            mock_uploader = MagicMock()
            mock_uploader.__enter__.return_value = mock_uploader
            mock_uploader.__exit__.return_value = False
            mock_uploader_class.return_value = mock_uploader

            provider = StorageProvider("s3", self.mock_cloud_storage_toml)
            provider.upload_files(Path("/test/source"), "/test/destination")

            # Should create 3 uploader instances (one for each parquet file)
            self.assertEqual(mock_uploader_class.call_count, 1)

            # Should upload all 3 files
            self.assertEqual(mock_uploader.upload_files.call_count, 1)

            mock_uploader.upload_files.assert_called_with(
                str(Path("/test/source/file1.parquet")),
                str(Path("/test/source/file2.parquet")),
                str(Path("/test/source/file3.parquet.crc")),
                destination_path="/test/destination",
            )


if __name__ == "__main__":
    unittest.main()
