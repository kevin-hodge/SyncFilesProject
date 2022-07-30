"""Entry

Author: Kevin Hodge
"""

from typing import Dict, List, Optional, KeysView


class entry:
    """Contains info on a file/folder.

    Attributes:
        mod_time (float): last modification time of entry.
        updated (bool): describes the modification status of entry.
    """
    def __init__(self):
        self.__updated: bool = False

    def set_updated(self, updated: bool = True) -> None:
        self.__updated = updated

    def get_updated(self) -> int:
        return self.__updated


class file_entry(entry):
    def __init__(self, mod_time: float = -1.0) -> None:
        self.__mod_time: float = mod_time
        super().__init__()

    def get_mod_time(self) -> float:
        return self.__mod_time


class dir_entry(entry):
    def __init__(self) -> None:
        self.__dict: Dict[str, entry] = dict()
        super().__init__()

    def __repr__(self, offset: int = 0) -> str:
        print_str: str = ""
        indent: str = 3 * offset * ' '
        for entry_name in self.get_keys():
            fstruct_entry: entry = self.get_entry(entry_name)
            print_str += self.print_entry(indent, entry_name, fstruct_entry)
            if isinstance(fstruct_entry, dir_entry):
                print_str += fstruct_entry.__repr__(offset + 1)
        return print_str

    def print_entry(self, indent: str, entry_name: str, entry: entry) -> str:
        entry_repr: str = f"{indent}{entry_name}"
        if isinstance(entry, file_entry):
            entry_repr += f": {entry.get_mod_time()}"
        if entry.get_updated() > 0:
            entry_repr += " X"
        return entry_repr + "\n"

    def add_entry(self, key: str, entry: entry) -> None:
        self.__dict[key] = entry

    def get_entry(self, requested_entry: str) -> entry:
        return self.__dict[requested_entry]

    def get_entry_path(self, keys: List[str]) -> Optional[entry]:
        if keys[0] in self.__dict:
            file_or_dir_entry: entry = self.__dict[keys[0]]
            if len(keys) == 1:
                return file_or_dir_entry
            elif len(keys) > 1 and isinstance(file_or_dir_entry, dir_entry):
                directory: dir_entry = file_or_dir_entry
                return directory.get_entry_path(keys[1:])
            else:
                raise KeyError("get_entry_path argument keys was not valid")
        else:
            return None

    def get_keys(self) -> KeysView[str]:
        return self.__dict.keys()
