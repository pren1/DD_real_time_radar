var express = require('express');
const io = require('socket.io-client')
const socket = io('https://api.vtbs.moe', { path: '/vds' });

const IO_Server = require('socket.io')

var app = express()
var server = app.listen(9003, function(){
  console.log("Node.js server created");
})
app.use(express.static('front-end'))
var io_= IO_Server(server, {pingTimeout: 60000});

io_.on("connection", function(socket) {
  console.log("socket.io connected " + socket.id)
})

const reg = /(.*)【(.*)|(.*)】(.*)|^[(（"“‘]|$[)）"”’]/;
socket.emit('join', 'all')
socket.on('danmaku', async danmaku => {
  var message = danmaku['message']
  const mid = danmaku['mid']
  const uname = "username"
  const timestamp = new Date().getTime()
  const roomid = danmaku['roomid']
  let matchres = message.match(reg);
  // Only send matches message to python client
  if (matchres && matchres.length > 0){
    if ([21752686, 8982686].includes(roomid)){
      console.log("room has been banned!")
    }
    else{
      message_length = message.replace(/[【】(（"“‘)）"”’]/g, "").length
      io_.send({ message, message_length, roomid, mid, uname, timestamp})
    }
  }
  console.log({ message, roomid, mid, uname, timestamp})
})
