import os
import json
from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtWidgets import QComboBox, QLabel, QFrame, QLineEdit, QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui  import QFont
from PyQt5.QtCore import QRect


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
        label.setFont(QFont("Yu Gothic", 10))
        label.setGeometry(QRect(5, -5, 390, 70))
        label.setText("ソフトウェアの新しいバージョンが検出されました。\n"
                      + "現在のバージョンは" + date + "で使えなくなります。\n"
                      + update_link + "から更新してください。")
        label.setOpenExternalLinks(True)
        # FIXME: 型の問題で update_link が文字列として出力される
        # 疲れたので誰か修正お願いします、いい案が思いつかないので
