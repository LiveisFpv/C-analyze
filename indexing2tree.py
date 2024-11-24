from enum import Enum
import cpp2py
import sys
import matplotlib.pyplot as plt
import pydot
from networkx.drawing.nx_agraph import graphviz_layout
import networkx as nx
import json

sys.setrecursionlimit(1000000)

# Объявляем дерево для хранения информации о ключевых словах
class Tree:
    def __init__(self, root:any, index_start:int=0, index_end:int=0, children:list|None=None):
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
        if (tree.index_start == self.index_start and tree.index_end == self.index_end) or tree==None:
            pass
        else:
            self.children.append(tree)
    def sort_tree(self):
        if self.children is not None:
            self.children.sort(key = lambda x: x.index_start)
        for child in self.children:
            child.sort_tree()
    def __str__(self) -> str:
        return self.root

class indexTree(cpp2py.analysis_c_code):
    class operator_type(Enum):
        LEFT_RIGHT=1
        LEFT=2
        RIGHT=3
    with open("operators.json", "r") as file:
        __operators=json.load(file)
    with open("keywords.json", "r") as file:
        __keywords=json.load(file)
    # Конструктор для создания дерева индексации
    def __init__(self, string:str=None, filepath:str=None):
        super().__init__()
        self.funcs=["input","print"]
        self.__funcs_ind=[0,0]
        self.__tree = Tree("global")
        self.level = 0
        if filepath is not None:
            self.run_file(filepath)
        if string is not None:
            self.run_from_string(string)
        self.__index_json = self.analyze_results
        self.__tree.index_end = self.__index_json["delimiters"]["}"][len(self.__index_json["delimiters"]["}"])-1][0] + 2
        self.__index_list=[]
        self.__create_index_list(self.__index_json)
        self.__index_list.sort(key = lambda x: x[0])
        self.__local_index={}
        self.__create_local_index()
        print(self.__index_list)
        print(self.__local_index)
    
    #Для поиска левых и правых операндов
    def __create_index_list(self,json:dict,Type:str|None=None)-> None:
        if isinstance(json,dict):
            for type in json:
                if Type==None:
                    self.__create_index_list(json[type],type)
                else:
                    self.__create_index_list(json[type],Type)
        else:
            json.sort(key = lambda x: x[0])
            for value in json:
                self.__index_list.append([value[0],value[1],Type])
            
    def __create_local_index(self)-> None:
        index=0
        for el in self.__index_list:
            self.__local_index[el[0]] = index
            index+=1


    def analyze_index_json(self)-> None:
        """Запускает анализ JSON-файла и строит дерево программы"""
        self.__build_tree_identificators()
        self.__build_tree_keywords()
        self.__build_tree_delimiter(["{", "}"])
        self.__build_tree_identificators("build_in_func")
        self.__build_tree_delimiter(["(", ")"])
        self.__build_tree_operators()
        self.__build_tree_delimiter(["[", "]"])
        self.__build_tree_keywords(type=1)
        self.__build_tree_identificators("")
        self.__build_tree_literals()
        self.__build_tree_keywords(type=2)
        self.__tree.children.append(Tree("main",self.__tree.index_end-1,self.__tree.index_end-1,[Tree("()",self.__tree.index_end-1,self.__tree.index_end-1,[])]))

    def __get_node(self, node: Tree,re:bool=True)-> tuple[bool, Tree]:
        index_start=node.index_start
        index_end=node.index_end
        """Вспомогательный метод для поиска узла по индексу"""
        tree = self.__tree
        if tree.children is None:
            return None
        length=len(tree.children)
        i=0
        while i < length:
            child=tree.children[i]
            if (child.index_start <= index_start) and (index_start <= child.index_end):
                if index_end <= child.index_end:
                    tree = child
                    length=len(tree.children)
                    i=0
                else:
                    if re==True:
                        child_temp=child
                        node.add_child(child)
                        tree.children[i] = node
                        return True, None
                continue
            i+=1
        return False, tree

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
                    left_operand-=1
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
            elif self.__index_list[right_operand][1] =="{":
                right_operand+=1
                open=1
                while open>0:
                    right_operand+=1
                    if self.__index_list[right_operand][1]=="}":
                        open-=1
                    if self.__index_list[right_operand][1]=="{":
                        open+=1
            else:
                if self.__index_list[right_operand][2]not in ["identificators","literals"]:
                    right_operand-=1
        else:
            return None, None
        if left_operand==local_operator_index and self.__index_list[local_operator_index][1]=="*" and type==self.operator_type.LEFT_RIGHT:
            return None,None
        else:
            return left_operand, right_operand

    def __build_tree_delimiter(self, delimiter:list=["{", "}"])->None:
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
                if delimiter[0] == "[":
                    delimiter_start=self.__index_list[self.__local_index[delimiter_start[0]]-1]   
                leaf = Tree(delimiter[0]+delimiter[1], delimiter_start[0])
                leafs.append(leaf)
                index_start += 1

            else:
                leaf = leafs.pop()
                leaf.index_end = delimiter_end[0]+1
                index_end += 1
                nodes.append(leaf)

        while len(nodes) > 0:
            node = nodes.pop()
            rebuild,parent = self.__get_node(node)
            if not rebuild:
                parent.add_child(node)

            
    """
    Ищет ключевые слова, впоследствии идентификаторам должны присвоится их типы
    Функции должны получить тип возвращаемого значения
    Ключевые слова по типу if, for, while зависимые блоки {} и ()
    Также if for while будут иметь конечный индекс {}, а начальный собственный
    """
    def __build_tree_keywords(self,type:int=0)->None:

        func=["for", "while", "if","else","return"]
        keywords_list=self.__index_json["keywords"]

        if type==0:

            for keyword in keywords_list:

                if keyword[1]in func:
                    left_operand, right_operand=self.__find_operand(keyword[0], self.operator_type.RIGHT)
                    
                    if keyword[1]=="else":
                        left_delimiter=self.__index_list[left_operand+1]
                        right_operand=self.__index_list[right_operand]
                        left_operand=self.__index_list[left_operand]
                    else:
                        left_operand=self.__index_list[left_operand]
                        left_delimiter=self.__index_list[right_operand+1]
                        right_operand=self.__index_list[right_operand]

                    if right_operand[1]!="}":
                        _, right_operand=self.__find_operand(right_operand[0], self.operator_type.RIGHT)
                        right_operand=self.__index_list[right_operand]
                   
                    node=Tree(keyword[1],left_operand[0],right_operand[0]+len(right_operand[1]))
                    rebuild,parent = self.__get_node(node)
                    if not rebuild:
                        parent.add_child(node)
                    if right_operand[1]=="}":
                        node=Tree(left_delimiter[1]+right_operand[1],left_delimiter[0],right_operand[0]+len(right_operand[1]))
                        rebuild,parent = self.__get_node(node)
                        if not rebuild:
                            parent.add_child(node)

        elif type==1:

            for keyword in keywords_list:

                if keyword[1]not in func and keyword[1] not in self.__keywords["types"]:

                    node = Tree(keyword[1], keyword[0], keyword[0]+len(keyword[1]))
                    rebuild,parent = self.__get_node(node)
                    if not rebuild:
                        parent.add_child(node)
        elif type==2:
            for keyword in keywords_list:
                if keyword[1] in self.__keywords["types"] :

                    local_index=self.__local_index[keyword[0]]
                    comma=True
                    local_index+=1
                    kol=0
                    while self.__index_list[local_index][1]=="*":
                        local_index+=1
                        kol+=1
                    while self.__index_list[local_index][2] not in ['keywords']:
                        if self.__index_list[local_index][1]in[";","{"]:
                            break
                        elif self.__index_list[local_index][2]=="identificators" and comma:
                            _,tree=self.__get_node(Tree(self.__index_list[local_index][1],self.__index_list[local_index][0],
                                                 self.__index_list[local_index][0]+len(self.__index_list[local_index][1])))
                            tree.root=f"{keyword[1]+'*'*kol} {tree.root}"
                            comma=False
                        elif self.__index_list[local_index][1]==",":
                            comma=True
                        local_index+=1

    def __build_tree_operators(self)->None:

        operators_list=self.__index_json["operators"]

        for operator in operators_list:
            left_operand, right_operand=self.__find_operand(operator[0], self.operator_type.LEFT_RIGHT)
            if left_operand is None and right_operand is None:
                continue
            left_operand=self.__index_list[left_operand]
            right_operand=self.__index_list[right_operand]
            node=Tree(operator[1],left_operand[0],right_operand[0]+len(right_operand[1]))
            rebuild,parent = self.__get_node(node)
            if not rebuild:
                parent.add_child(node)

    def __build_tree_identificators(self,type:str="function")->None:

        identificators=self.__index_json["identificators"]

        for identifier in identificators:
            
            if type=="function":
                if identifier[1] in self.funcs:
                    continue
                left_operand, right_operand=self.__find_operand(identifier[0], self.operator_type.RIGHT)
                l_b=self.__index_list[left_operand+1]
                left_operand=self.__index_list[left_operand]
                left_delimiter=self.__index_list[right_operand+1]
                right_operand=self.__index_list[right_operand]
                if right_operand[1]!=")":
                    continue
                if right_operand[1]!="}":
                    _, right_operand=self.__find_operand(right_operand[0], self.operator_type.RIGHT)
                    right_operand=self.__index_list[right_operand]
                node=Tree(identifier[1],left_operand[0],right_operand[0]+len(right_operand[1]))
                rebuild,parent = self.__get_node(node)
                if not rebuild:
                    parent.add_child(node)
                node=Tree(left_delimiter[1]+right_operand[1],left_delimiter[0],right_operand[0]+len(right_operand[1]))
                rebuild,parent = self.__get_node(node)
                if not rebuild:
                    parent.add_child(node)
                self.funcs.append(identifier[1])
                self.__funcs_ind.append(identifier[0])
            
            elif type=="build_in_func":
                left_operand, right_operand=self.__find_operand(identifier[0], self.operator_type.RIGHT)
                l_b=self.__index_list[left_operand+1]
                left_operand=self.__index_list[left_operand]
                left_delimiter=self.__index_list[right_operand+1]
                right_operand=self.__index_list[right_operand]
                if identifier[1] in self.funcs and identifier[0]!=self.__funcs_ind[self.funcs.index(identifier[1])]:
                    node=Tree(identifier[1],left_operand[0],right_operand[0]+len(right_operand[1]),[Tree("()",l_b[0],right_operand[0]+1)])
                    rebuild,parent = self.__get_node(node)
                    if not rebuild:
                        parent.add_child(node)
                    continue
            
            else:
                left_operand, right_operand=self.__find_operand(identifier[0], self.operator_type.RIGHT)
                left_operand=self.__index_list[left_operand]
                right_operand=self.__index_list[right_operand]
                if right_operand[1]==")":
                    continue
                node = Tree(identifier[1], identifier[0], identifier[0]+len(identifier[1]))
                rebuild,parent = self.__get_node(node)
                if not rebuild:
                    parent.add_child(node)
    
    def __build_tree_literals(self)->None:

        identificators=self.__index_json["literals"]

        for identifier in identificators:
            node = Tree(identifier[1], identifier[0], identifier[0]+len(identifier[1]))
            rebuild,parent = self.__get_node(node)
            if not rebuild:
                parent.add_child(node)

    def visualize_tree_by_levels(self) -> None: 
        self.__tree.sort_tree()
        """Метод для визуализации дерева по уровням"""
        G = nx.DiGraph()
        G1=nx.DiGraph()

        # Вспомогательная функция для добавления узлов и рёбер в граф
        def add_edges(node, parent=None, level=0):
            #label = f"{node.root} {node.index_start} {node.index_end}"
            label = f"{node.root}|{node.index_start}"
            G.add_node(label)
            G1.add_node(label.replace("|","\n\n"))
            if parent is not None:
                G.add_edge(parent, label)
                G1.add_edge(parent.replace("|","\n\n"), label.replace("|","\n\n"))
            for child in node.children:
                add_edges(child, label, level + 1)

        # Строим граф
        add_edges(self.__tree)
        # Используем Graphviz для автоматической компоновки
        pos = graphviz_layout(G,prog="dot")
        pos1={}
        for i in pos:
            pos1[i.replace("|","\n\n")]=pos[i]
        # Настройка визуализации
        plt.figure(figsize=(12, 8))
        nx.draw(G1, pos1, with_labels=True, node_size=1500, node_color='lightgray', font_size=7, arrows=True)
        plt.title("Tree Visualization by Levels (Centered)")
        plt.show()
    def print_tree(self):
        print(self.__tree)
    def tree_to_dict(self,node):
        """Преобразование дерева в словарь."""
        return {
            "root": node.root,
            "index_start": node.index_start,
            "index_end": node.index_end,
            "children": [self.tree_to_dict(child) for child in node.children],
        }

    def save_tree_to_json(self, filepath):
        """Сохранение дерева в JSON файл."""
        tree_dict = self.tree_to_dict(self.__tree)
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(tree_dict, file, indent=4, ensure_ascii=False)




if __name__ == "__main__":
    # Создаем дерево индексации
    tree = indexTree(filepath="test.cpp")
    tree.analyze_index_json()
    tree.save_tree_to_json("tree.json")
    # tree.visualize_tree_by_levels()
    
