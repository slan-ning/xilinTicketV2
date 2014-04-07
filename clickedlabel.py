__author__ = 'Administrator'

from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal


class ClickedLabel(QLabel):
    clicked = pyqtSignal(name='clicked')

    def __init(self, parent):
        QLabel.__init__(self, parent)

    def mouseReleaseEvent(self, ev):
        self.clicked.emit()