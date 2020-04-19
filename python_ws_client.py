from Socket_setting import Socket_setting
from MongoDB import MongoDB
from Fast_naive_bayes import Naive_Bayes
import requests
from flask import jsonify
import pdb
import pprint
import datetime, threading, time
from Client_Scheduling import Client_Secheduler

class python_ws_client(object):
    def __init__(self):
        'Connect to dataset, connect to js server via ws'
        self.mongo_db = MongoDB(update_rank_list=False)
        self.NB_classifier = Naive_Bayes()
        self.global_lock=threading.Lock()

        self.open_room_list = []
        self.ip_list = ['localhost', '18.223.43.172', '13.59.178.54', '18.218.167.172']
        # self.ip_list = ['localhost']
        self.socket_list = self.build_socket_dict_list_with_clients(self.ip_list)
        'Test the running time of target func'
        start_time = time.time()
        self.open_room_list = self.obtain_open_room_list_periodically()
        self.secheduler = Client_Secheduler(self.socket_list, self.open_room_list)
        self.period_seconds = int(time.time() - start_time) * 5
        self.Schedual_roomid_to_clients()
        # print("--- %s seconds ---" % (self.period_seconds))

    def build_socket_dict_list_with_clients(self, ip_list):
        'Build sockets'
        res = []
        for single_ip in ip_list:
            res.append({
                'ip': single_ip,
                'socket': Socket_setting(self.mongo_db, self.NB_classifier, global_lock = self.global_lock, ip_address=single_ip, port=9003)
            })
        return res

    def obtain_open_room_list_periodically(self):
        'Only concentrate on open room'
        contents = requests.get('https://api.vtbs.moe/v1/info').json()
        result = []
        for single in contents:
            if single['liveStatus'] == 1:
                result.append(single['roomid'])
        # pprint.pprint(result)
        return result

    def Schedual_roomid_to_clients(self):
        self.secheduler.renew_client_tasks_using_new_roomid_list(self.open_room_list)

    def begin_update_data_periodically(self):
        timerThread = threading.Thread(target=self.timer_func)
        timerThread.start()

    def timer_func(self):
        next_call = time.time()
        while True:
            print(f"update room list at: {datetime.datetime.now()}")
            start_time = time.time()
            self.open_room_list = self.obtain_open_room_list_periodically()
            self.Schedual_roomid_to_clients()
            self.period_seconds = int(time.time() - start_time) * 5
            print("--- %s seconds ---" % (self.period_seconds))
            next_call = next_call + self.period_seconds
            time.sleep(max(next_call - time.time(), 2))

if __name__ == '__main__':
    ws_listenser = python_ws_client()
    # ws_listenser.begin_update_data_periodically()
    # ws_listenser.obtain_open_room_list_periodically()
    # ws_listenser.build_socket_with_clients()