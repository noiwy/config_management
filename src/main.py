"""Эмулятор оболочки ОС.  Вариант 19. Этап 2: конфигурация."""

import argparse
import shlex
import zipfile
from vfs import VFS

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
        self.running = True
    
    def print_config(self):
        """Отладочный вывод всех параметров при запуске."""
        print("=== Параметры эмулятора ===")
        print(f"vfs_name    = {self.vfs_name}")
        print(f"vfs_path    = {self.vfs_path}")
        print(f"script_path = {self.script_path}")
        print("===========================")

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
        """Заглушка команды ls."""
        print(f"ls: аргументы = {args}")
        return True

    def cmd_cd(self, args):
        """Заглушка команды cd."""
        print(f"cd: аргументы = {args}")
        return True

    def cmd_conf_dump(self, args):
        """Служебная команда: выводит параметры эмулятора."""
        print(f"vfs_name    = {self.vfs_name}")
        print(f"vfs_path    = {self.vfs_path}")
        print(f"script_path = {self.script_path}")
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
                user_input = input(f"{self.vfs_name}> ")
            except (EOFError, KeyboardInterrupt):
                print("\nВыход.")
                break
            command, args = self.parse_command(user_input)
            if command is None:
                continue
            self.execute(command, args)


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