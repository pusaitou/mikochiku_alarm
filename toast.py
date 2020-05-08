
from PyQt5.QtWidgets import (
    QDesktopWidget, QMainWindow, QLabel, QFrame,
    QPushButton, QListWidget, QListWidgetItem)
from PyQt5.QtGui import QFont, QPixmap, QIcon
from PyQt5.QtCore import Qt, QSize, QThread, QObject, pyqtSignal, pyqtSlot
from functools import partial
from socket import timeout
from urllib.request import urlopen, HTTPError, URLError
import webbrowser
import logger

log = logger.get_logger(__name__)


class CloseButton(QPushButton):

    def __init__(self, parent=None):
        super(CloseButton, self).__init__(parent)
        self.setStyleSheet(open('./css/toast_button.css', encoding='utf-8').read())


class LazyLoader(QObject):
    drawIcon = pyqtSignal(bytes)
    done = pyqtSignal()

    @pyqtSlot()
    def load(self, vid):
        url = f'https://i1.ytimg.com/vi/{vid}/mqdefault.jpg'
        try:
            data = urlopen(url, timeout=10).read()
            self.drawIcon.emit(data)
        except (HTTPError, URLError) as error:
            log.error(f'エラー{error},{url}')
        except timeout:
            log.error(f'タイムアウト:{url}')
        # quit thread
        self.done.emit()


class VideoItem(QListWidgetItem):

    def __init__(self, video, item_height):
        super(VideoItem, self).__init__()
        self.setSizeHint(QSize(160, item_height))
        self.vid = video["vid"]
        # 動画タイトルを先に設定する。
        self.setFont(QFont("Yu Gothic", 9))
        self.setText(video["title"])
        # サムネイル読み込み：
        # なるべくトーストウィンドウと同時表示したいので、ブロッキングでトライする。(0.5秒)
        url = f'https://i1.ytimg.com/vi/{self.vid}/mqdefault.jpg'
        try:
            data = urlopen(url, timeout=0.5).read()
            self.drawIcon(data)
            return
        except (HTTPError, URLError, timeout):
            pass
        # 読み込みが遅かった場合（0.5秒以上）ここに飛ぶ。
        # 読み込み中のプレースホルダ設定
        self.setIcon(QIcon(QPixmap("./img/place_holder.bmp")))
        # バックグラウンドで画像読み込みを開始
        self.thread = QThread()
        self.loader = LazyLoader()
        self.loader.drawIcon.connect(self.drawIcon)
        self.loader.done.connect(self.thread.quit)
        self.loader.moveToThread(self.thread)
        self.thread.started.connect(partial(self.loader.load, self.vid))
        self.thread.start()

    def drawIcon(self, data: bytes):
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        scaled = pixmap.scaledToHeight(70, Qt.SmoothTransformation)
        icon = QIcon()
        # アイテム選択時にアイコンが青くならないように、normalとselectedに同じ画像を登録する。
        icon.addPixmap(scaled, QIcon.Normal)
        icon.addPixmap(scaled, QIcon.Selected)
        self.setIcon(icon)


class VideoItemList(QListWidget):

    def __init__(self, parent, already_open_browser):
        super(VideoItemList, self).__init__(parent)
        self.setFrameStyle(QFrame.NoFrame)
        self.setIconSize(QSize(125, 70))
        self.setWordWrap(True)
        self.setFocusPolicy(Qt.NoFocus)
        if already_open_browser:
            self.setStyleSheet(open('./css/toast_normal.css', encoding='utf-8').read())
        else:
            self.setStyleSheet(open('./css/toast_hover.css', encoding='utf-8').read())


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
        padding = 16
        item_height = 80
        title_height = 40
        list_height = min(len(self.videos), 3) * item_height
        width = 450
        height = title_height + list_height + padding
        desktop = QDesktopWidget().availableGeometry()
        d_bottom = desktop.bottom()
        d_right = desktop.right()

        self.setGeometry(d_right-width-10, d_bottom-height-10, width, height)
        # Notification text of starting live.
        lblNotice = QLabel(self)
        lblNotice.setFont(QFont("Yu Gothic", 12))
        lblNotice.setGeometry(padding, 11, width-title_height, 20)
        lblNotice.setText(parent.localized_text("started"))
        # Close Button
        btnClose = CloseButton(self)
        btnClose.setFlat(True)
        btnClose.clicked.connect(self.close)
        btnClose.setIcon(QIcon(QPixmap("./img/close_button.png")))
        btnClose.setIconSize(QSize(18, 18))
        btnClose.setGeometry(width-title_height, 0, title_height, title_height)
        # ListBox
        listView = VideoItemList(self, self.already_open_browser)
        listView.setGeometry(padding, title_height, width-padding*2, list_height)
        listView.itemClicked.connect(self.onItemClicked)

        for video in self.videos:
            # 動画情報アイテム
            item = VideoItem(video, item_height)
            listView.addItem(item)
            if not self.already_open_browser:
                listView.setToolTip('Click to open')
        self.show()

    def onItemClicked(self, item: QListWidgetItem):
        if self.already_open_browser:
            return
        webbrowser.open(
            "https://www.youtube.com/watch?v=" + item.vid)
        # トーストに表示されている動画が1つの場合、ブラウザを開いたらすぐトーストを閉じる。
        if len(self.videos) == 1:
            self.close()
