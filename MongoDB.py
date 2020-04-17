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
from radar_judge import *

class MongoDB(object):
	def __init__(self, update_rank_list = False):
		'To use this service, you need to install MongoDB first'
		self.myclient = pymongo.MongoClient(MONGODB_LOCAL)
		self.mydb = self.myclient[DATABASE_NAME]
		# Deal with different charts
		self.mid_info = self.mydb[MID_INFO]
		self.roomid_info = self.mydb[ROOMID_INFO]
		self.ranking = self.mydb[RANKING]
		self.maindb = self.mydb[MAINDB]
		self.sorted_list = [] # Initialize the ranked top list
		self.total_message_obtain = {}
		if update_rank_list:
			self.update_the_original_rank_list()
			'Also, we build the message lists'
			self.build_basic_message_sets()

	def build_basic_message_sets(self):
		_, mid_list = self.find_total_rank()
		print("Building messages for each people in the rank list")
		for uid in tqdm(mid_list):
			self.total_message_obtain[uid] = self.get_all_danmaku(uid)

	def update_message_sets(self, mydict):
		'This set saves all the received danmakus'
		uid = mydict['mid']
		room_id_info = list(self.roomid_info.find({'_id':mydict['roomid']}))[0]['room_nick_name']
		time_info = get_real_time(mydict['timestamp'])
		insert_target = {'roomid': room_id_info,
		                 'message': mydict['message'],
		                 'date_val': time_info
		                 }
		if uid in self.total_message_obtain:
			if room_id_info in self.total_message_obtain[uid]:
				'At here, this is a list'
				self.total_message_obtain[uid][room_id_info].insert(0, insert_target)
			else:
				self.total_message_obtain[uid][room_id_info] = [insert_target]
		else:
			self.total_message_obtain[uid] = {}
			self.total_message_obtain[uid][room_id_info] = [insert_target]

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
		# pprint.pprint(fin_res)
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
		'Do not forget to sort the ranking list'
		rank_list = list(self.ranking.find().sort("danmaku_len_count", -1))
		rank = 1
		for single_one in rank_list:
			if single_one['_id'] == mid:
				return rank
			rank += 1
		'This man does not exist in the rank list!'
		return -1

	def obtain_total_danmaku_count(self, mid):
		'How many danmaku intotal did this person sent'
		res = list(self.ranking.find({'_id':mid}))[0]
		return res['danmaku_len_count'], res['man_nick_name']

	def update_the_original_rank_list(self):
		'Up to date!'
		print("Updating original rank list...")
		self.ranking.drop()
		print("deleted previous ranking list")
		'get the list from dataset for one time. Later, we will update it when necessary...'
		rank_list_curosr = self.mid_info.find({'$where':"this.danmaku_count >= this.danmaku_threshord"}).sort("danmaku_len_count", -1)
		for single_rank in tqdm(rank_list_curosr):
			face, sign = get_sign_and_face_of_mid(single_rank['_id'])
			single_rank['face'] = face
			single_rank['sign'] = sign
			'Modify: also, we add the time information'
			'Get last danmaku time, record it'
			single_rank['keep_working_time'] = 0
			self.ranking.find_one_and_update({"_id": single_rank['_id']},
			                               {'$set': single_rank},
			                               upsert=True)
			# pprint.pprint(list(self.ranking.find()))
			# self.ranking.update({'_id': single_rank['_id']}, {'$set': single_rank})
		print("Ranking list Updated")
		# pprint.pprint(list(self.ranking.find()))
		# pdb.set_trace()

	def find_total_rank(self):
		'Up to date!'
		# pprint.pprint(self.ranking)
		# pdb.set_trace()
		res = []
		mid_list = []
		'do not forget to sort the rank list!'
		for data in self.ranking.find().sort("danmaku_len_count", -1):
			find_target_name = data['man_nick_name']
			if len(find_target_name) > 0:
				res.append({
					'name': find_target_name,
					'value': data['danmaku_len_count'],
					'uid': data['_id'],
					'face': data['face'],
					'sign': data['sign']
				})
				mid_list.append(data['_id'])
		# pprint.pprint(res[:5])
		return res, mid_list

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
		# pprint.pprint(year_month_slot)
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
		# pprint.pprint(final_res)
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
				"_id": {"roomid": "$roomid", "date_val": {"$dateToString": {
					"format": "%Y-%m-%d",
					"date": "$_id",
					"timezone": "Asia/Shanghai"
				}
				}
				        },
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
				# print(month_level_feed_in_res)
				# print(single_slot)
				final_res[single_slot]['data'].append(month_level_feed_in_res)
		if '1970-01' in final_res:
			final_res['1970-01']['x_axis'] = ['2019早期数据']
			final_res['早期数据'] = final_res.pop('1970-01')
		# pprint.pprint(final_res)
		# pdb.set_trace()
		'To get the accurate number'

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
				# {"$addFields": {
				# 	"danmaku_room_persentage": {"$divide": ["$room_danmaku_count", '$_id.total']},
				# }},
				# {"$sort": {"room_danmaku_count": -1}},
				{"$project": { "_id.total": 0}}
			]))
		front_end_res = []
		room_id_list = []
		for single in room_persentage:
			'Notice you add random val here'
			value = single['room_danmaku_count']
			name = list(self.roomid_info.find({'_id':single['_id']['roomid']}))[0]['room_nick_name']
			front_end_res.append({'value': value, 'name': name})
			roomid = single['_id']['roomid']
			room_id_list.append({'roomid': roomid, 'name': name})
		# pprint.pprint(front_end_res)
		# pprint.pprint(room_id_list)
		return {'pie_data': front_end_res, 'roomid_list': room_id_list}

	def update_everything_according_to_a_new_message(self, mydict):
		'Update the following four charts here'
		'Up to date!'
		self.update_maindb(mydict)
		self.update_mid_info_and_table_and_ranking(mydict)
		self.update_roomid_info_and_table(mydict)
		self.update_message_sets(mydict)

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

	def judge_interperter(self, mid):
		danmakus = self.maindb.aggregate([
			{'$match':{'mid': mid, 'timestamp':{'$gt':0}}},
			{'$sort':{'timestamp': 1}},
			{'$project':
				{
					'_id': 0,
					'roomid': 1,
					'timestamp': 1
				}
			}
		])
		now_room , now_time = 0, 0
		intp_process_cnt, in_process = 0, 0
		danmaku_count = 0
		for d in danmakus:
			if d['timestamp'] != 0:
				danmaku_count += 1
				if d['roomid'] != now_room:
					now_room = d['roomid']
					if in_process >= 10:
						intp_process_cnt += in_process
					in_process = 1
				else:
					time_diff = (d['timestamp'] - now_time)//1000
					if time_diff < 60*5: #5 minutes
						in_process += 1
					else:
						if in_process >= 10:
							intp_process_cnt += in_process
						in_process = 1
				now_time = d['timestamp'] 
		if in_process >= 10:
			intp_process_cnt += in_process
		if danmaku_count == 0:
			danmaku_count = 1
		process_rate = intp_process_cnt / danmaku_count
		return process_rate > 0.1

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
			if not self.judge_interperter(mid_val):
				self.mid_info.update({'_id': mid_val}, {'$set':{'danmaku_threshord': threshold * 2}})
				return
			nickname = get_nickname_of_mid(mid_val)
			'Assign this man a name'
			self.mid_info.update({'_id': mid_val},{'$set':{'man_nick_name': nickname}})
			print(f"get new initerpretation man: {nickname}, YEAH!")
			self.create_table_for_man(mid_val)

			'add face & sign information here'
			face, sign = get_sign_and_face_of_mid(info['_id'])
			info['face'] = face
			info['sign'] = sign
			'also, we add the time info here...'
			'We need to fill the following values here...'
			info['keep_working_time'] = 0
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

			'See if this man is working or not...'
			res = list(self.mydb[MID_TABLE_OF + str(info['_id'])].find().sort("timestamp", -1).limit(2))
			time_diff = abs(res[0]['timestamp'] - res[1]['timestamp'])
			diff_thres = WORKING_THRESHOLD * 60000.0

			if time_diff < diff_thres:
				'on live'
				info['keep_working_time'] = myquery['keep_working_time'] + time_diff

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
			print(f"{room_nick_name} has been inserted to the room name list, room id is: {room_id}")
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
		power = ((rank_length - self.obtain_current_rank(mid) + 1)/rank_length) ** 3

		'2. 最长高强度同传时间：持续力'
		durability = build_max_length(self, mid)

		'3. 平均弹幕长度：字长'
		danmaku_information = list(self.ranking.find({'_id': mid}))[0]
		danmaku_len = primary_len = (danmaku_information['danmaku_len_count']/danmaku_information['danmaku_count'])
		if danmaku_len < 6.8200:
			denominator = 6.8200
			base = 0.0
		elif danmaku_len < 7.6600:
			denominator = 7.6600
			base = 0.2
		elif danmaku_len < 9.2800:
			denominator = 9.2800
			base = 0.4
		elif danmaku_len < 10.6400:
			denominator = 10.6400
			base = 0.6
		else:
			denominator = 15.0000
			base = 0.8
		danmaku_len = 0.2 * danmaku_len / denominator + base + 0.2

		'4. DD范围指数： 射程'
		primary_range = DD_range(self, mid)
		dd_range = range_value(primary_range)

		'5. 反摸鱼指数： 肝'
		hardworking = anti_moyu(self, mid)

		'6. 平均每分钟字数：攻速'
		speed = build_speed(self, mid)
		
		'标准化&统计'
		max_value = [1.0, 3.0, 1.0, 1.0, 1.0, 90.0]
		primary_value = [power, durability[0], primary_len, primary_range, hardworking, speed]
		primary_value = [round(v, 2) for v in primary_value]
		value = [power, durability[0], danmaku_len, dd_range, hardworking, speed]
		standard = [round(min(1.2, value[i] / max_value[i]), 2) for i in range(6)] #允许最多达到表盘数值的1.2倍
		#points = [round(v*100) for v in standard]
		data = [{
                    'value': standard
                }]

		indicator = [
			{'name': f'破坏力{number_to_alphabet(standard[0])}', 'max': 1.0},
			{'name': f'持续力{number_to_alphabet(standard[1])}', 'max': 1.0},
			{'name': f'字长{number_to_alphabet(standard[2])}', 'max': 1.0},
			{'name': f'射程{number_to_alphabet(standard[3])}', 'max': 1.0},
			{'name': f'肝{number_to_alphabet(standard[4])}', 'max': 1.0},
			{'name': f'攻速{number_to_alphabet(standard[5])}', 'max': 1.0}
		]

		others = {
			'primary_value': primary_value,
			'longest_room':durability[1],
			'longest_date': durability[2]
		}
		return {'data': data, 'indicator': indicator, 'others': others}

	def build_huolonglive_tracker(self):
		'track every man status on the rank list, then shows those man who is working'
		all_man_list = list(self.ranking.find({}, { '_id': 1, 'man_nick_name': 1 }))
		current_time = int(time.time() * 1000.0)
		working_man_list = []
		for mid in all_man_list:
			'Find the chart of this man'
			res = list(self.mydb[MID_TABLE_OF + str(mid['_id'])].find().sort("timestamp", -1).limit(1))
			past_danmaku_time = res[0]['timestamp']
			# If appear within 5 mins
			diff_thres = WORKING_THRESHOLD * 60000.0
			time_diff = abs(current_time - past_danmaku_time)
			if time_diff < diff_thres:
				'on live'
				# print('on live')
				room_info = list(self.roomid_info.find({'_id': res[0]['roomid']}))[0]['room_nick_name']
				mid['room_info'] = room_info
				working_man_list.append(mid)
			else:
				'nope'
				# print(f'摸鱼: {mid}')
				find_res = list(self.ranking.find({'_id': mid['_id']}))[0]
				self.ranking.update_one(find_res, {"$set": {'keep_working_time': 0}})
		fin_res = []
		room_dict = {}
		user_id_mapping = {}
		for single_work_man in working_man_list:
			room_info = single_work_man['room_info']
			nick_name = single_work_man['man_nick_name']
			user_id = single_work_man['_id']
			'Get minutes'
			'For some reason, at least the working time is 1 minutes'
			working_time = int(max(1, list(self.ranking.find({'_id':single_work_man['_id']}))[0]['keep_working_time']/60000.0))
			fin_res.append(
				{'name': f"{nick_name}",
				 'value': working_time}
			)
			user_id_mapping[nick_name] = user_id
			if room_info in room_dict:
				room_dict[room_info] += 1
			else:
				room_dict[room_info] = 1

		inner_room_info = []
		room_id_mapping = {}
		for single_room in room_dict:
			inner_room_info.append(
				{'name': single_room,
				 'value': room_dict[single_room]}
			)
			room_id_mapping[single_room] = list(self.roomid_info.find({'room_nick_name':single_room}))[0]['_id']
		if len(fin_res) > 0 and len(inner_room_info):
			random.shuffle(fin_res)
			return {'man_value': fin_res, 'room_value': inner_room_info, 'user_id_mapping': user_id_mapping, 'room_id_mapping': room_id_mapping}
		else:
			return {'man_value': [{'name': '黑暗剑', 'value': 22}], 'room_value': [{'name': '摸鱼之王', 'value': 22}],
			        'user_id_mapping': {'黑暗剑': 15810}, 'room_id_mapping': {'摸鱼之王': 545318}}

	def obtain_man_status(self, uid):
		face, sign = self.get_face_and_sign(uid)
		danmaku_counts, nick_name = self.obtain_total_danmaku_count(uid)
		current_rank = self.obtain_current_rank(uid)
		is_working = self.real_time_monitor_info(uid)
		return {'danmaku_counts': danmaku_counts,
			          'current_rank': current_rank,
			          'is_working': is_working,
			          'face': face,
			          'sign': sign,
			          'nick_name': nick_name
			          }

	def get_all_danmaku(self, mid):
		res = list(
			self.mydb[MID_TABLE_OF + f"{mid}"].aggregate([
				{"$project": {
					"roomid": "$roomid",
					"message": "$message",
					"timeline": {
						"$toDate": {
							"$toLong": "$timestamp"
						}
					}
				}},
				{"$project": {
					"_id": {"roomid": "$roomid",
					        "message": "$message",
					        "date_val": {
						        "$dateToString": {
									"format": "%Y-%m-%d %H:%M:%S",
									"date": "$timeline",
									"timezone": "Asia/Shanghai"
										}
									}
							},
					}
				},
				{"$sort": {"_id.date_val": -1}}
			],
			allowDiskUse=True
			)
		)
		'Build room name dict'
		room_info_dict = {}
		room_id_list = list(self.roomid_info.find({}))
		for single in room_id_list:
			room_info_dict[single['_id']] = single['room_nick_name']

		'save messages to dict according to the room_id'
		danmaku_dict = {}
		for single in res:
			room_id = room_info_dict[single['_id']['roomid']]
			day_value = single['_id']['date_val'].split(' ')[0]
			if day_value == '1970-01-01':
				day_value = '早期数据'
			single['_id']['roomid'] = room_id
			if day_value == '早期数据':
				single['_id'] = {'同传弹幕': single['_id']['message'], '时间': '早期数据'}
			else:
				single['_id'] = {'同传弹幕': single['_id']['message'], '时间': single['_id']['date_val']}
			if room_id in danmaku_dict:
				if day_value in danmaku_dict[room_id]:
					danmaku_dict[room_id][day_value].append(single['_id'])
				else:
					danmaku_dict[room_id][day_value] = [single['_id']]
			else:
				danmaku_dict[room_id] = {}
				danmaku_dict[room_id][day_value] = [single['_id']]
		'Add time keys to each dict here'
		for single_room in danmaku_dict:
			danmaku_dict[single_room]['time_select'] = list(danmaku_dict[single_room].keys())
		return danmaku_dict

if __name__ == '__main__':
	mydict = {
  'message_length': 99,
  'roomid': 13946381,
  'mid': 139232167,
  'uname': '蒼月夢aitoyume',
  'timestamp': 1583301485000,
   'message': "测试～"
	}
	db = MongoDB(update_rank_list=False)
	db.get_all_danmaku(351290)
	db.build_basic_message_sets()
	db.update_message_sets(mydict)
	# db.get_all_danmaku(351290)
	# print(db.obtain_total_danmaku_count(13967))
	# db.build_message_room_persentage(13967)
	# Update patch 1
	# with open("update01.py", "r") as f:
	# 	exec(f.read())
	# pdb.set_trace()
	# print(db.obtain_current_rank(13967))
	# db.find_total_rank()
	# db.update_roomid_info_and_table(mydict)
	start_time = time.time()
	#print(db.build_radar_chart(13967))
	#print(db.build_radar_chart(27212086))
	#print(db.judge_interperter(13967))
	#print(db.judge_interperter(28464598))
	# db.update_mid_info_and_table_and_ranking(mydict)
	# pdb.set_trace()
	# db.build_man_chart(13967)
	# db.build_man_chart(351290)
	# pdb.set_trace()
	#pprint.pprint(db.build_huolonglive_tracker())
	# pdb.set_trace()
	# res = db.get_face_and_sign(13967)
	# db.update_mid_info_and_table_and_ranking(mydict)
	# db.find_total_rank()
	# db.build_room_chart(21560356)
	# res = db.build_message_room_persentage(13967)
	# db.build_man_chart(22038007)
	# print(db.obtain_total_danmaku_count(13967))
	# print(db.build_radar_chart(2907459))

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
	#pdb.set_trace()
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
