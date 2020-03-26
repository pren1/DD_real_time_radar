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
	face = 'https' + res.json()['data']['face'][4:]
	sign = res.json()['data']['sign']
	time.sleep(0.1)
	while len(face) == 0:
		time.sleep(0.5)
		print("Asking bilibili...just wait")
		face = 'https' + res.json()['data']['face'][4:]
		sign = res.json()['data']['sign']
	face = advance_face_link_director(face)
	return face, sign

def advance_face_link_director(face):
	if face[-4:] == '.jpg':
		return face + "_128x128.jpg"
	elif face[-4:] == '.gif':
		return face + "_128x128.gif"
	elif face[-4:] == '.png':
		return face + "_128x128.png"

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

def number_to_alphabet(number):
	'return alphabet'
	if number < 0.2:
		return 'E'
	elif number < 0.4:
		return 'D'
	elif number < 0.6:
		return 'C'
	elif number < 0.8:
		return 'B'
	else:
		return 'A'

def range_value(range):
	if range < 5:
		return 0.1
	elif range < 10:
		return 0.3
	elif range < 20:
		return 0.5
	elif range < 30:
		return 0.7
	elif range < 40:
		return 0.9
	else:
		return 1.1

if __name__ == '__main__':
	face, sign = get_sign_and_face_of_mid(74928521)
	pdb.set_trace()