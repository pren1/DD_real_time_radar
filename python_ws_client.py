from Socket_setting import Socket_setting
from MongoDB import MongoDB
from Fast_naive_bayes import Naive_Bayes

class python_ws_client(object):
    def __init__(self):
        'Connect to dataset, connect to js server via ws'
        self.mongo_db = MongoDB(update_rank_list=False)
        self.NB_classifier = Naive_Bayes()

    def build_socket_with_clients(self):
        # socket_1 = Socket_setting(self.mongo_db, self.NB_classifier, ip_address='18.223.43.172', port=9003)
        socket_1 = Socket_setting(self.mongo_db, self.NB_classifier, ip_address='localhost', port=9003)
        # socket_1.close_room(21564812)
        socket_1.watch_room(21564812)

if __name__ == '__main__':
    ws_listenser = python_ws_client()
    ws_listenser.build_socket_with_clients()