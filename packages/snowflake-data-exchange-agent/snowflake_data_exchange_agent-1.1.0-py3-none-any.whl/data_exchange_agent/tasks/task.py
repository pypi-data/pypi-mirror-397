"""Task class."""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Task:
    """
    Task class.

    This class represents a task that needs to be executed.
    """

    id: str
    engine: str
    database: str
    schema: str
    statement: str
    source_type: str
    upload_type: str
    upload_path: str

    def to_dict(self) -> dict:
        """
        Convert the Task to a dictionary.

        Returns:
            dict: The Task as a dictionary.

        """
        return asdict(self)
