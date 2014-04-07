__author__ = 'Administrator'
import requests
import xlstr


class Ticket:
    #座位信息
    first_seat = ''
    second_seat = ''
    soft_bed = ''
    hard_bed = ''
    hard_seat = ''

    #车站信息
    train_no = ''
    station_train_code = ''  #车次编号，例如K540
    from_station_telecode = ''
    from_station_name = ''
    to_station_telecode = ''
    to_station_name = ''
    yp_info = ''  #未知信息
    location_code = ''
    secret_str = ''
    start_train_date = ''  #乘车日期，例如20140127

    #乘车信息
    train_date = ''
    seat_type = ''

    def __init__(self, ticket_str:str):
        self.train_no = xlstr.substr(ticket_str, "train_no\":\"", "\"")
        self.from_station_telecode = xlstr.substr(ticket_str, "from_station_telecode\":\"", "\"")
        self.from_station_name = xlstr.substr(ticket_str, "from_station_name\":\"", "\"")
        self.to_station_telecode = xlstr.substr(ticket_str, "to_station_telecode\":\"", "\"")
        self.to_station_name = xlstr.substr(ticket_str, "to_station_name\":\"", "\"")
        self.yp_info = xlstr.substr(ticket_str, "yp_info\":\"", "\"")
        self.start_train_date = xlstr.substr(ticket_str, "start_train_date\":\"", "\"")
        self.train_date = ''#xlstr.DateFormat(self.start_train_date, "%Y-%m-%d")
        self.location_code = xlstr.substr(ticket_str, "location_code\":\"", "\"")
        self.secret_str = xlstr.substr(ticket_str, "secretStr\":\"", "\"")
        self.station_train_code = xlstr.substr(ticket_str, "station_train_code\":\"", "\"")

        self.first_seat = xlstr.substr(ticket_str, "\"zy_num\":\"", "\"")
        self.second_seat = xlstr.substr(ticket_str, "\"ze_num\":\"", "\"")
        self.soft_bed = xlstr.substr(ticket_str, "\"rw_num\":\"", "\"")
        self.hard_bed = xlstr.substr(ticket_str, "\"yw_num\":\"", "\"")
        self.hard_seat = xlstr.substr(ticket_str, "\"yz_num\":\"", "\"")

    def login(self):
        pass