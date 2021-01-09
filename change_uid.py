#!/usr/bin/python3
import pymongo
from radar_judge import *

class MongoDB(object):
    def __init__(self):
        'To use this service, you need to install MongoDB first'
        self.myclient = pymongo.MongoClient(MONGODB_LOCAL)
        self.mydb = self.myclient[DATABASE_NAME]
        self.mid_info = self.mydb[MID_INFO]

    def get_man_messages(self, mid):
        'return all the messages of this man'
        res = list(self.mydb[MID_TABLE_OF + str(mid)].find({}))
        print(len(list(self.mydb[MID_TABLE_OF + str(1395983)].find({}))))
        # self.mydb[MID_TABLE_OF + str(1395983)].insert(self.mydb[MID_TABLE_OF + str(mid)].find({}, {'_id': 0}))
        print(len(list(self.mydb[MID_TABLE_OF + str(1395983)].find({}))))

        self.mid_info.find_one_and_update({'_id': 1395983}, {'$inc':
                                                    {'danmaku_count': 68,
                                                     'danmaku_len_count': 800}
                                                }, new=True)
        print(list(self.mid_info.find({'_id': 1395983})))
        # print(list(self.mydb[MID_TABLE_OF + str(1395983)].find({})))

if __name__ == '__main__':
    db = MongoDB()
    db.get_man_messages('14510617')
