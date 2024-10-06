import json
import asyncio
import re
from enum import Enum

#Используем асинхронную среду для будущего анализа нескольких файлов одновременно
class analysis_c_code():
    # Все типы данных
    class __Types(Enum):
        identificators=1
        keywords=2
        delimiters=3
        operators=4
        literals=5
        comments=6
        preprocess=7
    __suffixes = ['.cpp', '.c', '.cxx', '.c++', '.cc', '.h', '.hpp', '.hxx', '.h++']
    with open("keywords.json", "r") as file:
        __keywords=json.load(file)
    with open("delimiters.json", "r") as file:
        __delimiters=json.load(file)
    with open("operators.json", "r") as file:
        __operators=json.load(file)
    with open("literals.json", "r") as file:
        __literals=json.load(file)
    
    def __init__(self):
        self.analyze_results ={"preprocess":[],
                               "identificators":[],
                               "keywords":{
                                   
                               },
                               "delimiters":{
                                   
                               },
                               "operators":{
                                   
                               },
                               "literals":[],
                               "comments":[]}
        for delimiter in self.__delimiters["delimiters"]:
            self.analyze_results["delimiters"][delimiter]=[]
        for operator_len in self.__operators:
            for operator_type in self.__operators[operator_len]:
                for operator in self.__operators[operator_len][operator_type]:
                    self.analyze_results["operators"][operator]=[]
        for keywords in self.__keywords:
            for keyword in self.__keywords[keywords]:
                self.analyze_results["keywords"][keyword]=[]
    
    
    def get_result(self):
        json_string = json.dumps(self.analyze_results, ensure_ascii=False, indent=4)
        return json_string
    
    def __beautiful_text(self):
        # Выводим текст в красивом виде
        output=""
        self.file_content=self.file_content_copy
        indexstart=0
        indexend=self.file_content.find('\n', indexstart+1)
        dictionary={}
        n=1
        for result_type, results in self.analyze_results.items():
                for result in results:
                    dictionary[result[0]]=[result_type, result[1]]
        while indexstart!=-1 or indexend<len(self.file_content):
            if indexend==-1:
                indexend=len(self.file_content)
                output += "\n"+str(n)+". "+self.file_content[indexstart:indexend]
                for i in range(indexstart, indexend):
                    if i in dictionary:
                        output += "\n    "+dictionary[i][0][:-1]+"-"+dictionary[i][1]
                break
            else:
                output += "\n"+str(n)+". "+self.file_content[indexstart:indexend]
                for i in range(indexstart, indexend+1):
                    if i in dictionary:
                        output += "\n    "+dictionary[i][0][:-1]+"-"+dictionary[i][1]
                n+=1
                indexstart=indexend+1
                indexend=self.file_content.find('\n', indexstart)
        return output

    # Запускаем обработку текста
    def run_from_string(self,string):
        self.file_content = string
        self.file_content_copy=string
        self.__analyze_code()
    
    # Запускаем основной цикл
    def run_file(self,file_path):
        self.file_path = file_path
        self.file_content_output = ""
        self.file_path_output = ""
        self.file_content = self.__read_file()
        self.file_content_copy=self.file_content
        self.__analyze_code()
        self.__write_json_file()
        #self._write_file(self.__beautiful_text())

    #Считывание из файла с допустимыми расширениями
    #Считываем файл с программой на языке C++
    def __read_file(self):
        read=False
        for suffix in self.__suffixes:
            if suffix in self.file_path:
                with open(self.file_path, 'r',encoding='utf-8') as file:
                    read=True
                    # путь до итогового файла
                    self.file_path_output=self.file_path.replace(suffix,".txt")
                    return file.read()
        if read is False:
            print("File format not supported")
            return ""

    def __replace_substring(self,original_string, start_index, end_index, replacement):
    # Формируем новую строку, используя срезы
        new_string = original_string[:start_index] + replacement + original_string[end_index:]
        return new_string
    
    # Запись результирующего json
    def __write_json_file(self):
        with open(self.file_path_output.replace(".txt",".json"), 'w', encoding='utf-8') as file:
            json.dump(self.analyze_results, file, ensure_ascii=False, indent=4)  # Используем параметры для форматирования и кодировки
        json_string = json.dumps(self.analyze_results, ensure_ascii=False, indent=4)
        print(json_string)

    #Просто запись в файл, больше и сказать нечего
    def _write_file(self,output):
        self.file_content_output=output
        with open(self.file_path_output, 'w') as file:
            file.write(self.file_content_output)
    
    # Исключаем из рассмотрения include и define
    def __analyze_preprocess(self):
        type=self.__Types.preprocess
        indexstart = self.file_content.find("#include")
        while indexstart != -1:
            indexend = sorted([self.file_content.find("\"",self.file_content.find("\"",indexstart)+1)+1,self.file_content.find(">",indexstart)+1,self.file_content.find("\n",indexstart)+1,len(self.file_content)])
            for i in indexend:
                if i !=0:
                    self.__add_to_json(type,indexstart,i)
                    self.file_content=self.__replace_substring(self.file_content,indexstart,i," "*(i-indexstart))
                    break

            indexstart = self.file_content.find("#include")
    # В последствии можно будет заменять define в коде    
        indexstart = self.file_content.find("#define")
        while indexstart != -1:
            indexend = sorted([self.file_content.find("/",indexstart),self.file_content.find("\n",indexstart),len(self.file_content),self.file_content.find(" ",indexstart)])
            for i in indexend:
                if i !=-1:
                    self.__add_to_json(type,indexstart,i)
                    self.file_content=self.__replace_substring(self.file_content,indexstart,i," "*(i-indexstart))
                    break
            indexstart = self.file_content.find("#define")
    # Удаляем не нужное    
        indexstart = self.file_content.find("#pragma")
        while indexstart != -1:
            indexend = sorted([self.file_content.find("/",indexstart),self.file_content.find("\n",indexstart),self.file_content.find(" ",indexstart)])
            for i in indexend:
                if i !=-1:
                    self.__add_to_json(type,indexstart,i)
                    self.file_content=self.__replace_substring(self.file_content,indexstart,i," "*(i-indexstart))
                    break
            indexstart = self.file_content.find("#pragma")

    # Индексируем все по категориям в Json файл
    def __add_to_json(self,type,indexstart,indexend,key=None):
        if key!=None:
            self.analyze_results[type.name][key].append([indexstart,self.file_content[indexstart:indexend]])
        else:
            self.analyze_results[type.name].append([indexstart,self.file_content[indexstart:indexend]])
    
    #Поиск комментариев в исходном коде
    def __analyze_comments(self):
        type=self.__Types.comments
        index=0
        while index < len(self.file_content)-1:
            #Однострочные комментарии
            if self.file_content[index]=="/" and self.file_content[index+1]=="/":
                indexend = self.file_content.find("\n",index)
                if indexend!= -1:
                    self.__add_to_json(type,index,indexend)
                    self.file_content=self.__replace_substring(self.file_content,index,indexend," "*(indexend-index))
                    index=indexend
                else:
                    indexend=len(self.file_content)
                    self.__add_to_json(type,index,indexend)
                    self.file_content=self.__replace_substring(self.file_content,index,indexend," "*(indexend-index))
                    index=indexend
            #Многострочные комментарии        
            elif self.file_content[index]=="/" and self.file_content[index+1]=="*":
                indexend = self.file_content.find("*/",index)
                if indexend!= -1:
                    self.__add_to_json(type,index,indexend+2)
                    self.file_content=self.__replace_substring(self.file_content,index,indexend+2," "*(indexend+2-index))
                    index=indexend+2
                else:
                    indexend=len(self.file_content)
                    self.__add_to_json(type,index,indexend)
                    self.file_content=self.__replace_substring(self.file_content,index,indexend," "*(indexend-index))
                    index=indexend
            else:
                index+=1
    
    def __analyze_keywords(self):
        type=self.__Types.keywords
        for keyword_type in self.__keywords:
            for keyword in self.__keywords[keyword_type]:
                indexstart=self.file_content.find(keyword)
                while indexstart!=-1:
                    indexend = indexstart + len(keyword)
                    if len(re.findall(r'[A-Za-zА-Яа-яёЁ_]',self.file_content[indexstart-1]))==0:
                        self.__add_to_json(type,indexstart,indexend,keyword)
                        self.file_content=self.__replace_substring(self.file_content,indexstart,indexend," "*(indexend-indexstart))
                    indexstart=self.file_content.find(keyword,indexend)
        pass
    
    def __analyze_delimiters(self):
        type=self.__Types.delimiters
        for delimiter in self.__delimiters["delimiters"]:
            indexstart=self.file_content.find(delimiter)
            while indexstart!=-1:
                indexend = indexstart + len(delimiter)
                self.__add_to_json(type,indexstart,indexend,delimiter)
                self.file_content=self.__replace_substring(self.file_content,indexstart,indexend," "*(indexend-indexstart))
                indexstart=self.file_content.find(delimiter,indexend)
    
    def __analyze_operators(self):
        type=self.__Types.operators
        for operator_len in self.__operators:
            for operator_type in self.__operators[operator_len]:
                for operator in self.__operators[operator_len][operator_type]:
                    indexstart=self.file_content.find(operator)
                    while indexstart!=-1:
                        indexend = indexstart + len(operator)
                        self.__add_to_json(type,indexstart,indexend,operator)
                        self.file_content=self.__replace_substring(self.file_content,indexstart,indexend," "*(indexend-indexstart))
                        indexstart=self.file_content.find(operator,indexend)
    
    def __analyze_identificators(self):
        type=self.__Types.identificators
        # Регулярное выражение для поиска всех слов
        pattern = r'\b[\wa-zA-Zа-яА-ЯёЁ_0-9]+\b'

        # Используем finditer для поиска всех слов и их начальных индексов
        matches = re.finditer(pattern, self.file_content)

        # Выводим все найденные слова и их индексы
        for match in matches:
            word = match.group()  # Слово
            start_index = match.start()  # Индекс первого символа слова
            self.__add_to_json(type,start_index,start_index+len(word))
            self.file_content=self.file_content.replace(match.group(), " "*len(match.group()),1)
            #print(word)

    def __find_numeric_literals(self):
        # Регулярное выражение для поиска числовых литералов
        numeric_regex = r'-?\b\d+(\.\d+)?([eE][-+]?\d+)?\b'

        # Найти все совпадения числовых литералов
        numeric_literals = re.finditer(numeric_regex, self.file_content)
        return numeric_literals
    def __analyze_literals(self):
        type=self.__Types.literals
        #Находим все остальные литералы
        for literal in self.__literals["literals"]:
            indexstart=self.file_content.find(literal)
            while indexstart!=-1:
                if literal=="\"" or literal=="\'":
                    indexend = self.file_content.find(literal,indexstart+1)+1
                else:
                    indexend=indexstart+len(literal)
                if indexend!=0:
                    self.__add_to_json(type,indexstart,indexend)
                    self.file_content=self.__replace_substring(self.file_content,indexstart,indexend," "*(indexend-indexstart))
                else:
                    break
                indexstart=self.file_content.find(literal,indexend)
        #Находим все цифры
        numeric_literals=self.__find_numeric_literals()
        #print(numeric_literals)
        #Отсеиваем среди них цифровые литералы
        for match in numeric_literals:
            number = match.group()  # Найденный числовой литерал
            indexstart = match.start()  # Индекс первого символа числового литерал
            indexend = indexstart+len(number)
            #print(re.findall(r'[A-Za-zА-Яа-яёЁ_]',self.file_content[indexstart-1]))
            if len(re.findall(r'[A-Za-zА-Яа-яёЁ_]',self.file_content[indexstart-1]))==0:
                self.__add_to_json(type,indexstart,indexend)
                self.file_content=self.__replace_substring(self.file_content,indexstart,indexend," "*(indexend-indexstart))


    #Анализируем код в порядке шапка-комментарии-литералы-операторы-блоки-ключ слова-идентификаторы
    def __analyze_code(self):
        self.__analyze_preprocess()
        #print(self.file_content)
        self.__analyze_comments()
        #print(self.file_content)
        self.__analyze_literals()
        #print(self.file_content)
        self.__analyze_operators()
        #print(self.file_content)
        self.__analyze_delimiters()
        #print(self.file_content)
        self.__analyze_keywords()
        #print(self.file_content)
        self.__analyze_identificators()
        #print(self.file_content)
        #self.write_file()
        #print(self.analyze_results)
        #self.write_json_file()

if __name__ == "__main__":
    def main():
        c2py=analysis_c_code()
        c2py.run_file("test.cpp")
    # Запуск основного цикла событий
    asyncio.run(main())