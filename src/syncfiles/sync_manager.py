"""Sync Manager

Author: Kevin Hodge
"""

from typing import List, Dict
from pathlib import Path
import shutil
from datetime import datetime, timezone
from syncfiles.file_structure import FileStructure


class SyncManager:
    """Synchronizes files and folders between two FileStructures.

    Tasks:
        - Handle updated folders.

    """
    def __init__(self, fstructs: List[FileStructure]) -> None:
        assert len(fstructs) == 2
        self.fstruct_dirs: List[str] = []
        self.fstructs_files_list: List[List[str]] = []
        self.fstructs_updated_list: List[List[str]] = []
        self.get_fstruct_info(fstructs)

    def get_fstruct_info(self, fstructs: List[FileStructure]) -> None:
        for fstruct in fstructs:
            self.fstruct_dirs.append(fstruct.directory_path)
            files_list: List[str] = self.remove_prefixes(fstruct.files_to_list(), self.fstruct_dirs[-1])
            self.fstructs_files_list.append(files_list)
            updated_list: List[str] = self.remove_prefixes(fstruct.get_updated_list(), self.fstruct_dirs[-1])
            self.fstructs_updated_list.append(updated_list)

    def remove_prefixes(self, files_list: List[str], prefix: str) -> List[str]:
        files_list_copy: List[str] = files_list[:]
        for index, entry in enumerate(files_list_copy):
            files_list_copy[index] = self.remove_prefix(entry, prefix)
        return files_list_copy

    def remove_prefix(self, fstruct_entry: str, prefix: str) -> str:
        assert self.starts_with(fstruct_entry, prefix)
        return self.remove_leading_slash(fstruct_entry[len(prefix):])

    def starts_with(self, entry: str, prefix: str) -> bool:
        if entry[:len(prefix)] == prefix:
            return True
        raise ValueError("starts_with argument entry does not contain prefix.")

    def remove_leading_slash(self, path: str) -> str:
        if path[0] == "/" or path[0] == "\\":
            return path[1:]
        else:
            return path

    def sync(self) -> None:
        visited_entries: Dict[str, int] = {}
        for fstruct_index, fstruct_list in enumerate(self.fstructs_files_list):
            for fstruct_entry in fstruct_list:
                if fstruct_entry not in visited_entries:
                    self.perform_entry_action(fstruct_entry, self.fstruct_dirs[fstruct_index])
                    visited_entries[fstruct_entry] = 0

    def perform_entry_action(self, fstruct_entry: str, parent_dir: str) -> None:
        attributes: List[int] = self.get_entry_attributes(fstruct_entry, parent_dir)
        self.execute_entry_action(attributes, fstruct_entry)

    def get_entry_attributes(self, fstruct_entry: str, parent_dir: str) -> List[int]:
        attributes: List[int] = [0] * 5
        entry_path: Path = Path(parent_dir) / fstruct_entry
        if Path(entry_path).is_file():
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
        elif self.check_attributes(attributes, [1, 1, 1, 1, 0]):
            self.delete_file_from(fstruct_entry, dir2)
            self.copy_file_from_to(fstruct_entry, dir1, dir2)
        elif self.check_attributes(attributes, [1, 1, 1, 0, 1]):
            self.delete_file_from(fstruct_entry, dir1)
            self.copy_file_from_to(fstruct_entry, dir2, dir1)
        elif self.check_attributes(attributes, [1, 1, 1, 1, 1]):
            new_name_dir1: str = self.rename_with_timestamp(fstruct_entry, dir1)
            self.copy_file_from_to(new_name_dir1, dir1, dir2)
            new_name_dir2: str = self.rename_with_timestamp(fstruct_entry, dir2)
            self.copy_file_from_to(new_name_dir2, dir2, dir1)

    def check_attributes(self, attributes: List[int], compare_list: List[int]) -> bool:
        for index, attr in enumerate(attributes):
            if compare_list[index] != -1 and compare_list[index] != attr:
                return False
        return True

    def copy_file_from_to(self, fstruct_entry: str, from_dir: str, to_dir: str) -> None:
        source: str = str(Path(from_dir) / fstruct_entry)
        dest: str = str(Path(to_dir) / fstruct_entry)
        shutil.copyfile(source, dest)

    def delete_file_from(self, fstruct_entry: str, from_dir: str) -> None:
        entry_path: Path = Path(from_dir) / fstruct_entry
        entry_path.unlink()

    def rename_with_timestamp(self, fstruct_entry: str, parent_dir: str) -> str:
        entry_path: Path = Path(parent_dir) / fstruct_entry
        new_path: Path = self.get_name_with_timestamp(entry_path)
        new_path = self.attempt_rename(new_path, entry_path)
        return (str(new_path.name))

    def get_name_with_timestamp(self, entry_path: Path) -> Path:
        entry_timestamp: datetime = datetime.fromtimestamp(entry_path.stat().st_mtime, tz=timezone.utc)
        timestamp_format: str = "%Y-%m-%d-%H-%M-%S-%f"
        timestamp: str = entry_timestamp.strftime(timestamp_format)
        new_name: str = f"{str(entry_path)} ({timestamp})"
        return entry_path.parent / new_name

    def attempt_rename(self, new_path: Path, entry_path: Path) -> Path:
        for attempt in range(100):
            if attempt == 0:
                path_name: Path = new_path
            try:
                entry_path.rename(path_name)
                return path_name
            except FileExistsError:
                path_name = Path(f"{path_name} {attempt}")
        raise FileExistsError(f"{str(entry_path)} has been copied 100 times.")
