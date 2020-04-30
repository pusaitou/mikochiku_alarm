from PyQt5.QtWidgets import (
    QDesktopWidget, QMainWindow, QLabel, QFrame,
    QPushButton, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import QRect, Qt, QSize
from urllib.request import urlopen
import webbrowser


class CloseButton(QPushButton):

    def __init__(self, parent=None):
        super(CloseButton, self).__init__(parent)

    def enterEvent(self, event):
        self.setStyleSheet(
            "border-color: rgb(255, 100, 100);"
            "border-style: solid;"
            "border-width: 1px;"
        )

    def leaveEvent(self, event):
        self.setStyleSheet("border-width: 0px;")


class VideoItemList(QListWidget):

    def __init__(self, parent, already_open_browser):
        super(VideoItemList, self).__init__(parent)
        self.already_open_browser = already_open_browser
        self.setFrameStyle(QFrame.NoFrame)
        self.setIconSize(QSize(160, 80))
        self.setWordWrap(True)
        # クリック時、テキストに枠線が表示されるのを防ぐ。
        self.setFocusPolicy(Qt.NoFocus)
        # マウスホバー時にQListWidgetItem内のオブジェクトが動かないよう
        # 最初から透明なボーダーを描画しておく。
        self.setStyleSheet(
            """
            QListWidget {
                background-color: transparent;
            }
            QListWidget::item {
                background: rgba(255, 212, 212, 0);
                selection-color: rgb(0, 0 ,0);
                border:1px solid rgba(255, 100, 100, 0);
            }"""
        )

    def enterEvent(self, event):
        if self.already_open_browser:
            return
        self.setStyleSheet(
            """
            QListWidget::item {
                background: rgb(255, 212, 212);
                selection-color: rgb(0, 0 ,0);
                border:1px solid rgb(255, 100, 100);
            }
            QListWidget::item:selected {
                selection-color: rgb(0, 0 ,0);
            }
            """
        )

    def leaveEvent(self, event):
        if self.already_open_browser:
            return
        self.setStyleSheet(
            """
            QListWidget {
                background-color: transparent;
            }
            QListWidget::item {
                background: rgba(255, 212, 212, 0);
                selection-color: rgb(0, 0 ,0);
                border:1px solid rgba(255, 100, 100, 0);
            }
            QListWidget::item:selected {
                selection-color: rgb(0, 0 ,0);
                border: 1px solid rgba(255, 100, 100, 0);
            }
            """
        )


class Toast(QMainWindow):

    def __init__(self, parent, videos, already_open_browser):
        '''
        videos : List[dict] :
            dict{ vid: 動画ID, title: 動画タイトル } のリスト

        already_open_browser : bool :
            配信ページが既にブラウザで開かれている場合True
        '''
        super(Toast, self).__init__(
            parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.videos = videos
        self.already_open_browser = already_open_browser
        self.initUI(parent)

    def initUI(self, parent):
        width = 450
        height = 140
        desktop = QDesktopWidget().availableGeometry()
        d_bottom = desktop.bottom()
        d_right = desktop.right()

        self.setGeometry(d_right-width-10, d_bottom-height-10, width, height)
        # Notification text of starting live.
        lblNotice = QLabel(self)
        lblNotice.setFont(QFont("Yu Gothic", 12))
        lblNotice.setGeometry(QRect(20, 10, width-25, 20))
        lblNotice.setText(parent.localized_text("started"))
        # Close Button
        btnClose = CloseButton(self)
        btnClose.setFlat(True)
        btnClose.clicked.connect(self.close)
        btnClose.setIcon(QIcon(QPixmap("close_button.png")))
        btnClose.setIconSize(QSize(20, 20))
        btnClose.setGeometry(width-30-2, 4, 30, 30)
        # ListBox
        listView = VideoItemList(self, self.already_open_browser)
        listView.setGeometry(20, 40, width-55, 80)
        listView.itemClicked.connect(self.onItemClicked)

        for video in self.videos:
            # 動画情報アイテム
            item = QListWidgetItem()
            item.setSizeHint(QSize(160, 80))
            # 動画サムネイル・タイトル
            url = f'https://i1.ytimg.com/vi/{video["vid"]}/mqdefault.jpg'
            data = urlopen(url).read()
            pixmap = QPixmap()
            pixmap.loadFromData(data)
            scaled = pixmap.scaledToHeight(70, Qt.SmoothTransformation)
            icon = QIcon()
            # マウスホバー時にアイコンが青くならないように、normalとselectedに同じ画像を登録する。
            icon.addPixmap(scaled, QIcon.Normal)
            icon.addPixmap(scaled, QIcon.Selected)
            item.setIcon(icon)
            item.vid = video["vid"]
            item.setFont(QFont("Yu Gothic", 9))
            item.setText(video["title"])
            listView.addItem(item)
        self.show()

    def onItemClicked(self, item: QListWidgetItem):
        if self.already_open_browser:
            return
        webbrowser.open(
            "https://www.youtube.com/watch?v=" + item.vid)
        # トーストに表示されている動画が1つの場合、ブラウザを開いたらすぐトーストを閉じる。
        if len(self.videos) == 1:
            self.close()
