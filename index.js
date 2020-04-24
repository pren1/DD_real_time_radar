var express = require('express');
const io = require('socket.io-client')
const socket = io('https://api.vtbs.moe', { autoConnect: false })

const IO_Server = require('socket.io')
// const dispatch = new Server(9003, { serveClient: false })

var app = express()
var server = app.listen(9003, function(){
  console.log("Node.js server created");
})
app.use(express.static('front-end'))
var io_= IO_Server(server, {pingTimeout: 60000});

io_.on("connection", function(socket) {
  console.log("socket.io connected " + socket.id)
  // io_.send("Hello from node.js")
  socket.on("something", function(data) {
    console.log("Received something")
    console.log(data)
  })

  socket.on("message", function(data) {
    console.log("Received message")
    console.log(data)
  })
})

// const { LiveWS } = require('bilibili-live-ws')
const wait = ms => new Promise(resolve => setTimeout(resolve, ms))

const got = require('got')
const { KeepLiveWS } = require('bilibili-live-ws')
const no = require('./env')

const rooms = new Set()

let address
let key

const opened = new Set()
const lived = new Set()
const printStatus = () => {
  // 如果不要打印连接状况就注释掉下一行
  console.log(`living/opening: ${lived.size}/${opened.size}`)
}

const refreshWssUrls = async () => {
  const { data: { host_server_list: [{ host }], token } } = await got('https://api.live.bilibili.com/room/v1/Danmu/getConf').json().catch(() => ({ data: {} }))
  if (host && token) {
    address = `wss://${host}/sub`
    key = token
  }
}

setInterval(refreshWssUrls, 1000 * 60 * 10)

//const reg = /【(.*)】|【(.*)|(.*)】/;
const reg = /(.*)【(.*)|(.*)】(.*)|^[(（"“‘]|$[)）"”’]/;

const openRoom = ({ roomid, mid }) => {
  opened.add(roomid)
  console.log(`OPEN: ${roomid}`)
  printStatus()
  const live = new KeepLiveWS(roomid, { address, key })
  live.on('live', () => {
    lived.add(roomid)
    console.log(`LIVE: ${roomid}`)
    printStatus()
  })
  live.on('error', () => {
    lived.delete(roomid)
    console.log(`ERROR: ${roomid}`)
    printStatus()
  })
  live.on('close', () => {
    lived.delete(roomid)
    console.log(`CLOSE: ${roomid}`)
    printStatus()
    live.params[1] = { key, address }
  })

  live.on('DANMU_MSG', async ({ info }) => {
    if (!info[0][9]) {
      var message = info[1]
      const mid = info[2][0]
      const uname = info[2][1]
      const timestamp = info[0][4]
      let matchres = message.match(reg);
      // Only send matches message to python client
      if (matchres && matchres.length > 0){
        // remove all 【】from message
        // message = message.replace(/[【】(（"“‘)）"”’]/g, "")
        message_length = message.replace(/[【】(（"“‘)）"”’]/g, "").length
        io_.send({ message, message_length, roomid, mid, uname, timestamp})
      }
      const listen_length = rooms.size
      console.log({ message, roomid, mid, uname, timestamp, listen_length})
    }
  })
}

const watch = ({ roomid, mid }) => {
  if (!rooms.has(roomid)) {
    rooms.add(roomid)
    console.log(`WATCH: ${roomid}`)
    openRoom({ roomid, mid })
  }
}

socket.on('info', async info => {
  info
    .filter(({ roomid }) => roomid)
    .filter(({ roomid }) => !no.includes(roomid))
    .forEach(({ roomid, mid }) => watch({ roomid, mid }))
  console.log('REFRESH')
})

const start = () => refreshWssUrls().then(socket.open()).catch(start)
start()
