__author__ = 'Administrator'

from ui_main import Ui_MainWindow
from PyQt5.QtWidgets import QMainWindow
from PyQt5.Qt import *
from configparser import ConfigParser
from c12306 import C12306
from c12306 import C12306Error
from PyQt5.QtGui import QPixmap
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import QByteArray
from PyQt5.QtCore import QTimer
from ticket import Ticket
from PyQt5.QtWidgets import QLineEdit
from ticket import SeatType
import time
import webbrowser
from searchthread import SearchThread

class MainWindow(QMainWindow, Ui_MainWindow):
    _config = ConfigParser()
    _my12306 = C12306()
    _search_running = False
    buying=False

    def __init__(self):
        super(MainWindow, self).__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowCloseButtonHint | Qt.MSWindowsFixedSizeDialogHint)
        #响应事件
        self.loginBtn.clicked.connect(self.login)
        self.lb_auth_img.clicked.connect(self.show_login_auth_code)
        self.lb_buy_img.clicked.connect(self.show_buy_auth_image)
        self.slider.valueChanged.connect(self.query_interval_changed)
        self.searchBtn.clicked.connect(self.search)
        self.btn_url_12306.clicked.connect(self.open_12306_site)
        #加载验证码
        self.show_login_auth_code()
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
            self.edit_train_num.setText(config_dict['specified_train'])
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
            self.show_message('登陆成功!')
        except C12306Error as e:
            self.show_message(e.value)


    def show_login_auth_code(self):
        img_data = self._my12306.auth_code_img('login')
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(img_data))
        self.lb_auth_img.setPixmap(pixmap)
        self.lb_auth_img.setScaledContents(True)
        self.lb_auth_img.show()

    def show_buy_auth_image(self):
        img_data = self._my12306.auth_code_img('passenger')
        pixmap = QPixmap()
        pixmap.loadFromData(QByteArray(img_data))
        self.lb_buy_img.setPixmap(pixmap)
        self.lb_buy_img.setScaledContents(True)
        self.lb_buy_img.show()


    def query_interval_changed(self, value):
        self.lb_speed_num.setText(str(value/2) + "s")

    def search(self, start: bool):
        if start:
            self.buying=False
            self.from_station = self.edit_from_station.text()
            self.to_station = self.edit_to_station.text()
            self.train_date = self.dateControl.date().toString("yyyy-MM-dd")

            self._config.set('DEFAULT', 'fromstation', self.from_station)
            self._config.set('DEFAULT', 'tostation', self.to_station)
            self._config.set('DEFAULT', 'traindate', self.train_date)
            self._config.set('DEFAULT', 'interval', str(self.slider.sliderPosition()))
            self._config.set('DEFAULT','specified_train',self.edit_train_num.text())

            with open('config.ini', 'w') as configfile:
                self._config.write(configfile)
                configfile.close()
            self.passager_table.save_to_config()

            if self.cb_rob_mode.checkState()==Qt.Checked :
                self.search_thread_start()
            else:
                #定时执行
                self._timer=QTimer()
                self._timer.timeout.connect(self.interval_search)
                self._timer.start(self.slider.sliderPosition()*500)

            self.keep_online_timer=QTimer()
            self.keep_online_timer.timeout.connect(self._my12306.keep_online)
            self.keep_online_timer.timeout.connect(self.clear_message)
            self.keep_online_timer.start(5*60*1000)

            self.searchBtn.setText('停止')
        else:
            try:
                self._timer.stop()
            except:
                pass

            try:
                self.search_thread_stop()
                self.keep_online_timer.stop()
            finally:
                self.searchBtn.setText('开始')

    def interval_search(self):
        try:
            data=self._my12306.search_ticket(self.from_station,self.to_station,self.train_date)
            ticketList=self.get_need_seat(data)

            if len(ticketList)>0 :
                self.show_message('发现有票，开始购买，如错误请重新点开始')
                self.searchBtn.setChecked(False)
                self.search(False)
                for ticket in ticketList:
                    self.buyTicket(ticket)
            else:
                self.show_message('没有合适的票')

        except C12306Error as e:
            self.show_message(e.value)

    def cdn_list(self):
        return ['218.59.186.76',
                '61.138.219.85',
                '220.165.142.51',
                '222.211.64.119',
                '182.140.236.27',
                '115.231.171.70',
                '115.231.22.80',
                '111.206.169.23',
                '111.206.217.106',
                '124.161.229.46',
                '175.154.189.30',
                '59.63.173.166',
                '218.87.111.178',
                '211.138.121.106',
                '211.138.121.108',
                '211.138.121.109',
                '218.60.106.91',
                '125.221.95.107',
                '123.138.60.183',
                '113.200.235.30',
                '61.156.243.247',
                '219.145.171.61',
                '124.115.20.49',
                '210.39.4.18',
                '210.39.4.17',
                '162.105.28.233',
                '113.107.112.214',
                '125.90.204.122',
                '113.107.112.87',
                '113.107.56.96',
                '222.186.132.79',
                '117.27.245.62',
                '125.78.240.186',
                '220.162.97.209']

    def search_thread_start(self):
        cdnList=self.cdn_list()
        self.searchThreadList=[]

        interval=self.slider.sliderPosition()/2
        i=0

        for ip in cdnList:
            i+=1
            thread=SearchThread(self.from_station,self.to_station,self.train_date,i,self._my12306.leftTicketUrl,interval,ip)
            thread.searchThreadCallback.connect(self.search_thread_callback)
            thread.start()
            self.searchThreadList.append(thread)

    def search_thread_stop(self):
        try:
            for thread in self.searchThreadList:
                thread.stop()
        except:
            pass

    def search_thread_callback(self,data):

        ticketList=self.get_need_seat(data)

        if self.buying ==True:
            return

        if len(ticketList)>0 :
            self.show_message('发现有票，开始购买，如错误请重新点开始')
            self.buying=True
            self.searchBtn.setChecked(False)
            for thread in self.searchThreadList :
                thread.stop()

            for ticket in ticketList:
                self.buyTicket(ticket)
            self.search(False)
        else:
            self.show_message('没有合适的票')

    def get_need_seat(self,ticketInfo):
        ticketList=[]
        needSeatNum=len(self.passager_table.selectedPassenger())
        specified_train=self.edit_train_num.text().strip()

        for info in ticketInfo:
            if specified_train!='' and info['queryLeftNewDTO']['station_train_code'] not in specified_train:
                continue
            if self.cb_first_seat.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['zy_num'],needSeatNum):
                ticketList.append(Ticket(info,'M'))
            elif self.cb_second_seat.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['ze_num'],needSeatNum):
                ticketList.append(Ticket(info,'O'))
            elif self.cb_soft_bed.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['rw_num'],needSeatNum):
                ticketList.append(Ticket(info,'4'))
            elif self.cb_hard_bed.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['yw_num'],needSeatNum):
                ticketList.append(Ticket(info,'3'))
            elif self.cb_hard_seat.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['yz_num'],needSeatNum):
                ticketList.append(Ticket(info,'1'))
            elif self.cb_stand.checkState()==Qt.Checked and self.is_ticket_enough(info['queryLeftNewDTO']['wz_num'],needSeatNum):
                trainCode=info['queryLeftNewDTO']['station_train_code']
                if 'G' in trainCode or 'D' in trainCode:
                    ticketList.append(Ticket(info,'O'))
                else:
                    ticketList.append(Ticket(info,'1'))

        return ticketList

    def is_ticket_enough(self,ticketNumStr,needNum):
        if ticketNumStr in ('--','*','无') :
            return False
        if ticketNumStr=='有':
            return True

        return int(ticketNumStr)>=needNum

    def buyTicket(self,ticket):
        try:
            self.show_message('开始购买:'+ticket.train_date+' '+ticket.station_train_code+SeatType[ticket.seat_type])
            self._my12306.submit_order(ticket)

            passengerList=self.passager_table.selectedPassenger()

            buying=True

            while buying:
                self.show_buy_auth_image()
                (yzcode,ret)=QInputDialog.getText(None,'验证码','请输入购买验证码',QLineEdit.Normal)
                if ret==False:
                    self.show_message('您取消了购票')
                    return False

                status=self._my12306.check_order(ticket,passengerList,yzcode)

                if status ==True:
                    self.show_message('nice! 有票!')

                    if self._my12306.confirm_order(yzcode) :
                        self.show_message('<div style="color:green">抢票成功，速速到12306.cn付款</div>')
                    else:
                        self.show_message('抢票失败!')

                    buying=False
                else :
                    self.show_message('验证码错误，请重新输入!')
                    buying=True

        except C12306Error as e:
            buying=False
            self.show_message(e.value)


    def show_message(self,msg):
        self.memo.ensureCursorVisible()
        self.memo.append(time.strftime("%m-%d %H:%M:%S ", time.localtime()) +msg)
        self.memo.moveCursor(QTextCursor.End)

    def clear_message(self):
        print("清空!")
        self.memo.clear()

    def open_12306_site(self):
        webbrowser.open("https://kyfw.12306.cn/otn/queryOrder/initNoComplete")



