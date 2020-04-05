#from MongoDB import MongoDB
from constants import *
import datetime
import time

get_date = lambda ts: datetime.datetime.fromtimestamp(ts/1000).strftime("%Y-%m-%d")
get_days = lambda d1,d2: (datetime.datetime.strptime(d2, "%Y-%m-%d") - \
	datetime.datetime.strptime(d1, "%Y-%m-%d")).days

'最长高强度同传时间'

def get_room_name(db, roomid):
	name = db.roomid_info.find_one({'_id':roomid})
	if name == None:
		return ""
	else:
		return name['room_nick_name']

def build_max_length(db, mid):
	get_room_name = lambda roomid: db.roomid_info.find_one({'_id':roomid})['room_nick_name']
	time_list = (
		db.mydb[MID_TABLE_OF + str(mid)].aggregate([
			{"$sort":{"timestamp":1}},
			{"$project":
				{
					"_id" : 0,
					"roomid" : 1,
					"timestamp" : 1
				}
			}
		]))

	threshold = 1000 * 60 * 5 # 5 minutes
	last_time, now_time, start_time = 0, 0, 0
	max_time, max_start_time = 0, 0
	now_room, max_room = 0, 0
	for d in time_list:
		last_time = now_time
		now_time = d['timestamp']
		if now_time == 0:
			continue
		if now_room != d['roomid'] or now_time - last_time > threshold:
			if last_time - start_time > max_time:
				max_time = last_time - start_time
				max_start_time = start_time
				max_room = now_room
			now_room = d['roomid']
			start_time = now_time
	return max_time/1000/3600, get_room_name(max_room), get_date(max_start_time)
'平均每分钟字数'
def build_speed(db, mid):
	time_list = (
		db.mydb[MID_TABLE_OF + str(mid)].aggregate([
			{"$sort":{"timestamp":1}},
			{"$project":
				{
					"_id" : 0,
					"message_length" : 1,
					"timestamp" : 1
				}
			}
		]))

	threshold = 1000 * 20 # 20 seconds
	last_time, now_time, = 0, 0
	total_time, total_length = 0, 0
	for d in time_list:
		last_time = now_time
		now_time = d['timestamp']
		if now_time == 0:
			continue
		if now_time - last_time < threshold:
			total_time += now_time - last_time
			total_length += d['message_length']
	speed = 0
	if total_time > 0:
		speed = total_length / (total_time/1000/60)
	return round(speed, 2) # by minutes
'DD范围指数'
def DD_range(db, mid):
	rooms = list(
		db.mydb[MID_TABLE_OF + str(mid)].aggregate([
			{"$group":
				{"_id":"$roomid",
				"count":{"$sum": 1}}
			}
		]))
	dd_score = 0
	for d in rooms:
		if d['count'] < 100:
			dd_score += (d['count']/100) ** 3
		else:
			dd_score += 1
	return dd_score
'反摸鱼指数'
def anti_moyu(db, mid):
	danmaku_period = list(db.mydb[MID_TABLE_OF + f"{mid}"].aggregate([
		{"$project": {
			"_id": {
				"$toDate": {
					"$toLong": "$timestamp"
				}
			}
		}},
		{"$group": {
			"_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$_id"}},
			"count": {"$sum": 1},
		}},
		{"$sort": {"_id": 1}}
		]))
	#for i in danmaku_period:
	#	print(i['_id'])
	valid = [day for day in danmaku_period if day['_id']!='1970-01-01' and day['count']>50]
	if len(valid) < 2:
		return 0
	else:
		return (len(valid) / get_days(valid[0]['_id'],valid[-1]['_id']))** .3

"""
if __name__ == '__main__':
	db = MongoDB()
	
	print(build_max_length(db, 13967))
	print(build_max_length(db, 27212086))
	print(build_max_length(db, 28232182))
	print(build_max_length(db, 2907459))

	print(DD_range(db, 13967))
	print(DD_range(db, 27212086))
	print(DD_range(db, 28232182))
	print(DD_range(db, 2907459))

	print(build_speed(db, 13967))
	print(build_speed(db, 27212086))
	print(build_speed(db, 28232182))
	print(build_speed(db, 2907459))

	print(anti_moyu(db, 13967))
	print(anti_moyu(db, 27212086))
	print(anti_moyu(db, 28232182))
	print(anti_moyu(db, 2907459))
"""
