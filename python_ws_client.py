import socketio
from MongoDB import MongoDB
class python_ws_client(object):
    def __init__(self):
        'Connect to dataset, connect to js server via ws'
        self.mongo_db = MongoDB()
        self.sio = socketio.Client()
        self.sio.on('connect', self.socket_connected)
        self.sio.on('message', self.message_received)
        self.sio.connect('http://localhost:9003')

    def socket_connected(self):
        print("Connected with js server")
        print(self.sio.eio.sid)

    def message_received(self, message):
        self.mongo_db.insert_one(message)
        print(f"insered: {message}")

    def get_database(self):
        return self.mongo_db

if __name__ == '__main__':
    ws_listenser = python_ws_client()