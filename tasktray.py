from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5 import QtGui
import settings

class TrayWidget(QSystemTrayIcon):
 
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.create_actions()
        self.create_menu()       
        self.create_icon()

    def create_actions(self):
        self.quitAction = QAction(self)
        self.quitAction.setText(self.tr("&Quit"))
        self.quitAction.triggered.connect(self.quit)

    def create_menu(self):
        self.trayIconMenu = QMenu(self.parent)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)        

    def create_icon(self):
        self.setContextMenu(self.trayIconMenu)
        self.setIcon(QtGui.QIcon(settings.ICON))
    
    def quit(self, force=False):
        print("quit()")
