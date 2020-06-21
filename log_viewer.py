import os
import logger
from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtWidgets import QComboBox, QLabel, QFrame, QLineEdit, QPushButton, QTextEdit
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QRect


class LogViewer(QMainWindow):

    def __init__(self, parent=None):
        super(LogViewer, self).__init__(parent)
        self.initUI_log()

    def initUI_log(self):
        log_output = QTextEdit(self)
        log_output.setReadOnly(True)
        log_output.setGeometry(5, 5, 790, 590)

        with open(logger.get_logfile_path(), encoding="UTF-8") as file:
            log_output.insertPlainText(file.read())

        font = log_output.font()
        font.setFamily("Yu Gothic")
        font.setPointSize(10)

        self.setGeometry(400, 400, 800, 600)
        self.setWindowTitle("Log Output")
        self.show()
