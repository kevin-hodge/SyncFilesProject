"""Sync States

Author: Kevin Hodge
"""

from typing import List, Optional
import time
from syncfiles.file_structure import FileStructure
from syncfiles.sync_ui import SyncUI
from syncfiles.config_manager import ConfigManager
from syncfiles.sync_exception import SyncException
from syncfiles.sync_manager import SyncManager
from syncfiles.sync_state_machine import SyncState, End


class StateData:
    fstructs: List[FileStructure] = []
    error_raised: bool = False
    error: Optional[SyncException] = None
    exit_request: bool = False
    sync_required: bool = False
    verbose: bool = False

    def __init__(self, config: ConfigManager, ui: SyncUI, verbose: bool = False) -> None:
        self.fstructs = []
        self.error_raised = False
        self.error = None
        self.exit_request = False
        self.exit_required = False
        self.config = config
        self.ui = ui
        self.verbose = verbose


class DataState(SyncState):
    name: str = "Unkown State"

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
        except SyncException as err:
            self.set_error_raised()
            self.state_data.error = err
            self.state_data.error.set_prev_state(self.name)
        except Exception as err:
            self.set_error_raised()
            self.state_data.error = SyncException(str(err))

    def run_commands(self) -> None:
        """Commands run by default run function"""


class Initial(DataState):
    name: str = "Initial"

    def run_commands(self) -> None:
        if self.verbose:
            print("Initializing...")

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
    name: str = "Check"

    def run_commands(self) -> None:
        if self.verbose:
            print("Checking...")

        for index, fstruct in enumerate(self.get_fstructs()):
            fstruct.update_file_structure()
            changes: int = fstruct.check_file_structure(self.config.read_last_sync_file())
            if changes > 0:
                self.set_sync_required()
            if self.verbose:
                print(f"Directory {str(index + 1)}:")
                print(fstruct.print_file_structure(), end="")

    def get_next(self) -> SyncState:
        if self.get_error_raised():
            return Error(self.state_data)
        elif self.get_exit_request():
            return Final(self.state_data)
        elif self.get_sync_required():
            return Sync(self.state_data)
        return Wait(self.state_data)


class Wait(DataState):
    name: str = "Wait"

    def __init__(self, *args, **kwargs) -> None:
        self.sleep_time: float = 10.0
        super().__init__(*args, **kwargs)

    def run_commands(self) -> None:
        if self.verbose:
            print("Waiting...")

        if self.prompt_user_to_exit():
            return None

        time.sleep(self.sleep_time)

    def set_sleep_time(self, sleep_time: float) -> None:
        self.sleep_time = sleep_time

    def prompt_user_to_exit(self) -> bool:
        if self.ui.exit_prompt():
            self.set_exit_request()
        return self.get_exit_request()

    def get_next(self) -> SyncState:
        if self.get_error_raised():
            return Error(self.state_data)
        elif self.get_exit_request():
            return Final(self.state_data)
        return Check(self.state_data)


class Sync(DataState):
    name: str = "Sync"

    def run_commands(self) -> None:
        if self.verbose:
            print("Syncing...")

        synchonizer: SyncManager = SyncManager(self.get_fstructs())
        synchonizer.sync()
        self.config.write_last_sync_file(synchonizer.get_last_sync())

        self.set_sync_required(False)

    def get_next(self) -> SyncState:
        if self.get_error_raised():
            return Error(self.state_data)
        return Wait(self.state_data)


class Error(DataState):
    name: str = "Error"
    next_state: Optional[SyncState] = None

    def run(self) -> None:
        assert self.error is not None
        if self.verbose:
            print("Error...")
            print(self.error.get_error_message())

        if self.error.get_error_id() == "sync_dirs_do_not_exist":
            self.next_state = Initial(self.state_data)

    def get_next(self) -> SyncState:
        if self.next_state is not None:
            return self.next_state
        return Final(self.state_data)


class Final(DataState):
    name: str = "Final"

    def run(self) -> None:
        if self.verbose:
            print("Exiting...")

    def get_next(self) -> SyncState:
        return End()
