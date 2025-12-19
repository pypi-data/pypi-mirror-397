"""
Configuration-related constants.

Note: Double underscores (__) in constant names represent dots (.) in the actual
configuration path. For example, APPLICATION__WORKERS represents "application.workers".

Note: Short keys (without section prefix) are for within-section access only.
For cross-section access, use the full path constants (e.g., APPLICATION__WORKERS).
"""

SELECTED_TASK_SOURCE = "selected_task_source"

APPLICATION = "application"
WORKERS = "workers"
DEBUG_MODE = "debug_mode"
TASK_FETCH_INTERVAL = "task_fetch_interval"
AGENT_ID = "agent_id"
APPLICATION__WORKERS = f"{APPLICATION}.{WORKERS}"
APPLICATION__DEBUG_MODE = f"{APPLICATION}.{DEBUG_MODE}"
APPLICATION__TASK_FETCH_INTERVAL = f"{APPLICATION}.{TASK_FETCH_INTERVAL}"
APPLICATION__AGENT_ID = f"{APPLICATION}.{AGENT_ID}"

SERVER = "server"
HOST = "host"
PORT = "port"
SERVER__HOST = f"{SERVER}.{HOST}"
SERVER__PORT = f"{SERVER}.{PORT}"

TASK_SOURCE = "task_source"

CONNECTIONS = "connections"
SOURCE = "source"
TARGET = "target"
CONNECTIONS__SOURCE = f"{CONNECTIONS}.{SOURCE}"
CONNECTIONS__TARGET = f"{CONNECTIONS}.{TARGET}"
