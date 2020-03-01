import requests
from datetime import datetime

def show_me_your_room_id(room_id):
	'Get room id name'
	url = 'https://api.live.bilibili.com/live_user/v1/UserInfo/get_anchor_in_room?roomid=' + str(room_id)
	res = requests.get(url)
	return res.json()['data']['info']['uname']

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
