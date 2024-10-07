from enum import Enum
import cpp2py
import sys
import matplotlib.pyplot as plt
import networkx as nx
import json

sys.setrecursionlimit(1000000)

class Tree:
    def __init__(self, root, index_start=0, index_end=0, children=None):
        self.root = root
        self.index_start = index_start
        self.index_end = index_end
        self.children = children if children else []

    def add_child(self, tree):
        self.children.append(tree)

    def __str__(self):
        return self.root


class OperatorTree(Tree):
    def __init__(self, root, index_start=0, index_end=0, children=None):
        super().__init__(root, index_start, index_end, children)

    # Метод добавления операторов будет расширен, если нужны приоритеты.
    def add_child(self, tree):
        super().add_child(tree)


class IndexTree(cpp2py.analysis_c_code):
    class OperatorType(Enum):
        LEFT_RIGHT = 1
        LEFT = 2
        RIGHT = 3

    with open("operators.json", "r") as file:
        __operators = json.load(file)

    with open("keywords.json", "r") as file:
        __keywords = json.load(file)

    def __init__(self, string=None, filepath=None):
        super().__init__()
        self.__tree = Tree("global")
        self.level = 0
        if filepath:
            self.run_file(filepath)
        if string:
            self.run_from_string(string)

        self.__index_json = self.analyze_results
        self.__tree.index_end = self.__index_json["delimiters"]["}"][-1][0] + 1
        self.__index_list = []
        self.__create_index_list(self.__index_json)
        self.__index_list.sort(key=lambda x: x[0])
        self.__local_index = {}
        self.__create_local_index()

    def __create_index_list(self, json_data, Type=None):
        """Создает список индексов с типами (ключевые слова, операторы и т.д.)"""
        if isinstance(json_data, dict):
            for type_ in json_data:
                self.__create_index_list(json_data[type_], type_)
        else:
            json_data.sort(key=lambda x: x[0])
            for value in json_data:
                self.__index_list.append([value[0], value[1], Type])

    def __create_local_index(self):
        """Создает локальный индекс для быстрого поиска по индексам"""
        for idx, el in enumerate(self.__index_list):
            self.__local_index[el[0]] = idx

    def __get_node(self, index):
        """Получает узел для данного индекса"""
        tree = self.__tree
        while tree.children:
            for child in tree.children:
                if child.index_start <= index <= child.index_end:
                    tree = child
                    break
            else:
                break
        return tree

    def __find_operand(self, index_start, operator_type):
        """Находит левые и правые операнды для оператора"""
        local_operator_index = self.__local_index[index_start]
        left_operand = right_operand = local_operator_index

        if operator_type in {self.OperatorType.LEFT, self.OperatorType.LEFT_RIGHT}:
            left_operand = local_operator_index - 1
            if self.__index_list[left_operand][1] in [")", "]"]:
                left_operand = self.__process_brackets(left_operand, is_left=True)
            else:
                if self.__index_list[left_operand][2] not in ["identificators", "literals"]:
                    left_operand += 1

        if operator_type in {self.OperatorType.RIGHT, self.OperatorType.LEFT_RIGHT}:
            right_operand = local_operator_index + 1
            if self.__index_list[right_operand][1] in ["("]:
                right_operand = self.__process_brackets(right_operand)
            elif self.__index_list[right_operand + 1][1] == "[":
                right_operand = self.__process_brackets(right_operand, is_array=True)
            elif self.__index_list[right_operand][1] == "{":
                right_operand = self.__process_brackets(right_operand, is_curly=True)
            else:
                if self.__index_list[right_operand][2] not in ["identificators", "literals"]:
                    right_operand -= 1

        return left_operand, right_operand

    def __process_brackets(self, operand, is_left=False, is_array=False, is_curly=False):
        """Обрабатывает операнды в скобках и возвращает конечный индекс"""
        if is_left:
            close = 1
            while close > 0:
                operand -= 1
                if self.__index_list[operand][1] in [")", "]"]:
                    close += 1
                elif self.__index_list[operand][1] in ["(", "["]:
                    close -= 1
        else:
            open_count = 1
            while open_count > 0:
                operand += 1
                if self.__index_list[operand][1] in [")", "]", "}"]:
                    open_count -= 1
                elif self.__index_list[operand][1] in ["(", "[", "{"]:
                    open_count += 1
        return operand

    def analyze_index_json(self):
        """Анализирует JSON и строит дерево программы"""
        self.__build_tree_keywords()
        self.__build_tree_operators()
        self.__build_tree_identificators()
        self.__build_tree_literals()

    def __build_tree_keywords(self):
        """Строит поддеревья для ключевых слов"""
        for keyword in self.__index_json["keywords"]:
            left_operand, right_operand = self.__find_operand(keyword[0], self.OperatorType.RIGHT)
            node = Tree(keyword[1], self.__index_list[left_operand][0], self.__index_list[right_operand][0] + len(self.__index_list[right_operand][1]))
            parent = self.__get_node(node.index_start)
            parent.add_child(node)

    def __build_tree_operators(self):
        """Строит поддеревья для операторов"""
        for operator in self.__index_json["operators"]:
            left_operand, right_operand = self.__find_operand(operator[0], self.OperatorType.LEFT_RIGHT)
            node = Tree(operator[1], self.__index_list[left_operand][0], self.__index_list[right_operand][0] + len(self.__index_list[right_operand][1]))
            parent = self.__get_node(node.index_start)
            parent.add_child(node)

    def __build_tree_identificators(self):
        """Строит поддеревья для идентификаторов"""
        for identifier in self.__index_json["identificators"]:
            left_operand, right_operand = self.__find_operand(identifier[0], self.OperatorType.RIGHT)
            node = Tree(identifier[1], self.__index_list[left_operand][0], self.__index_list[right_operand][0] + len(self.__index_list[right_operand][1]))
            parent = self.__get_node(node.index_start)
            parent.add_child(node)

    def __build_tree_literals(self):
        """Строит поддеревья для литералов"""
        for literal in self.__index_json["literals"]:
            node = Tree(literal[1], literal[0], literal[0] + len(literal[1]))
            parent = self.__get_node(node.index_start)
            parent.add_child(node)

    def visualize_tree_by_levels(self):
        """Метод для визуализации дерева по уровням"""
        G = nx.DiGraph()

        def add_edges(node, parent=None, level=0, pos={}, level_pos={}):
            label = f"{node.root}\n{node.index_start}\n{node.index_end}"
            G.add_node(label)

            if parent is not None:
                G.add_edge(parent, label)

            if level not in level_pos:
                level_pos[level] = 0
            pos[label] = (level_pos[level], -level)
            level_pos[level] += 1

            for child in node.children:
                add_edges(child, label, level + 1, pos, level_pos)

        pos = {}
        add_edges(self.__tree, pos=pos, level_pos={})

        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue', font_size=7, arrows=True)
        plt.title("Tree Visualization by Levels")
        plt.show()


if __name__ == "__main__":
    tree = IndexTree(filepath="test.cpp")
    tree.analyze_index_json()
    tree.visualize_tree_by_levels()
