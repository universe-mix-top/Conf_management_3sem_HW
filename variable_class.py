import math


class Variable:
    """
    Класс для представления переменной или константы.
    """

    def __init__(self, app_self, name: str, equation: int | str | list | tuple, isconst=False):
        super().__init__()
        self.app_self = app_self
        self.name = name
        self.equation = equation
        self.value = self.calculate(equation)
        self.isconst = isconst

    def __repr__(self):
        return f'<class=variable name={self.name} type={type(self.equation).__name__} value={self.value} equation={self.equation}>'

    def __str__(self):
        return self.__repr__()

    def calculate_tuple(self, line: tuple[str, str | int, ...]):
        """
        Вычисляет значение для выражения в формате кортежа.

        Args:
            tuple_expression: Кортеж вида (операция, операнд1, операнд2, ...)

        Returns:
            Результат вычисления

        Raises:
            ValueError: При ошибке вычисления
            Exception: При недостаточном количестве операндов или неверных данных
        """
        operation, *operators = line
        i = -1

        if len(operators) < 2:
            raise Exception('Недостаточное количество операндов для операции') from None

        while (i := i + 1) < len(operators):
            try:
                operators[i] = self.calculate(operators[i])
            except Exception as e:
                raise Exception(f'Константа или переменная с таким именем не найдена: {e}') from None

        try:
            if operation == '+':
                if list in map(type, operators):
                    raise TypeError('в операции сложения не может быть массива')
                var = sum(operators)

            elif operation == '-':
                if list in map(type, operators):
                    raise TypeError('в операции вычитания не может быть массива')
                var = operators[0] - sum(operators[1:])

            elif operation == '*':
                if list in map(type, operators):
                    raise TypeError('в операции умножения не может быть массива')
                var = math.prod(operators)

            elif operation == 'mod':
                if list in map(type, operators):
                    raise TypeError('в операции деления с остатком не может быть массива')
                var = operators[0]
                for i in operators[1:]:
                    var %= i

            elif operation == 'min':
                if list in map(type, operators):
                    raise TypeError('в операции деления с остатком не может быть массива')
                var = min(operators)

            else:
                raise Exception('неизвестная операция, доступны только +/-/*/mod/min')

            return var

        except ValueError as e:
            raise ValueError(f'ошибка при вычислении : {e}') from None

    def calculate(self, expression):
        """
        Рекурсивно вычисляет значение выражения.
        Args:
            expression: Выражение для вычисления (кортеж, список, число или строка)

        Returns:
            Вычисленное значение

        Raises:
            Exception: При ошибке вычисления
        """
        try:
            if type(expression) is tuple:  # для вычисления
                return self.calculate_tuple(expression)

            elif type(expression) is list:  # для списков
                return list(map(lambda x: self.calculate(x), expression))

            elif type(expression) is int:  # для чисел
                return expression

            elif type(expression) is str and expression.isnumeric():  # для чисел в виде строки
                return int(expression)

            elif type(expression) is str and expression in self.app_self.CONSTS.keys():  # для констант
                return self.app_self.CONSTS.get(expression).value

            elif type(expression) is str and expression in self.app_self.VARIABLE.keys():  # для переменных
                return self.app_self.VARIABLE.get(expression).value

            else:
                raise Exception('Ошибка в выражении') from None

        except Exception as e:
            raise Exception(f'ошибка при вычислении: {e}') from None


def main():
    # только для теста
    class TestApp():
        """
        Тестовый класс для демонстрации работы Variable.
        """
        SYS_PARAMS = {}
        CONSTS = {}
        VARIABLE = {}

        def __repr__(self):
            return f'<SYS_PARAMS={self.SYS_PARAMS} CONSTS={self.CONSTS} VARIABLE={self.VARIABLE}>'

        def __str__(self):
            return self.__repr__()

        def run(self):
            """
            Инициализирует переменные и константы
            """
            self.CONSTS['number'] = Variable(app, 'number', 1, isconst=True)
            self.CONSTS['operator'] = Variable(app, 'operator', 'number', isconst=True)
            self.VARIABLE['addition'] = Variable(app, 'addition', ('+', '5', 4))
            self.VARIABLE['substraction'] = Variable(app, 'substraction', ('-', 'number', 2))
            self.VARIABLE['multiplication'] = Variable(app, 'multiplication', ('min', '4', '2', '3'))
            self.VARIABLE['modulo'] = Variable(app, 'modulo', ('mod', '5', '2'))
            self.VARIABLE['list'] = Variable(app, 'list', ['addition', '6', ('+', ('-', 9, '6'), 2, 2)])
            self.VARIABLE['void_list'] = Variable(app, 'void_list', [])

        def display(self):
            """
            Формирует строковое представление текущего состояния приложения.

            Returns:
                Строка с информацией о константах и переменных
            """
            ubyl = 'CONSTS:\n'
            for key, val in self.CONSTS.items():
                ubyl += f'{key} : {val.equation}  ==  {val.value}\n'

            ubyl += '\nVARIABLE:\n'
            for key, val in self.VARIABLE.items():
                ubyl += f'{key} : {val.equation}  ==  {val.value}\n'
            return ubyl

    app = TestApp()
    app.run()
    print(app.display())


if __name__ == '__main__':
    main()
