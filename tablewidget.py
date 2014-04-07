__author__ = 'Administrator'

from PyQt5.QtWidgets import QTableWidget
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui


class TableWidget(QTableWidget):
    def __init__(self, parent):
        #QTableWidget.__init__(self, parent)
        super(TableWidget,self).__init__(parent)


    def create_menu(self):
        '''''
        创建右键菜单
        '''
        # 必须将ContextMenuPolicy设置为Qt.CustomContextMenu
        # 否则无法使用customContextMenuRequested信号
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        # 设置表头宽度
        self.setColumnWidth(0, 30)
        self.setColumnWidth(1, 60)
        self.setColumnWidth(2, 84)
        self.setColumnWidth(3, 154)

        # 创建QMenu
        self.contextMenu = QtWidgets.QMenu(self)
        self.actionAdd = self.contextMenu.addAction('添加')
        self.actionDel = self.contextMenu.addAction('删除')
        # 将动作与处理函数相关联
        # 这里为了简单，将所有action与同一个处理函数相关联，
        # 当然也可以将他们分别与不同函数关联，实现不同的功能
        self.actionAdd.triggered.connect(self.action_add)
        self.actionDel.triggered.connect(self.action_del)


    def showContextMenu(self, pos):
        '''''
        右键点击时调用的函数
        '''
        # 菜单显示前，将它移动到鼠标点击的位置
        self.contextMenu.move(QtGui.QCursor.pos())
        self.contextMenu.show()

    def action_add(self):
        insert_row=self.rowCount()
        self.insertRow(insert_row)

        check_item=QtWidgets.QTableWidgetItem('')
        check_item.setCheckState(QtCore.Qt.Checked)

        self.setItem(insert_row,0,check_item)

    def action_del(self):
        select_list=self.selectedItems()
        for item in select_list:
            self.removeRow(item.row())
