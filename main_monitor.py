'follow target user'
from python_ws_client import python_ws_client
from util import *

class main_monitor(object):
	def __init__(self):
		self.ws_listenser = python_ws_client()
		self.database = self.ws_listenser.get_database()

	def target_latest_room(self, target_name):
		'Find latest room info'
		latest_room_info = self.database.latest_room(uname=target_name)
		# print(latest_room_info)
		print(clear_room_info_format(latest_room_info))





