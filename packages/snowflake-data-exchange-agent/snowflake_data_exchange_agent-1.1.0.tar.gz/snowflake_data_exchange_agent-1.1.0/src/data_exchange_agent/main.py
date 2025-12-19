"""
Main entry point for the data exchange agent application.

This module provides the main function and command-line interface for starting
the data exchange agent server with configurable parameters.
"""

import argparse

from data_exchange_agent.constants.config_defaults import (
    DEFAULT__SERVER__HOST,
    DEFAULT__SERVER__PORT,
)
from data_exchange_agent.container import create_container
from data_exchange_agent.servers.flask_app import FlaskApp
from data_exchange_agent.utils.decorators import print_error_with_message


@print_error_with_message(error_message="Error starting the Data Exchange Agent application.")
def main() -> None:
    """
    Start the data exchange agent application.

    Starts a Flask web server that manages data processing tasks. The server provides endpoints to:
    - Start and stop task processing
    - Get status of tasks being handled
    - Add new tasks to be processed

    Command line arguments:
        -w, --workers: Number of worker threads
        -i, --interval: Interval in seconds to fetch tasks from the API
        --host: Host to bind to
        --port: Port to bind to
        --debug: Enable debug mode

    Returns:
        None

    """
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description="Data Exchange Agent Flask Server")
    parser.add_argument("-w", "--workers", type=int, help="Number of worker threads")
    parser.add_argument(
        "-i",
        "--interval",
        type=int,
        help="Interval in seconds to fetch tasks from the API",
    )
    parser.add_argument("--host", default=DEFAULT__SERVER__HOST, help="Host to bind to")
    parser.add_argument("-p", "--port", type=int, default=DEFAULT__SERVER__PORT, help="Port to bind to")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    # Initialize the container
    _ = create_container(args)

    # Create and start the Flask app
    flask_app = FlaskApp()
    flask_app.create_app()
    flask_app.start_server()


if __name__ == "__main__":
    main()
