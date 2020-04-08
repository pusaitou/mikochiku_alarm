#!/usr/bin/env python3

import sys
import os
import time
import webbrowser
import requests
import pygame.mixer
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QApplication, QLabel, QGridLayout, QListWidget
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
        self.ch_dic = {
            "ときのそら":"UCp6993wxpyDPHUpavwDFqgg",
            "AZKi":"UC0TXe_LYZ4scaW2XMyi5_kw",
            "ロボ子さん":"UCDqI2jOz0weumE8s7paEk6g",
            "さくらみこ":"UC-hM6YJuNYVAmUWxeIr9FeA",
            "白上フブキ":"UCdn5BQ06XqgXoAxIhbqw5Rg",
            "夏色まつり":"UCQ0UDLQCjY0rmuxCDE38FGg",
            "夜空メル":"UCD8HOxPs4Xvsm8H0ZxXGiBw",
            "赤井はあと":"UC1CfXB_kRs3C-zaeTG3oGyg",
            "アキ・ローゼンタール":"UCFTLzh12_nrtzqBPsTCqenA",
            "湊あくあ":"UC1opHUrw8rvnsadT-iGp7Cg",
            "癒月ちょこ":"UC1suqwovbL1kzsoaZgFZLKg",
            "百鬼あやめ":"UC7fk0CB07ly8oSl0aqKkqFg",
            "紫咲シオン":"UCXTpFs_3PqI41qX2d9tL2Rw",
            "大空スバル":"UCvzGlP9oQwU--Y0r9id_jnA",
            "大神ミオ":"UCp-5t9SrOQwXMU7iIjQfARg",
            "猫又おかゆ":"UCvaTdHTWBGv3MKj3KVqJVCw",
            "戌神ころね":"UChAnqc_AY5_I3Px5dig3X1Q",
            "不知火フレア":"UCvInZx9h3jC2JzsIzoOebWg",
            "白銀ノエル":"UCdyqAaZDKHXg4Ahi7VENThQ",
            "宝鐘マリン":"UCCzUftO8KOVkV4wQG1vkUvg",
            "兎田ぺこら":"UC1DCedRgGHBdm81E1llLhOQ",
            "潤羽るしあ":"UCl_gCybOJRIgOXw6Qb4qJzQ",
            "星街すいせい":"UC5CwaMl1eIgY8h02uZw7u8A",
            "天音かなた":"UCZlDXzGoo7d44bwdNObFacg",
            "桐生ココ":"UCS9uQI-jC3DE0L4IpXyvr6w",
            "角巻わため":"UCqm3BQLlJfvkTsX_hvm0UmA",
            "常闇トワ":"UC1uv2Oq6kNxgATlCiez59hw",
            "姫森ルーナ":"UCa9Y57gfeY0Zro_noHRVrnw"
            }
        self.old_video_id_list = []
        self.initUI()

    def initUI(self):      

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.check_live)
        self.timer.setInterval(5000)
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
        self.alarm_stop.move(80, 360)
        self.alarm_stop.clicked[bool].connect(self.stop_alarm)
        
        self.listWidget = QListWidget(self)
        self.listWidget.resize(300,150)
        self.listWidget.addItem("ときのそら");
        self.listWidget.addItem("AZKi");
        self.listWidget.addItem("ロボ子さん");
        self.listWidget.addItem("さくらみこ");
        self.listWidget.addItem("白上フブキ");
        self.listWidget.addItem("夏色まつり");
        self.listWidget.addItem("夜空メル");
        self.listWidget.addItem("赤井はあと");
        self.listWidget.addItem("アキ・ローゼンタール");
        self.listWidget.addItem("湊あくあ");
        self.listWidget.addItem("癒月ちょこ");
        self.listWidget.addItem("百鬼あやめ");
        self.listWidget.addItem("紫咲シオン");
        self.listWidget.addItem("大空スバル");
        self.listWidget.addItem("大神ミオ");
        self.listWidget.addItem("猫又おかゆ");
        self.listWidget.addItem("戌神ころね");
        self.listWidget.addItem("不知火フレア");
        self.listWidget.addItem("白銀ノエル");
        self.listWidget.addItem("宝鐘マリン");
        self.listWidget.addItem("兎田ぺこら");
        self.listWidget.addItem("潤羽るしあ");
        self.listWidget.addItem("星街すいせい");
        self.listWidget.addItem("天音かなた");
        self.listWidget.addItem("桐生ココ");
        self.listWidget.addItem("角巻わため");
        self.listWidget.addItem("常闇トワ");
        self.listWidget.addItem("姫森ルーナ");

        self.listWidget.move(30,200)

        self.listWidget.itemClicked.connect(self.clicked)
         
        self.setGeometry(300, 300, 400, 400)
        self.setWindowTitle('みこ畜アラーム')

        self.show()
    def clicked(self, qmodelindex):
        self.search_ch_id = self.ch_dic[self.listWidget.currentItem().text()]
        
    def check_live(self):
        buff_video_id_set = self.get_live_video_id(self.search_ch_id)
        print(self.listWidget.selectedIndexes())
        if self.listWidget.selectedIndexes() is None:
            print("aaaa")
            self.search_ch_id = ""
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
                        self.alarm_stop.setText("ストップ")
                        if self.webbrowser_cb.checkState():
                            webbrowser.open("https://www.youtube.com/watch?v=" + getting_video_id)
                        if self.alarm_cb.checkState():
                            self.alarm_sound()


    def stop_alarm(self):
        pygame.mixer.music.stop()
        self.alarm_stop.setEnabled(True)
        self.alarm_stop.setText("待機中")


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
