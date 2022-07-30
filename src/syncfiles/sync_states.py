"""Sync States

Author: Kevin Hodge
"""

from typing import List, Optional
from syncfiles.file_structure import FileStructure
from syncfiles.sync_ui import SyncUI
from syncfiles.config_manager import ConfigManager
from syncfiles.sync_exception import SyncException
from syncfiles.sync_state_machine import SyncState, End


class StateData:
    fstructs: List[FileStructure] = []
    error_raised: bool = False
    error: Optional[SyncException] = None
    exit_request: bool = False
    sync_required: bool = False
    verbose: bool = False

    def __init__(self, config: ConfigManager, ui: SyncUI, verbose: bool = False) -> None:
        self.config = config
        self.ui = ui
        self.verbose = verbose


class DataState(SyncState):
    def __init__(self, state_data: StateData) -> None:
        self.state_data: StateData = state_data
        self.config: ConfigManager = self.state_data.config
        self.ui: SyncUI = self.state_data.ui
        self.verbose: bool = self.state_data.verbose
        self.error: Optional[SyncException] = self.state_data.error

    def get_fstructs(self) -> List[FileStructure]:
        return self.state_data.fstructs

    def add_fstruct(self, directory: FileStructure) -> None:
        self.state_data.fstructs.append(directory)

    def get_exit_request(self) -> bool:
        return self.state_data.exit_request

    def set_exit_request(self, exit_request: bool = True) -> None:
        self.state_data.exit_request = exit_request

    def get_sync_required(self) -> bool:
        return self.state_data.sync_required

    def set_sync_required(self, sync_required: bool = True) -> None:
        self.state_data.sync_required = sync_required

    def get_error_raised(self) -> bool:
        return self.state_data.error_raised

    def set_error_raised(self, error_raised: bool = True) -> None:
        self.state_data.error_raised = error_raised

    def run(self) -> None:
        try:
            self.run_commands()
        except Exception as err:
            self.set_error_raised()
            self.error = SyncException(err)

    def run_commands(self) -> None:
        """Commands run by default run function"""


class Initial(DataState):
    def run_commands(self) -> None:
        sync_directories: List[str] = self.get_sync_directories()
        self.initialize_file_structures(sync_directories)

    def get_sync_directories(self) -> List[str]:
        sync_directories: List[str] = self.config.read_sync_directories()
        while len(sync_directories) < self.config.get_min_dir():
            new_dir: str = self.ui.directory_prompt(
                len(sync_directories), self.config.get_min_dir())
            sync_directories = self.config.check_sync_directory(new_dir, sync_directories)
        self.config.write_sync_directories(sync_directories)
        return sync_directories

    def initialize_file_structures(self, sync_directories: List[str]) -> None:
        if self.verbose:
            print("Directories to sync:")
        for dir in sync_directories:
            self.add_fstruct(FileStructure(dir, verbose=self.verbose))
            if self.verbose:
                print(self.get_fstructs()[-1].get_directory_path())

    def get_next(self) -> SyncState:
        if self.get_error_raised():
            return Error(self.state_data)
        if self.get_exit_request():
            return Final(self.state_data)
        return Check(self.state_data)


class Check(DataState):
    def run_commands(self) -> None:
        pass
        # for index, fstruct in enumerate(self.get_fstructs()):
        #     fstruct.update_file_structure()
        #     if self.verbose:
        #         print(f"Directory {str(index + 1)}:")
        #         print(fstruct.print_file_structure(), end="")
        #     changes: int = fstruct.check_file_structure(self.config.read_last_sync_file())
        #     if changes > 0:
        #         self.set_sync_required()

    def get_next(self) -> SyncState:
        if self.get_error_raised():
            return Error(self.state_data)
        elif self.get_exit_request():
            return Final(self.state_data)
        elif self.get_sync_required():
            return Sync(self.state_data)
        return Wait(self.state_data)


class Wait(DataState):
    def run_commands(self) -> None:
        pass

    def get_next(self) -> SyncState:
        if self.get_error_raised():
            return Error(self.state_data)
        if self.get_exit_request():
            return Final(self.state_data)
        elif self.get_sync_required():
            return Sync(self.state_data)
        return Check(self.state_data)


class Sync(DataState):
    def run_commands(self) -> None:
        pass

    def get_next(self) -> SyncState:
        if self.get_error_raised():
            return Error(self.state_data)
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
