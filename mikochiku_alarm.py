#!/usr/bin/env python3

import sys
import os
import time
import webbrowser
import requests
import pygame.mixer
import json
import settings
import config_tab
import re
from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QApplication, QLabel, QListWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer


PY3 = sys.version_info[0] == 3
if PY3:
    from urllib.parse import urlencode
    from queue import Queue
else:
    from Queue import Queue
    from urllib import urlencode

PATTERN_LIVE_VIDEO  = re.compile(
    r'window\["ytInitialData"\] = (.*LIVE_NOW.*?"videoId":"([^"]+)".*);')

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
    'AppleWebKit/537.36 (KHTML, like Gecko) '
    'Chrome/69.0.3497.100 Safari/537.36'}

class MikochikuAlarm(QWidget):

    def __init__(self, parent=None):
        super(MikochikuAlarm, self).__init__(parent)
        self.search_ch_id = settings.CHID
        self.old_video_id_list = []
        # メンバー一覧のjsonを取得し、memberに格納
        with open(".\\channel\\hololive.json", encoding="UTF-8") as file:
            self.member = json.load(file)

        # Checks which os is being used then sets the correct path
        if   os.name == "posix": self.lang_path = "lang/"
        elif os.name == "nt"   : self.lang_path = ".\\lang\\"

        self.initUI()

    def initUI(self):

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_live)
        self.timer.setInterval(40000)
        self.timer.start()

        sakura_miko = QLabel(self)
        sakura_miko.setPixmap(QPixmap(resource_path(settings.ICON)))
        sakura_miko.move(65, 70)

        self.alarm_cb = QCheckBox(self.localized_text("alarm"), self)
        self.alarm_cb.toggle()

        # self.loop_cb = QCheckBox('アラームをループ再生する', self)
        # self.loop_cb.move(20, 40)
        # self.loop_cb.toggle()

        self.webbrowser_cb = QCheckBox(self.localized_text("webbrowser"), self)
        self.webbrowser_cb.toggle()

        self.alarm_stop = QPushButton(self.localized_text("waiting"), self)
        # self.alarm_stop.setCheckable(True)
        # self.alarm_stop.setEnabled(False)
        self.alarm_stop.clicked[bool].connect(self.stop_alarm)

        self.config_btn = QPushButton("config", self)
        self.config_btn.clicked.connect(self.cfg_dialog)
        self.dialogs = list()

        # setGeometry
        self.alarm_cb     .setGeometry( 10,  10, 250, 20)
        self.webbrowser_cb.setGeometry( 10,  30, 250, 20)
        self.alarm_stop   .setGeometry( 80,  80,  80, 25)
        self.config_btn   .setGeometry(195, 120,  60, 25)

        self.setGeometry(300, 300, 260, 150)
        self.setWindowTitle(self.localized_text("title"))

        # メンバー名をlistWidgetに格納
        self.listWidget = QListWidget(self)
        for v in self.member:
            self.listWidget.addItem(v['name'])
        self.listWidget.move(30, 200)
        self.listWidget.itemClicked.connect(self.clicked)

        self.show()

    def cfg_dialog(self):
        dialog = config_tab.ConfigTab(self)
        self.dialogs.append(dialog)

    # FIXME: 関数名が抽象的すぎる
    def clicked(self, qmode8ndex):
        # 要素番号使うのでcurrentRow()に変更
        member = self.member[self.listWidget.currentRow()]
        self.search_ch_id = member['channel_id']

    def check_live(self):
        getting_video_id = self.get_live_video_id(self.search_ch_id)
        print("getting_video_id", getting_video_id)
        print("self.old_video_id_list", self.old_video_id_list)
        if not getting_video_id:
            return
        if getting_video_id in self.old_video_id_list:
            return
        # A LIVE BROADCAST HAS BEEN FOUND.
        self.old_video_id_list.append(getting_video_id)
        if len(self.old_video_id_list) > 30:
            self.old_video_id_list.pop(0)
        print("")
        print(self.get_text(self.get_locale_json(), "started"))
        self.alarm_stop.setEnabled(False)
        self.alarm_stop.click()
        self.alarm_stop.setText(self.get_text(
            self.get_locale_json(), "stop"))
        self.alarm_stop.setEnabled(True)
        if self.webbrowser_cb.checkState():
            webbrowser.open(
                "https://www.youtube.com/watch?v=" + getting_video_id)
        if self.alarm_cb.checkState():
            self.alarm_sound()

    def get_locale_json(self):
        '''Not Implemented'''
        pass

    def get_text(self, locale_json, message):
        '''temporary  implementation'''
        return message

    def stop_alarm(self):
        pygame.mixer.music.stop()
        self.alarm_stop.setEnabled(True)
        self.alarm_stop.setText(self.localized_text("waiting"))

    def alarm_sound(self):
        # loop = 1
        # if self.loop_cb.checkState():
        loop_count = 5
        pygame.mixer.music.play(loop_count)
        pygame.mixer.music.play(loop_count)

    def get_live_video_id(self, search_ch_id):
        with requests.Session() as session:
            html = session.get("https://www.youtube.com/channel/" + search_ch_id, headers=HEADERS, timeout=10)
            matching = re.search(PATTERN_LIVE_VIDEO, html.text)
            if matching:
                video_id= matching.group(2)
                return video_id
            return None

    def load_locale_json(self): # from json file
        path = self.lang_path +"locale.json"
        with open(path, mode='r') as file:
            dict_json = json.load(file)
            return dict_json["locale"]

    def localized_text(self, content):
        path = self.lang_path + self.load_locale_json() + ".json"
        with open(path, encoding="UTF-8") as file:
            dict_json = json.load(file)
        return dict_json[content]


def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


def main():
    # cnt = 0
    # for line in os.popen("tasklist"):
    #     buff = line.split()
    #     if buff:
    #         if buff[0] == 'mikochiku_alarm.exe':
    #             cnt += 1
    #             if cnt > 2:
    #                 sys.exit()
    pygame.mixer.init()
    if os.path.exists(settings.ALARM):
        pygame.mixer.music.load(settings.ALARM)
    else:
        pygame.mixer.music.load(resource_path(settings.ALARM))
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path(settings.ICON)))
    mk = MikochikuAlarm()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
