"""Sync Manager

Author: Kevin Hodge
"""

from typing import List
from syncfiles.file_structure import FileStructure


class SyncManager:
    """Takes FileStructures as inputs and synchronizes them.

    Condition: If FILE or FOLDER exists in one FileStructure, but not the other, and it IS marked as UPDATED.
    Action: It should be COPIED from the FileStructure that it exists in to the other FileStructure.

    Condition: If FILE or FOLDER exists in one FileStructure, but not the other, and it IS NOT marked as UPDATED.
    Action: It should be DELETED from the FileStructure that it exists in.

    Condition: If FILE or FOLDER exists in both FileStructures and IS marked as UPDATED in ONLY ONE FileStructure.
    Action: It should be DELETED from the FileStructure in which it IS NOT marked as UPDATED and COPIED from the
        FileStructure in which it IS marked as UPDATED to the other FileStructure.

    """
    def __init__(self, fstruct_list: List[FileStructure]) -> None:
        pass
