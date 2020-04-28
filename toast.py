from PyQt5.QtWidgets import (
    QDesktopWidget, QMainWindow, QLabel, QFrame, QPushButton, QHBoxLayout)
from PyQt5.QtGui import QFont, QPixmap, QIcon, QPalette
from PyQt5.QtCore import QRect, Qt, QSize
from urllib.request import urlopen
import webbrowser

class HoverButton(QPushButton):

    def __init__(self, parent=None):
        super(HoverButton, self).__init__(parent)

    def enterEvent(self, event):
        self.setStyleSheet(
            "border-color:lightpink; border-style:solid; border-width:1px;")
        
    def leaveEvent(self, event):
        self.setStyleSheet("border-width:0px;")


class HoverFrame(QFrame):
            
    def __init__(self, parent, vid, title, width, callback, opened):
        super(HoverFrame, self).__init__(parent)
        self.vid = vid
        self.callback = callback
        self.opened = opened
        self.setFrameStyle(QFrame.NoFrame)
        self.setLayout(QHBoxLayout())

    def enterEvent(self, event):
        print(self.opened)
        if self.opened:
            return
        self.setStyleSheet(
            "border-color:lightpink; border-style:solid; border-width:1px;")
        self.setStyleSheet(f"background-color:rgb(255,212,212);")

    def leaveEvent(self, event):
        if self.opened:
            return
        self.setStyleSheet(f"background-color: { QPalette.Background};")

    def mousePressEvent(self, event):
        if self.opened:
            return
        webbrowser.open(
            "https://www.youtube.com/watch?v=" + self.vid)
        self.callback()
    

class Toast(QMainWindow):

    def __init__(self, parent, vid, title, opened):
        super(Toast, self).__init__(
            parent, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.initUI(parent, vid, title, opened)

    def initUI(self, parent, vid, title, opened):
        width = 450
        height = 140
        desktop = QDesktopWidget().availableGeometry()
        d_bottom = desktop.bottom()
        d_right = desktop.right()

        self.setGeometry(d_right-width-10, d_bottom-height-10, width, height)
        self.setWindowTitle("")

        # Notification text of statrting live.
        lblNotice = QLabel(self)
        lblNotice.setFont(QFont("Yu Gothic", 12))
        lblNotice.setGeometry(QRect(25, 10, width-25, 20))
        lblNotice.setText(parent.localized_text("started"))
        lblNotice.setFont(QFont("Yu Gothic", 12))
        lblNotice.setGeometry(QRect(15, 10, width-25, 20))
        lblNotice.setText(parent.localized_text("started"))

        # Close Button
        btnClose = HoverButton(self)
        btnClose.setFlat(True)
        btnClose.clicked.connect(self.close)
        btnClose.setIcon(QIcon(QPixmap("close_button.png")))
        btnClose.setIconSize(QSize(20, 20)) 
        btnClose.setGeometry(width-30-6, 6, 30, 30)

        # 動画情報フレーム
        frmVideoItem= HoverFrame(self, vid, title, width, self.hide, opened)
        frmVideoItem.setGeometry(25, 35, width-55, height-50)

        # 動画サムネイル
        url = f'https://i1.ytimg.com/vi/{vid}/mqdefault.jpg'
        data = urlopen(url).read()
        pixmap = QPixmap()
        pixmap.loadFromData(data)
        scaled = pixmap.scaledToHeight(60, Qt.SmoothTransformation)
        lblImage = QLabel(self)
        lblImage.setPixmap(scaled)
        frmVideoItem.layout().addWidget(
            lblImage, alignment=(Qt.AlignCenter | Qt.AlignLeft))

        # 動画タイトル
        lblTitle = QLabel(self)
        lblTitle.setWordWrap(True)
        lblTitle.setFont(QFont("Yu Gothic", 10))
        lblTitle.setAlignment(Qt.AlignJustify)
        lblTitle.setText(title)
        frmVideoItem.layout().addWidget(
            lblTitle, alignment=(Qt.AlignCenter | Qt.AlignLeft))
        
        self.show()

    def hide(self):
        '''
        動画フレームがクリックされ、動画ページ表示されたらすぐ閉じる。
        '''
        self.close()
