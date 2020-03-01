#!/usr/bin/python3
import pymongo
import pprint

class MongoDB(object):
	def __init__(self):
		'To use this service, you need to install MongoDB first'
		self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		self.mydb = self.myclient["danmaku_db"]
		self.mycol = self.mydb["naive"]

	def insert_one(self, my_dict):
		'add one message into the database'
		self.mycol.insert_one(my_dict)

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

if __name__ == '__main__':
	# mydict = {'message': '【诶…装备全让我卸下来了 没问题吗】', 'roomid': 21449083, 'mid': 393489, 'uname': '猫にこ', 'timestamp': 1583017729907}
	db = MongoDB()
	# db.delete_whole_dataset()
	# db.insert_one(mydict)
	# db.obtain_rank()
	# pprint.pprint(db.obtain_target_uname_data(uname='空崎そらさき'))
	# print(db.latest_room(uname='空崎そらさき'))
