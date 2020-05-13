import os
import json
import mikochiku_alarm
from PyQt5.QtWidgets import QWidget, QMainWindow
from PyQt5.QtWidgets import QComboBox, QLabel, QFrame, QLineEdit, QPushButton, QCheckBox
from PyQt5.QtGui     import QFont
from PyQt5.QtCore import Qt
import settings

class ConfigTab(QMainWindow):

    def __init__(self, parent=None):
        super(ConfigTab, self).__init__(parent)
        self.initUI_sub()
        self.parent_obj = parent

    def initUI_sub(self):
        self.header("Language", 10)
        self.language_cmb()

        self.header("Channel", 80)
        self.channel_cmb()

        self.header("Add channel", 210)
        self.channel_adder()

        self.toggle_tasktray(335)

        self.setGeometry(580, 300, 220, 370)
        self.setWindowTitle("Config")
        self.show()

    def language_cmb(self):
        self.language_cmb = QComboBox(self)
        self.language_cmb.addItem("language")
        self.language_cmb.addItems(["日本語", "中文", "English"])
        self.language_cmb.currentTextChanged.connect(self.replace_locale_json)
        self.language_cmb.setGeometry(10, 40, 200,25)

    def channel_cmb(self):
        if   os.name == "posix": self.ch_path = "channel/"
        elif os.name == "nt"   : self.ch_path = ".\\channel\\"

        with open(self.ch_path + "nijisanji.json", encoding="UTF-8") as file:
            self.nijisanji = json.load(file)
        with open(self.ch_path + "hololive.json" , encoding="UTF-8") as file:
            self.hololive  = json.load(file)
        with open(self.ch_path + "other_ch.json" , encoding="UTF-8") as file:
            self.other_ch  = json.load(file)

        self.nijisanji_cmb = QComboBox(self)
        self.hololive_cmb  = QComboBox(self)
        self.other_ch_cmb  = QComboBox(self)

        self.nijisanji_cmb.addItem("nijisanji")
        self.hololive_cmb .addItem("hololive")
        self.other_ch_cmb .addItem("other")

        for v in self.nijisanji:
            self.nijisanji_cmb.addItem(v["name"])
        for v in self.hololive:
            self.hololive_cmb.addItem(v["name"])
        for v in self.other_ch:
            self.other_ch_cmb.addItem(v["name"])

        self.nijisanji_cmb.setGeometry(10, 110, 200, 25)
        self.hololive_cmb .setGeometry(10, 140, 200, 25)
        self.other_ch_cmb .setGeometry(10, 170, 200, 25)

    def channel_adder(self):
        self.label("name", 240)
        name_inp = QLineEdit(self)
        name_inp.setGeometry(50, 240, 160, 25)

        self.label("URL", 270)
        name_inp = QLineEdit(self)
        name_inp.setGeometry(50, 270, 160, 25)

        clear_btn = QPushButton("clear", self)
        clear_btn.setGeometry(50, 300, 75, 25)

        ok_btn = QPushButton("ok", self)
        ok_btn.setGeometry(135, 300, 75, 25)

    def header(self, text, y):
        header = QLabel(self)
        header.setFont(QFont("Yu Gothic", 15))
        header.setText(text)
        header.setGeometry(10, y, 200, 25)

    def label(self, text, y):
        label = QLabel(self)
        # label.setFont(QFont("Yu Gothic", 10))
        label.setFont(QFont("Helvetica [Cronyx]", 10))
        label.setText(text)
        label.setGeometry(10, y, 40, 25)

    def replace_locale_json(self):
        # miko = mikochiku_alarm.MikochikuAlarm(self)

        path = self.parent_obj.lang_path + "locale.json"
        with open(path, mode='r') as file:
            dict_json = json.load(file)
            selected = self.get_locale_cmb()
        if not selected:
            pass
        else:
            dict_json["locale"] = selected
            with open(path, mode='w') as file:
                json.dump(dict_json, file)

        self.parent_obj.update_ui_language()

    def get_locale_cmb(self):
        if   self.language_cmb.currentText() == "日本語" : return "ja_JP"
        elif self.language_cmb.currentText() == "中文"   : return "zh_CN"
        elif self.language_cmb.currentText() == "English": return "en_US"

    def toggle_tasktray(self, y):
        cb = QCheckBox(self)
        cb.setFont(QFont("Yu Gothic", 9))
        cb.setText("Store in the task tray")
        cb.setCheckState(Qt.Checked)
        cb.setGeometry(10, y, 200, 25)
