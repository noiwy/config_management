"""Эмулятор оболочки ОС. Вариант 19. Этап 1: REPL."""

import shlex


class ShellEmulator:
    """Эмулятор командной строки."""

    def __init__(self, vfs_name="VFS"):
        """Инициализация. vfs_name — имя VFS для приглашения."""
        self.vfs_name = vfs_name
        self.running = True

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

    def cmd_cd(self, args):
        """Заглушка команды cd."""
        print(f"cd: аргументы = {args}")

    def cmd_exit(self, args):
        """Выход из эмулятора."""
        print("Выход.")
        self.running = False

    def execute(self, command, args):
        """Выполняет команду по имени."""
        commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }
        if command in commands:
            commands[command](args)
        else:
            print(f"Ошибка: неизвестная команда '{command}'")

    def run(self):
        """Главный цикл: читаем ввод, выполняем, повторяем."""
        print(f"Добро пожаловать в эмулятор {self.vfs_name}!")
        print("Введите 'exit' для выхода.")
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


if __name__ == "__main__":
    emulator = ShellEmulator()
    emulator.run()