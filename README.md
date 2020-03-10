# DD_real_time_radar
Detect the danmaku data in realtime, then track the target Simultaneous interpretation man

本项目继承自：[bilibili-vtuber-live-danmaku-relay](https://github.com/dd-center/bilibili-vtuber-live-danmaku-relay)

1. ✅ 监听所有vtuber直播间弹幕 已完成 --- by Kinori
2. ✅ Python端构建数据库，并将弹幕信息插入 已完成 --- by pren1
3. ✅ 弹幕信息优化：仅需要字数信息 已完成 --- by pren1
4. ✅ 弹幕数实时排名/最后弹幕发言追踪 已完成 --- by pren1
5. ✅ 整合/后端命令行版本 建立一个demo 已完成 --- by pren1
6. ✅ 写文档 已完成 --- by pren1
7. ✅ 前端准备中 py通过ws向js传消息/加入EON以实时显示数据 施工中 --- by pren1
8. ✅ 将2020/2/20前的弹幕数据库添加到MongoDB 已完成 --- by scPointer
    1. ✅添加索引，修改attributes格式
    2. ✅增加辅助表：同传信息/直播间信息/排名
9. ✅修改数据库设计
    1. ✅各个同传man/直播间都有自己的表格
    2. ✅优化数据库名/表名等常量的存储方法
    3. ✅其他提高效率/可读性的小优化  详见log目录下20200307.txt
10. 开启后端数据传输接口：
    1. ✅ 更新各个表格
    2. ✅ 获取实时top rank （最多100条/s）
    3. 为各个同传man设计个人页面显示内容
        1. 直播间总弹幕占比 （环状图）✅ 
        2. 当前是否正在同传（待讨论）❎ （摸了
        3. 同传弹幕折线图 （时间 & 直播间 & 弹幕数）✅ 
        4. Rank ❎ （摸了
        5. 当前弹幕总数，及其他弹幕数据 ❎ （摸了
    4. 月榜 周榜 ❎ （摸了
    5. 直播间同传man折线图 ❎ （摸了
                                                                                             
☁️ Introduction
目前实现的功能有：实时创建同传排行榜（考虑过去的数据）

⚡️ Quick start

1. 下载repo
```
git clone https://github.com/pren1/DD_real_time_radar.git
```
2. 安装mongodb
3. 开启mongodb
```
mongod
```
4. 到项目根目录下，安装相关包
```
npm install
npm install --save express
```
5. 运行js服务器
```
node index.js
```
6. 运行python端程序
```
python3 python_ws_client.py
```
7. 运行前端程序
[这里](https://github.com/dd-center/DD_real_time_radar_frontend)

8. 运行后端数据库接口
```
python3 Interface.py
```

💼 Interface

接收POST，例如：
```
`http://localhost:5000/processjson?uid=13967&chart_type=message&roomid=4664126`
```

1. 获取同传man排行榜信息

    uid: 必须 
    
    chart_type: 'ladder'
    
    roomid: 不必要
    
    返回：
    ```json5
    {'code': 0,  
      'message': 
      'return initialize rank_list', 
      'data': db.find_total_rank()
    ,}
    ```
    数据格式例子：
    ```json5
    [{'name': '夜行游鬼', 'uid': 13967, 'value': 116935},
     {'name': '殿子desu', 'uid': 27212086, 'value': 105000},
     {'name': '快递员小黑', 'uid': 28232182, 'value': 44218},
     {'name': '精神王Pro液控煤炉专精', 'uid': 42522, 'value': 32799},
     {'name': 'Searrle', 'uid': 119808, 'value': 32120},
     {'name': '涼風青葉頑張るぞい', 'uid': 37718180, 'value': 29603},]
    ```

2. 获取同传man个人弹幕直播间分布（饼形图）

    uid: 必须 
    
    chart_type: 'pie'
    
    roomid: 不必要
    
    返回：
    ```json5
    {
      'code': 1, 
      'message': 'pie data',
      'data': db.build_message_room_persentage(uid)
    ,}
    ```
    
    数据格式例子：
    
    ```json5
    [{'name': '夏色祭Official', 'value': 1.13772090730698},
     {'name': '花丸晴琉Official', 'value': 0.40185592950192084},
     {'name': '角卷绵芽Official', 'value': 0.7013105215650967},
     {'name': 'hololive', 'value': 0.5667098025458158},
     {'name': '犬山玉姬Official', 'value': 1.0088815410499794},
     {'name': '天音彼方Official', 'value': 0.15708231751645768},]
    ```

3. 获取同传man过往弹幕数据（柱状图）

    uid: 必须 
    
    chart_type: 'bar'
    
    roomid: 不必要
    
    返回：
    ```json5
    {'code': 2, 
    'message': 'bar whole data', 
    'data': db.build_man_chart(uid)}
    ```
    
    数据格式例子：
    
    ```json5
     '2020-02': {'data': [{'data': [1119,
                                    '',
                                    '',
                                    2691,
                                    '',
                                    '',
                                    '',
                                    1234,
                                    1910,
                                    '',
                                    '',
                                    '',
                                    '',
                                    1754,
                                    '',
                                    ''],
                           'name': '花丸晴琉Official',
                           'stack': '总量',
                           'type': 'bar'},
                          {'data': ['',
                                    966,
                                    879,
                                    685,
                                    653,
                                    829,
                                    '',
                                    '',
                                    '',
                                    1135,
                                    '',
                                    426,
                                    582,
                                    '',
                                    '',
                                    ''],
                           'name': '夏色祭Official',
                           'stack': '总量',
                           'type': 'bar'},
                          ],
                 'x_axis': ['2020-02-01',
                            '2020-02-02',
                            '2020-02-03',
                            '2020-02-05',
                            '2020-02-06',
                            '2020-02-07',
                            '2020-02-08',
                            '2020-02-09',
                            '2020-02-10',
                            '2020-02-11',
                            '2020-02-12',
                            '2020-02-13',
                            '2020-02-14',
                            '2020-02-15',
                            '2020-02-16',
                            '2020-02-18']}}
    ```

4. 获取目标同传man弹幕总数

    uid: 必须 
    
    chart_type: 'danmaku_counter'
    
    roomid: 不必要
    
    返回：
    ```json5
    {'code': 3, 
    'message': 'danmaku counts', 
    'data': db.obtain_total_danmaku_count(uid)}
    ```
    
    数据格式例子：
    ```json5
    116945
    ```

5. 获取目标同传man当前排名

    uid: 必须 
    
    chart_type: 'rank'
    
    roomid: 不必要
    
    返回：
    ```json5
    {'code': 4, 
    'message': 'rank of this man', 
    'data': db.obtain_current_rank(uid)}
    ```
    
    数据格式例子：
    ```json5
    1
    ```

5. 查询目标同传man是否在摸鱼。若否，返回目标所在直播间

    uid: 必须 
    
    chart_type: 'isworking'
    
    roomid: 不必要
    
    返回：
    ```json5
    {'code':5, 
    'message': 'whether this man is working or not', 
    'data': db.real_time_monitor_info(uid)}
    ```
    
    数据格式例子：
    ```json5
    "摸鱼中"
    ```

6. 查询目标同传man在目标直播间发过的所有弹幕，按时间排序

    uid: 必须 
    
    chart_type: 'message'
    
    roomid: 必须
    
    返回：
    ```json5
    {'code': 6, 
    'message': 'return message of a man in a room', 
    'data': db.get_man_messages(mid=uid, roomid=roomid)}
    ```
    
    数据格式例子：
    ```json5
    [{'message': '【萝卜：不会让你睡的哦】', 'roomid': 4664126, 'timestamp': 1580389478054},
     {'message': '【超级会想戴上的啊】', 'roomid': 4664126, 'timestamp': 0},
     {'message': '【喜欢~喜欢戴着的这个】', 'roomid': 4664126, 'timestamp': 0},
     {'message': '【没有眼镜活不下去】', 'roomid': 4664126, 'timestamp': 0},
     {'message': '【多少钱是多少钱？】', 'roomid': 4664126, 'timestamp': 0},]
    ```

7.  获取直播间过往弹幕数据（柱状图）

    uid: 必须 
    
    chart_type: 'room_info'
    
    roomid: 必须
    
    返回：
    ```json5
    {'code': 7, 
    'message': "return room message", 
    'data': db.build_room_chart(roomid=roomid)}
    ```
    
    数据格式例子：
    ```json5
    '2020-02': {'data': [{'data': ['', '', '', '', '', '', '', '', '', '', '', 57],
                           'name': 'Agine',
                           'stack': '总量',
                           'type': 'bar'},
                          {'data': ['',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    173],
                           'name': '汐崎柒',
                           'stack': '总量',
                           'type': 'bar'},
                          {'data': ['', 11, 21, 17, 14, 20, 17, 40, 51, 21, 37, 36],
                           'name': '烛龙神',
                           'stack': '总量',
                           'type': 'bar'},
                          {'data': [233,
                                    '',
                                    '',
                                    233,
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    '',
                                    ''],
                           'name': 'Mr_Vergil',
                           'stack': '总量',
                           'type': 'bar'}],
                 'x_axis': ['2020-02-01',
                            '2020-02-02',
                            '2020-02-04',
                            '2020-02-07',
                            '2020-02-08',
                            '2020-02-09',
                            '2020-02-10',
                            '2020-02-13',
                            '2020-02-14',
                            '2020-02-15',
                            '2020-02-16',
                            '2020-02-20']}}
    ```
8. 错误代码
    > chart_type 错误 
    ```json5
    {'code': -1, 'message': "nothing returned", 'data': []}
    ```
    > UID 未提供
    ```json5
    {'code': -2, 'message': "Undefined uid", 'data': []}
    ```
    > chart_type 未提供
    ```json5
    {'code': -3, 'message': "Undefined chart type", 'data': []}
    ```
    > roomid 未提供
    ```json5
    {'code': -4, 'message': 'no roomid provided', 'data': []}
    ```