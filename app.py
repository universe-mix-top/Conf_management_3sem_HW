import json
import os
import re
import sys
from re import fullmatch
from variable_class import Variable


class Applecation:
    """
    Основной класс приложения для обработки выражений.
    Управляет константами, переменными и системными параметрами.
    """
    SYS_PARAMS = {}
    CONSTS = {}
    VARIABLE = {}

    def args_parser(self, args_line):
        """
        Парсит аргументы командной строки.

        Args:
            args_line: Список аргументов командной строки

        Returns:
            Словарь с параметрами и их значениями

        Raises:
            IndexError: При неправильном формате аргументов
        """
        params = {}
        try:
            for arg in args_line:
                if '-' in arg:
                    arg = arg.removeprefix('-')
                    param = arg
                    continue

                params[param] = params.get(param, []) + [arg]
        except IndexError:
            raise IndexError('Ошибка при обработке аргументов командной строки') from None
        return params

    def rebild(self, source_dict):
        """
        Извлекает значения из словаря объектов Variable.

        Args:
            source_dict: Словарь объектов Variable

        Returns:
            Словарь с именами и значениями
        """
        return {key: item.value for key, item in source_dict.items()}

    def control_operations(self, com):
        """
        Обрабатывает объявление переменной или константы.

        Args:
            command: Строка с командой

        Raises:
            Exception: При попытке переопределить константу или неверном формате
        """
        if fullmatch(r'var [a-z]+ .+', com) is not None:
            com = list(re.findall(f'var ([a-z]+) (.+)', com)[0])
            com[1] = self.evaluate_expression(com[1].strip())
            if com[0] in self.CONSTS.keys():
                raise Exception('попытка изменить существующую константу')
            self.CONSTS[com[0]] = Variable(self, com[0], com[1], isconst=True)

        elif fullmatch(r'[a-z]+ = .+', com) is not None:
            com = list(re.findall(f'([a-z]+) = (.+)', com)[0])
            com[1] = self.evaluate_expression(com[1].strip())
            self.VARIABLE[com[0]] = Variable(self, com[0], com[1], isconst=False)

        else:
            raise Exception('ошибка при инициализации константы или переменной')

    def split_operations(self, text, sep=' '):
        """
        Разделяет строку с учетом скобок.
        Не разделяет внутри парных скобок.

        Args:
            text: Текст для разделения
            sep: Разделитель

        Returns:
            Список частей строки
        """
        result = []
        current_part = ''
        bracket_level = 0
        for char in text:
            if char == sep and bracket_level <= 0:
                result.append(current_part)
                current_part = ''
                continue
            elif char in '([{':
                bracket_level += 1
            elif char in ')]}':
                bracket_level -= 1
            current_part += char
        result.append(current_part)
        return result

    def evaluate_expression(self, com):
        """
        Преобразует строковое выражение во внутренний формат.

        Args:
            com: Строковое выражение

        Returns:
            Выражение во внутреннем формате (кортеж, список, число или строка)

        Raises:
            ValueError: При неизвестном формате выражения
        """
        if fullmatch(r"@\((\+|-|\*|min|mod)(\s[^\s]+)+\s?\)", com) is not None:
            com, operators = list(re.findall(r"@\((\+|-|\*|min|mod)\s(.+)\s?\)", com)[0])
            operators = self.split_operations(operators, ' ')

            com = [com] + [self.evaluate_expression(i.strip()) for i in operators]
            com = tuple(com)

        elif fullmatch(r'\{\s?(.+\.\s)*.+\.?\s?\}', com) is not None:
            com = list(re.findall(r"\{(.+)\}", com)[0])
            com = self.split_operations(com, '.')

            i = -1
            while (i := i + 1) < len(com):
                com[i] = self.evaluate_expression(com[i].strip())

        elif fullmatch(r"\{\s?\}", com) is not None:
            com = []

        elif fullmatch(r"[a-z]*", com) is not None:
            com = str(com)

        elif fullmatch(r"[1-9][0-9]*", com) is not None:
            com = int(com)

        else:
            raise ValueError('неизвесная комманда') from None

        return com

    def line_handler(self, lines):
        """
        Обрабатывает многострочный текст с командами.

        Args:
            lines: Многострочный текст для обработки
        """
        for line in lines.split('\n'):
            for com in line.split(';'):
                if "'" in com:
                    com = com.split("'")[0]

                com = com.strip()
                if com == '': continue
                self.control_operations(com)

    def preparation(self):
        """
        Подготавливает приложение к работе.
        Парсит аргументы командной строки и проверяет обязательные параметры.

        Raises:
            Exception: Если не указан путь для записи JSON-файла
        """
        self.SYS_PARAMS.update(self.args_parser(sys.argv[1:]))

        if 'write_file_path' not in self.SYS_PARAMS.keys():
            raise Exception('запишите путь для json-файла [-write_file_path]: нет пути для записи json-файла') from None

    def run(self):
        """
        Запускает основную логику приложения.
        Читает входные данные из файла или стандартного ввода.

        Raises:
            Exception: Если указанный файл не существует
        """
        if 'read_file_path' in self.SYS_PARAMS.keys():
            path = self.SYS_PARAMS.get('read_file_path')[0]
            if not os.path.exists(path):
                raise Exception('read_file_path : такого пути не существует') from None

            with open(f'{path}', 'r') as f:
                self.line_handler(f.read())

        else:
            self.line_handler(sys.stdin.read())

    def data(self):
        """
        Формирует словарь с данными приложения для экспорта.

        Returns:
            Словарь с константами и переменными
        """
        data = {
            'CONSTANTS': self.rebild(self.CONSTS),
            'VARIABLES': self.rebild(self.VARIABLE)
        }
        return data

    def save(self):
        """
        Сохраняет данные приложения в JSON-файл.
        """
        data = self.data()
        path = self.SYS_PARAMS.get('write_file_path')[0]

        with open(f'{path}', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)

    def show(self):
        """
        Формирует строковое представление текущего состояния приложения.

        Returns:
            Строка с информацией о системе, константах и переменных
        """
        ubyl = 'SYS_PARAMS:\n'
        for key, val in self.SYS_PARAMS.items():
            ubyl += f'{key} : {val}\n'

        ubyl += '\nCONSTS:\n'
        for key, val in self.CONSTS.items():
            ubyl += f'{key} : {val.equation}  ==  {val.value}\n'

        ubyl += '\nVARIABLE:\n'
        for key, val in self.VARIABLE.items():
            ubyl += f'{key} : {val.equation}  ==  {val.value}\n'
        return ubyl


def main():
    app = Applecation()
    app.preparation()
    app.run()
    app.save()
    print(app.show())


if __name__ == '__main__':
    main()
