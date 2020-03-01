'follow target user'
from util import *
import pdb

class leader_board_drawer(object):
	def __init__(self, data_base):
		self.database = data_base

	def process_leader_board(self, k_largest=10):
		rank_res = self.database.obtain_rank()[:k_largest]
		print("************************************************")
		for single in rank_res:
			self.target_latest_room(single['_id'])
		print("************************************************")

	def target_latest_room(self, target_name):
		'Find latest room info'
		latest_room_info = self.database.latest_room(uname=target_name)
		# print(latest_room_info)
		print(clear_room_info_format(latest_room_info))





