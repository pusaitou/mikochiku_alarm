#!/usr/bin/env python3

import sys
import os
import time
import webbrowser
import requests
import pygame.mixer
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QComboBox, QWidget, QCheckBox, QPushButton, QApplication, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer


PY3 = sys.version_info[0] == 3
if PY3:
    from urllib.parse import urlencode
    from queue import Queue
else:
    from Queue import Queue
    from urllib import urlencode


class MikochikuAlarm(QWidget):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.search_ch_id = "UC-hM6YJuNYVAmUWxeIr9FeA"
        self.old_video_id_list = []
        self.initUI()

    def initUI(self):      

        self.language = "日本語"

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_live)
        self.timer.setInterval(40000)
        self.timer.start()

        label = QLabel(self)
        label.setPixmap(QPixmap(resource_path("icon.ico")))
        label.move(60,70)

        self.alarm_cb = QCheckBox('配信が始まったらアラームを鳴らす', self)
        self.alarm_cb.move(20, 20)
        self.alarm_cb.toggle()
        

        # self.loop_cb = QCheckBox('アラームをループ再生する', self)
        # self.loop_cb.move(20, 40)
        # self.loop_cb.toggle()

        self.webbrowser_cb = QCheckBox('配信が始まったら自動でブラウザを開く', self)
        self.webbrowser_cb.move(20, 40)
        self.webbrowser_cb.toggle()

        self.alarm_stop = QPushButton("待機中", self)
        # self.alarm_stop.setCheckable(True)
        # self.alarm_stop.setEnabled(False)
        self.alarm_stop.move(80, 80)
        self.alarm_stop.clicked[bool].connect(self.stop_alarm)

        self.combo = QComboBox(self)
        self.combo.move(0,130)
        self.combo.addItems(["日本語","English"])
        self.combo.activated.connect(self.set_language)

        self.setGeometry(300, 300, 250, 150)
        self.setWindowTitle('みこ畜アラーム')

        self.show()

    def set_language(self):
        if self.combo.currentText() == "日本語":
            self.language = "日本語"
            self.alarm_cb.setText("配信が始まったらアラームを鳴らす")
            self.webbrowser_cb.setText("配信が始まったら自動でブラウザを開く")
            self.alarm_stop.setText("待機中")
            self.setWindowTitle('みこ畜アラーム')

        elif self.combo.currentText() == "English":
            self.language = "English"
            self.alarm_cb.setText("Play alarm when stream starts")
            self.webbrowser_cb.setText("Open browser when stream starts")
            self.alarm_stop.setText("Waiting")
            self.setWindowTitle("Miko livestream alarm")

        #self.initUI()

    def check_live(self):
        buff_video_id_set = self.get_live_video_id(self.search_ch_id)
        print("buff_video_id_set",buff_video_id_set)
        print("self.old_video_id_list", self.old_video_id_list)
        if buff_video_id_set:
            for getting_video_id in buff_video_id_set:
                if not getting_video_id == "" and not getting_video_id is None: 
                    if not getting_video_id in self.old_video_id_list:
                        self.old_video_id_list.append(getting_video_id)
                        if len(self.old_video_id_list) > 30:
                            self.old_video_id_list = self.old_video_id_list[1:]
                        print("")
                        print("配信が始まりました")
                        # self.alarm_stop.setEnabled(False)
                        self.alarm_stop.click()

                        if self.language == "日本語":
                            self.alarm_stop.setText("ストップ")
                        elif self.language == "English":
                            self.alarm_stop.setText("Stop")

                        if self.webbrowser_cb.checkState():
                            webbrowser.open("https://www.youtube.com/watch?v=" + getting_video_id)
                        if self.alarm_cb.checkState():
                            self.alarm_sound()


    def stop_alarm(self):
        pygame.mixer.music.stop()
        self.alarm_stop.setEnabled(True)

        if self.language == "日本語":
            self.alarm_stop.setText("待機中")
        elif self.language == "English":
            self.alarm_stop.setText("Waiting")


    def alarm_sound(self):
        # loop = 1
        # if self.loop_cb.checkState():
        loop_count = 5
        pygame.mixer.music.play(loop_count)
        pygame.mixer.music.play(loop_count)

    def get_live_video_id(self, search_ch_id):
        dict_str = ""
        video_id_set = set()
        try:
            session = requests.Session()
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36'}
            html = session.get("https://www.youtube.com/channel/" + search_ch_id, headers=headers, timeout=10)
            soup = BeautifulSoup(html.text, 'html.parser')
            keyword = 'window["ytInitialData"]'
            for scrp in soup.find_all("script"):
                if keyword in str(scrp):
                    dict_str = str(scrp).split(' = ', 1)[1]
            dict_str = dict_str.replace('false', 'False')
            dict_str = dict_str.replace('true', 'True')

            index = dict_str.find("\n")
            dict_str = dict_str[:index-1]
            dics = eval(dict_str)
            for section in dics.get("contents", {}).get("twoColumnBrowseResultsRenderer", {}).get("tabs", {})[0].get("tabRenderer", {}).get("content", {}).get("sectionListRenderer", {}).get("contents", {}):
                for itemsection in section.get("itemSectionRenderer", {}).get("contents", {}):
                    items = {}
                    if "shelfRenderer" in itemsection:
                        for items in itemsection.get("shelfRenderer", {}).get("content", {}).values():
                            for item in items.get("items", {}):
                                for videoRenderer in item.values():
                                    for badge in videoRenderer.get("badges", {}):
                                        if badge.get("metadataBadgeRenderer", {}).get("style", {}) == "BADGE_STYLE_TYPE_LIVE_NOW":
                                            video_id_set.add(videoRenderer.get("videoId", ""))
                    elif "channelFeaturedContentRenderer" in itemsection:
                        for item in itemsection.get("channelFeaturedContentRenderer", {}).get("items", {}):
                            for badge in item.get("videoRenderer",{}).get("badges",{}):
                                if badge.get("metadataBadgeRenderer",{}).get("style","") == "BADGE_STYLE_TYPE_LIVE_NOW":
                                    video_id_set.add(item.get("videoRenderer",{}).get("videoId",""))
        except:
            return video_id_set
        
        return video_id_set


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
    if os.path.exists("alarm.mp3"):
        pygame.mixer.music.load("alarm.mp3")
    else:
        pygame.mixer.music.load(resource_path("alarm.mp3"))
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(resource_path("icon.ico")))
    mk = MikochikuAlarm()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
