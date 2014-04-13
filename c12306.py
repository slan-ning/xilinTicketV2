__author__ = 'Administrator'
import requests
import xlstr
import json


class C12306:
    username = ''
    password = ''
    domain = 'kyfw.12306.cn'
    http=requests.session()

    def __init__(self):
        self.http.get("https://" + self.domain + "/otn/", verify=False)
        res = self.http.get('https://kyfw.12306.cn/otn/login/init', verify=False)
        assert isinstance(res, requests.Response)

        if not '/otn/dynamicJs/loginJs' in res.text:
            raise C12306Error('初始化页面错误')

        dynamic_js_url = xlstr.substr(res.text, "/otn/dynamicJs/loginJs", "\"");
        dynamic_js = self.http.get("https://kyfw.12306.cn" + dynamic_js_url, verify=False)


    def login(self, username, password,auth_code):
        self.username = username
        self.password = password

        data={'loginUserDTO.user_name':self.username,'userDTO.password':self.password,'randCode':auth_code}
        headers={'x-requested-with':'XMLHttpRequest'}

        res=self.http.post("https://"+self.domain+"/otn/login/loginAysnSuggest",data,verify=False,headers=headers)

        if not 'loginCheck":"Y"},"' in res.text:
            raise C12306Error('登录失败:'+''.join(res.json()['messages']))

        return True


    def auth_code_img(self, module='passenger'):
        url = "https://" + self.domain + "/otn/passcodeNew/getPassCodeNew?module=" + module + "&rand=sjrand"
        res = self.http.get(url, verify=False)
        assert isinstance(res, requests.Response)
        return res.content


class C12306Error(Exception):
    def __init__(self, val):
        self.value = val

    def __str__(self):
        repr(self.value)
