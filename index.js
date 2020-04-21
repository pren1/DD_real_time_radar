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

const openRoom = ({ roomid, mid }) => new Promise(resolve => {
  console.log(`OPEN: ${roomid}`)
  // const live = new LiveWS(roomid)
  const live = new KeepLiveWS(roomid, { address, key })
  const autorestart = setTimeout(() => {
    console.log(`AUTORESTART: ${roomid}`)
    live.close()
  }, 1000 * 60 * 60 * 18)
  let timeout = setTimeout(() => {
    console.log(`TIMEOUT: ${roomid}`)
    live.close()
  }, 1000 * 45)
  live.once('live', () => console.log(`LIVE: ${roomid}`))
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
      console.log({ message, roomid, mid, uname, timestamp})
    }
  })

  live.on('heartbeat', () => {
    clearTimeout(timeout)
    timeout = setTimeout(() => {
      console.log(`TIMEOUT: ${roomid}`)
      live.close()
    }, 1000 * 45)
  })
  live.on('close', () => {
    clearTimeout(autorestart)
    clearTimeout(timeout)
    live.params[1] = { key, address }
    // resolve({ roomid })
  })
  live.on('error', () => {
    console.log(`ERROR: ${roomid}`)
  })
})

const watch = async ({ roomid, mid }) => {
  if (!rooms.has(roomid)) {
    rooms.add(roomid)
    console.log(`WATCH: ${roomid}`)
    while (true) {
      await openRoom({ roomid, mid })
      console.log(`CLOSE: ${roomid}`)
      await wait(50)
      console.log(`REOPEN: ${roomid}`)
    }
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