"""Тесты для эмулятора оболочки ОС."""

import os
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(
    0,
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"),
)

from main import ShellEmulator
from vfs import VFS


def _make_zip(files):
    """Создаёт временный ZIP с указанными файлами."""
    fd, path = tempfile.mkstemp(suffix=".zip")
    os.close(fd)
    with zipfile.ZipFile(path, "w") as zf:
        for name, content in files.items():
            zf.writestr(name, content)
    return path


class TestParser(unittest.TestCase):
    """Тесты парсера команд."""

    def setUp(self):
        self.emulator = ShellEmulator()

    def test_simple_command(self):
        """Простая команда без аргументов."""
        cmd, args = self.emulator.parse_command("ls")
        self.assertEqual(cmd, "ls")
        self.assertEqual(args, [])

    def test_quoted_args(self):
        """Аргументы в кавычках разбираются корректно."""
        cmd, args = self.emulator.parse_command('cd "Моя папка"')
        self.assertEqual(cmd, "cd")
        self.assertEqual(args, ["Моя папка"])


class TestVFS(unittest.TestCase):
    """Тесты виртуальной файловой системы."""

    def test_load_simple(self):
        """Загрузка простого архива."""
        path = _make_zip({"readme.md": "hello"})
        try:
            vfs = VFS()
            vfs.load_from_zip(path)
            self.assertEqual(vfs.count_files(), 1)
            self.assertEqual(vfs.count_dirs(), 0)
        finally:
            os.remove(path)


class TestRmCommand(unittest.TestCase):
    """Тесты команды rm."""

    def _load(self, path):
        em = ShellEmulator(vfs_path=path)
        em.vfs = VFS()
        em.vfs.load_from_zip(path)
        em.current_path = []
        return em

    def test_remove_file(self):
        """Файл удаляется из дерева VFS."""
        path = _make_zip({"readme.md": "hello"})
        try:
            em = self._load(path)
            em.cmd_rm(["readme.md"])
            children = em.vfs.root["children"]
            self.assertNotIn("readme.md", children)
        finally:
            os.remove(path)

    def test_zip_not_modified(self):
        """Исходный ZIP-архив не изменяется при удалении."""
        path = _make_zip({"readme.md": "hello"})
        try:
            with open(path, "rb") as f:
                before = f.read()
            em = self._load(path)
            em.cmd_rm(["readme.md"])
            with open(path, "rb") as f:
                after = f.read()
            self.assertEqual(before, after)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()