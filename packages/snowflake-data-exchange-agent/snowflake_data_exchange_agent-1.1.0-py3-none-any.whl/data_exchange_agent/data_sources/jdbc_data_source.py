"""JDBC data source implementation."""

import os

import jaydebeapi
import pyarrow as pa
import pyarrow.parquet as pq

from dependency_injector.wiring import Provide, inject

from data_exchange_agent.constants import container_keys
from data_exchange_agent.constants.paths import build_actual_results_folder_path
from data_exchange_agent.data_sources.base import BaseDataSource
from data_exchange_agent.data_sources.jdbc_jar_dict import JDBCJarDict
from data_exchange_agent.data_sources.sql_command_type import SQLCommandType
from data_exchange_agent.data_sources.sql_parser import get_read_only_sql_command_type
from data_exchange_agent.utils.sf_logger import SFLogger


class JDBCDataSource(BaseDataSource):
    """
    A JDBC data source implementation.

    This class provides a way to export data from a JDBC data source to a Parquet file.

    Attributes:
        statement (str): The SQL statement to execute
        results_folder_path (str): The path to the results folder
        driver_name (str): The name of the driver
        driver_class_name (str): The class name of the driver
        jar_path (str): The path to the jar file

    """

    @property
    def statement(self) -> str:
        """The statement to execute."""
        return self._statement

    @property
    def results_folder_path(self) -> str:
        """The path to the results folder."""
        return self._results_folder_path

    @property
    def base_file_name(self) -> str:
        """The base file name."""
        return self._base_file_name

    @inject
    def __init__(
        self,
        source_authentication_info: dict,
        statement: str,
        results_folder_path: str = None,
        base_file_name: str = "result",
        logger: SFLogger = Provide[container_keys.SF_LOGGER],
    ) -> None:
        """
        Initialize a new JDBCDataSource.

        Args:
            source_authentication_info (dict): The source authentication information
            statement (str): The SQL statement to execute
            results_folder_path (str): The path to the results folder
            base_file_name (str): The base file name
            logger (SFLogger): The logger instance

        """
        self.logger: SFLogger = logger
        jdbc_jar_dict: JDBCJarDict = JDBCJarDict()
        jdbc_jar_dict.download_all_jars()
        self._statement: str = statement
        self._results_folder_path: str = (
            build_actual_results_folder_path() if results_folder_path is None else results_folder_path
        )
        self._base_file_name: str = base_file_name
        self.driver_name: str = source_authentication_info.get("driver_name")
        self.driver_class_name: str = jdbc_jar_dict.get_jar_class_name(self.driver_name)
        self.jar_path: str = jdbc_jar_dict.get_jar_path(self.driver_name)
        self.__url: str = source_authentication_info.get("url")
        self.__driver_args: list[str] = [
            source_authentication_info.get("username"),
            source_authentication_info.get("password"),
        ]

    def export_data(self) -> bool:
        """
        Export data to a Parquet file.

        Returns:
            bool: True if the data was exported successfully, False otherwise

        Raises:
            Exception: If the SQL statement is not a read-only operation

        """
        # Check if the SQL statement is a read-only operation
        sql_command_type = get_read_only_sql_command_type(self.statement)
        if sql_command_type not in (
            SQLCommandType.SELECT,
            SQLCommandType.WITH,
            SQLCommandType.DESCRIBE,
            SQLCommandType.DESC,
            SQLCommandType.SHOW,
            SQLCommandType.EXPLAIN,
        ):
            raise Exception("The SQL statement is not a read-only operation.")

        conn: jaydebeapi.Connection = None
        try:
            # Create a connection to the database
            conn = jaydebeapi.connect(
                self.driver_class_name,
                self.__url,
                self.__driver_args,
                self.jar_path,
            )
        except Exception as e:
            self.logger.error(
                f"Error creating a connection to the database using the '{self.driver_name}' driver. Error: {e}"
            )
            raise e

        try:
            # Export data to Parquet file
            self._export_sql_results_to_parquet(
                conn,
                self.statement,
                parquet_folder_path=self.results_folder_path,
                batch_size=50000,
            )
        except Exception as e:
            self.logger.error(f"Error exporting data to a Parquet file. Error: {e}")
            raise e
        finally:
            if conn:
                conn.close()

        return True

    def _export_sql_results_to_parquet(
        self,
        conn: jaydebeapi.Connection,
        sql_query: str,
        parquet_folder_path: str = "data_chunks",
        batch_size: int = 50000,
    ) -> None:
        """
        Export SQL results to a Parquet file.

        Args:
            conn (jaydebeapi.Connection): The database connection
            sql_query (str): The SQL query to execute
            parquet_folder_path (str): The path to the output directory
            batch_size (int): The number of rows to fetch in each batch

        """
        cursor: jaydebeapi.Cursor = None
        try:
            # Execute SQL query
            cursor: jaydebeapi.Cursor = conn.cursor()
            self.logger.info(f"Start: Execution of query: {sql_query}...")
            cursor.execute(sql_query)
            self.logger.info(f"End: Execution of query: {sql_query}.")

            # Create output directory
            os.makedirs(parquet_folder_path, exist_ok=True)

            parquet_file = os.path.join(parquet_folder_path, f"{self.base_file_name}_001.parquet")
            self._write_chunks_to_single_parquet(cursor, parquet_file, batch_size=batch_size)
        finally:
            if cursor:
                cursor.close()

    def _write_chunks_to_single_parquet(self, cursor: jaydebeapi.Cursor, output_file: str, batch_size: int = 50000):
        """
        Write query results to a single Parquet file in chunks.

        Args:
            cursor (jaydebeapi.Cursor): The cursor to use for writing the results
            output_file (str): The path to the output file
            batch_size (int): The number of rows to fetch in each batch

        """
        self.logger.info(f"Start: Writing chunks to single parquet file {output_file}...")
        column_names = [desc[0] for desc in cursor.description]
        writer = None

        try:
            while True:
                rows = cursor.fetchmany(batch_size)
                if not rows:
                    break

                # Convert to PyArrow Table
                columns = list(zip(*rows, strict=False))
                arrays = [pa.array(col) for col in columns]
                table = pa.Table.from_arrays(arrays, names=column_names)

                if writer is None:
                    # Create writer with schema from first batch
                    writer = pq.ParquetWriter(output_file, table.schema)

                # Write chunk as a row group
                writer.write_table(table)

        finally:
            if writer:
                writer.close()
        self.logger.info(f"End: Writing chunks to single parquet file {output_file}.")
