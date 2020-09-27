import socketio
from MongoDB import MongoDB
from Fast_naive_bayes import Naive_Bayes
# from leader_board_drawer import leader_board_drawer

class python_ws_client(object):
    def __init__(self):
        'Connect to dataset, connect to js server via ws'
        self.mongo_db = MongoDB(update_rank_list=False)
        self.leader_board_index = 0
        self.sio = socketio.Client()
        self.sio.on('connect', self.socket_connected)
        self.sio.on('message', self.message_received)
        self.sio.connect('http://localhost:9003')
        self.NB_classifier = Naive_Bayes()
        # self.leader_board = leader_board_drawer(self.mongo_db)

    def socket_connected(self):
        print("Connected with js server")
        print(self.sio.eio.sid)

    def message_received(self, message):
        'on received danmakus'
        is_interpretation, log_meg = self.NB_classifier.decide_class(message['message'])
        print(f"{log_meg}")
        if is_interpretation:
            self.mongo_db.update_everything_according_to_a_new_message(message)
        # self.leader_board_index += 1
        # if self.leader_board_index % 10 == 0 and self.leader_board_index >= 10:
        #     'Draw leader board'
        #     self.leader_board.process_leader_board(k_largest=10)

    def send_message(self):
        self.sio.emit("something", "Hello from python.")
        self.sio.send("hello")

if __name__ == '__main__':
    ws_listenser = python_ws_client()
    # ws_listenser.send_message()