from enum import Enum
import cpp2py
import sys
import matplotlib.pyplot as plt
import networkx as nx
import json

sys.setrecursionlimit(1000000)

# Объявляем дерево для хранения информации о ключевых словах
class Tree:
    def __init__(self, root, index_start=0, index_end=0, children=None):
        self.root = root
        if children is None:
            self.children = []
        else:
            self.children = children
        self.index_start = index_start
        self.index_end = index_end

    def add_child(self, tree):
        if self.children is None:
            self.children = []
        self.children.append(tree)

    def __str__(self) -> str:
        return self.root

class operator_Tree(Tree):
    def __init__(self,root, index_start=0, index_end=0, children=None):
        super().__init__(root, index_start, index_end, children)
    #Добавляем операции в порядке приоритетов
    def add_child(self,tree):
        pass

class indexTree(cpp2py.analysis_c_code):
    class operator_type(Enum):
        LEFT_RIGHT=1
        LEFT=2
        RIGHT=3
    with open("operators.json", "r") as file:
        __operators=json.load(file)
    # Конструктор для создания дерева индексации
    def __init__(self, string=None, filepath=None):
        super().__init__()
        self.__tree = Tree("global")
        self.level = 0
        if filepath is not None:
            self.run_file(filepath)
        if string is not None:
            self.run_from_string(string)
        self.__index_json = self.analyze_results
        self.__tree.index_end = self.__index_json["delimiters"]["}"][len(self.__index_json["delimiters"]["}"])-1][0] + 1
        self.__index_list=[]
        self.__create_index_list(self.__index_json)
        self.__index_list.sort(key = lambda x: x[0])
        self.__local_index={}
        self.__create_local_index()
        print(self.__index_list)
        print(self.__local_index)
    
    #Для поиска левых и правых операндов
    def __create_index_list(self,json,Type=None):
        if isinstance(json,dict):
            for type in json:
                if Type==None:
                    self.__create_index_list(json[type],type)
                else:
                    self.__create_index_list(json[type],Type)
        else:
            for value in json:
                self.__index_list.append([value[0],value[1],Type])
            
    def __create_local_index(self):
        index=0
        for el in self.__index_list:
            self.__local_index[el[0]] = index
            index+=1


    def analyze_index_json(self):
        """Запускает анализ JSON-файла и строит дерево программы"""
        self.__build_tree_delimiter(["{", "}"])
        self.__build_tree_keywords()
        self.__build_tree_delimiter(["(", ")"])
        self.__build_tree_operators()
        self.__build_tree_delimiter(["[", "]"])
        self.__build_tree_identificators()
        self.__build_tree_literals()

    def __get_node(self, index):
        tree = self.__tree
        """Вспомогательный метод для поиска узла по индексу"""
        if tree.children is None:
            return None
        length=len(tree.children)
        i=0
        while i < length:
            child=tree.children[i]
            if (child.index_start <= index) and (index <= child.index_end):
                tree = child
                length=len(tree.children)
                i=0
                continue
            i+=1
        return tree

    def __build_tree_delimiter(self, delimiter=["{", "}"]):
        """Основной метод для разбора программы и построения дерева"""
        delimiters = self.__index_json["delimiters"]
        length = len(delimiters[delimiter[0]])
        index_start = 0
        index_end = 0
        leafs = []
        nodes = []

        while index_start < length or index_end < length:
            if index_start < length:
                delimiter_start = delimiters[delimiter[0]][index_start]
            if index_end < length:
                delimiter_end = delimiters[delimiter[1]][index_end]

            if index_start < length and delimiter_start[0] < delimiter_end[0]:
                # Создаем узел для нового блока {}
                leaf = Tree(delimiter[0]+delimiter[1], delimiter_start[0])
                leafs.append(leaf)
                index_start += 1
            else:
                leaf = leafs.pop()
                leaf.index_end = delimiter_end[0]
                index_end += 1
                nodes.append(leaf)
        while len(nodes) > 0:
            node = nodes.pop()
            parent = self.__get_node(node.index_start)
            parent.add_child(node)
    """
    Ищет ключевые слова, впоследствии идентификаторам должны присвоится их типы
    Функции должны получить тип возвращаемого значения
    Ключевые слова по типу if, for, while зависимые блоки {} и ()
    Также if for while будут иметь конечный индекс {}, а начальный собственный
    """
    def __build_tree_keywords(self):
        keywords_list=self.__index_json["keywords"]
        for keyword in keywords_list:
            pass
    """
    Ищет оператор, индекс начала для оператора будет его крайний левый операнд, а конца крайний правый операнд
    В последстивие операнды станут потомками, для скобок необходима впоследствие пересборка дерева
    """
    def __find_operand(self,index_start:int,type:operator_type)-> list:
        local_operator_index=self.__local_index[index_start]
        left_operand=local_operator_index
        right_operand=local_operator_index
        if type==self.operator_type.LEFT or type==self.operator_type.LEFT_RIGHT:
            left_operand=local_operator_index-1
            if self.__index_list[left_operand][1] in [")","]"]:
                close=1
                if self.__index_list[left_operand][1]==")":
                    while close>0:
                        left_operand-=1
                        if self.__index_list[left_operand][1]==")":
                            close+=1
                        if self.__index_list[left_operand][1]=="(":
                            close-=1
                else:
                    while close>0:
                        left_operand-=1
                        if self.__index_list[left_operand][1]=="]":
                            close+=1
                        if self.__index_list[left_operand][1]=="[":
                            close-=1
            else:
                if self.__index_list[left_operand][2] not in ["identificators","literals"]:
                    left_operand+=1
        if type==self.operator_type.RIGHT or type==self.operator_type.LEFT_RIGHT:
            right_operand=local_operator_index+1
            if self.__index_list[right_operand][1] in ["("]:
                open=1
                while open>0:
                    right_operand+=1
                    if self.__index_list[right_operand][1]==")":
                        open-=1
                    if self.__index_list[right_operand][1]=="(":
                        open+=1
            elif self.__index_list[right_operand+1][1]=="[":
                right_operand+=1
                open=1
                while open>0:
                    right_operand+=1
                    if self.__index_list[right_operand][1]=="]":
                        open-=1
                    if self.__index_list[right_operand][1]=="[":
                        open+=1
            else:
                if self.__index_list[right_operand][2]not in ["identificators","literals"]:
                    right_operand-=1
        else:
            return None, None
        return left_operand, right_operand

    def __build_tree_operators(self):
        operators_list=self.__index_json["operators"]
        for operator in operators_list:
            left_operand, right_operand=self.__find_operand(operator[0], self.operator_type.LEFT_RIGHT)
            left_operand=self.__index_list[left_operand]
            right_operand=self.__index_list[right_operand]
            node=Tree(operator[1],left_operand[0],right_operand[0])
            parent = self.__get_node(node.index_start)
            parent.add_child(node)

    def __build_tree_identificators(self):
        identificators=self.__index_json["identificators"]
        for identifier in identificators:
            node = Tree(identifier[1], identifier[0], identifier[0])
            parent = self.__get_node(node.index_start)
            parent.add_child(node)
    def __build_tree_literals(self):
        identificators=self.__index_json["literals"]
        for identifier in identificators:
            node = Tree(identifier[1], identifier[0], identifier[0])
            parent = self.__get_node(node.index_start)
            parent.add_child(node)

    def visualize_tree_by_levels(self):
        """Метод для визуализации дерева по уровням"""
        G = nx.DiGraph()

        # Вспомогательная функция для добавления узлов и рёбер в граф
        def add_edges(node, parent=None, level=0, pos={}, level_pos={}):
            label = f"{node.root}\n{node.index_start}\n{node.index_end}"
            G.add_node(label)

            if parent is not None:
                G.add_edge(parent, label)

            if level not in level_pos:
                level_pos[level] = 0
            pos[label] = (level_pos[level], -level)
            level_pos[level] += 1  # Увеличиваем позицию для следующего узла на этом уровне

            for child in node.children:
                add_edges(child, label, level + 1, pos, level_pos)

        # Строим граф
        pos = {}
        add_edges(self.__tree, pos=pos, level_pos={})

        # Настройка визуализации
        plt.figure(figsize=(12, 8))
        nx.draw(G, pos, with_labels=True, node_size=1000, node_color='lightblue', font_size=7, arrows=True)
        plt.title("Tree Visualization by Levels")
        plt.show()

if __name__ == "__main__":
    # Создаем дерево индексации
    tree = indexTree(filepath="test.cpp")
    tree.analyze_index_json()
    tree.visualize_tree_by_levels()
