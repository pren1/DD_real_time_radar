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

<p>
    <img src="image/Img.png"/>
</p>

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



