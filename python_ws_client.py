import socketio
from MongoDB import MongoDB
mongo_db = MongoDB()
print("dataset established")
sio = socketio.Client()

@sio.on('connect')
def socket_connected():
    print("Connected with js server")
    print(sio.eio.sid)

@sio.on("message")
def message_received(message):
    mongo_db.insert_one(message)
    print(f"insered: {message}")

sio.connect('http://localhost:9003')