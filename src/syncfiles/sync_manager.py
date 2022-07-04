"""Sync Manager

Author: Kevin Hodge
"""

from typing import List, Dict
from pathlib import Path
import shutil
from syncfiles.file_structure import FileStructure


class SyncManager:
    """Synchronizes files and folders between two FileStructures.

    Tasks:
        - get list of all entries from each file structure.
        - get list of all updated entries from each file structure.
        - loop through file structures and create a dictionary of visited entries
            - dictionary key should be path of entry, value should indicate if the entry is a file, if it exists in dir
            1, if it exists in dir 2, if it is updated in dir 1, and if it is updated in dir 2.
        - handle following cases for 2 directories:
            - if ENTRY IN dir 1, NOT IN dir 2, and UPDATED in dir 1:
                - COPY from dir 1 to dir 2
            - if ENTRY IN dir 1, NOT IN dir 2, and NOT UPDATED in dir 2:
                - DELETE from dir 1
            - if ENTRY NOT IN dir 1, IN dir 2, and UPDATED in dir 2:
                - COPY from dir 2 to dir 1
            - if ENTRY NOT IN dir 1, IN dir 2, and NOT UPDATED in dir 2:
                - DELETE from dir 2
            - if ENTRY IN dir 1 AND dir 2, and UPDATED in dir 1 and NOT UPDATED in dir 2:
                - DELETE from dir 2 AND COPY from dir 1 to dir 2
            - if ENTRY IN dir 1 AND dir 2, and NOT UPDATED in dir 1 and UPDATED in dir 2:
                - DELETE from dir 1 AND COPY from dir 2 to dir 1
            - if ENTRY IN dir 1 AND dir 2, and UPDATED in dir 1 and UPDATED in dir 2:
                - RENAME entry in dir 1 and dir 2 AND COPY from dir 2 to dir 1 AND COPY from dir 1 to dir 2

    """
    def __init__(self, fstructs: List[FileStructure]) -> None:
        assert len(fstructs) == 2
        self.visited_entries: Dict[str, int] = {}
        self.fstruct_dirs: List[str] = []
        self.fstructs_files_list: List[List[str]] = []
        self.fstructs_updated_list: List[List[str]] = []
        for fstruct in fstructs:
            self.fstruct_dirs.append(fstruct.directory_path)
            self.fstructs_files_list.append(fstruct.files_to_list())
            self.fstructs_updated_list.append(fstruct.get_updated_list())
        self.sync()

    def sync(self) -> None:
        for fstruct_list in self.fstructs_files_list:
            for fstruct_entry in fstruct_list:
                if fstruct_entry not in self.visited_entries:
                    self.perform_entry_action(fstruct_entry)
                    self.visited_entries[fstruct_entry] = 0

    def perform_entry_action(self, fstruct_entry: str) -> None:
        attributes: List[int] = self.get_entry_attributes(fstruct_entry)
        self.execute_entry_action(attributes, fstruct_entry)

    def get_entry_attributes(self, fstruct_entry: str) -> List[int]:
        attributes: List[int] = [0] * 5
        if Path(fstruct_entry).is_file():
            attributes[0] = 1
        if fstruct_entry in self.fstructs_files_list[0]:
            attributes[1] = 1
        if fstruct_entry in self.fstructs_files_list[1]:
            attributes[2] = 1
        if fstruct_entry in self.fstructs_updated_list[0]:
            attributes[3] = 1
        if fstruct_entry in self.fstructs_updated_list[1]:
            attributes[4] = 1
        return attributes

    def execute_entry_action(self, attributes: List[int], fstruct_entry: str) -> None:
        dir1: str = self.fstruct_dirs[0]
        dir2: str = self.fstruct_dirs[1]
        if self.check_attributes(attributes, [1, 1, 0, 1, -1]):
            self.copy_file_from_to(fstruct_entry, dir1, dir2)
        elif self.check_attributes(attributes, [1, 1, 0, 0, -1]):
            self.delete_file_from(fstruct_entry, dir1)
        elif self.check_attributes(attributes, [1, 0, 1, -1, 1]):
            self.copy_file_from_to(fstruct_entry, dir2, dir1)
        elif self.check_attributes(attributes, [1, 0, 1, -1, 0]):
            self.delete_file_from(fstruct_entry, dir2)

    def check_attributes(self, attributes: List[int], compare_list: List[int]) -> bool:
        for index, attr in enumerate(attributes):
            if compare_list[index] != -1 and compare_list[index] != attr:
                return False
        return True

    def copy_file_from_to(self, fstruct_entry: str, from_dir: str, to_dir: str) -> None:
        relative_path: str = self.remove_prefix(fstruct_entry, from_dir)
        dest: str = str(Path(to_dir) / relative_path)
        shutil.copyfile(fstruct_entry, dest)

    def remove_prefix(self, fstruct_entry: str, prefix: str) -> str:
        assert self.starts_with(fstruct_entry, prefix)
        return self.remove_leading_slash(fstruct_entry[len(prefix):])

    def starts_with(self, entry: str, prefix: str) -> bool:
        if entry[:len(prefix)] == prefix:
            return True
        else:
            raise ValueError("starts_with argument entry does not contain prefix.")

    def remove_leading_slash(self, path: str) -> str:
        if path[0] == "/" or path[0] == "\\":
            return path[1:]
        else:
            return path

    def delete_file_from(self, fstruct_entry: str, from_dir: str) -> None:
        assert self.starts_with(fstruct_entry, from_dir)
        Path(fstruct_entry).unlink()