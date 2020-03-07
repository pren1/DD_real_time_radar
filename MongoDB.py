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
		self.top_number = 300
		self.sorted_list = [] # Initialize the ranked top list

	def find_total_rank(self):
		input_data = list(self.ranking.find().sort("danmaku_count", -1))
		pprint.pprint(input_data)
		res = []
		for data in input_data:
			find_target_name = list(self.mid_info.find({'mid':data['_id']}))
			if len(find_target_name) > 0:
				res.append({
					'name': find_target_name[0]['man_nick_name'],
					'value': data['danmaku_count'],
					'uid': data['_id']
				})
		pprint.pprint(res)
		return res

	def find_rank_within_past_period(self, mydict):
		test = mydict['timestamp'] - 86400000*90
		t1 = get_real_time(test)
		res = list(self.maindb.aggregate([
			{'$match': {'timestamp': {'$gt': test}}},
			{'$group':
				{
					'_id': "$mid",
					'danmaku_count': {'$sum': 1},
					'danmaku_len_count': {'$sum': "$message_length"},
					'avg_danmaku_len': {'$avg': "$message_length"}
				}
			},
			{'$sort':
				{
					"danmaku_count": -1,
					'_id': 1
				}
			},
			{'$limit': 300}
		]))
		# pdb.set_trace()

	def build_room_chart(self, mydict):
		res = list(self.maindb.aggregate([
			{'$match': {"roomid": mydict['roomid']}},
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
			{'$match': {'count': {'$gt': 10}}},
			{"$sort": {"_id.date_val": -1}}
		]))
		pprint.pprint(res)
		# pdb.set_trace()

	def build_man_chart(self, mid):
		res = list(self.maindb.aggregate([
			{'$match': {"mid": mid}},
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
		# pprint.pprint(res)
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
					name=list(self.roomid_info.find({'roomid':single_room_slot}))[0]['room_nick_name'],
					data=month_level_format_change(current_level_room_info[single_room_slot], date_x_axis)
				)
				final_res[single_slot]['data'].append(month_level_feed_in_res)
		pprint.pprint(final_res)
		return final_res

	def build_message_room_persentage(self, mid):
		room_persentage = list(
			self.maindb.aggregate([
				{'$match': {"mid": mid}},
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
		for single in room_persentage:
			value = single['danmaku_room_persentage'] + random.uniform(0, 1)
			name = list(self.roomid_info.find({'roomid':single['_id']['roomid']}))[0]['room_nick_name']
			front_end_res.append({'value': value, 'name': name})
		pprint.pprint(front_end_res)
		return front_end_res
		# pdb.set_trace()

	def update_everything_according_to_a_new_message(self, mydict):
		'Update the following four charts here'
		self.update_maindb(mydict)
		self.update_mid_info_and_table(mydict)
		self.update_roomid_info_and_table(mydict)
		#self.update_ranking(mydict)

	def update_maindb(self, mydict):
		'Just insert to the original chart'
		insert_target = {'message_length': mydict['message_length'],
		                              'roomid': mydict['roomid'],
		                              'mid': mydict['mid'],
		                              'timestamp': mydict['timestamp'],
									  'message': mydict['message']
		                              }
		self.maindb.insert_one(insert_target)
		res = list(self.maindb.find({'mid': mydict['mid']}))

	def create_table_for_man(self, mid_val):
		history_danmaku = list(self.maindb.find({'mid': mid_val},
													{'_id': 0,
													'message_length': 1,
													'roomid': 1,
													'timestamp': 1,
													'message': 1
													}))
		new_table = self.mydb[MID_TABLE_OF+str(mid_val)]
		new_table.insert_many(history_danmaku)
		new_table.create_index([('roomid', 1),('timestamp', 1)])

	def update_mid_info_and_table(self, mydict):
		'update mid if the upcoming nickname does not exist in the current mid_chart'
		mid_val = int(mydict['mid'])
		# print('your mid is ',mid_val)
		row = self.mid_info.find_one({'_id':mid_val})
		if row is None:
			'Cannot find this mid, insert this man into the track chart'
			'A man who has sent over DANMAKU_THRESHORD interpretation danmakus can have its own table'
			self.mid_info.insert_one({'_id': mid_val,
									 'man_nick_name': '',
									 'danmaku_count': 0,
									 'danmaku_len_count': 0,
									 'danmaku_threshord': DANMAKU_THRESHORD #UNFINISHED, we need more info of this man
									 })										#please get more info from api of bilibili
		info = self.mid_info.find_one_and_update({'_id': mid_val}, {'$inc':
													{'danmaku_count':1,
													'danmaku_len_count':mydict['message_length']}
												}, new = True)
		count, threshord = info['danmaku_count'], info['danmaku_threshord']
		if count == threshord:
			nickname = get_nickname_of_mid(mid_val)
			self.mid_info.update({'_id': mid_val},{'$set':{'man_nick_name': nickname}})
			print(f"get new initerpretation man: {nickname}")
			self.create_table_for_man(mid_val)
		elif count > threshord:
			self.update_mid_table(mydict)

	def update_roomid_info_and_table(self, mydict):
		'I think this func will not be used before simon updates his roomid list'
		room_id = mydict['roomid']
		row = self.roomid_info.find_one({'_id':room_id})
		if row is None:
			room_nick_name = show_me_your_room_id(room_id=room_id)
			self.roomid_info.insert_one({'_id': room_id,
										'room_nick_name': room_nick_name #UNFINISHED, we need more info of this room
										})								 #please get more info from api of bilibili

			self.update_room_table(mydict)
			self.mydb[ROOM_TABLE_OF+str(room_id)].create_index([('mid',1),('timestamp',1)])
			print(f"{room_nick_name} has been inserted to the room name list")
		else:
			self.update_room_table(mydict)

	def update_mid_table(self, mydict):
		self.mydb[MID_TABLE_OF+str(mydict['mid'])].insert_one({'message_length': mydict['message_length'],
														'roomid': mydict['roomid'],
														'timestamp': mydict['timestamp'],
														'message': mydict['message']
														})
	def update_room_table(self, mydict):
		self.mydb[ROOM_TABLE_OF+str(mydict['roomid'])].insert_one({'message_length': mydict['message_length'],
														'mid': mydict['mid'],
														'timestamp': mydict['timestamp'],
														'message': mydict['message']
														})

	def update_nickname_in_roomid_info(self, roomid = 0):
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

	def reset_threshord_of(self, midlist, new_threshord):
		for mid in tqdm(midlist):
			prev_info = self.mid_info.find_one({'_id':mid})
			has_table = (prev_info['danmaku_count'] >= prev_info['danmaku_threshord'])
			print(prev_info['danmaku_count'],prev_info['danmaku_threshord'])
			try:
				info = self.mid_info.find_one_and_update({'_id':mid},
												{'$set':{'danmaku_threshord':new_threshord}},
												new = True)
			except:
				print(f"can't find mid {mid}")
				continue

			"if danmaku_count hasn't reach danmaku_threshord"
			print(info['danmaku_count'],info['danmaku_threshord'])
			if has_table and info['danmaku_count'] < info['danmaku_threshord']:
				self.mydb[MID_TABLE_OF+str(mid)].drop()
				print(f"table of mid {mid} dropped")


	def update_ranking(self, mydict):
		'Here is the pipline'
		'1. get the input data'
		input_message_info = list(self.maindb.aggregate([{'$match': {"mid": mydict['mid']}},
		                                                       {'$group':
			                                                       {'_id': "$mid",
																	'danmaku_count': {'$sum': 1},
																	'danmaku_len_count': {'$sum': "$message_length"},
																	'avg_danmaku_len': {'$avg': "$message_length"}
																	}
																}]))[0]
		assert len(input_message_info) > 0, "Fatal error, the target mid does not exist, which should never happen"
		'2. see if it exists in the ladder'
		res = list(self.ranking.find({'_id': input_message_info['_id']}))
		if len(res) > 0:
			'exist, then we just upgrade the data of the ladder'
			myquery = res[0]
			newvalues = {"$set": input_message_info}
			self.ranking.update_one(myquery, newvalues)
			print(f"Updated ranklist: from {myquery} to {input_message_info}")
		else:
			'Otherwise, insert the new thing'
			self.ranking.insert_one(input_message_info)
			print("Not exist in ladder, inserted")
		'Sort the whole ranking list'
		self.sorted_list = list(self.ranking.find().sort("danmaku_count", -1))[:self.top_number]
		assert len(self.sorted_list) == self.top_number, "top list length error"

if __name__ == '__main__':
	mydict = {
  'message_length': 99,
  'roomid': 4664126,
  'mid': 13967,
  'uname': '蒼月夢aitoyume',
  'timestamp': 1583301481099
	}
	db = MongoDB()
	# Update patch 1
	# with open("update01.py", "r") as f:
	# 	exec(f.read())
	# pdb.set_trace()




	import time
	start_time = time.time()
	db.find_total_rank()
	pdb.set_trace()
	# db.find_rank_within_past_period(mydict)
	# db.build_room_chart(mydict)
	db.build_man_chart(13967)
	pdb.set_trace()
	db.build_message_room_persentage(13967)
	pdb.set_trace()
	# db.update_everything_according_to_a_new_message(mydict)
	# db.update_until_200220(mydict)
	print("--- %s seconds ---" % (time.time() - start_time))
	# db.update_top300(mydict)
	# db.update_mid_to_nickname(mydict)
	# db.update_roomid_to_nickname(mydict)
	# db.update_until_200220(mydict)
	# db.delete_whole_dataset()
	# db.insert_one(mydict)
	# db.obtain_rank()
	# pprint.pprint(db.obtain_target_uname_data(uname='空崎そらさき'))
	# print(db.latest_room(uname='空崎そらさき'))
