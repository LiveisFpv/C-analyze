import interface
import cpp2py
import sys
import asyncio
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtGui import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtPrintSupport import *
from qasync import QEventLoop

class JsonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)

        # Определение стилей для подсветки
        self.keyword_format = QTextCharFormat()
        self.keyword_format.setForeground(QColor("blue"))

        self.string_format = QTextCharFormat()
        self.string_format.setForeground(QColor("green"))

        self.number_format = QTextCharFormat()
        self.number_format.setForeground(QColor("magenta"))

        self.boolean_format = QTextCharFormat()
        self.boolean_format.setForeground(QColor("red"))

        self.null_format = QTextCharFormat()
        self.null_format.setForeground(QColor("gray"))

        # Определение правил подсветки синтаксиса
        self.rules = [
            (r'"[^"\\]*(\\.[^"\\]*)*"', self.string_format),  # Строки
            (r'\b\d+(\.\d+)?([eE][-+]?\d+)?\b', self.number_format),  # Числа
            (r'\btrue\b|\bfalse\b', self.boolean_format),  # Логические значения
            (r'\bnull\b', self.null_format)  # null
        ]

    def highlightBlock(self, text):
        # Применение правил подсветки к каждому блоку текста
        for pattern, text_format in self.rules:
            expression = QtCore.QRegularExpression(pattern)
            match_iterator = expression.globalMatch(text)

            while match_iterator.hasNext():
                match = match_iterator.next()
                start = match.capturedStart()
                length = match.capturedLength()
                self.setFormat(start, length, text_format)

class Cpp2py(interface.Ui_MainWindow, QMainWindow):
    def __init__(self, parent=None):
        super(Cpp2py, self).__init__(parent)
        self.setupUi(self)
        self.setup_run()

        # Применение подсветки синтаксиса JSON к ResultTextBrowser
        self.json_highlighter = JsonHighlighter(self.ResultTextBrowser.document())

    def setup_run(self):
        self.Open.triggered.connect(self.open_task)
        self.Save.triggered.connect(self.save_task)
        self.CodeTextEdit.textChanged.connect(self.analyze_task)

    def open_task(self):
        # Открываем диалоговое окно для выбора файла
        file_name = QFileDialog.getOpenFileName(self, "Open File", "", "C/C++ files (*.cpp *.c)")
        if file_name[0]:
            # Получаем имя файла и открываем его
            file = open(file_name[0], 'r', encoding="utf-8")
            # Получаем содержимое файла
            content = file.read()
            # Закрываем файл
            file.close()
            # Выводим код на экран
            self.CodeTextEdit.setPlainText(content)
            asyncio.create_task(self.start_analyze())
    def analyze_task(self):
        # Запускаем анализ кода в отдельном потоке
        asyncio.create_task(self.start_analyze())
    async def start_analyze(self):
        # Получаем текст кода
        code = self.CodeTextEdit.toPlainText()
        # Преобразуем текст кода в ликсемы
        c2py = cpp2py.analysis_c_code()
        await c2py.run_from_string(code)
        # Выводим результаты анализа
        result = await c2py.get_result()
        self.ResultTextBrowser.setPlainText(result)
    
    def save_task(self):
        # Открываем диалоговое окно для сохранения файла
        file_name = QFileDialog.getSaveFileName(self, "Save File", "", "txt files (*.txt)")
        if file_name[0]:
            # Получаем текст кода
            code = self.ResultTextBrowser.toPlainText()
            # Записываем текст в файл
            with open(file_name[0], 'w', encoding="utf-8") as file:
                file.write(code)

async def main():
    # Создаем приложение PyQt6
    app = QApplication(sys.argv)

    # Создаем основной объект окна
    window = Cpp2py()
    window.show()

    # Запускаем цикл событий asyncio совместно с PyQt6
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    
    with loop:
        loop.run_forever()

if __name__ == "__main__":
    asyncio.run(main())