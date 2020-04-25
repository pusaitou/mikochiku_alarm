#!/usr/bin/env python3

import sys
import os
import time
import webbrowser
import pygame.mixer
import json
import settings
import config_tab
import release_notice
import log_viewer
import re
import vparser
from PyQt5.QtWidgets import QWidget, QCheckBox, QPushButton, QApplication, QLabel, QListWidget, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QTimer
from httpreq import HttpRequest


PY3 = sys.version_info[0] == 3
if PY3:
    from urllib.parse import urlencode
    from queue import Queue
else:
    from Queue import Queue
    from urllib import urlencode



class MikochikuAlarm(QWidget):

    def __init__(self, parent=None):
        super(MikochikuAlarm, self).__init__(parent)
        self.search_ch_id = settings.CHID
        self.old_video_id_list = []
        self.request = HttpRequest()
        # メンバー一覧のjsonを取得し、memberに格納
        with open(".\\channel\\hololive.json", encoding="UTF-8") as file:
            self.member = json.load(file)
        # Checks which os is being used then sets the correct path
        if   os.name == "posix": self.lang_path = "lang/"
        elif os.name == "nt"   : self.lang_path = ".\\lang\\"

        self.initUI()
        # 起動直後にチャンネルIDを調べる
        self.check_live()


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

        self.webbrowser_cb = QCheckBox(self.localized_text("webbrowser"), self)
        self.webbrowser_cb.toggle()

        self.alarm_state = "waiting"
        self.alarm_stop = QPushButton(self.localized_text("waiting"), self)

        self.alarm_stop.clicked[bool].connect(self.stop_alarm)

        self.config_btn = QPushButton("config", self)
        self.config_btn.clicked.connect(self.config_dialog)
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
        self.listWidget.itemClicked.connect(self.set_target_channel)

        # v 更新通知 / ログ出力 タブ表示用
        # self.notice_dialog()
        # self.log_viewer_dialog()

        self.show()

    def config_dialog(self):
        config = config_tab.ConfigTab(self)
        self.dialogs.append(config)

    def notice_dialog(self):
        notice = release_notice.ReleaseNotice(self)
        self.dialogs.append(notice)

    def log_viewer_dialog(self):
        log_out = log_viewer.LogViewer(self)
        self.dialogs.append(log_out)

    def set_target_channel(self, qmode8ndex):
        # 要素番号使うのでcurrentRow()に変更
        member = self.member[self.listWidget.currentRow()]
        self.search_ch_id = member['channel_id']

    def check_live(self):
        buff_video_id_set = self.get_live_video_id(self.search_ch_id)
        print("buff_video_id_set", buff_video_id_set)
        print("self.old_video_id_list", self.old_video_id_list)
        for getting_video_id in buff_video_id_set:
            if getting_video_id in self.old_video_id_list:
                return
            self.old_video_id_list.append(getting_video_id)
            if len(self.old_video_id_list) > 30:
                self.old_video_id_list.pop(0)
            print("")
            print(self.localized_text("started"))
            self.alarm_stop.click()
            self.alarm_state = "stop"
            self.alarm_stop.setText(self.localized_text("stop"))
            if self.webbrowser_cb.checkState():
                webbrowser.open(
                    "https://www.youtube.com/watch?v=" + getting_video_id)
            if self.alarm_cb.checkState():
                self.alarm_sound()

    def stop_alarm(self):
        pygame.mixer.music.stop()
        self.alarm_stop.setEnabled(True)
        self.alarm_state = "waiting"
        self.alarm_stop.setText(self.localized_text("waiting"))

    def alarm_sound(self):
        # loop = 1
        # if self.loop_cb.checkState():
        loop_count = 5
        pygame.mixer.music.play(loop_count)
        pygame.mixer.music.play(loop_count)

    def get_live_video_id(self, search_ch_id):
        try:
            source = vparser.get_source_json(self.request, search_ch_id)
            video_ids  = vparser.extract_video_ids(source)
            return set(video_ids)
        except vparser.InvalidChannelIDException:
            # チャンネルページが見つからない場合
            # TODO: アラートダイアログをポップアウトさせたい
            print(f'{search_ch_id} は、存在しないチャンネルです。')
        except Exception as e:
            print(e)
            print(f'不明なエラーが発生しました')        
        return set()

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

    def update_ui_language(self):
        self.setWindowTitle(self.localized_text("title"))
        self.webbrowser_cb.setText(self.localized_text("webbrowser"))
        self.alarm_cb.setText(self.localized_text("alarm"))
        self.alarm_stop.setText(self.localized_text(self.alarm_state))


def resource_path(relative):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative)
    return os.path.join(relative)


def main():
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
