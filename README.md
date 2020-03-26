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
10. 开启后端数据传输接口：--- by pren1
    1. ✅ 更新各个表格
    2. ✅ 获取实时top rank （最多100条/s）
    3. 为各个同传man设计个人页面显示内容
        1. 直播间总弹幕占比 （环状图）✅ 
        2. 当前是否正在同传（待讨论）❎ （反正做出了了
        3. 同传弹幕折线图 （时间 & 直播间 & 弹幕数）✅ 
        4. Rank ✅
        5. 当前弹幕总数，及其他弹幕数据 ✅
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
    [{'face': 'http://i2.hdslb.com/bfs/face/b5aad263be5753ff5293f4888fd2ec071f9b1c11.jpg',
      'name': '夜行游鬼',
      'sign': '虚拟克苏鲁系键盘主播，在黑夜中游荡的鬼魂，在此祝愿你们快乐',
      'uid': 13967,
      'value': 116935},
     {'face': 'http://i1.hdslb.com/bfs/face/d205c6960ce4702957765378cb530636db0086ae.jpg',
      'name': '殿子desu',
      'sign': 'huolonglive所属，沉着稳重的同时，又有着想用喷火解决一切的一面！！ 憧憬神龙而进行烤肉修行的轻飘飘龙骑士殿子',
      'uid': 27212086,
      'value': 105000},
     {'face': 'http://i2.hdslb.com/bfs/face/c4d2962af5b43755bc8fca7993da0646c15d50cf.jpg',
      'name': '快递员小黑',
      'sign': 'huolonglive所属，喜欢收集脑袋的虚拟肝增生快D员绿皮黑',
      'uid': 28232182,
      'value': 44218},
     {'face': 'http://i2.hdslb.com/bfs/face/759058c702ec401c96ad8f21e2e9304edd4b6df3.jpg',
      'name': '精神王Pro液控煤炉专精',
      'sign': '只有懒鬼可以改变懒鬼',
      'uid': 42522,
      'value': 32799},
     {'face': 'http://i1.hdslb.com/bfs/face/d09a136270ce2109ffece1d57465026d6c61a76f.jpg',
      'name': 'Searrle',
      'sign': 'ʅ（◞‿◟）ʃ',
      'uid': 119808,
      'value': 32120}]
    ```

2. 获取同传man个人弹幕直播间分布（饼形图）,以及获取同传man去过的直播间

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
    {'pie_data': 
         [{'name': '夏色祭Official', 'value': 1.13772090730698},
         {'name': '花丸晴琉Official', 'value': 0.40185592950192084},
         {'name': '角卷绵芽Official', 'value': 0.7013105215650967},
         {'name': 'hololive', 'value': 0.5667098025458158},
         {'name': '犬山玉姬Official', 'value': 1.0088815410499794},
         {'name': '天音彼方Official', 'value': 0.15708231751645768},],
    'roomid_list': 
        [{'name': '物述有栖Official', 'roomid': 21449083},
         {'name': '皆守ひいろOfficial', 'roomid': 21425985},
         {'name': '百鬼绫目Official', 'roomid': 21130785},
         {'name': '时乃空Official', 'roomid': 8899503},
         {'name': '大空昴Official', 'roomid': 21129632},
         {'name': '郡道美玲Official', 'roomid': 21575212}]
    }
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

4. 获取目标同传man弹幕总数, 目标同传man当前排名, 查询目标同传man是否在摸鱼。若否，返回目标所在直播间

    uid: 必须 
    
    chart_type: 'danmaku_counter'
    
    roomid: 不必要
    
    返回：
    ```json5
    {'code': 3, 'message': '[danmaku counts, rank of this man, whether this man is working or not, face, sign]',
		                'data': {'danmaku_counts': db.obtain_total_danmaku_count(uid),
		                         'current_rank': db.obtain_current_rank(uid),
		                         'is_working': db.real_time_monitor_info(uid),
						       'face': face,
		                         'sign': sign
		                         }}
    ```
    
    数据格式例子：
    ```json5
    {
    'danmaku_counts': 116945,
    'current_rank': 1,
    'is_working': "摸鱼中",
    'face': ('http://i2.hdslb.com/bfs/face/b5aad263be5753ff5293f4888fd2ec071f9b1c11.jpg',
    'sign': '虚拟克苏鲁系键盘主播，在黑夜中游荡的鬼魂，在此祝愿你们快乐'
    } 
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
8. 雷达图

    uid: 必须 
    
    chart_type: 'radar'
    
    roomid: 不必须
    
    返回：
    ```json5
    {'code': 4, 'message': 'radar map',
		                'data': db.build_radar_chart(uid)
		                }
    ```
    
    数据格式例子：
    ```json5
    {'data': 
        [{
           'value': 
                 [1.0, 
                  0.8543151325235512, 
                  0.6736793096660223, 
                  0.9, 
                  0.3916657402577412, 
                  0.23606796351053716]
           }], 
           'indicator': [
                   {'name': '破坏力A', 'max': 1.0}, 
                   {'name': '持续力A', 'max': 1.0}, 
                   {'name': '精密动作性B', 'max': 1.0}, 
                   {'name': '射程距离A', 'max': 1.0}, 
                   {'name': '速度A', 'max': 1.0}, 
                   {'name': '成长性D', 'max': 1.0}
       ]
    }
    ```
9. 错误代码
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