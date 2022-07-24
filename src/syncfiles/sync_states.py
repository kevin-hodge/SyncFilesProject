"""Sync States

Author: Kevin Hodge
"""

from typing import List
from syncfiles.file_structure import FileStructure
from syncfiles.sync_gui import SyncGUI
from syncfiles.config_manager import ConfigManager
from syncfiles.sync_state_machine import SyncState, End


class StateData:
    directories: List[FileStructure] = []
    exit_request: bool = False
    sync_required: bool = False
    verbose: bool = False

    def __init__(self, config: ConfigManager, gui: SyncGUI, verbose: bool = False) -> None:
        self.config = config
        self.gui = gui
        self.verbose = verbose

    def get_directories(self) -> List[FileStructure]:
        return self.directories

    def set_directories(self, directories: List[FileStructure]) -> None:
        self.directories = directories

    def get_exit_request(self) -> bool:
        return self.exit_request

    def set_exit_request(self, exit_request: bool = True) -> None:
        self.exit_request = exit_request

    def get_sync_required(self) -> bool:
        return self.sync_required

    def set_sync_required(self, sync_required: bool = True) -> None:
        self.sync_required = sync_required


class DataState(SyncState):
    def __init__(self, state_data: StateData) -> None:
        self.state_data: StateData = state_data


class Initial(DataState):
    def run(self) -> None:
        sync_directories: List[str] = self.get_sync_directories()
        self.initialize_file_structures(sync_directories)

    def get_next(self) -> SyncState:
        return Wait(self.state_data)

    def get_sync_directories(self) -> List[str]:
        sync_directories: List[str] = self.state_data.config.read_sync_directories()
        while len(sync_directories) < self.state_data.config.get_min_dir():
            new_dir: str = self.state_data.gui.directory_prompt(
                len(sync_directories), self.state_data.config.get_min_dir())
            sync_directories = self.state_data.config.check_sync_directory(new_dir, sync_directories)
        self.state_data.config.write_sync_directories(sync_directories)
        return sync_directories

    def initialize_file_structures(self, sync_directories: List[str]) -> None:
        self.state_data.set_directories(sync_directories)
        if self.state_data.verbose:
            for dir in self.state_data.get_directories():
                print("Directories to sync:")
                print(dir.get_directory_path())


class Check(DataState):
    def run(self) -> None:
        pass

    def get_next(self) -> SyncState:
        if self.state_data.exit_request:
            return Final(self.state_data)
        elif self.state_data.sync_required:
            return Sync(self.state_data)
        return Wait(self.state_data)


class Wait(DataState):
    def run(self) -> None:
        pass

    def get_next(self) -> SyncState:
        if self.state_data.exit_request:
            return Final(self.state_data)
        elif self.state_data.sync_required:
            return Sync(self.state_data)
        return Wait(self.state_data)


class Sync(DataState):
    def run(self) -> None:
        pass

    def get_next(self) -> SyncState:
        return Wait(self.state_data)


class Error(DataState):
    def run(self) -> None:
        pass

    def get_next(self) -> SyncState:
        return Final(self.state_data)


class Final(DataState):
    def run(self) -> None:
        pass

    def get_next(self) -> SyncState:
        return End()
