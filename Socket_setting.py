import socketio
import time

class Socket_setting(object):
    def __init__(self, MongoDB, NB_classifier, global_lock, ip_address, server_id, port=9003):
        'Connect to dataset, connect to js server via ws'
        self.mongo_db = MongoDB
        self.NB_classifier = NB_classifier
        self.global_lock = global_lock
        self.ip_address = ip_address
        self.server_id = server_id
        self.port = port
        self.client_room_list = [] # The one that saved the rooms in target server
        self.ping_time = -1
        self.pong_time = -1
        self.sio = socketio.Client()
        self.sio.on('connect', self.socket_connected)
        self.sio.on('message', self.message_received)
        self.sio.on('Client_room_list', self.fetch_client_rooms)
        self.sio.on('disconnect', self.handle_disconnection)
        self.sio.on('Pong', self.pong_received)
        self.sio.connect(f'http://{self.ip_address}:{self.port}')

    def connection_detect_suit(self):
        '1. ping'
        self.send_Ping()
        # '2. wait 5 seconds'
        time.sleep(5)
        '3. check results'
        result = self.check_connection()
        if not result:
            # print(f"restarting: {self.ip_address}")
            self.socket_reconnect()
        else:
            pass
            # print(f"{self.ip_address} is connected")
        return result

    def check_connection(self):
        print(f"time distance: {self.pong_time - self.ping_time}")
        if self.pong_time == -1 or self.ping_time == -1:
            print("Something wrong here")
            return False

        if self.pong_time < self.ping_time:
            return False
        else:
            return True

    def pong_received(self, client_time):
        'receive time from client'
        # print(f"received: {pong_time}")
        self.pong_time = int(round(time.time() * 1000))

    def send_Ping(self):
        'Run this ping first, then wait at pong_part...'
        self.ping_time = int(round(time.time() * 1000))
        self.sio.emit("ping", self.ping_time)

    def fetch_client_rooms(self, room_list):
        # print(f"Client room list: {room_list} from {self.ip_address}")
        self.client_room_list = room_list

    def socket_reconnect(self):
        'litterally, reconnect the current socket'
        self.sio.eio.disconnect()
        self.sio.connect(f'http://{self.ip_address}:{self.port}')

    def handle_disconnection(self):
        print("Disconnected, get connected again...")
        # self.sio.connect(f'http://{self.ip_address}:{self.port}')

    def socket_connected(self):
        print("Connected with js server")
        print(self.sio.eio.sid)

    def message_received(self, message):
        # print(f"server id: {self.sio.eio.sid}, message id: {message['global_sid']}")
        if self.sio.eio.sid == message['global_sid']:
            'on received danmakus'
            is_interpretation, log_meg = self.NB_classifier.decide_class(message['message'])
            # print(f"{log_meg}")
            self.global_lock.acquire()
            # print(f"Lock aquired by {self.ip_address}")
            self.mongo_db.increment_danmaku_counter_of_server(self.server_id)
            print(log_meg + f"from: {self.ip_address}")
            if is_interpretation:
                self.mongo_db.update_everything_according_to_a_new_message(message)
            self.global_lock.release()
        else:
            print("Duplicate message, ignored :P")

    def watch_room(self, roomid):
        self.sio.emit("watch_room", roomid)

    def close_room(self, roomid):
        self.sio.emit("close_room", roomid)

    # def send_message(self):
    #     self.sio.emit("something", "Hello from python.")
    #     self.sio.send("hello")