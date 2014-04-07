__author__ = 'Administrator'
from PyQt5 import QtWidgets

import sys
from mainwindow import MainWindow
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())