__author__ = 'Administrator'
from PyQt5.QtCore import (QThread,pyqtSignal,QSemaphore,QUrl)
from PyQt5.QtNetwork import (QNetworkAccessManager,QNetworkRequest)
import requests
import xxtea
import time
import json
import random

mutex=QSemaphore(20)

class SearchThread(QThread):
    domain = 'kyfw.12306.cn' #请求域名（真实连接地址）
    host='kyfw.12306.cn' #请求的域名（host）
    http = requests.session()
    stopSignal=False
    threadId=1
    leftTicketUrl="leftTicket/query"
    requests.packages.urllib3.disable_warnings()

    searchThreadCallback= pyqtSignal(list)

    def __init__(self,from_station,to_station,train_date,threadId,leftTicketUrl,interval=2,domain=''):
        super(SearchThread,self).__init__()
        if domain!='':
            self.domain=domain

        self.threadId=threadId
        self.from_station=from_station
        self.to_station=to_station
        self.train_date=train_date
        self.interval=interval
        self.leftTicketUrl=leftTicketUrl


    def run(self):
        time.sleep(self.threadId)

        userAgent="Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2062.120 Safari/537.36"
        headers={'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',"host":self.host\
            ,'Cache-Control':'no-cache','Pragma':"no-cache","User-Agent":userAgent,"X-Requested-With":"XMLHttpRequest"}

        t=str(random.random())

        dataUrl='?leftTicketDTO.train_date='+self.train_date\
            +"&leftTicketDTO.from_station="+self.stationCode[self.from_station]+"&leftTicketDTO.to_station="+\
            self.stationCode[self.to_station]+"&purpose_codes=ADULT"

        logUrl='https://' + self.domain + '/otn/leftTicket/log'+dataUrl
        url='https://' + self.domain + '/otn/'+self.leftTicketUrl+dataUrl


        self.http.get(logUrl,verify=False,headers=headers)
        jc_fromStation=xxtea.unicodeStr(self.from_station+","+self.stationCode[self.from_station])
        jc_toStation=xxtea.unicodeStr(self.to_station+","+self.stationCode[self.to_station])
        self.http.cookies.set("_jc_save_fromStation",jc_fromStation)
        self.http.cookies.set("_jc_save_toStation",jc_toStation)
        self.http.cookies.set('_jc_save_fromDate',self.train_date)
        self.http.cookies.set('_jc_save_toDate',"2014-01-01")
        self.http.cookies.set('_jc_save_wfdc_flag','dc')

        ret=self.http.get(url,verify=False,headers=headers)
        ticketInfo=ret.json()

        if ticketInfo['status']!=True :
            print(ticketInfo)

        cookies=self.http.cookies.get_dict()
        cookieStr=";".join('%s=%s' % (key, value) for (key, value) in cookies.items())

        self.http.get(logUrl,verify=False,headers=headers)
        self.req=QNetworkRequest()
        self.req.setUrl(QUrl(url))
        self.req.setRawHeader("Referer","https://kyfw.12306.cn/otn/leftTicket/init")
        self.req.setRawHeader("host",self.host)
        self.req.setRawHeader("Cache-Control","no-cache")
        self.req.setRawHeader("Pragma","no-cache")
        self.req.setRawHeader("User-Agent",userAgent)
        self.req.setRawHeader("Cookie",cookieStr)

        while not self.stopSignal:
            mutex.acquire(1)
            self.search_ticket(self.from_station,self.to_station,self.train_date)
            mutex.release(1)
            time.sleep(self.interval)


    def search_ticket(self, fromStation, toStation, date):
        try:
            self.netWorkManager=QNetworkAccessManager()
            self.reply=self.netWorkManager.get(self.req)
            self.reply.ignoreSslErrors()
            self.reply.finished.connect(self.search_finished)
            self.exec()

        except Exception as e:
            print("ip:"+self.domain+"查询发生错误："+e.__str__())
            return False



    def search_finished(self):
        try:
            ret=self.reply.readAll()
            ret=str(ret,'utf8')
            ticketInfo=json.loads(ret)
            self.reply=None
            self.netWorkManager=None
            self.exit()
            if ticketInfo['status']!=True or ticketInfo['messages']!=[] :
                print(self.domain)
                print(ticketInfo)
                return False

            if len(ticketInfo['data'])<=0:
                return False

            data=ticketInfo['data']
            ret=None
            ticketInfo=None

            self.searchThreadCallback.emit(data)
        except Exception as e:
            print(e.__str__())

    def load_station_code(self,stationCode):
        self.stationCode = stationCode
        return True

    def stop(self):
        self.stopSignal=True