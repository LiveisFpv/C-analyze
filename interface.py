# Form implementation generated from reading ui file '.\interface.ui'
#
# Created by: PyQt6 UI code generator 6.6.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1016, 715)
        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.CodeTextEdit = QtWidgets.QPlainTextEdit(parent=self.centralwidget)
        self.CodeTextEdit.setObjectName("CodeTextEdit")
        self.horizontalLayout.addWidget(self.CodeTextEdit)
        self.ResultTextBrowser = QtWidgets.QTextBrowser(parent=self.centralwidget)
        self.ResultTextBrowser.setObjectName("ResultTextBrowser")
        self.horizontalLayout.addWidget(self.ResultTextBrowser)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1016, 26))
        self.menubar.setObjectName("menubar")
        self.menu = QtWidgets.QMenu(parent=self.menubar)
        self.menu.setObjectName("menu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.Open = QtGui.QAction(parent=MainWindow)
        self.Open.setObjectName("Open")
        self.Save = QtGui.QAction(parent=MainWindow)
        self.Save.setObjectName("Save")
        self.menu.addAction(self.Open)
        self.menu.addAction(self.Save)
        self.menubar.addAction(self.menu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "cppanalyz"))
        self.menu.setTitle(_translate("MainWindow", "Файл"))
        self.Open.setText(_translate("MainWindow", "Открыть"))
        self.Save.setText(_translate("MainWindow", "Сохранить"))
