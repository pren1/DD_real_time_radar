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
8. ✅ 将整体数据库添加到mongodb，添加索引，转化格式 已完成 --- by scPointer
9. 开启后端数据传输接口：
    1. ✅ 更新各个表格
    2. ✅ 获取实时top rank （最多100条/s）
    3. 为各个同传man设计个人页面显示内容
        1. 直播间总弹幕占比 （环状图）
        2. 当前是否正在同传（待讨论）
        3. 同传弹幕折线图 （时间 & 直播间 & 弹幕数）
        4. Rank
        5. 当前弹幕总数，及其他弹幕数据
        6. 
    4. 月榜 周榜
    5. 直播间同传man折线图
                                                                                             




☁️ Introduction
目前实现的功能有：实时创建同传排行榜（未考虑过去的数据）

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


