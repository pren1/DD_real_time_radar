import socketio

class Socket_setting(object):
    def __init__(self, MongoDB, NB_classifier, global_lock, ip_address, server_id, port=9003):
        'Connect to dataset, connect to js server via ws'
        self.mongo_db = MongoDB
        self.NB_classifier = NB_classifier
        self.global_lock = global_lock
        self.ip_address = ip_address
        self.server_id = server_id
        self.port = port
        self.sio = socketio.Client()
        self.sio.on('connect', self.socket_connected)
        self.sio.on('message', self.message_received)
        self.sio.on('disconnect', self.handle_disconnection)
        self.sio.connect(f'http://{self.ip_address}:{self.port}')

    def handle_disconnection(self):
        print("Disconnected, get connected again...")
        # self.sio.connect(f'http://{self.ip_address}:{self.port}')

    # def socket_reconnect(self):
    #     self.sio.connect(f'http://{self.ip_address}:{self.port}')

    def socket_connected(self):
        print("Connected with js server")
        print(self.sio.eio.sid)

    def message_received(self, message):
        'on received danmakus'
        is_interpretation, log_meg = self.NB_classifier.decide_class(message['message'])
        # print(f"{log_meg}")
        self.global_lock.acquire()
        # print(f"Lock aquired by {self.ip_address}")
        self.mongo_db.increment_danmaku_counter_of_server(self.server_id)
        if is_interpretation:
            # print(log_meg + f"from: {self.ip_address}")
            self.mongo_db.update_everything_according_to_a_new_message(message)
        self.global_lock.release()

    def watch_room(self, roomid):
        self.sio.emit("watch_room", roomid)

    def close_room(self, roomid):
        self.sio.emit("close_room", roomid)

    # def send_message(self):
    #     self.sio.emit("something", "Hello from python.")
    #     self.sio.send("hello")