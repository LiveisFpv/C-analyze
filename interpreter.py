class Interpreter:
    def __init__(self, syntax_tree):
        """
        Инициализация интерпретатора с синтаксическим деревом.
        """
        self.tree = syntax_tree
        self.variables = {}  # Хранилище переменных
        self.functions = {}  # Хранилище функций

    def find_parent(self, tree, target):
        """
        Находит родительский узел для заданного узла.
        :param tree: текущий узел дерева
        :param target: целевой узел
        :return: родительский узел или None
        """
        for child in tree.children:
            if child is target:
                return tree
            parent = self.find_parent(child, target)
            if parent:
                return parent
        return None

    def execute(self, node=None):
        """
        Рекурсивное выполнение узлов синтаксического дерева.
        """
        if node is None:
            node = self.tree
        if node.root == "global":
            for child in node.children:
                self.execute(child)
            return 0
        # Оператор возврата
        if node.root == "return":
            return ReturnValue(self.execute(node.children[0]))
        
        
        # Операторы ввода/вывода
        if node.root == "print":
            # Выводим значения параметров
            values = [self.execute(child) for child in node.children[0].children]
            print(*values)
            return None

        if node.root == "input":
            # Читаем строку от пользователя
            for inp in node.children[0].children:
                user_input = input()
                try:
                    # Пробуем преобразовать ввод в число
                    self.variables[inp.root]=int(user_input) if user_input.isdigit() else float(user_input)
                except ValueError:
                    # Возвращаем как строку, если не число
                    self.variables[inp.root] = f"\"{user_input}\""
            return None
            # prompt = self.execute(node.children[0]) if node.children[0] else ""
            # user_input = input(prompt)
        
        # Условия
        if node.root == "if":
            condition = self.execute(node.children[0].children[0])  # Проверяем логическое выражение
            if condition:
                self.execute(node.children[1])  # Выполняем тело "if"
                return None  # Прерываем выполнение, не проверяя "else"
            else:
                # Ищем узел "else" на том же уровне
                parent_node = self.find_parent(self.tree, node)
                if parent_node:
                    else_index = parent_node.children.index(node) + 1
                    if else_index < len(parent_node.children):
                        next_node = parent_node.children[else_index]
                        if next_node.root == "else":
                            self.execute(next_node.children[0])  # Выполняем тело "else"
                            return None
        if node.root == "else":
            return None
        # Циклы
        if node.root == "for":
            self.execute(node.children[0].children[0])  # Инициализация
            while self.execute(node.children[0].children[1]):  # Условие
                self.execute(node.children[1])  # Тело цикла
                self.execute(node.children[0].children[2])  # Обновление
            return None
        if node.root == "while":
            while self.execute(node.children[0]):
                self.execute(node.children[1])
            return None
        # Определение функций
        if node.root.startswith("int") or node.root.startswith("void") or node.root.startswith("float") or node.root.startswith("string") or node.root.startswith("bool"):
            # Проверяем, есть ли параметры и тело
            if len(node.children) == 2 and node.children[0].root == "()" and node.children[1].root == "{}":
                func_name = node.root.split()[1]  # Название функции
                self.functions[func_name] = node  # Сохраняем узел функции
                return None
            # Инициализируем переменные
            else:
                if node.root.startswith("int"):
                    var_name = node.root.split()[1]
                    self.variables[var_name] = 0
                    return None
                elif node.root.startswith("float"):
                    var_name = node.root.split()[1]
                    self.variables[var_name] = 0.0
                    return None
                elif node.root.startswith("string"):
                    var_name = node.root.split()[1]
                    self.variables[var_name] = "\"\""
                    return None
                elif node.root.startswith("bool"):
                    var_name = node.root.split()[1]
                    self.variables[var_name] = False
                    return None

        # Вызов функции
        if node.root in self.functions:
            func_node = self.functions[node.root]
            param_nodes = func_node.children[0].children  # Параметры
            body_node = func_node.children[1]  # Тело функции

            # Подготавливаем локальные переменные
            args = [self.execute(arg) for arg in node.children[0].children]
            local_vars = dict(zip([param.root.split()[1] for param in param_nodes], args))
            original_vars = self.variables.copy()  # Сохраняем глобальные переменные
            self.variables.update(local_vars)

            # Выполняем тело функции
            result = None
            for statement in body_node.children:
                result = self.execute(statement)
                if isinstance(result, ReturnValue):  # Оператор возврата
                    result = result.value
                    break

            # Восстанавливаем глобальные переменные
            self.variables = original_vars
            return result

        # Арифметические и логические операции
        if node.root in {"+","+=","-=","*=","/=", "-", "*","%", "/", "<", ">", "<=", ">=", "==", "!=", "&&", "||", "!", "^", "&", "|"}:
            if node.root in {"!", "&&", "||"}:  # Логические операции
                if node.root == "!":
                    return not self.execute(node.children[0])
                left = self.execute(node.children[0])
                right = self.execute(node.children[1])
                if node.root == "&&":
                    return bool(left and right)
                if node.root == "||":
                    return bool(left or right)
            elif node.root in {"&", "|", "^"}:  # Побитовые операции
                left = self.execute(node.children[0])
                right = self.execute(node.children[1])
                if node.root == "&":
                    return left & right
                if node.root == "|":
                    return left | right
                if node.root == "^":
                    return left ^ right
            elif node.root in {"+=","-=","*=","/="}:# Синтаксический сахар
                left = self.execute(node.children[0])
                right = self.execute(node.children[1])
                try:
                    self.variables[node.children[0].root] = eval(f"{left} {node.root[0]} {right}")
                    return self.variables[node.children[0].root]
                except:
                    raise NameError(f"Переменная '{node.children[0].root}' не определена")
            else:  # Арифметические операции
                left = self.execute(node.children[0])
                right = self.execute(node.children[1])
                return eval(f"{left} {node.root} {right}")

        # Присваивание
        if node.root == "=":
            var_name = node.children[0].root
            value = self.execute(node.children[1])
            self.variables[var_name.split()[1]] = value
            return value

        # Массивы
        if node.root == "[]":
            array_name = node.children[0].root
            index = self.execute(node.children[1])
            return self.variables[array_name][index]

        if node.root == "[]=":
            array_name = node.children[0].root
            index = self.execute(node.children[1])
            value = self.execute(node.children[2])
            self.variables[array_name][index] = value
            return value

        # Переменные
        if node.root.isidentifier():
            if node.root in self.variables:
                return self.variables[node.root]
            else:
                raise NameError(f"Переменная '{node.root}' не определена")

        # Числа
        if node.root.isdigit():
            return int(node.root)
        # Строковые константы
        if node.root.startswith('"') and node.root.endswith('"'):
            return node.root.strip('"')
        # Арифметические операции в скобках
        if node.root == "()":
            # Выполняем содержимое скобок
            if len(node.children) == 1:
                return self.execute(node.children[0])
            else:
                raise ValueError("Скобки должны содержать только один дочерний узел.")
        # Блок кода
        if node.root == "{}":
            for child in node.children:
                self.execute(child)
            return None

        
        
        # По умолчанию
        raise ValueError(f"Неизвестный узел: {node.root}")

    def run(self):
        """
        Запуск интерпретации дерева.
        """
        return self.execute(self.tree)


class ReturnValue:
    """
    Вспомогательный класс для обработки оператора возврата.
    """
    def __init__(self, value):
        self.value = value


# Пример использования
if __name__ == "__main__":
    import json
    import indexing2tree

    # Подгружаем дерево из JSON (пример с вашим деревом)
    with open("tree.json", "r") as file:
        tree_data = json.load(file)

    # Преобразуем JSON в дерево
    def json_to_tree(data):
        node = indexing2tree.Tree(data["root"], data["index_start"], data["index_end"])
        node.children = [json_to_tree(child) for child in data.get("children", [])]
        node.children.sort(key=lambda x: x.index_start)
        return node

    root = json_to_tree(tree_data)

    # Интерпретация дерева
    interpreter = Interpreter(root)
    try:
        result = interpreter.run()
        print(f"Exit code: {result}")
    except Exception as e:
        print(f"Error: {str(e)}")