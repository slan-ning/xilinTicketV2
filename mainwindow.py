__author__ = 'Administrator'

from ui_main import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.Qt import *
from configparser import ConfigParser
from c12306 import C12306
from c12306 import C12306Error
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QByteArray
from PyQt5.QtCore import QTimer
from ticket import Ticket


class MainWindow(QMainWindow, Ui_MainWindow):
    _config = ConfigParser()
    _my12306 = C12306()
    _search_running = False

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        #响应事件
        self.loginBtn.clicked.connect(self.login)
        self.lb_auth_img.clicked.connect(self.show_auth_code)
        self.slider.valueChanged.connect(self.query_interval_changed)
        self.searchBtn.clicked.connect(self.search)
        #加载验证码
        self.show_auth_code()
        self.passager_table.create_menu()

        self._config.read("config.ini")
        config_dict = self._config.defaults()

        try:
            username = config_dict['username']
            password = config_dict['password']
            self.edit_username.setText(username)
            self.edit_password.setText(password)
            self.edit_from_station.setText(config_dict['fromstation'])
            self.edit_to_station.setText(config_dict['tostation'])
            self.slider.setValue(int(config_dict['interval']))
            self.dateControl.setDate(QDate.fromString(config_dict['traindate'],"yyyy-MM-dd"))
            self.passager_table.load_from_config()
        except:
            pass

    def login(self):
        username = self.edit_username.text()
        password = self.edit_password.text()
        auth_code = self.edit_auth_code.text()
        self._config.set('DEFAULT', 'username', username)
        self._config.set('DEFAULT', 'password', password)
        with open('config.ini', 'w') as configfile:
            self._config.write(configfile)
            configfile.close()

        try:
            self._my12306.login(username, password, auth_code)
            self.memo.append('登陆成功!')
        except C12306Error as e:
            self.memo.append(e.value)


    def show_auth_code(self):
        img_data = self._my12306.auth_code_img('login')
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(img_data))
        self.lb_auth_img.setPixmap(pixmap)
        self.lb_auth_img.setScaledContents(True)
        self.lb_auth_img.show()

    def query_interval_changed(self, value):
        self.lb_speed_num.setText(str(value) + "s")

    def search(self, start: bool):
        if start:
            self.from_station = self.edit_from_station.text()
            self.to_station = self.edit_to_station.text()
            self.train_date = self.dateControl.date().toString("yyyy-MM-dd")

            self._config.set('DEFAULT', 'fromstation', self.from_station)
            self._config.set('DEFAULT', 'tostation', self.to_station)
            self._config.set('DEFAULT', 'traindate', self.train_date)
            self._config.set('DEFAULT', 'interval', str(self.slider.sliderPosition()))

            with open('config.ini', 'w') as configfile:
                self._config.write(configfile)
                configfile.close()
            self.passager_table.save_to_config()

            #定时执行
            self._timer=QTimer()
            self._timer.timeout.connect(self.interval_search)
            self._timer.start(self.slider.sliderPosition()*1000)
            self.searchBtn.setText('停止')
        else:
            self._timer.stop()
            self.searchBtn.setText('开始')


    def interval_search(self):
        try:
            data=self._my12306.search_ticket(self.from_station,self.to_station,self.train_date)
            ticketList=self.get_need_seat(data)

            for ticket in ticketList:
                self.buyTicket(ticket)

        except C12306Error as e:
            self.memo.append(e.value)

    def get_need_seat(self,ticketInfo):
        ticketList=[]
        needSeatNum=len(self.passager_table.selectedPassenger())

        for info in ticketInfo:
            if self.cb_first_seat.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['zy_num'],needSeatNum):
                ticketList.append(Ticket(info,'M'))
            elif self.cb_second_seat.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['ze_num'],needSeatNum):
                ticketList.append(Ticket(info,'0'))
            elif self.cb_soft_bed.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['rw_num'],needSeatNum):
                ticketList.append(Ticket(info,'4'))
            elif self.cb_hard_bed.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['yw_num'],needSeatNum):
                ticketList.append(Ticket(info,'3'))
            elif self.cb_hard_seat.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['yz_num'],needSeatNum):
                ticketList.append(Ticket(info,'1'))
            elif self.cb_stand.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['wz_num'],needSeatNum):
                ticketList.append(Ticket(info,'1'))

        return ticketList

    def is_ticket_enough(self,ticketNumStr,needNum):
        if ticketNumStr in ('--','*','无') :
            return False
        if ticketNumStr=='有':
            return True

        return int(ticketNumStr)>needNum

    def buyTicket(self,ticket):
        pass


