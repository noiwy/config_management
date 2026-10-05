"""Эмулятор оболочки ОС.  Вариант 19. Этап 2: конфигурация."""

import argparse
import shlex
import zipfile
from vfs import VFS
import getpass
import os
import platform

class ShellEmulator:
    """Эмулятор командной строки."""

    def __init__(self, vfs_name="VFS", vfs_path=None, script_path=None):
        """
        Инициализация.

        vfs_name — имя VFS для приглашения.
        vfs_path — путь к файлу VFS (из аргументов командной строки).
        script_path — путь к стартовому скрипту.
        """
        self.vfs_name = vfs_name
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.vfs = None
        self.current_path = []
        self.running = True
    
    def print_config(self):
        """Отладочный вывод всех параметров при запуске."""
        print("=== Параметры эмулятора ===")
        print(f"vfs_name    = {self.vfs_name}")
        print(f"vfs_path    = {self.vfs_path}")
        print(f"script_path = {self.script_path}")
        print("===========================")

    def _get_node(self):
        """Возвращает узел текущей папки."""
        return self._node_at(self.current_path)

    def load_vfs(self):
        """Загружает VFS из ZIP-архива, если путь задан."""
        if not self.vfs_path:
            return
        try:
            self.vfs = VFS(name="my_vfs")
            self.vfs.load_from_zip(self.vfs_path)
            print(f"VFS '{self.vfs.name}' загружена: "
                  f"{self.vfs.count_files()} файлов, "
                  f"{self.vfs.count_dirs()} папок")
        except FileNotFoundError:
            print(f"Ошибка: файл VFS '{self.vfs_path}' не найден")
            self.running = False
        except zipfile.BadZipFile:
            print(f"Ошибка: файл '{self.vfs_path}' не является ZIP-архивом")
            self.running = False

    def parse_command(self, user_input):
        """Разбирает строку на команду и аргументы. Учитывает кавычки."""
        try:
            parts = shlex.split(user_input)
        except ValueError:
            print("Ошибка: неправильные кавычки")
            return None, []
        if not parts:
            return None, []
        return parts[0], parts[1:]

    def cmd_ls(self, args):
        """Показывает содержимое текущей папки."""
        if self.vfs is None:
            print("Ошибка: VFS не загружена")
            return False
        node = self._get_node()
        if node is None or node["type"] != "dir":
            print("Ошибка: текущая папка недоступна")
            return False

        names = sorted(node["children"].keys())
        if not names:
            return True

        for name in names:
            child = node["children"][name]
            if child["type"] == "dir":
                print(f"{name}/")
            else:
                print(name)
        return True

    def cmd_cd(self, args):
        """Переход в другую папку."""
        if self.vfs is None:
            print("Ошибка: VFS не загружена")
            return False
        if not args:
            self.current_path = []
            return True

        target = args[0]

        if target.startswith("/"):
            new_path = []
            parts = [p for p in target.split("/") if p]
        else:
            new_path = list(self.current_path)
            parts = [p for p in target.split("/") if p]

        for part in parts:
            if part == ".":
                continue
            if part == "..":
                if new_path:
                    new_path.pop()
                continue
            node = self._node_at(new_path)
            if node is None or "children" not in node:
                print(f"Ошибка: папка '{target}' не найдена")
                return False
            if part not in node["children"]:
                print(f"Ошибка: папка '{target}' не найдена")
                return False
            child = node["children"][part]
            if child["type"] != "dir":
                print(f"Ошибка: '{target}' — не папка")
                return False
            new_path.append(part)

        self.current_path = new_path
        return True

    def _node_at(self, path):
        """Возвращает узел дерева по указанному пути (список имён)."""
        if self.vfs is None:
            return None
        node = self.vfs.root
        for part in path:
            if "children" not in node or part not in node["children"]:
                return None
            node = node["children"][part]
        return node

    def cmd_conf_dump(self, args):
        """Служебная команда: выводит параметры эмулятора."""
        print(f"vfs_name    = {self.vfs_name}")
        print(f"vfs_path    = {self.vfs_path}")
        print(f"script_path = {self.script_path}")
        return True

    def cmd_whoami(self, args):
        """Печатает имя текущего пользователя."""
        print(getpass.getuser())
        return True

    def cmd_uname(self, args):
        """Печатает информацию о системе."""
        print(platform.system())
        print(platform.release())
        return True

    def cmd_clear(self, args):
        """Очищает экран консоли."""
        os.system("cls" if os.name == "nt" else "clear")
        return True


    def _resolve_path(self, target):
        """Разбирает путь. Возвращает (путь_родителя, имя) или None."""
        if target.startswith("/"):
            base = []
            parts = [p for p in target.split("/") if p]
        else:
            base = list(self.current_path)
            parts = [p for p in target.split("/") if p]
        if not parts:
            return None
        for part in parts[:-1]:
            if part == "..":
                if base:
                    base.pop()
                continue
            if part == ".":
                continue
            node = self._node_at(base)
            if node is None or "children" not in node:
                return None
            if part not in node["children"]:
                return None
            if node["children"][part]["type"] != "dir":
                return None
            base.append(part)
        return base, parts[-1]

    def cmd_rm(self, args):
        """Удаляет файл из VFS (только в памяти)."""
        if self.vfs is None:
            print("Ошибка: VFS не загружена")
            return False
        if not args:
            print("Ошибка: не указан файл для удаления")
            return False

        resolved = self._resolve_path(args[0])
        if resolved is None:
            print(f"Ошибка: путь '{args[0]}' не найден")
            return False

        parent_path, name = resolved
        parent = self._node_at(parent_path)
        if parent is None or name not in parent.get("children", {}):
            print(f"Ошибка: файл '{args[0]}' не найден")
            return False
        if parent["children"][name]["type"] != "file":
            print(f"Ошибка: '{args[0]}' — не файл (папки удалять нельзя)")
            return False

        del parent["children"][name]
        return True

    def cmd_help(self, args):
        """Выводит список команд с описанием."""
        print("Доступные команды:")
        print("  ls             - показать содержимое текущей папки")
        print("  cd <путь>      - перейти в другую папку")
        print("  whoami         - вывести имя пользователя")
        print("  uname          - вывести информацию о системе")
        print("  clear          - очистить экран")
        print("  rm <файл>      - удалить файл из VFS")
        print("  help           - вывести этот список")
        print("  conf-dump      - вывести параметры эмулятора")
        print("  exit           - выйти из эмулятора")
        return True

    def cmd_exit(self, args):
        """Выход из эмулятора."""
        print("Выход.")
        self.running = False
        return True

    def execute(self, command, args):
        """
        Выполняет команду по имени.
        Возвращает True, если команда выполнилась, иначе False.
        """
        commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "whoami": self.cmd_whoami,
            "uname": self.cmd_uname,
            "clear": self.cmd_clear,
            "rm": self.cmd_rm,
            "help": self.cmd_help,
            "conf-dump": self.cmd_conf_dump,
            "exit": self.cmd_exit,
        }
        if command in commands:
            commands[command](args)
            return True
        print(f"Ошибка: неизвестная команда '{command}'")
        return False


    def run_script(self):
        """
        Выполняет стартовый скрипт, если он задан.
        Останавливается при первой ошибке.
        """
        if not self.script_path:
            return
        try:
            with open(self.script_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Ошибка: файл скрипта '{self.script_path}' не найден")
            self.running = False
            return

        for line in lines:
            line = line.strip()
            if not line:
                continue

            print(f"{self.vfs_name}> {line}")

            command, args = self.parse_command(line)
            if command is None:
                self.running = False
                return

            ok = self.execute(command, args)
            if not ok:
                print(f"Ошибка в скрипте на строке: {line}")
                self.running = False
                return

    def run(self):
        """Главный цикл: читаем ввод, выполняем, повторяем."""
        self.print_config()
        print(f"Добро пожаловать в эмулятор {self.vfs_name}!")
        print("Введите 'exit' для выхода.")
        
        self.load_vfs()
        self.run_script()

        while self.running:
            try:
                user_input = input(f"{self.vfs_name}{self._prompt_path()}> ")
            except (EOFError, KeyboardInterrupt):
                print("\nВыход.")
                break
            command, args = self.parse_command(user_input)
            if command is None:
                continue
            self.execute(command, args)
    def _prompt_path(self):
        """Возвращает путь для приглашения."""
        if not self.current_path:
            return ":/"
        return ":/" + "/".join(self.current_path)


def parse_args():
    """Разбирает аргументы командной строки."""
    parser = argparse.ArgumentParser(
        description="Эмулятор оболочки ОС (Вариант 19)"
    )
    parser.add_argument(
        "--vfs",
        dest="vfs_path",
        default=None,
        help="Путь к файлу VFS",
    )
    parser.add_argument(
        "--script",
        dest="script_path",
        default=None,
        help="Путь к стартовому скрипту",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    emulator = ShellEmulator(
        vfs_path=args.vfs_path,
        script_path=args.script_path,
    )
    emulator.run()