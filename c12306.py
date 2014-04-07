__author__ = 'Administrator'
import requests
import xlstr


class C12306:
    username = ''
    password = ''
    domain = 'kyfw.12306.cn'

    def __init__(self):
        requests.get("https://" + self.domain + "/otn/", verify=False)
        res = requests.get('https://kyfw.12306.cn/otn/login/init', verify=False)
        assert isinstance(res, requests.Response)

        if not '/otn/dynamicJs/loginJs' in res.text:
            raise C12306Error('初始化页面错误')

        dynamic_js_url = xlstr.substr(res.text, "/otn/dynamicJs/loginJs", "\"");
        dynamic_js = requests.get("https://kyfw.12306.cn" + dynamic_js_url, verify=False)

    def login(self, username, password,auth_code):
        self.username = username
        self.password = password

    def auth_code_img(self, module='passenger'):
        url = "https://" + self.domain + "/otn/passcodeNew/getPassCodeNew?module=" + module + "&rand=sjrand"
        res = requests.get(url, verify=False)
        assert isinstance(res, requests.Response)
        return res.content


class C12306Error(Exception):
    def __init__(self, val):
        self.value = val

    def __str__(self):
        repr(self.value)
