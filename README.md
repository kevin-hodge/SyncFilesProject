# SyncFilesProject
----------------
Ground Rules:
This is a simple project that will sync a file structure located in two locations on a computer (mac).
The two locations will be defined in a text file (sync_directories_file.txt) that will be in the library's __init__.py
directory.
The file sync will occur (a.k.a. the executable will run) when the library is imported.
    - Should program just start when the computer starts and wait for a time of day to run?
    - Can continuously running program check for edits to one or both files?
The __init__.py file of the library will have a call to run the executable.
    - What if the library run is not the most up-to-date library?
        - Could just make sure I only edit the file in the python install directory
    - Possible to have .exe run when a file in the file structure is closed?
    - Possible to check which files have been most recently edited?
        - If so, could just sync the files that have been edited and leave the rest (if last dates of edit/sync match).
The executable will be located in the same library directory as the __init__.py file.
Requirements:
Req #1: The program shall determine the working directory.
Req #2: The program shall find sync_directories_file.txt (text file containing the sync directories).
Req #3: The program shall open and read sync_directories_file.txt.
Req #4: The program shall retrieve the names and file structure of all files and folders in both directories.
Req #5: The program shall determine the Most_Recently_Updated_Directory and the To_Sync_Directory.
Req #6: The program shall copy all files in the Most_Recently_Updated_Directory to the To_Sync_Directory.
Req #7: The program shall notify the user if either directory cannot be found.
Req #8: The program shall be implemented as a finite state machine.
Req #9: The program shall be version controlled in a github repository.
Req #10: File structures shall be stored in a class "FileStructure"
