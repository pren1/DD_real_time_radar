#!/usr/bin/python3
import pymongo
import pprint
import pdb
from util import *
from constants import MONGODB_LOCAL, DATABASE_NAME
from constants import MID_INFO, ROOMID_INFO, RANKING, MAINDB
from constants import MID_TABLE_OF, ROOM_TABLE_OF
from constants import DANMAKU_THRESHORD

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
		self.mid_info.update({'_id': mid_val}, {'$inc':
													{'danmaku_count':1,
													'danmaku_len_count':mydict['message_length']}
												})
		info = self.mid_info.find_one({'_id': mid_val})
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
"""
	def obtain_rank(self):
	'sort uname with message length sum'
	x = self.mycol.aggregate([{"$group": {"_id": '$uname', "count": {"$sum": "$message_length"}}},
	                          {"$sort":{"count":-1}}])
	# pprint.pprint(list(x))
	return [x_ for x_ in x]
	
	def obtain_target_uname_data(self, uname):
	'get all the info of uname, only for debug'
	return list(self.mycol.find({"uname":uname}, {"_id": 0}).sort("message_length", -1))
	
	def delete_whole_dataset(self):
	'remove the whole dataset, use with care'
	self.mycol.drop()
	
	def latest_room(self, uname):
	'where_is_the_latest_room_this_man_occur'
	return list(self.mycol.find({"uname":uname}, {"_id": 0, "message_length": 0}).sort("timestamp", -1).limit(1))
"""

if __name__ == '__main__':
	mydict = {
  'message_length': 99,
  'roomid': 530171,
  'mid': 12283728,
  'uname': '蒼月夢aitoyume',
  'timestamp': 1583301481099
	}
	db = MongoDB()
	import time
	start_time = time.time()
	db.update_everything_according_to_a_new_message(mydict)
	print("--- %s seconds ---" % (time.time() - start_time))
	# db.update_ranking(mydict)
	# db.update_mid_info(mydict)
	# db.update_roomid_info(mydict)
	# db.update_maindb(mydict)
	# db.delete_whole_dataset()
	# db.insert_one(mydict)
	# db.obtain_rank()
	# pprint.pprint(db.obtain_target_uname_data(uname='空崎そらさき'))
	# print(db.latest_room(uname='空崎そらさき'))
