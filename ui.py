import sys
from PyQt5.QtGui import QColor
from PyQt5 import QtGui, QtCore
import os
from PyQt5.QtWidgets import(
    QApplication, 
    QMainWindow, 
    QFileDialog, 
    QWidget, 
    QGridLayout,
    QLineEdit,
    QPushButton, 
    QLabel,  
    QTextEdit,
    QAction, QVBoxLayout)
from analyzer import SataicCodeAnalayzer
from pathlib import Path


class FileViewer(QWidget):
    def __init__(self):
        super(FileViewer, self).__init__()
        self.text = QTextEdit(self)
        self.initUI()
        

    def initUI(self):
        self.setWindowTitle('Static Code Analyzer')
        self.setGeometry(100, 100, 800, 600)
        self.text.setGeometry(0, 0, 800, 600)
        self.text.setFontPointSize(16)
        self.text.setTextColor(QColor("#FFA500"))
        self.setStyleSheet("background-color:#444;")
        self.show()
      

                
class MainWindow(QWidget):
    text_Changed = QtCore.pyqtSignal(str)
    
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.initUI()

     
    def initUI(self): 
        self.setWindowTitle("Choose File")
        self.setGeometry(900,200, 400, 100)
        
        layout = QGridLayout()
        self.setLayout(layout)
        
        file_broweser_btn = QPushButton('Browse Files')
        file_broweser_btn.clicked.connect(self.open_file_dialog)        
        layout.addWidget(file_broweser_btn, 0,0)
        
        self.show()
        
    @QtCore.pyqtSlot()
    def open_file_dialog(self):
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Select a File", 
            os.getenv('HOME'), 
            "(*.py)"
        )
       
        analyzer = SataicCodeAnalayzer()
        result = analyzer.check_file(filename)
        self.text_Changed.emit(result)

        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    viewr = FileViewer()
    window = MainWindow()  
    window.text_Changed.connect(viewr.text.append)
    sys.exit(app.exec())