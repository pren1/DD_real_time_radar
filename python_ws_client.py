import socketio

sio = socketio.Client()


@sio.on('connect')
def socket_connected():
    print("Connected")
    print(sio.eio.sid)


@sio.on("message")
def message_received(message):
    # print(sid)
    print(message)

sio.connect('http://localhost:9003')

# sio.emit("something", "Hello from python.")
# sio.send("hello")

# sio.wait()