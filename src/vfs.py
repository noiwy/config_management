"""Виртуальная файловая система (VFS) для эмулятора."""

import base64
import zipfile


class VFS:
    """Виртуальная файловая система в памяти."""

    def __init__(self, name="VFS"):
        """Создаёт пустую VFS с заданным именем."""
        self.name = name
        self.root = {"type": "dir", "children": {}}

    def load_from_zip(self, zip_path):
        """Загружает содержимое ZIP-архива в память."""
        with zipfile.ZipFile(zip_path, "r") as zf:
            for name in zf.namelist():
                if name.endswith("/"):
                    continue
                data = zf.read(name)
                content, is_binary = self._decode_content(data)
                self._add_file(name, content, is_binary)

    def _decode_content(self, data):
        """Декодирует содержимое файла. Возвращает (content, is_binary)."""
        try:
            return data.decode("utf-8"), False
        except UnicodeDecodeError:
            return base64.b64encode(data).decode("ascii"), True

    def _add_file(self, path, content, is_binary):
        """Добавляет файл в дерево по указанному пути."""
        parts = [p for p in path.split("/") if p]
        if not parts:
            return
        current = self.root
        for part in parts[:-1]:
            children = current["children"]
            if part not in children:
                children[part] = {"type": "dir", "children": {}}
            current = children[part]
        current["children"][parts[-1]] = {
            "type": "file",
            "content": content,
            "is_binary": is_binary,
        }

    def count_files(self):
        """Возвращает общее число файлов в VFS."""
        return self._count(self.root, "file")

    def count_dirs(self):
        """Возвращает число папок в VFS (не считая корень)."""
        return self._count(self.root, "dir") - 1

    def _count(self, node, type_name):
        """Рекурсивно считает узлы заданного типа."""
        if node["type"] == "file":
            return 1 if type_name == "file" else 0
        total = 1 if type_name == "dir" else 0
        for child in node["children"].values():
            total += self._count(child, type_name)
        return total