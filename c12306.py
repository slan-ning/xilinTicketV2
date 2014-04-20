__author__ = 'Administrator'
import requests
import xlstr
import json


class C12306:
    username = ''
    password = ''
    domain = 'kyfw.12306.cn'
    http = requests.session()
    stationCode = {}

    def __init__(self):
        self.http.get("https://" + self.domain + "/otn/", verify=False)
        res = self.http.get('https://kyfw.12306.cn/otn/login/init', verify=False)
        assert isinstance(res, requests.Response)

        if not '/otn/dynamicJs/loginJs' in res.text:
            raise C12306Error('初始化页面错误')

        dynamic_js_url = xlstr.substr(res.text, "/otn/dynamicJs/loginJs", "\"");
        dynamic_js = self.http.get("https://kyfw.12306.cn" + dynamic_js_url, verify=False)
        self.load_station_code()

    def load_station_code(self):
        """Load station telcode from 12306.cn

        加载车站电报码，各个请求中会用到
        :raise C12306Error:
        """
        res = requests.get('https://kyfw.12306.cn/otn/resources/js/framework/station_name.js', verify=False)
        if res.status_code != 200:
            raise C12306Error('加载车站信息错误,请重开!')

        stationStrs = xlstr.substr(res.text, "'", "'")
        stationList = stationStrs.split('@')
        stationDict = {}

        for stationStr in stationList:
            station = stationStr.split("|")
            if len(station) > 3:
                stationDict[station[1]] = station[2]

        self.stationCode = stationDict


    def login(self, username, password, auth_code):
        self.username = username
        self.password = password

        data = {'loginUserDTO.user_name': self.username, 'userDTO.password': self.password, 'randCode': auth_code}
        headers = {'X-Requested-With': 'XMLHttpRequest'}

        res = self.http.post("https://" + self.domain + "/otn/login/loginAysnSuggest", data, verify=False,
                             headers=headers)

        if not 'loginCheck":"Y"},"' in res.text:
            raise C12306Error('登录失败:' + ''.join(res.json()['messages']))

        return True


    def auth_code_img(self, module='passenger'):
        url = "https://" + self.domain + "/otn/passcodeNew/getPassCodeNew?module=" + module + "&rand=sjrand"
        res = self.http.get(url, verify=False)
        assert isinstance(res, requests.Response)
        return res.content


    def search_ticket(self, fromStation, toStation, date, host=''):
        if host == '':
            host = self.domain

        headers={'Referer':'https://kyfw.12306.cn/otn/leftTicket/init'}

        url='https://' + host + '/otn/leftTicket/query?leftTicketDTO.train_date='+date\
            +"&leftTicketDTO.from_station="+self.stationCode[fromStation]+"&leftTicketDTO.to_station="+\
            self.stationCode[toStation]+"&purpose_codes=ADULT"

        res = self.http.get(url,verify=False,headers=headers)
        ticketInfo=res.json()
        if ticketInfo['status']!=True or ticketInfo['messages']!=[] :
            raise C12306Error('查询错误:'+''.join(ticketInfo['messages']))

        if len(ticketInfo['data'])<=0:
            raise C12306Error('查询错误:'+'没有找到直达车次，请重新查询!')

        return ticketInfo['data']



class C12306Error(Exception):
    def __init__(self, val):
        self.value = val

    def __str__(self):
        str(self.value)
