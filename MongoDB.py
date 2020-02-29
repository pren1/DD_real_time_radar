#!/usr/bin/python3
import pymongo

class MongoDB(object):
	def __init__(self):
		self.myclient = pymongo.MongoClient("mongodb://localhost:27017/")
		dblist = self.myclient.list_database_names()
		if "danmaku_db" in dblist:
			print("dataset has existed！")
		else:
			'create new dataset'
			self.mydb = self.myclient["danmaku_db"]
			self.mycol = self.mydb["naive"]

	def insert_one(self, my_dict):
		self.mycol.insert_one(my_dict)
