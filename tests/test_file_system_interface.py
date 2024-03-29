"""Tests file_system_interface.

Author: Kevin Hodge
"""

import unittest
from typing import List
import tests.tfuncs as tfuncs
from pathlib import Path
from syncfiles.file_system_interface import DBInterface, FSInterface


class FSInterfaceTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs) -> None:
        self.tf: tfuncs.TFunctions = tfuncs.TFunctions()
        super().__init__(*args, **kwargs)

    @tfuncs.handle_test_dirs
    def test_file_exists(self) -> None:
        path: FSInterface = FSInterface(str(self.tf.test_path1))
        self.assertTrue(path.exists())

    def test_file_does_not_exist(self) -> None:
        path: FSInterface = FSInterface(str(self.tf.test_path1))
        self.assertFalse(path.exists())

    @tfuncs.handle_test_dirs
    def test_iterdir(self) -> None:
        file_list: List[str] = []
        for i in range(5):
            test_filename: str = f"test_file{i}.txt"
            file_list.append(test_filename)
            test_filepath: str = str(self.tf.test_path1 / test_filename)
            tfuncs.create_file(test_filepath)

        path: FSInterface = FSInterface(str(self.tf.test_path1))
        out_file_list: List[str] = []
        for entry in path.iterdir():
            self.assertTrue(entry.exists())
            self.assertTrue(isinstance(entry, FSInterface))
            out_file_list.append(entry.get_name())
        self.assertCountEqual(file_list, out_file_list)

    @tfuncs.handle_test_dirs
    def test_is_file(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")
        tfuncs.create_file(test_file)

        path: FSInterface = FSInterface(test_file)
        self.assertTrue(path.is_file())

    def test_not_is_file(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")

        path: FSInterface = FSInterface(test_file)
        self.assertFalse(path.is_file())

    @tfuncs.handle_test_dirs
    def test_is_dir(self) -> None:
        test_folder: str = str(self.tf.test_path1)
        path: FSInterface = FSInterface(test_folder)
        self.assertTrue(path.is_dir())

    def test_not_is_dir(self) -> None:
        test_folder: str = str(self.tf.test_path1)
        path: FSInterface = FSInterface(test_folder)
        self.assertFalse(path.is_dir())

    @tfuncs.handle_test_dirs
    def test_get_name(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")
        tfuncs.create_file(test_file)

        path: FSInterface = FSInterface(test_file)
        self.assertTrue(path.get_name(), "test_file.txt")

    @tfuncs.handle_test_dirs
    def test_get_mod_time(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")
        tfuncs.create_file(test_file)

        path: FSInterface = FSInterface(test_file)
        self.assertEqual(path.get_mod_time(), Path(test_file).stat().st_mtime)

    def test_repr(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")
        path: FSInterface = FSInterface(test_file)
        self.assertEqual(str(test_file), str(path))

    def test_truediv(self) -> None:
        test_path: str = str(self.tf.test_path1)
        path: DBInterface = FSInterface(test_path) / "test_file.txt"
        self.assertEqual(str(self.tf.test_path1 / "test_file.txt"), str(path))

    def test_cwd(self) -> None:
        self.assertTrue(isinstance(FSInterface.cwd(), FSInterface))
        self.assertEqual(str(Path.cwd()), str(FSInterface.cwd()))

    @tfuncs.handle_test_dirs
    def test_context_manager_write(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")
        tfuncs.create_file(test_file)

        path: FSInterface = FSInterface(test_file)
        with path.open("w") as file:
            file.write("This file is updated.")

        with open(test_file) as file:
            self.assertEqual(file.read(), "This file is updated.")

    @tfuncs.handle_test_dirs
    def test_context_manager_read(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")
        tfuncs.create_file(test_file)

        with open(test_file, "w") as file:
            file.write("This file is updated.")

        path: FSInterface = FSInterface(test_file)
        with path.open() as file:
            self.assertEqual(file.read(), "This file is updated.")

    @tfuncs.handle_test_dirs
    def test_unlink(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")
        tfuncs.create_file(test_file)

        path: FSInterface = FSInterface(test_file)
        path.unlink()

        self.assertFalse(Path(test_file).exists())

    @tfuncs.handle_test_dirs
    def test_parent(self) -> None:
        test_folder: str = str(self.tf.test_path1)
        test_file: str = str(Path(test_folder) / "test_file.txt")

        path: FSInterface = FSInterface(test_file)
        self.assertEqual(str(path.get_parent()), test_folder)
        self.assertTrue(isinstance(path.get_parent(), FSInterface))

    @tfuncs.handle_test_dirs
    def test_rename(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")
        tfuncs.create_file(test_file)

        path: FSInterface = FSInterface(test_file)
        new_file_name: str = str(self.tf.test_path1 / "new_test_file.txt")
        new_path: FSInterface = FSInterface(new_file_name)
        path.rename(new_path)
        self.assertFalse(path.exists())
        self.assertTrue(new_path.exists())

    @tfuncs.handle_test_dirs
    def test_copyfile(self) -> None:
        test_file: str = str(self.tf.test_path1 / "test_file.txt")
        tfuncs.create_file(test_file)

        new_file: str = str(self.tf.test_path2 / "test_file.txt")
        FSInterface.copyfile(test_file, new_file)
        self.assertTrue(Path(new_file).exists())

    @tfuncs.handle_test_dirs
    def test_mkdir(self) -> None:
        test_dir: str = str(self.tf.test_path1 / "test_folder")
        FSInterface(test_dir).mkdir(exist_ok=True)

        self.assertTrue(Path(test_dir).exists())

    @tfuncs.handle_test_dirs
    def test_rmtree(self) -> None:
        test_dir: str = str(self.tf.test_path1 / "test_folder")
        tfuncs.create_directory(test_dir)
        self.assertTrue(Path(test_dir).exists())

        FSInterface(test_dir).rmtree()
        self.assertFalse(Path(test_dir).exists())

    @tfuncs.handle_test_dirs
    def test_mkdir_parents(self) -> None:
        test_folder: str = str(self.tf.test_path1 / "test_folder")
        tfuncs.create_directory(test_folder)
        test_file: str = str(Path(test_folder) / "test_file.txt")
        tfuncs.create_file(test_file)

        new_folder: str = str(self.tf.test_path1 / "new_folder")
        new_file: str = str(Path(new_folder) / "test_file.txt")
        FSInterface(new_file).mkdir(parents=True, exist_ok=True)
        self.assertTrue(Path(new_folder).exists())
        self.assertTrue(Path(new_file).exists())
