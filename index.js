/* eslint-disable semi */
/* eslint-disable @typescript-eslint/camelcase */
const express = require('express');
const io = require('socket.io-client')
const socket = io('https://api.vtbs.moe')
const relay = io('https://api.vtbs.moe', { path: '/vds' })

const IO_Server = require('socket.io')
// const dispatch = new Server(9003, { serveClient: false })

relay.on('connect', () => relay.emit('join', 'all'))
relay.on('connect', () => console.log('Relay Connected'))

const app = express()
const server = app.listen(9003, function() {
  console.log('Node.js server created');
})
app.use(express.static('front-end'))
const io_ = IO_Server(server, { pingTimeout: 60000 });

io_.on('connection', function(socket) {
  console.log('socket.io connected ' + socket.id)
  // io_.send("Hello from node.js")
  socket.on('something', function(data) {
    console.log('Received something')
    console.log(data)
  })

  socket.on('message', function(data) {
    console.log('Received message')
    console.log(data)
  })
})

// const reg = /【(.*)】|【(.*)|(.*)】/;
const reg = /(.*)【(.*)|(.*)】(.*)|^[(（"“‘]|$[)）"”’]/;

relay.on('danmaku', ({ message, roomid, mid, uname, timestamp }) => {
  const matchres = message.match(reg);
  // Only send matches message to python client
  if (matchres && matchres.length > 0) {
    if ([21752686, 8982686].includes(roomid)) {
      console.log('room has been banned!')
    } else {
      const message_length = message.replace(/[【】(（"“‘)）"”’]/g, '').length
      io_.send({ message, message_length, roomid, mid, uname, timestamp })
    }
  }
  console.log({ message, roomid, mid, uname, timestamp })
})
