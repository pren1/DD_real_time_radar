import socketio

sio = socketio.Client()

@sio.on('connect')
def socket_connected():
    print("Connected with js server")
    print(sio.eio.sid)

@sio.on("message")
def message_received(message):
    print(message)

sio.connect('http://localhost:9003')