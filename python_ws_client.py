from Socket_setting import Socket_setting
from MongoDB import MongoDB
from Fast_naive_bayes import Naive_Bayes
import requests
from flask import jsonify
import pdb
import pprint
import datetime, threading, time
# from Client_Scheduling import Client_Secheduler

class python_ws_client(object):
    def __init__(self):
        'Connect to dataset, connect to js server via ws'
        self.mongo_db = MongoDB(update_rank_list=False)
        # self.mongo_db.clean_up_serverdb()
        self.NB_classifier = Naive_Bayes()
        self.global_lock=threading.Lock()

        # self.open_room_list = []
        # self.ip_list = ['localhost', '18.222.55.98', '18.188.26.14', '18.219.63.159']
        # self.ip_list = ['localhost']
        # self.server_id_dict = {}
        # for index, ip in enumerate(self.ip_list):
        #     self.server_id_dict[ip] = index + 1
        # self.socket_list = self.build_socket_dict_list_with_clients(self.ip_list)
        # 'Test the running time of target func'
        # start_time = time.time()
        # self.open_room_list = self.obtain_open_room_list_periodically()
        # self.secheduler = Client_Secheduler(self.socket_list, self.open_room_list, self.mongo_db.room_info_dict)
        # self.period_seconds = int(time.time() - start_time) * 5
        # self.Schedual_roomid_to_clients()
        # print("--- %s seconds ---" % (self.period_seconds))
        self.socket = Socket_setting(self.mongo_db, self.NB_classifier, global_lock=self.global_lock, ip_address='localhost',
                       server_id=0, port=9003)

    # def build_socket_dict_list_with_clients(self, ip_list):
    #     'Build sockets'
    #     res = []
    #     for single_ip in ip_list:
    #         res.append({
    #             'ip': single_ip,
    #             'socket': Socket_setting(self.mongo_db, self.NB_classifier, global_lock = self.global_lock, ip_address=single_ip, server_id = self.server_id_dict[single_ip], port=9003)
    #         })
    #     return res

    # def obtain_open_room_list_periodically(self):
    #     'Only concentrate on open room'
    #     contents = requests.get('https://api.vtbs.moe/v1/info').json()
    #     result = []
    #     for single in contents:
    #         if single['liveStatus'] == 1:
    #             result.append(single['roomid'])
    #     pprint.pprint(f"overhead: {len(result)}")
    #     print(f"overhead: {len(result)}", file=open("log.txt", "a"))
    #     return result

    # def Schedual_roomid_to_clients(self):
    #     # self.secheduler.renew_every_socket_connection()
    #     self.secheduler.renew_client_tasks_using_new_roomid_list(self.open_room_list)
    #     tempory_client_dict = self.secheduler.find_client_dict()
    #     room_list_dict = self.secheduler.find_room_id_name_dict()
    #     current_event_dict = self.secheduler.current_event
    #     server_status = self.secheduler.server_status
    #
    #     'Then, we could write into the database, the information would be shown on the website..'
    #     for single_key in tempory_client_dict:
    #         # print(f"overhead: {tempory_client_dict[single_key]}")
    #         Server_dict = {
    #             'server id': self.server_id_dict[single_key],
    #             'overhead': tempory_client_dict[single_key],
    #             'room_list': room_list_dict[single_key],
    #             'current_event': current_event_dict[single_key],
    #             'server_status': server_status[single_key]
    #         }
    #         self.global_lock.acquire()
    #         self.mongo_db.update_server_db_according_to_server_dict(Server_dict)
    #         self.global_lock.release()
    #     # print(self.mongo_db.get_updated_server_info())

    # def begin_update_data_periodically(self):
    #     timerThread = threading.Thread(target=self.timer_func)
    #     timerThread.start()
    #
    #     reconnectionThread = threading.Thread(target=self.periodically_reconnecton())
    #     reconnectionThread.start()

    # def periodically_reconnecton(self):
    #     'say, every single minute'
    #     while True:
    #         time.sleep(40)
    #         print(f"test at: {datetime.datetime.now()}")
    #         print(f"test at: {datetime.datetime.now()}", file=open("log.txt", "a"))
    #         self.secheduler.renew_every_socket_connection()

    # def timer_func(self):
    #     while True:
    #         try:
    #             self.open_room_list = self.obtain_open_room_list_periodically()
    #             self.Schedual_roomid_to_clients()
    #         except BaseException as error:
    #             time.sleep(20)
    #             print('An exception occurred: {}, will try again later...'.format(error))
    #             print('An exception occurred: {}, will try again later...'.format(error), file=open("log.txt", "a"))
    #         else:
    #             time.sleep(20)

if __name__ == '__main__':
    ws_listenser = python_ws_client()
    # ws_listenser.begin_update_data_periodically()
    # ws_listenser.obtain_open_room_list_periodically()
    # ws_listenser.build_socket_with_clients()