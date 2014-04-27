__author__ = 'Administrator'
import requests
import xlstr
import time


class Ticket:
    #车票信息
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
    train_date_utc=''
    seat_type = ''

    def __init__(self, ticket_obj, buy_type):
        self.train_no = ticket_obj['queryLeftNewDTO']['train_no']
        self.from_station_telecode = ticket_obj['queryLeftNewDTO']['from_station_telecode']
        self.from_station_name = ticket_obj['queryLeftNewDTO']['from_station_name']
        self.to_station_telecode = ticket_obj['queryLeftNewDTO']['to_station_telecode']
        self.to_station_name = ticket_obj['queryLeftNewDTO']['to_station_name']
        self.yp_info = ticket_obj['queryLeftNewDTO']['yp_info']
        self.start_train_date = ticket_obj['queryLeftNewDTO']['start_train_date']
        self.location_code = ticket_obj['queryLeftNewDTO']['location_code']
        self.secret_str = ticket_obj['secretStr']
        self.station_train_code = ticket_obj['queryLeftNewDTO']['station_train_code']

        trainTime = time.strptime(self.start_train_date, '%Y%m%d')
        self.train_date = time.strftime('%Y-%m-%d', trainTime)
        self.train_date_utc=time.strftime('%a %b %d %H:%M:%S UTC+0800 %Y',trainTime)

        self.seat_type = buy_type


SeatType={'M':'一等座','0':'二等座','4':'软卧','3':'硬卧','1':'硬座/无坐'}