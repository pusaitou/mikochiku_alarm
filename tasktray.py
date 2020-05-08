from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
import settings


class TrayWidget(QSystemTrayIcon):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.create_actions()
        self.create_menu()
        self.create_icon()

    def create_actions(self):
        # Action - Quit app
        self.quitAction = QAction(self)
        self.quitAction.setText(self.tr("&Quit"))
        self.quitAction.triggered.connect(self.quit)
        # Acton - Show main widget (menu and double click the tray icon)
        self.showMainWidgetAction = QAction(self)
        self.showMainWidgetAction.setText(self.tr("Show &Main Widget"))
        self.showMainWidgetAction.setShortcutVisibleInContextMenu(True)
        self.showMainWidgetAction.triggered.connect(self.showMainWidget)
        # Action - Show configulation dialog
        self.showConfigAction = QAction(self)
        self.showConfigAction.setText(self.tr("&Config"))
        self.showConfigAction.triggered.connect(self.showConfig)
        # Trigger event when tasktray icon double clicked
        self.activated.connect(self.iconActivated)

    def create_menu(self):
        self.trayIconMenu = QMenu(self.parent)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)
        self.trayIconMenu.addAction(self.showMainWidgetAction)
        self.trayIconMenu.addAction(self.showConfigAction)

    def create_icon(self):
        self.setContextMenu(self.trayIconMenu)
        self.setIcon(QtGui.QIcon(settings.ICON))

    def quit(self, force=False):
        self.parent.close()

    def showMainWidget(self, force=False):
        self.parent.setVisible(True)
        self.parent.setWindowState(self.parent.windowState() & ~(Qt.WindowMinimized | Qt.WindowActive))

    def showConfig(self, force=False):
        # When the configuration dialog is displayed,
        # the main widget is also displayed at the same time.
        self.parent.setVisible(True)
        self.parent.setWindowState(self.parent.windowState() & ~(Qt.WindowMinimized | Qt.WindowActive))
        self.parent.config_dialog()

    def iconActivated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.showMainWidget()
