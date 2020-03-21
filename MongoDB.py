#!/usr/bin/python3
import pymongo
import pprint
import pdb
from util import *
import datetime
import random
from front_end_data_format import *
from tqdm import tqdm
from constants import *
import time
from datetime import datetime
import numpy as np
from scipy.stats import entropy

class MongoDB(object):
	def __init__(self):
		'To use this service, you need to install MongoDB first'
		self.myclient = pymongo.MongoClient(MONGODB_LOCAL)
		self.mydb = self.myclient[DATABASE_NAME]
		# Deal with different charts
		self.mid_info = self.mydb[MID_INFO]
		self.roomid_info = self.mydb[ROOMID_INFO]
		self.ranking = self.mydb[RANKING]
		self.maindb = self.mydb[MAINDB]
		self.sorted_list = [] # Initialize the ranked top list
		self.update_the_original_rank_list()

	def get_man_messages(self, mid, roomid):
		'return all the messages of this man'
		res = list(self.mydb[MID_TABLE_OF + str(mid)].find({'roomid':roomid}).sort("timestamp", -1))
		fin_res = []
		for single in res:
			fin_res.append({
				'roomid': roomid,
				'message': single['message'],
				'timestamp': single['timestamp']
			})
		pprint.pprint(fin_res)
		return fin_res

	def real_time_monitor_info(self, mid):
		'figure out currently, where is this man working'
		'Find the chart of this man'
		res = list(self.mydb[MID_TABLE_OF + str(mid)].find().sort("timestamp",-1).limit(1))
		current_time = int(time.time()*1000.0)
		past_danmaku_time = res[0]['timestamp']
		past_room = list(self.roomid_info.find({'_id':res[0]['roomid']}))[0]['room_nick_name'],
		# If appear within 5 mins
		diff_thres = WORKING_THRESHOLD * 60000.0
		time_diff = abs(current_time - past_danmaku_time)
		if time_diff < diff_thres:
			'on live'
			return f"{past_room}"
		else:
			'nope'
			return f"摸鱼中"

	def get_face_and_sign(self, mid):
		'Notice that this mid must be within the rank list!'
		data = list(self.ranking.find({'_id': mid}))[0]
		assert len(data) != 0, "Fatal ERROR, this man should be contained in the ranking list!"
		return data['face'], data['sign']

	def obtain_current_rank(self, mid):
		rank_list = list(self.ranking.find())
		rank = 1
		for single_one in rank_list:
			if single_one['_id'] == mid:
				return rank
			rank += 1
		'This man does not exist in the rank list!'
		return -1

	def obtain_total_danmaku_count(self, mid):
		'How many danmaku intotal did this person sent'
		return list(self.ranking.find({'_id':mid}))[0]['danmaku_count']  + random.randint(0, 1000)

	def update_the_original_rank_list(self):
		'Up to date!'
		print("Updating original rank list...")
		self.ranking.drop()
		print("deleted previous ranking list")
		'get the list from dataset for one time. Later, we will update it when necessary...'
		rank_list_curosr = self.mid_info.find({'$where':"this.danmaku_count >= this.danmaku_threshord"}).sort("danmaku_count", -1)
		for single_rank in tqdm(rank_list_curosr):
			face, sign = get_sign_and_face_of_mid(single_rank['_id'])
			single_rank['face'] = face
			single_rank['sign'] = sign
			self.ranking.find_one_and_update({"_id": single_rank['_id']},
			                               {'$set': single_rank},
			                               upsert=True)
			# pdb.set_trace()
			# self.ranking.update({'_id': single_rank['_id']}, {'$set': single_rank})
		print("Ranking list Updated")
		pprint.pprint(list(self.ranking.find()))
		# pdb.set_trace()

	def find_total_rank(self):
		'Up to date!'
		# pprint.pprint(self.ranking)
		res = []
		for data in self.ranking.find():
			find_target_name = data['man_nick_name']
			if len(find_target_name) > 0:
				res.append({
					'name': find_target_name,
					'value': data['danmaku_count'],
					'uid': data['_id'],
					'face': data['face'],
					'sign': data['sign']
				})
		pprint.pprint(res[:5])
		return res

	# def find_rank_within_past_period(self, mydict, past_date = 90):
	# 	test = mydict['timestamp'] - 86400000*past_date
	# 	t1 = get_real_time(test)
	# 	res = list(self.maindb.aggregate([
	# 		{'$match': {'timestamp': {'$gt': test}, 'man_nick_name.1': {'$exists': True}}},
	# 		{'$group':
	# 			{
	# 				'_id': "$mid",
	# 				'danmaku_count': {'$sum': 1},
	# 				'danmaku_len_count': {'$sum': "$message_length"},
	# 				'avg_danmaku_len': {'$avg': "$message_length"}
	# 			}
	# 		},
	# 		{'$sort':
	# 			{
	# 				"danmaku_count": -1,
	# 				'_id': 1
	# 			}
	# 		}
	# 	]))
	# 	pprint.pprint(res)
	# 	pdb.set_trace()

	def build_room_chart(self, roomid):
		'Up to date!'
		res = list(self.mydb[ROOM_TABLE_OF + f"{roomid}"].aggregate([
			{"$project": {
				"_id": {
					"$toDate": {
						"$toLong": "$timestamp"
					}
				},
				"mid": "$mid"
			}},
			{"$group": {
				"_id": {"mid": "$mid", "date_val": {"$dateToString": {"format": "%Y-%m-%d", "date": "$_id"}}},
				"count": {"$sum": 1},
			}},
			{'$match': {'count': {'$gt': ROOM_DANMAKU_THRESHOLD}}},
			{"$sort": {"_id.date_val": -1}}
		]))
		'First, we put data into different year-month~'
		year_month_slot = build_year_month_slot_dict(res)
		pprint.pprint(year_month_slot)
		'Then, for each year month slot, we handle the data'
		final_res = {}
		for single_slot in year_month_slot:
			'Build a list for each slot'
			'Build a list for each slot'
			current_level_man_info, date_x_axis = extract_suitable_roomid_timeline(year_month_slot[single_slot])
			final_res[single_slot] = {'data': [], 'x_axis': date_x_axis}
			'Then, we could iterate the date & roomid here'
			for single_man_slot in current_level_man_info:
				month_level_feed_in_res = \
					build_front_end_data_format(
						name=list(self.mid_info.find({'_id': single_man_slot}))[0]['man_nick_name'],
						data=month_level_format_change(current_level_man_info[single_man_slot], date_x_axis)
					)
				final_res[single_slot]['data'].append(month_level_feed_in_res)
		pprint.pprint(final_res)
		# pdb.set_trace()
		return final_res

	def build_man_chart(self, mid):
		'Up to date!'
		res = list(self.mydb[MID_TABLE_OF + f"{mid}"].aggregate([
			{"$project": {
				"_id": {
					"$toDate": {
						"$toLong": "$timestamp"
					}
				},
				"roomid": "$roomid"
			}},
			{"$group": {
				"_id": {"roomid": "$roomid", "date_val": {"$dateToString": {"format": "%Y-%m-%d", "date": "$_id"}}},
				"count": {"$sum": 1},
			}},
			{"$sort": {"_id.date_val": -1}}
		]))
		'First, we put data into different year-month~'
		year_month_slot = build_year_month_slot_dict(res)
		'Then, for each year month slot, we handle the data'
		final_res = {}
		for single_slot in year_month_slot:
			'Build a list for each slot'
			current_level_room_info, date_x_axis = extract_suitable_timeline(year_month_slot[single_slot])
			final_res[single_slot] = {'data': [], 'x_axis': date_x_axis}
			# pprint.pprint(current_level_res)
			# pprint.pprint(date_x_axis)
			'Then, we could iterate the date & roomid here'
			for single_room_slot in current_level_room_info:
				month_level_feed_in_res = \
					build_front_end_data_format(
					name=list(self.roomid_info.find({'_id':single_room_slot}))[0]['room_nick_name'],
					data=month_level_format_change(current_level_room_info[single_room_slot], date_x_axis)
				)
				final_res[single_slot]['data'].append(month_level_feed_in_res)
		pprint.pprint(final_res)
		return final_res

	def build_message_room_persentage(self, mid):
		'Up to date!'
		'return room persentage & room name'
		room_persentage = list(
			self.mydb[MID_TABLE_OF + f"{mid}"].aggregate([
				{'$group':
					 {'_id': "",
					  "total": {'$sum':1},
					  "room set": {'$push': '$roomid'}
					  }
				 },
				{'$unwind': "$room set"},
				{'$group':
					 {'_id': {"roomid": "$room set", "total": "$total"},
					  'room_danmaku_count': {'$sum': 1}
					  }
				 },
				{"$addFields": {
					"danmaku_room_persentage": {"$divide": ["$room_danmaku_count", '$_id.total']},
				}},
				{"$sort": {"danmaku_room_persentage": -1}},
				{"$project": { "_id.total": 0, "room_danmaku_count": 0}}
			]))
		front_end_res = []
		room_id_list = []
		for single in room_persentage:
			'Notice you add random val here'
			value = single['danmaku_room_persentage'] + random.uniform(0, 1)
			name = list(self.roomid_info.find({'_id':single['_id']['roomid']}))[0]['room_nick_name']
			front_end_res.append({'value': value, 'name': name})
			roomid = single['_id']['roomid']
			room_id_list.append({'roomid': roomid, 'name': name})
		# pprint.pprint(front_end_res)
		pprint.pprint(room_id_list)
		return {'pie_data': front_end_res, 'roomid_list': room_id_list}

	def update_everything_according_to_a_new_message(self, mydict):
		'Update the following four charts here'
		'Up to date!'
		self.update_maindb(mydict)
		self.update_mid_info_and_table_and_ranking(mydict)
		self.update_roomid_info_and_table(mydict)

	def update_maindb(self, mydict):
		'Just insert to the original chart'
		'Up to date!'
		insert_target = {'message_length': mydict['message_length'],
		                              'roomid': mydict['roomid'],
		                              'mid': mydict['mid'],
		                              'timestamp': mydict['timestamp'],
									  'message': mydict['message']
		                              }
		self.maindb.insert_one(insert_target)
		# res = list(self.maindb.find({'mid': mydict['mid']}))[-1]
		# print(res)

	def update_mid_info_and_table_and_ranking(self, mydict):
		'Up to date!'
		'update mid if the upcoming nickname does not exist in the current mid_chart'
		mid_val = int(mydict['mid'])
		# print('your mid is ',mid_val)
		row = self.mid_info.find_one({'_id':mid_val})
		if row is None:
			'Cannot find this mid, insert this man into the track chart'
			'A man who has sent over DANMAKU_THRESHORD interpretation danmakus can have its own table'
			self.mid_info.insert_one({'_id': mid_val,
									 'danmaku_count': 0,
									 'danmaku_len_count': 0,
									 'danmaku_threshord': DANMAKU_THRESHORD, #UNFINISHED, we need more info of this man, please get more info from api of bilibili
									 'man_nick_name': ''
									 })
		info = self.mid_info.find_one_and_update({'_id': mid_val}, {'$inc':
													{'danmaku_count':1,
													'danmaku_len_count':mydict['message_length']}
												}, new = True)
		count, threshold = info['danmaku_count'], info['danmaku_threshord']
		if count == threshold:
			nickname = get_nickname_of_mid(mid_val)
			'Assign this man a name'
			self.mid_info.update({'_id': mid_val},{'$set':{'man_nick_name': nickname}})
			print(f"get new initerpretation man: {nickname}, YEAH!")
			self.create_table_for_man(mid_val)

			'add face & sign information here'
			face, sign = get_sign_and_face_of_mid(info['_id'])
			info['face'] = face
			info['sign'] = sign
			'Besides, we also add this man to the ladder~'
			assert len(list(self.ranking.find({'_id': info['_id']}))) == 0, "Fatal ERROR, this man should not be contained in the ranking list!"
			'Make sure the ranking list is up to date. That is, it contains all the candidates'
			self.ranking.insert_one(info)
		elif count > threshold:
			self.update_mid_table(mydict)
			find_res = list(self.ranking.find({'_id': info['_id']}))
			assert len(find_res) == 1, "Fatal ERROR, this man should be contained in the ranking list!"
			'Also, we update the data within the ranking charts'
			myquery = find_res[0]
			newvalues = {"$set": info}
			self.ranking.update_one(myquery, newvalues)
			print(f"Updated ranklist: from {myquery} to {info}")
		else:
			print("Threshold not meet, keep doing your work!")

	def create_table_for_man(self, mid_val):
		'Up to date!'
		history_danmaku = list(self.maindb.find({'mid': mid_val},
													{'_id': 0,
													'message_length': 1,
													'roomid': 1,
													'timestamp': 1,
													'message': 1
													}))
		new_table = self.mydb[MID_TABLE_OF+str(mid_val)]
		new_table.insert_many(history_danmaku)
		new_table.create_index([('roomid', 1)])
		new_table.create_index([('timestamp',-1)])

	def update_mid_table(self, mydict):
		'Up to date!'
		'Insert to the corresponding table'
		self.mydb[MID_TABLE_OF+str(mydict['mid'])].insert_one({'message_length': mydict['message_length'],
														'roomid': mydict['roomid'],
														'timestamp': mydict['timestamp'],
														'message': mydict['message']
														})

	def update_roomid_info_and_table(self, mydict):
		'Up to date!'
		'I think this func will not be used before simon updates his roomid list'
		room_id = mydict['roomid']
		row = self.roomid_info.find_one({'_id':room_id})
		if row is None:
			room_nick_name = show_me_your_room_id(room_id=room_id)
			self.roomid_info.insert_one({'_id': room_id,
										'room_nick_name': room_nick_name #UNFINISHED, we need more info of this room
										})								 #please get more info from api of bilibili

			self.update_room_table(mydict)
			self.mydb[ROOM_TABLE_OF+str(room_id)].create_index([('mid',1)])
			self.mydb[ROOM_TABLE_OF+str(room_id)].create_index([('timestamp',-1)])
			print(f"{room_nick_name} has been inserted to the room name list")
		else:
			self.update_room_table(mydict)


	def update_room_table(self, mydict):
		'Up to date!'
		self.mydb[ROOM_TABLE_OF+str(mydict['roomid'])].insert_one({'message_length': mydict['message_length'],
														'mid': mydict['mid'],
														'timestamp': mydict['timestamp'],
														'message': mydict['message']
														})

	def update_nickname_in_roomid_info(self, roomid = 0):
		'Never used'
		if roomid != 0:
			self.roomid_info.update({'_id': roomid},
									{'$set':{'room_nick_name': show_me_your_room_id(roomid)}})
			return
		'if roomid == 0, update nickname of every room'
		info = list(self.roomid_info.find())
		for room in tqdm(info):
			nick_name = show_me_your_room_id(room['_id'])
			self.roomid_info.update({'_id':room['_id']},
									{'$set':{'room_nick_name':nick_name}})

	def update_nickname_in_mid_info(self, mid = 0):
		'Never used'
		if mid != 0:
			self.mid_info.update({'_id': mid},
									{'$set':{'man_nick_name': get_nickname_of_mid(mid)}})
			return
		'if mid == 0, update nickname of every interpretation man'
		info = list(self.mid_info.find())
		for man in tqdm(info):
			if man['danmaku_count'] >= man['danmaku_threshord']:
				nick_name = get_nickname_of_mid(man['_id'])
				self.mid_info.update({'_id':man['_id']},
									{'$set':{'man_nick_name':nick_name}})
				print(f"update the nickname of {man['_id']} to {nick_name}")

	def reset_threshord_of(self, midlist, new_threshold):
		'Never used'
		for mid in tqdm(midlist):
			prev_info = self.mid_info.find_one({'_id':mid})
			has_table = (prev_info['danmaku_count'] >= prev_info['danmaku_threshord'])
			print(prev_info['danmaku_count'],prev_info['danmaku_threshord'])
			try:
				info = self.mid_info.find_one_and_update({'_id':mid},
												{'$set':{'danmaku_threshord':new_threshold}},
												new = True)
			except:
				print(f"can't find mid {mid}")
				continue

			"if danmaku_count hasn't reach danmaku_threshord"
			print(info['danmaku_count'],info['danmaku_threshord'])
			if has_table and info['danmaku_count'] < info['danmaku_threshord']:
				self.mydb[MID_TABLE_OF+str(mid)].drop()
				print(f"table of mid {mid} dropped")

	def build_radar_chart(self, mid):
		'deal with different properties'
		'1. 弹幕数： 破坏力'
		rank_length = len(list(self.ranking.find()))
		power = (rank_length - self.obtain_current_rank(mid) + 1)/rank_length
		'2. 最长弹幕连续：持续力'
		time_list = list(
			self.mydb[MID_TABLE_OF + str(mid)].aggregate([
				{'$match': {'timestamp': {'$gt': 0}}},
				{"$group": {
					"_id": "",
					"first_date": {"$first": "$timestamp"},
					"second_date": {"$last": "$timestamp"}
					}
				},
				{"$project":
					{
						"datediff": {
							"$subtract": ["$first_date", "$second_date"]
						},
						"first_date": "$first_date",
						"second_date": "$second_date"
					}
				}
			])
		)[0]

		durability = time_list['datediff']/(int(time.time() * 1000.0) - time_list['second_date'])

		'3. 水群间隔： 精密度'
		danmaku_period = list(self.mydb[MID_TABLE_OF + f"{mid}"].aggregate([
			{"$project": {
				"_id": {
					"$toDate": {
						"$toLong": "$timestamp"
					}
				}
			}},
			{"$group": {
				"_id": {"date_val": {"$dateToString": {"format": "%Y-%m", "date": "$_id"}}},
				"count": {"$sum": 1},
			}},
			{"$sort": {"_id.date_val": -1}}
		]))

		danmaku_list = np.asarray([x['count'] for x in danmaku_period])
		danmaku_list = danmaku_list/np.sum(danmaku_list)
		uniform_list = np.ones(len(danmaku_list))/len(danmaku_list)
		precision = 1.0 - entropy(danmaku_list, uniform_list)
		'4. DD等级： 射程'
		range = len(
			list(
				self.mydb[MID_TABLE_OF + f"{mid}"].find().distinct("roomid")
			)
		)
		range = range_value(range)
		'5. 平均弹幕长度：speed'
		danmaku_information = list(self.ranking.find({'_id': mid}))[0]
		speed = (danmaku_information['danmaku_len_count']/danmaku_information['danmaku_count'])
		if speed < 6.8200:
			denominator = 6.8200
			base = 0.0
		elif speed < 7.6600:
			denominator = 7.6600
			base = 0.2
		elif speed < 9.2800:
			denominator = 9.2800
			base = 0.4
		elif speed < 10.6400:
			denominator = 10.6400
			base = 0.6
		else:
			denominator = 15.0000
			base = 0.8
		speed = min(0.2 * speed / denominator + base + 0.2, 1.0)
		'6. potential'
		potential = min(1 - (power + durability + precision + range + speed)/5. + 0.6, 1.0)
		data = [{
                    'value': [power, durability, precision, range, speed, potential]
                }]

		indicator = [
			{'name': f'破坏力{number_to_alphabet(power)}', 'max': 1.0},
			{'name': f'持续力{number_to_alphabet(durability)}', 'max': 1.0},
			{'name': f'精密动作性{number_to_alphabet(precision)}', 'max': 1.0},
			{'name': f'射程距离{number_to_alphabet(range)}', 'max': 1.0},
			{'name': f'速度{number_to_alphabet(speed)}', 'max': 1.0},
			{'name': f'成长性{number_to_alphabet(potential)}', 'max': 1.0}
		]
		return {'data': data, 'indicator': indicator}

if __name__ == '__main__':
	mydict = {
  'message_length': 99,
  'roomid': 4664126,
  'mid': 1395983,
  'uname': '蒼月夢aitoyume',
  'timestamp': 1583301481099,
   'message': "测试～"
	}
	db = MongoDB()
	# Update patch 1
	# with open("update01.py", "r") as f:
	# 	exec(f.read())
	# pdb.set_trace()

	start_time = time.time()
	# res = db.get_face_and_sign(13967)
	# db.update_mid_info_and_table_and_ranking(mydict)
	# db.find_total_rank()
	# db.build_room_chart(21560356)
	# res = db.build_message_room_persentage(13967)
	# db.build_man_chart(22038007)
	# print(db.obtain_total_danmaku_count(13967))
	print(db.build_radar_chart(2907459))

	# print(db.real_time_monitor_info(13967))
	# print(db.obtain_current_rank(13967))
	# print(db.obtain_total_danmaku_count(13967))
	# db.build_message_room_persentage(13967)
	# db.get_man_messages(13967, 4664126)
	# db.find_total_rank()
	# db.find_rank_within_past_period(mydict)
	# db.build_room_chart(mydict['roomid'])
	# db.build_man_chart(13967)
	# db.build_message_room_persentage(13967)
	# db.update_everything_according_to_a_new_message(mydict)
	print("--- %s seconds ---" % (time.time() - start_time))
	pdb.set_trace()
	# db.find_rank_within_past_period(mydict)
	# db.update_everything_according_to_a_new_message(mydict)
	# db.update_until_200220(mydict)

	# db.update_top300(mydict)
	# db.update_mid_to_nickname(mydict)
	# db.update_roomid_to_nickname(mydict)
	# db.update_until_200220(mydict)
	# db.delete_whole_dataset()
	# db.insert_one(mydict)
	# db.obtain_rank()
	# pprint.pprint(db.obtain_target_uname_data(uname='空崎そらさき'))
	# print(db.latest_room(uname='空崎そらさき'))
