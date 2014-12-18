__author__ = 'Administrator'
import requests
import xlstr
import urllib.parse
import urllib
import xxtea
import random
import time



class C12306:
    username = ''
    password = ''
    domain = 'kyfw.12306.cn' #请求域名（真实连接地址）
    host='kyfw.12306.cn' #请求的域名（host）
    http = requests.session()
    leftTicketUrl="leftTicket/query"
    stationCode = {}
    loginDynamicKey=''
    loginDynamicVal=''

    def __init__(self,domain=''):
        if domain!='':
            self.domain=domain

        headers={"host":self.host}
        self.http.get("https://" + self.domain + "/otn/", verify=False,headers=headers)
        res = self.http.get('https://'+self.domain+'/otn/login/init', verify=False,headers=headers)
        assert isinstance(res, requests.Response)

        if not 'src=\"/otn/dynamicJs/' in res.text:
            raise C12306Error('初始化页面错误')

        dynamic_js_url = xlstr.substr(res.text, "src=\"/otn/dynamicJs/", "\"")
        ret=self.http.get("https://"+self.domain+"/otn/dynamicJs/" + dynamic_js_url, verify=False,headers=headers).text
        self.loginDynamicKey=xlstr.substr(ret,"gc(){var key='","'")
        self.loginDynamicVal=(xxtea.encrypt("1111",self.loginDynamicKey))

        #隐藏的监测url
        ready_str=xlstr.substr(ret,"$(document).ready(",")};")
        if ready_str.find("jq({url")>0 :
            checkHelperUrl=xlstr.substr(ready_str,"jq({url :'","'")
            self.http.get("https://"+self.domain+checkHelperUrl,verify=False,headers=headers)

        self.load_station_code()

    def load_station_code(self):
        """Load station telcode from 12306.cn

        加载车站电报码，各个请求中会用到
        :raise C12306Error:
        """
        header={"host":self.host}
        res = requests.get('https://'+self.domain+'/otn/resources/js/framework/station_name.js', verify=False,headers=header)
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

        headers = {'X-Requested-With': 'XMLHttpRequest','host':self.host,"Referer":"https://kyfw.12306.cn/otn/login/init"}

        checkData={"randCode":auth_code,"rand":"sjrand","randCode_validate":""}
        self.http.post("https://" + self.domain + "/otn/passcodeNew/checkRandCodeAnsyn",checkData,verify=False,headers=headers)
        time.sleep(1)


        data = {'loginUserDTO.user_name': self.username, 'userDTO.password': self.password, 'randCode': auth_code\
            ,"randCode_validate":"","myversion":"undefined"}
        data[self.loginDynamicKey]=self.loginDynamicVal


        res = self.http.post("https://" + self.domain + "/otn/login/loginAysnSuggest", data, verify=False,
                             headers=headers)

        if not 'loginCheck":"Y"},"' in res.text:
            print(res.text)
            raise C12306Error('登录失败:' + ''.join(res.json()['messages']))

        return True


    def auth_code_img(self, module='passenger'):
        if module=='passenger':
            url="https://" + self.domain + "/otn/passcodeNew/getPassCodeNew.do?module=passenger&rand=randp"
        else:
            url = "https://" + self.domain + "/otn/passcodeNew/getPassCodeNew?module=" + module + "&rand=sjrand"
        res = self.http.get(url, verify=False,headers={"host":self.host})
        assert isinstance(res, requests.Response)
        return res.content

    def load_search_page(self):
        headers={'Referer':'https://kyfw.12306.cn/otn/login/init',"host":self.host}
        leftText=self.http.get("https://"+self.domain+"/otn/leftTicket/init",verify=False,headers=headers).text
        self.leftTicketUrl=xlstr.substr(leftText,"var CLeftTicketUrl = '","'")

        dynamic_js_url = xlstr.substr(leftText, "src=\"/otn/dynamicJs/", "\"")
        ret=self.http.get("https://"+self.domain+"/otn/dynamicJs/" + dynamic_js_url, verify=False,headers=headers).text

        #隐藏的监测url
        ready_str=xlstr.substr(ret,"$(document).ready(",")};")
        if ready_str.find("jq({url")>0 :
            checkHelperUrl=xlstr.substr(ready_str,"jq({url :'","'")
            self.http.get("https://"+self.domain+checkHelperUrl,verify=False,headers=headers)

        self.searchDynamicKey=xlstr.substr(ret,"gc(){var key='","'")
        self.searchDynamicVal=urllib.parse.quote_plus(xxtea.encrypt("1111",self.searchDynamicKey))

        self.auth_code_img('login')

    def search_ticket(self, fromStation, toStation, date):

        headers={'Referer':'https://kyfw.12306.cn/otn/leftTicket/init',"host":self.host\
            ,"X-Requested-With":"XMLHttpRequest"}

        jc_fromStation=xxtea.unicodeStr(fromStation+","+self.stationCode[fromStation])
        jc_toStation=xxtea.unicodeStr(toStation+","+self.stationCode[toStation])
        self.http.cookies.set("_jc_save_fromStation",jc_fromStation)
        self.http.cookies.set("_jc_save_toStation",jc_toStation)
        self.http.cookies.set('_jc_save_fromDate',date)
        self.http.cookies.set('_jc_save_toDate',"2014-05-01")
        self.http.cookies.set('_jc_save_wfdc_flag','dc')

        t=str(random.random())
        dataUrl='?leftTicketDTO.train_date='+date\
            +"&leftTicketDTO.from_station="+self.stationCode[fromStation]+"&leftTicketDTO.to_station="+\
            self.stationCode[toStation]+"&purpose_codes=ADULT"
        logUrl='https://' + self.domain + '/otn/leftTicket/log'+dataUrl
        url='https://' + self.domain + '/otn/'+self.leftTicketUrl+dataUrl

        self.http.get(logUrl,verify=False,headers=headers)
        res = self.http.get(url,verify=False,headers=headers)
        ticketInfo=res.json()
        if ticketInfo['status']!=True or ticketInfo['messages']!=[] :
            print(ticketInfo)
            raise C12306Error('查询错误:'+''.join(ticketInfo['messages']))

        if len(ticketInfo['data'])<=0:
            raise C12306Error('查询错误:'+'没有找到直达车次，请重新查询!')

        return ticketInfo['data']

    def submit_order(self,ticket):
        """

        :param ticket: Ticket
        :return: :raise C12306Error:
        """
        data='secretStr='+ticket.secret_str+'&train_date='+ticket.train_date+'&back_train_date='+ticket.train_date+\
              '&tour_flag=dc&purpose_codes=ADULT&query_from_station_name='+ticket.from_station_name+\
              '&query_to_station_name='+ticket.to_station_name+'&undefined&'+self.searchDynamicKey+"="+self.searchDynamicVal
        headers={'Referer':'https://kyfw.12306.cn/otn/leftTicket/init','X-Requested-With':'XMLHttpRequest'\
            ,'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',"host":self.host}

        data=data.encode()

        self.http.post('https://'+self.domain+'/otn/login/checkUser',{"_json_att":""},verify=False,headers=headers)

        res=self.http.post('https://'+self.domain+'/otn/leftTicket/submitOrderRequest',data,verify=False,headers=headers)

        orderInfo=res.json()
        if orderInfo['status']!=True:
            raise C12306Error('提交订单错误:'+''.join(orderInfo['messages']))

        res=self.http.post('https://'+self.domain+'/otn/confirmPassenger/initDc',{'_json_att':''},verify=False,headers=headers)
        pageText=res.text

        self.Token=xlstr.substr(pageText,"globalRepeatSubmitToken = '","'")
        self.keyCheck=xlstr.substr(pageText,"'key_check_isChange':'","'")
        self.leftTicketStr=xlstr.substr(pageText,"leftTicketStr':'","'")
        self.trainLocation=xlstr.substr(pageText,"train_location':'","'")

        dynamic_js_url = xlstr.substr(res.text, "src=\"/otn/dynamicJs/", "\"");
        dynamic_js = self.http.get("https://"+self.domain +"/otn/dynamicJs/"+ dynamic_js_url, verify=False,headers=headers)


        #隐藏的监测url
        ready_str=xlstr.substr(dynamic_js.text,"$(document).ready(",")};")
        if ready_str.find("jq({url")>0 :
            checkHelperUrl=xlstr.substr(ready_str,"jq({url :'","'")
            self.http.get("https://"+self.domain+checkHelperUrl,verify=False,headers=headers)

        self.dynamicKey=xlstr.substr(dynamic_js.text,"gc(){var key='","'")
        self.dynamicVal=xxtea.encrypt("1111",self.dynamicKey)
        self.dynamicVal=urllib.parse.quote_plus(self.dynamicVal)

        if  len(self.Token)!=32 :
            raise C12306Error('预定页面获取失败!')

        return True


    def check_order(self,Ticket,passengerList,randCode):
        if len(passengerList)<1 :
            raise C12306Error('没有勾选乘客，无法购票!')

        headers={'Referer':'https://kyfw.12306.cn/otn/confirmPassenger/initDc','X-Requested-With':'XMLHttpRequest'\
            ,'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',"host":self.host}

        checkData={"randCode":randCode,"rand":"randp","REPEAT_SUBMIT_TOKEN":self.Token}
        ret=self.http.post("https://" + self.domain + "/otn/passcodeNew/checkRandCodeAnsyn",checkData,verify=False,headers=headers)
        ret=ret.json()
        time.sleep(1)

        if(ret['status']!=True or ret['data']['result']!='1'):
            print(ret)
            return False

        ticketInfo=[]
        oldPassengerInfo=[]
        for passenger in passengerList:
            ticketStr=Ticket.seat_type+",0,"+passenger['ticketType']+","+passenger['name']+',1,'+passenger['idcard']+','+\
                      passenger['telephone']+',N'
            ticketInfo.append(ticketStr)
            oldPStr=passenger['name']+',1,'+passenger['idcard']+','+passenger['ticketType']
            oldPassengerInfo.append(oldPStr)
        ticketStrs=urllib.parse.quote_plus('_'.join(ticketInfo))
        oldPassengerStrs=urllib.parse.quote_plus('_'.join(oldPassengerInfo))

        pstr="cancel_flag=2&bed_level_order_num=000000000000000000000000000000&passengerTicketStr="+ticketStrs\
             +"&oldPassengerStr="+oldPassengerStrs+"&tour_flag=dc&randCode="+randCode+"&"+self.dynamicKey+"="+self.dynamicVal+\
             "&_json_att=&REPEAT_SUBMIT_TOKEN="+self.Token


        pstr=pstr.encode()

        res=self.http.post('https://'+self.domain+'/otn/confirmPassenger/checkOrderInfo',pstr,headers=headers)

        orderInfo=res.json()
        if orderInfo['status']!=True:
            raise C12306Error('提交订单错误:'+''.join(orderInfo['messages']))

        if orderInfo['data']['submitStatus'] ==False and  '验证码' in orderInfo['data']['errMsg']:
            return False

        if orderInfo['data']['submitStatus'] ==True:
            pstr="train_date="+urllib.parse.quote_plus(Ticket.train_date_utc)+"&train_no="+Ticket.train_no+"&stationTrainCode="+\
                 Ticket.station_train_code+"&seatType="+Ticket.seat_type+"&fromStationTelecode="+\
                 Ticket.from_station_telecode+"&toStationTelecode="+Ticket.to_station_telecode+"&leftTicket="+\
                 Ticket.yp_info+"&purpose_codes=00&_json_att=&REPEAT_SUBMIT_TOKEN="+self.Token

            pstr=pstr.encode()
            res=self.http.post('https://'+self.domain+'/otn/confirmPassenger/getQueueCount',pstr,headers=headers).json()

            if res['status']!=True:
                raise C12306Error('查询排队队列错误:'+''.join(res['messages']))

            if res['data']['op_2']!='false':
                raise C12306Error('排队人数已满，取消操作!')
            else:
                self.passengerStr="passengerTicketStr="+ticketStrs+"&oldPassengerStr="+oldPassengerStrs
                return True
        else:
            raise C12306Error('订单错误:'+''.join(orderInfo['data']['errMsg']))

    def confirm_order(self,randCode):
        pstr=self.passengerStr+"&randCode="+randCode+"&purpose_codes=00"+\
             "&key_check_isChange="+self.keyCheck+"&leftTicketStr="+self.leftTicketStr+\
             "&train_location="+self.trainLocation+"&_json_att=&REPEAT_SUBMIT_TOKEN="+self.Token
        pstr=pstr.encode()

        headers={'Referer':'https://kyfw.12306.cn/otn/confirmPassenger/initDc','X-Requested-With':'XMLHttpRequest'\
            ,'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',"host":self.host}

        res=self.http.post("https://"+self.domain+"/otn/confirmPassenger/confirmSingleForQueue",pstr,headers=headers).json()

        if res['status']==True :
            return True
        elif '请重试' in res['messages']:
            return self.confirm_order(randCode)
        else:
            raise C12306Error('确认订单出现错误:'+res['messages'])

    def keep_online(self):
        print("keep online")
        headers={'Referer':'https://kyfw.12306.cn/otn/leftTicket/init','X-Requested-With':'XMLHttpRequest'\
            ,'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',"host":self.host}
        self.http.get("https://"+self.domain+"/otn/queryOrder/initNoComplete",headers={"host":self.host})


class C12306Error(Exception):
    def __init__(self, val):
        self.value = val

    def __str__(self):
        str(self.value)
