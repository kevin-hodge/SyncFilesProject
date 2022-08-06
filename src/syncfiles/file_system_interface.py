"""Handle all file system interactions

Author: Kevin Hodge
"""

from abc import ABC, abstractmethod
from typing import Generator, Any
from pathlib import Path


class DBInterface(ABC):
    @abstractmethod
    def __init__(self, directory: str) -> None:
        """Create Path."""

    @abstractmethod
    def exists(self) -> bool:
        """Check entry existence."""

    @abstractmethod
    def iterdir(self) -> Any:
        """Generator returns DBInterface objects."""

    @abstractmethod
    def is_file(self) -> bool:
        """Indicates if object represents a file."""

    @abstractmethod
    def is_dir(self) -> bool:
        """Indicates if object represents a directory."""

    @abstractmethod
    def get_name(self) -> str:
        """Gets last entry in path."""

    @abstractmethod
    def get_mod_time(self) -> float:
        """Gets last modification time."""

    @abstractmethod
    def __repr__(self) -> str:
        """Returns string representation."""

    @abstractmethod
    def __truediv__(self, other) -> Any:
        """Returns path with other added to end."""


class FSInterface(DBInterface):
    def __init__(self, directory: str) -> None:
        self.__path: Path = Path(directory)

    def exists(self) -> bool:
        return self.__path.exists()

    def iterdir(self) -> Generator[DBInterface, None, None]:
        for entry in self.__path.iterdir():
            yield FSInterface(str(entry))

    def is_file(self) -> bool:
        return self.__path.is_file()

    def is_dir(self) -> bool:
        return self.__path.is_dir()

    def get_name(self) -> str:
        return self.__path.name

    def get_mod_time(self) -> float:
        return self.__path.stat().st_mtime

    def __repr__(self) -> str:
        return str(self.__path)

    def __truediv__(self, other: Any) -> Any:
        return FSInterface(str(self.__path / other))
