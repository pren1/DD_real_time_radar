#!/usr/bin/python3
import pymongo

class MongoDB(object):
	def __init__(self):
		'To use this service, you need to install MongoDB first'
		self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		self.mydb = self.myclient["danmaku_db"]
		self.mycol = self.mydb["naive"]

	def insert_one(self, my_dict):
		'add one message into the database'
		self.mycol.insert_one(my_dict)

	def find_one(self):
		for x in self.mycol.find({'uname': '栀夏暮年'}, {"_id": 0}):
			print(x)

if __name__ == '__main__':
	# mydict = {'message': '【诶…装备全让我卸下来了 没问题吗】', 'roomid': 21449083, 'mid': 393489, 'uname': '猫にこ', 'timestamp': 1583017729907}
	db = MongoDB()
	# db.insert_one(mydict)
	db.find_one()
