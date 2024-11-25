import ast
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
            print(*values,sep="",end="")
            return None

        if node.root == "input":
            # Читаем строку от пользователя
            for inp in node.children[0].children:
                user_input = input()
                try:
                    # Пробуем преобразовать ввод в число
                    if (self.variables[inp.root]["type"] == "int" or self.variables[inp.root]["type"] == "bool") and not user_input.isdigit():
                        raise TypeError(f"Аргумент должен быть int")
                    elif self.variables[inp.root]["type"] == "float":
                        try:
                            float(user_input)
                        except TypeError:
                            raise TypeError(f"Аргумент должен быть float")
                    else:
                        self.variables[inp.root]["value"] = f"\"{user_input}\""
                    self.variables[inp.root]["value"]=int(user_input) if user_input.isdigit() else float(user_input)
                except Exception as e:
                    raise TypeError(e)
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
        if node.root.startswith(("int", "float", "string", "bool","void")):
            # Проверяем, есть ли параметры и тело
            if len(node.children) == 2 and node.children[0].root == "()" and node.children[1].root == "{}":
                func_name = node.root.split()[1]  # Название функции
                self.functions[func_name] = node  # Сохраняем узел функции
                return func_name
            # Инициализируем переменные
            else:
                if node.root.startswith("int"):
                    var_name = node.root.split()[1]
                    self.variables[var_name] = {
                        "type": "int",
                        "value": 0
                    }
                    return var_name
                elif node.root.startswith("float"):
                    var_name = node.root.split()[1]
                    self.variables[var_name] = {
                        "type": "float",
                        "value": 0.0
                    }
                    return var_name
                elif node.root.startswith("string"):
                    var_name = node.root.split()[1]
                    self.variables[var_name] = {
                        "type": "string",
                        "value": "\"\""
                    }
                    return var_name
                elif node.root.startswith("bool"):
                    var_name = node.root.split()[1]
                    self.variables[var_name] = {
                        "type": "bool",
                        "value": False
                    }
                    return var_name

        # Вызов функции
        if node.root in self.functions:
            func_node = self.functions[node.root]
            param_nodes = func_node.children[0].children  # Параметры
            body_node = func_node.children[1]  # Тело функции

            # Подготавливаем локальные переменные
            args = [self.execute(arg) for arg in node.children[0].children]
            if len(args)!= len(param_nodes):
                raise ValueError(f"Неправильное количество аргументов функции '{node.root}', передано аргументов {len(args)}, ожидает {len(param_nodes)}")
            for i in range(len(args)):
                arg=args[i]
                param_type = param_nodes[i].root.split()[0]
                if param_type == "int" and not isinstance(arg, int):
                    raise TypeError(f"Аргумент 'int' функции '{node.root}' должен быть int, а получен {type(arg).__name__}")
                elif param_type == "float" and not isinstance(arg, (int,float)):
                    raise TypeError(f"Аргумент 'float' функции '{node.root}' должен быть float или int, а получен {type(arg).__name__}")
                elif param_type == "string" and not isinstance(arg, str):
                    raise TypeError(f"Аргумент'string' функции '{node.root}' должен быть str, а получен {type(arg).__name__}")
                elif param_type == "bool" and not isinstance(arg, bool):
                    raise TypeError(f"Аргумент 'bool' функции '{node.root}' должен быть bool, а получен {type(arg).__name__}")
            local_vars = {}
            for i,param in enumerate(param_nodes):
                local_vars[param.root.split()[1]] = {
                    "type": param.root.split()[0],
                    "value": args[i]
                }
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
                    self.variables[node.children[0].root]["value"] = eval(f"{left} {node.root[0]} {right}")
                    return self.variables[node.children[0].root]["value"]
                except:
                    raise NameError(f"Переменная '{node.children[0].root}' не определена")
            else:  # Арифметические операции
                left = self.execute(node.children[0])
                right = self.execute(node.children[1])
                return eval(f"{left} {node.root} {right}")

        # Присваивание
        if node.root == "=":
            var_name = node.children[0].root
            if var_name == "[]":
                value = self.execute(node.children[1])
                index = self.execute(node.children[0].children[1])
                self.variables[node.children[0].children[0].root]["value"][index] = value
            else:
                value = self.execute(node.children[1])
                if len(var_name.split())>1:
                    var_name = self.execute(node.children[0])
                self.variables[var_name]["value"] = value
            return value

        # Массивы
        if node.root == "[]":
            array_name = node.children[0].root
            if len(array_name.split())>1:
                typ,array_name = array_name.split()
                self.variables[array_name] = {
                    "type": typ,
                    "value":[None] * self.execute(node.children[1])
                }
                return None
            else:
                index = self.execute(node.children[1])
                return self.variables[array_name]["value"][index]

        if node.root == "[]=":
            array_name = node.children[0].root
            index = self.execute(node.children[1])
            value = self.execute(node.children[2])
            self.variables[array_name]["value"][index] = value
            return value

        # Переменные
        if node.root.isidentifier():
            if node.root in self.variables:
                return self.variables[node.root]["value"]
            else:
                raise NameError(f"Переменная '{node.root}' не определена")

        # Числа
        if node.root.isdigit():
            return int(node.root)
        # Строковые константы
        if node.root.startswith('"') and node.root.endswith('"'):
            
            stripped_value = ast.literal_eval(node.root)
            return stripped_value
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
    from indexing2tree import indexTree
    tree = indexTree(filepath="test.cpp")
    tree.analyze_index_json()
    tree.save_tree_to_json("tree.json")
    print("\n")
    print("-"*30)
    print("\n")
    # Подгружаем дерево из JSON
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