import requests
from datetime import datetime
import time
import pdb

def show_me_your_room_id(room_id):
	'Get room id name'
	url = 'https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room?roomid=' + str(room_id)
	res = requests.get(url)
	name = res.json()['data']['info']['uname']
	while len(name) == 0:
		# time.sleep(1)
		res = requests.get(url)
		name = res.json()['data']['name']
	return name

def get_nickname_of_mid(mid):
	'Get nickname from mid'
	url = 'https://api.bilibili.com/x/space/acc/info?mid='+str(mid)
	res = requests.get(url)
	name = res.json()['data']['name']
	while len(name) == 0:
		# time.sleep(1)
		res = requests.get(url)
		name = res.json()['data']['name']
	return name

def get_sign_and_face_of_mid(mid):
	url = 'https://api.bilibili.com/x/space/acc/info?mid=' + str(mid)
	res = requests.get(url)
	face = res.json()['data']['face']
	sign = res.json()['data']['sign']
	time.sleep(1)
	while len(face) == 0:
		time.sleep(1)
		print("Asking bilibili...just wait")
		face = res.json()['data']['face']
		sign = res.json()['data']['sign']
	return face, sign

def get_real_time(timestamp):
	'change timestamp to real time'
	your_dt = datetime.fromtimestamp(int(timestamp)/1000)  # using the local timezone
	return your_dt.strftime("%Y-%m-%d %H:%M:%S")

def clear_room_info_format(room_info):
	'clean the room_info, return a string'
	# room_id = show_me_your_room_id(room_info[0]['roomid'])
	room_id = room_info[0]['roomid']
	user_name = room_info[0]['uname']
	time_stamp = get_real_time(room_info[0]['timestamp'])
	build_string = f"{user_name} 于 {time_stamp} 在 {room_id} 同传"
	return build_string

if __name__ == '__main__':
	face, sign = get_sign_and_face_of_mid(74928521)
	pdb.set_trace()