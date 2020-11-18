'Scheduling the roomid to each client server'
import pdb
import pprint
from util import show_me_your_room_id

class Client_Secheduler(object):
	def __init__(self, socket_dict_list, initial_room_id_list, room_info_dict):
		self.socket_dict_list = socket_dict_list
		self.max_available_clients = len(socket_dict_list)
		self.room_info_dict = room_info_dict
		self.each_client_capacity = 64
		'extra room gets truncated'
		self.room_id_list = initial_room_id_list[:self.each_client_capacity * self.max_available_clients]
		if len(self.room_id_list) == 0:
			print("Room id list empty, no one is on live. Are you sure?")
		self.client_task_dict = {}
		self.build_initial_client_tasks()
		self.current_event = {}
		self.server_status = {}
		for single_ip in socket_dict_list:
			self.current_event[single_ip['ip']] = []
			self.server_status[single_ip['ip']] = False

	def renew_every_socket_connection(self):
		print('Check every socket connection, otherwise we get disconnected')
		for ip in self.client_task_dict:
			self.server_status[ip] = self.client_task_dict[ip]['socket'].connection_detect_suit()
		pprint.pprint(self.server_status)
		print(self.server_status, file=open("log.txt", "a"))

	def build_initial_client_tasks(self):
		for index, single_room in enumerate(self.room_id_list):
			'assign to client according to the index'
			current_socket_dict = self.socket_dict_list[index%self.max_available_clients]
			'Direct the clients via socket'
			current_socket_dict['socket'].watch_room(single_room)
			if current_socket_dict['ip'] in self.client_task_dict:
				self.client_task_dict[current_socket_dict['ip']]['roomid_list'].append(single_room)
			else:
				self.client_task_dict[current_socket_dict['ip']] = {'roomid_list': [single_room], 'socket': current_socket_dict['socket']}
		pprint.pprint(self.client_task_dict)

	def renew_client_tasks_using_new_roomid_list(self, new_list):
		'Do not do anything when the list does not change'
		# if new_list == self.room_id_list:
		# 	return
		'Always renew'
		removed_list, added_list = self.get_difference_between_two_lists(old_list=self.room_id_list, new_list=new_list)
		if removed_list:
			print(f"observe changes: Removed_list: {removed_list}")
			print(f"observe changes: Removed_list: {removed_list}", file=open("log.txt", "a"))
		if added_list:
			print(f"observe changes, added_list: {added_list}")
			print(f"observe changes, added_list: {added_list}", file=open("log.txt", "a"))
		'Remove roomid within removed_list'
		for remove_room in removed_list:
			self.Stop_monitoring_target_roomid(remove_room)
		'Add roomid within added_list'
		for add_room in added_list:
			self.Assign_task_to_one_client(add_room)
		self.room_id_list = new_list
		'At this point, the self.client_task_dict contains the assignment of each server'
		for ip in self.client_task_dict:
			target_room_id_list = self.client_task_dict[ip]['roomid_list']
			client_room_id_list = self.client_task_dict[ip]['socket'].client_room_list
			removed_list, added_list = self.get_difference_between_two_lists(old_list=client_room_id_list, new_list=target_room_id_list)
			if removed_list or added_list:
				print(f"For {ip}, remove: {removed_list}, add: {added_list}")
				print(f"For {ip}, remove: {removed_list}, add: {added_list}", file=open("log.txt", "a"))
			for remove_room in removed_list:
				print(f"Removing roomid: {remove_room} from {ip}")
				print(f"Removing roomid: {remove_room} from {ip}", file=open("log.txt", "a"))
				self.client_task_dict[ip]['socket'].close_room(remove_room)

			for add_room in added_list:
				print(f"Assigning roomid: {add_room} to {ip}")
				print(f"Assigning roomid: {add_room} to {ip}", file=open("log.txt", "a"))
				self.client_task_dict[ip]['socket'].watch_room(add_room)

	def get_difference_between_two_lists(self, old_list, new_list):
		total_set = set(old_list + new_list)
		removed_list = []
		added_list = []
		for single in total_set:
			if single in old_list and single in new_list:
				continue
			elif single in old_list and single not in new_list:
				removed_list.append(single)
			elif single not in old_list and single in new_list:
				added_list.append(single)
			else:
				assert 1 == 0, "Fatal logic error"
		return removed_list, added_list

	def Stop_monitoring_target_roomid(self, roomid):
		if roomid not in self.room_info_dict:
			self.room_info_dict[roomid] = show_me_your_room_id(room_id=roomid)
		for ip in self.client_task_dict:
			if roomid in self.client_task_dict[ip]['roomid_list']:
				'Find it, direct the client to remove it'
				self.push_info_to_current_event(f'{self.room_info_dict[roomid]} 已下播', ip)
				# print(f"Removing roomid: {roomid} from {ip}")
				'Do not forget to remove the roomid from corresponding dict'
				self.client_task_dict[ip]['roomid_list'].remove(roomid)
				# self.client_task_dict[ip]['socket'].close_room(roomid)
				return
		print(f"No where is roomid {roomid}!!!")
		print(f"No where is roomid {roomid}!!!", file=open("log.txt", "a"))

	def Assign_task_to_one_client(self, roomid):
		if roomid not in self.room_info_dict:
			self.room_info_dict[roomid] = show_me_your_room_id(room_id=roomid)
		'Before everything, let us find the most suitable client'
		suitable_ip = self.find_suitable_client_ip()
		if suitable_ip != 'overburden':
			self.push_info_to_current_event(f'{self.room_info_dict[roomid]} 已上播', suitable_ip)
			# print(f"Assigning roomid: {roomid} to {suitable_ip}")
			self.client_task_dict[suitable_ip]['roomid_list'].append(roomid)
			# self.client_task_dict[suitable_ip]['socket'].watch_room(roomid)

	def push_info_to_current_event(self, information, ip):
		if ip in self.current_event:
			self.current_event[ip].append(information)
		else:
			self.current_event[ip] = [information]

	def find_client_dict(self):
		tempory_client_dict = {}
		for ip in self.client_task_dict:
			tempory_client_dict[ip] = len(self.client_task_dict[ip]['roomid_list'])
		return tempory_client_dict

	def find_room_id_name_dict(self):
		room_id_dict = {}
		for ip in self.client_task_dict:
			res = []
			for x in self.client_task_dict[ip]['roomid_list']:
				if x not in self.room_info_dict:
					self.room_info_dict[x] = show_me_your_room_id(room_id=x)
				res.append(self.room_info_dict[x])
			room_id_dict[ip] = res
		return room_id_dict

	def find_suitable_client_ip(self):
		tempory_client_dict = {}
		for ip in self.client_task_dict:
			tempory_client_dict[ip] = len(self.client_task_dict[ip]['roomid_list'])
		'Get ip with minimum overhead'
		target_ip = min(tempory_client_dict, key = tempory_client_dict.get)
		if tempory_client_dict[target_ip] >= self.each_client_capacity:
			print("Too many live rooms, we are overburden. Wont keep monitoring new room until things become better")
			print("Too many live rooms, we are overburden. Wont keep monitoring new room until things become better", file=open("log.txt", "a"))
			return 'overburden'
		return target_ip