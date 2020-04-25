import os
import json
from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtWidgets import QComboBox, QLabel, QFrame, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui  import QFont
from PyQt5.QtCore import QRect, Qt


class ReleaseNotice(QMainWindow):

    def __init__(self, parent=None):
        super(ReleaseNotice, self).__init__(parent)
        self.initUI_notice()

    def initUI_notice(self):
        self.notice()

        self.setGeometry(400, 400, 400, 80)
        self.setWindowTitle("Notice")
        self.show()

    def notice(self):
        date = "2020年5月30日"
        update_link = \
            """<a href=\"https://github.com/pusaitou/mikochiku_alarm/releases\">こちら</a>"""
        label = QLabel(self)
        label.setTextInteractionFlags(Qt.LinksAccessibleByMouse)
        label.setTextFormat(Qt.RichText)
        label.setFont(QFont("Yu Gothic", 10))
        label.setGeometry(QRect(5, 5, 390, 70))
        label.setText('<center>ソフトウェアの新しいバージョンが検出されました。<br> '
                      + "現在のバージョンは" + date + "で使えなくなります。<br>"
                      + update_link + "から更新してください。</center>")
        label.setOpenExternalLinks(True)
