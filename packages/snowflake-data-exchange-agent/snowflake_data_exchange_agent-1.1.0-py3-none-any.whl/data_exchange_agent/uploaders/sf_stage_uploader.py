"""Snowflake stage uploader implementation."""

from data_exchange_agent.data_sources.sf_connection import SnowflakeDataSource
from data_exchange_agent.interfaces.uploader import UploaderInterface
from dependency_injector.wiring import Provide, inject


class SFStageUploader(UploaderInterface):
    """
    Uploader class for staging files to Snowflake.

    This class implements the UploaderInterface to handle uploading files
    to a Snowflake stage location.
    """

    PUT_STATUS_KEY = "status"
    UPLOADED_STATUS = "UPLOADED"

    @inject
    def configure(
        self,
        snowflake_datasource: SnowflakeDataSource = Provide["snowflake_datasource"],
    ) -> None:
        """
        Configure the Snowflake stage uploader.

        Args:
            snowflake_datasource: Snowflake data source (injected dependency)

        """
        self.snowflake_datasource = snowflake_datasource

    def connect(self) -> None:
        """
        Connect to Snowflake.

        Establishes a fresh connection to Snowflake. Safe to call multiple times
        as it will reuse existing valid connections or create new ones as needed.

        """
        if self.snowflake_datasource and not self.snowflake_datasource.is_closed():
            # Connection exists and is open, no need to reconnect
            return

        self.snowflake_datasource.create_connection()

    def disconnect(self) -> None:
        """
        Disconnect from Snowflake.

        Closes the active Snowflake connection if one exists and is open.
        Sets the connection to None after closing to ensure proper cleanup.

        """
        if self.snowflake_datasource and not self.snowflake_datasource.is_closed():
            self.snowflake_datasource.close_connection()
            self.snowflake_datasource = None

    def upload_file(self, source_file: str, destination_path: str) -> None:
        """
        Upload a file to a Snowflake stage.

        Args:
            source_file (str): Local file path to upload
            destination_path (str): Snowflake stage path to upload to

        Returns:
            None

        """
        with self.snowflake_datasource as snowflake_datasource:
            self._upload_file(snowflake_datasource, source_file, destination_path)

    def upload_files(self, *source_files: str, destination_path: str) -> None:
        """
        Upload a list of files to a Snowflake stage.

        Args:
            *source_files: Variable length argument list of source file paths to upload.
            destination_path: The destination path to upload the files to.

        Returns:
            None

        """
        with self.snowflake_datasource as snowflake_datasource:
            for source_file in source_files:
                self._upload_file(snowflake_datasource, source_file, destination_path)

    def _upload_file(
        self,
        snowflake_datasource: SnowflakeDataSource,
        source_file: str,
        destination_path: str,
    ) -> None:
        """
        Upload a file to a Snowflake stage.

        Args:
            snowflake_datasource: Snowflake data source
            source_file (str): Local file path to upload
            destination_path (str): Snowflake stage path to upload to

        Returns:
            None

        """
        put_command = f"PUT file://{source_file} {destination_path} OVERWRITE = TRUE"

        try:
            raw_result = next(
                iter(snowflake_datasource.execute_statement(put_command)), None
            )
        except Exception as e:
            raise Exception(
                f"Failed to upload file {source_file} to {destination_path}. Error: {e}"
            ) from e
        if (
            raw_result is None
            or raw_result.get(self.PUT_STATUS_KEY, None) != self.UPLOADED_STATUS
        ):
            raise Exception(
                f"Failed to upload file {source_file} to {destination_path}."
            )
