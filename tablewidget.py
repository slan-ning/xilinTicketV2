__author__ = 'Administrator'

from PyQt5.QtWidgets import QTableWidget
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from configparser import ConfigParser


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
        self.setColumnWidth(4, 60)

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

        ticketTypeItem=QtWidgets.QTableWidgetItem('成人票')

        self.setItem(insert_row,0,check_item)
        self.setItem(insert_row,4,ticketTypeItem)

    def action_del(self):
        select_list=self.selectedItems()
        for item in select_list:
            self.removeRow(item.row())

    def selectedPassenger(self):
        itemCount=self.rowCount()
        passengerList=[]

        for i in range(itemCount):
            if self.item(i,0).checkState() ==QtCore.Qt.Checked:
                ticketTypeStr=self.item(i,4).text()

                if '儿童' in ticketTypeStr :
                    ticketType='2'
                elif '学生' in ticketTypeStr:
                    ticketType='3'
                elif '军残' in ticketTypeStr:
                    ticketType='4'
                else:
                    ticketType='1'

                passenger={'name':self.item(i,1).text(),'ticketType':ticketType,\
                           'telephone':self.item(i,2).text(),'idcard':self.item(i,3).text()}
                passengerList.append(passenger)

        return passengerList


    def save_to_config(self):

        itemCount=self.rowCount()
        config=ConfigParser()
        config.read('config.ini')

        passengerConfig={'passenger':{'count':itemCount}}

        for i in range(itemCount):
                passengerConfig['passenger']['name'+str(i)]=self.item(i,1).text()
                passengerConfig['passenger']['telephone'+str(i)]=self.item(i,2).text()
                passengerConfig['passenger']['idcard'+str(i)]=self.item(i,3).text()
                passengerConfig['passenger']['ticketType'+str(i)]=self.item(i,4).text()
                passengerConfig['passenger']['check'+str(i)]=True if self.item(i,0).checkState()==QtCore.Qt.Checked else False

        config.read_dict(passengerConfig)

        with open('config.ini', 'w') as configfile:
            config.write(configfile)
            configfile.close()


    def load_from_config(self):
        config=ConfigParser()
        config.read('config.ini')

        num=config.getint('passenger','count')
        for i in range(num):
            self.insertRow(i)
            check=config.getboolean('passenger','check'+str(i))
            name=config.get('passenger','name'+str(i))
            telephone=config.get('passenger','telephone'+str(i))
            idcard=config.get('passenger','idcard'+str(i))
            ticketType=config.get('passenger','ticketType'+str(i))

            check_item=QtWidgets.QTableWidgetItem('')
            check_item.setCheckState(QtCore.Qt.Checked if check else QtCore.Qt.Unchecked)

            name_item=QtWidgets.QTableWidgetItem(name)
            telephone_item=QtWidgets.QTableWidgetItem(telephone)
            idcard_item=QtWidgets.QTableWidgetItem(idcard)
            ticket_type_item=QtWidgets.QTableWidgetItem(ticketType)

            self.setItem(i,0,check_item)
            self.setItem(i,1,name_item)
            self.setItem(i,2,telephone_item)
            self.setItem(i,3,idcard_item)
            self.setItem(i,4,ticket_type_item)





