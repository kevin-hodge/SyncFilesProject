"""Handle all file system interactions

Author: Kevin Hodge
"""

from abc import ABC, abstractmethod, abstractclassmethod
from typing import Generator, Any
from pathlib import Path
import shutil


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

    @classmethod
    @abstractclassmethod
    def cwd(cls) -> Any:
        """Gets current working directory."""

    @abstractmethod
    def open(self, mode: str = "r") -> Any:
        """Context manager for Database object."""

    @abstractmethod
    def unlink(self) -> None:
        """Deletes file."""

    @abstractmethod
    def get_parent(self) -> Any:
        """Gets path without last entry (name)."""

    @abstractmethod
    def rename(self, new_path: Any) -> Any:
        """Renames and returns Database object."""

    @classmethod
    @abstractclassmethod
    def copyfile(cls, old_path: str, new_path: str) -> None:
        """Copies file at old_path to new_path."""


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

    def __truediv__(self, other: Any) -> DBInterface:
        return FSInterface(str(self.__path / other))

    @classmethod
    def cwd(cls) -> DBInterface:
        return cls(str(Path.cwd()))

    def open(self, mode: str = "r") -> Any:
        return self.__path.open(mode)

    def unlink(self) -> None:
        self.__path.unlink()

    def get_parent(self) -> DBInterface:
        return FSInterface(str(self.__path.parent))

    def rename(self, new_path: Any) -> DBInterface:
        return FSInterface(str(self.__path.rename(new_path.__path)))

    @classmethod
    def copyfile(cls, old_path: str, new_path: str) -> None:
        shutil.copyfile(old_path, new_path)
