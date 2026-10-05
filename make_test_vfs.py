"""Генератор тестовых VFS-архивов для эмулятора."""

import zipfile


def make_minimal():
    """Минимальная VFS: один файл в корне."""
    with zipfile.ZipFile("vfs_minimal.zip", "w") as zf:
        zf.writestr("readme.md", "Hello, minimal VFS!")


def make_few_files():
    """Несколько файлов в корне."""
    with zipfile.ZipFile("vfs_few_files.zip", "w") as zf:
        zf.writestr("readme.md", "Read me first.")
        zf.writestr("notes.txt", "Some notes.")
        zf.writestr("data.csv", "id,name\n1,Alice\n2,Bob")


def make_deep():
    """Глубокая структура: не менее 3 уровней вложенности."""
    with zipfile.ZipFile("vfs_deep.zip", "w") as zf:
        zf.writestr("readme.md", "Root readme")
        zf.writestr("home/user/docs/notes.txt", "Deep notes")
        zf.writestr("home/user/docs/archive/old.txt", "Very deep file")


if __name__ == "__main__":
    make_minimal()
    make_few_files()
    make_deep()
    print("Созданы архивы: vfs_minimal.zip, vfs_few_files.zip, vfs_deep.zip")