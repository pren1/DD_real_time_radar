#!/usr/bin/python3
import pymongo
import pprint
import pdb
from util import *

class MongoDB(object):
	def __init__(self):
		'To use this service, you need to install MongoDB first'
		self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		self.mydb = self.myclient["danmaku_db"]
		# Deal with different charts
		self.mid_to_nickname = self.mydb["mid_to_nickname"]
		self.roomid_to_nickname = self.mydb["roomid_to_nickname"]
		self.rank_top300 = self.mydb["rank_top300"]
		self.until_200220 = self.mydb["until_200220"]
		self.top_number = 300
		self.sorted_list = [] # Initialize the ranked top list

	def build_message_room_persentage(self, mydict):
		total_length = self.until_200220.find({"mid": mydict['mid']}).count()
		test_case = self.until_200220.aggregate([{'$match': {"mid": mydict['mid']}},
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
			                                         "weight": {"$divide": ["$room_danmaku_count", '$_id.total']},
		                                         }},
		                                         {"$sort": {"weight": -1}}
		                                         ])
		res = list(test_case)

		test_case2 = list(self.until_200220.aggregate([{'$match': {"mid": mydict['mid']}},
		                                         {'$group':
			                                        {'_id': "$roomid",
			                                         'room_danmaku_count': {'$sum': 1}
													}
												 },
		                                         {"$addFields": {
			                                         "weight": {"$divide": ["$room_danmaku_count", total_length]},
		                                         }},
		                                         {"$sort": {"weight": -1}}
		                                         ]))
		pdb.set_trace()




	def update_everything_according_to_a_new_message(self, mydict):
		'Update the following four charts here'
		self.update_until_200220(mydict)
		self.update_mid_to_nickname(mydict)
		self.update_roomid_to_nickname(mydict)
		self.update_rank_top300(mydict)

	def update_until_200220(self, mydict):
		'Just insert to the original chart'
		insert_target = {'message_length': mydict['message_length'],
		                              'roomid': mydict['roomid'],
		                              'mid': mydict['mid'],
		                              'timestamp': mydict['timestamp']
		                              }
		self.until_200220.insert_one(insert_target)
		res = list(self.until_200220.find({'mid':mydict['mid']}))
		# pdb.set_trace()

	def update_mid_to_nickname(self, mydict):
		'update mid if the upcoming nickname does not exist in the current mid_chart'
		mid_val = mydict['mid']
		uname = mydict['uname']
		if len(list(self.mid_to_nickname.find({'mid':mid_val}))) == 0:
			# Cannot find this mid, insert this man into the track chart
			self.mid_to_nickname.insert_one({'mid': mid_val, 'man_nick_name': uname})
			print(f"{uname} has been inserted to the name list")
		else:
			print("This man existed in the nickname list, do nothing")

	def update_roomid_to_nickname(self, mydict):
		'I think this func will not be used before simon updates his roomid list'
		room_id = mydict['roomid']
		if len(list(self.roomid_to_nickname.find({'roomid':room_id}))) == 0:
			room_nick_name = show_me_your_room_id(room_id=room_id)
			self.roomid_to_nickname.insert_one({'roomid': room_id, 'room_nick_name': room_nick_name})
			print(f"{room_nick_name} has been inserted to the room name list")
		else:
			print("This room has existed in the room nickname list, do nothing")

	def update_rank_top300(self, mydict):
		'Here is the pipline'
		'1. get the input data'
		input_message_info = list(self.until_200220.aggregate([{'$match': {"mid": mydict['mid']}},
		                                                       {'$group':
			                                                       {'_id': "$mid",
																	'danmaku_count': {'$sum': 1},
																	'danmaku_len_count': {'$sum': "$message_length"},
																	'avg_danmaku_len': {'$avg': "$message_length"}
																	}
																}]))[0]
		assert len(input_message_info) > 0, "Fatal error, the target mid does not exist, which should never happen"
		'2. see if it exists in the ladder'
		res = list(self.rank_top300.find({'_id': input_message_info['_id']}))
		if len(res) > 0:
			'exist, then we just upgrade the data of the ladder'
			myquery = res[0]
			newvalues = {"$set": input_message_info}
			self.rank_top300.update_one(myquery, newvalues)
			print(f"Updated ranklist: from {myquery} to {input_message_info}")
		else:
			'Otherwise, insert the new thing'
			self.rank_top300.insert_one(input_message_info)
			print("Not exist in ladder, inserted")
		'Sort the whole rank_top300 list'
		self.sorted_list = list(self.rank_top300.find().sort("danmaku_count", -1))[:self.top_number]
		assert len(self.sorted_list) == self.top_number, "top list length error"

	# def obtain_rank(self):
	# 	'sort uname with message length sum'
	# 	x = self.mycol.aggregate([{"$group": {"_id": '$uname', "count": {"$sum": "$message_length"}}},
	# 	                          {"$sort":{"count":-1}}])
	# 	# pprint.pprint(list(x))
	# 	return [x_ for x_ in x]
	#
	# def obtain_target_uname_data(self, uname):
	# 	'get all the info of uname, only for debug'
	# 	return list(self.mycol.find({"uname":uname}, {"_id": 0}).sort("message_length", -1))
	#
	# def delete_whole_dataset(self):
	# 	'remove the whole dataset, use with care'
	# 	self.mycol.drop()
	#
	# def latest_room(self, uname):
	# 	'where_is_the_latest_room_this_man_occur'
	# 	return list(self.mycol.find({"uname":uname}, {"_id": 0, "message_length": 0}).sort("timestamp", -1).limit(1))

if __name__ == '__main__':
	mydict = {
  'message_length': 99,
  'roomid': 530171,
  'mid': 13967,
  'uname': '蒼月夢aitoyume',
  'timestamp': 1583301481099
	}
	db = MongoDB()
	import time
	start_time = time.time()
	db.build_message_room_persentage(mydict)
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
