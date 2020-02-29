#!/usr/bin/python3
import pymongo

class MongoDB(object):
	def __init__(self):
		self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		dblist = self.myclient.list_database_names()
		if "danmaku_db" in dblist:
			print("dataset has existed！")

		self.mydb = self.myclient["danmaku_db"]
		self.mycol = self.mydb["naive"]

	def insert_one(self, my_dict):
		self.mycol.insert_one(my_dict)

if __name__ == '__main__':
	mydict = {'message': '【诶…装备全让我卸下来了 没问题吗】', 'roomid': 21449083, 'mid': 393489, 'uname': '猫にこ', 'timestamp': 1583017729907}
	db = MongoDB()
	db.insert_one(mydict)
