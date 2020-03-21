from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import *
import pdb
from MongoDB import MongoDB
db = MongoDB()
'interface to front end'
app = Flask(__name__)
CORS(app, supports_credentials=True)
@app.route('/processjson', methods=['POST'])
def processjson():
	print(request.args)
	if request.args.get('uid') == None or request.args.get('uid') == 'undefined':
		print("UID undefined!")
		return jsonify({'code': -2, 'message': "Undefined uid",
		                'data': []})

	if request.args.get('chart_type') == None or request.args.get('chart_type') == 'undefined':
		print("chart type undefined!")
		return jsonify({'code': -3, 'message': "Undefined chart type", 'data': []})

	uid = int(request.args.get('uid'))
	chart_type = request.args.get('chart_type')

	print(uid)
	print(chart_type)

	if chart_type == 'ladder':
		print("ladder")
		return jsonify({'code': 0, 'message': 'return initialize rank_list', 'data': db.find_total_rank()})

	if chart_type == 'pie':
		return jsonify({'code': 1, 'message': 'pie data','data': db.build_message_room_persentage(uid)})

	if chart_type == 'bar':
		return jsonify({'code': 2, 'message': 'bar whole data', 'data': db.build_man_chart(uid)})

	if chart_type == 'man_status':
		print("get the status of this person")
		face, sign = db.get_face_and_sign(uid)
		return jsonify({'code': 3, 'message': '[danmaku counts, rank of this man, whether this man is working or not, face, sign]',
		                'data': {'danmaku_counts': db.obtain_total_danmaku_count(uid),
		                         'current_rank': db.obtain_current_rank(uid),
		                         'is_working': db.real_time_monitor_info(uid),
								 'face': face,
		                         'sign': sign
		                         }})

	if chart_type == 'radar':
		print("Radar!")
		return jsonify({'code': 4, 'message': 'radar map',
		                'data': db.build_radar_chart(uid)
		                })


	# if chart_type == 'danmaku_counter':
	# 	print('danmaku_counter')
	# 	return jsonify({'code': 3, 'message': 'danmaku counts', 'data': db.obtain_total_danmaku_count(uid)})
	#
	# if chart_type == 'rank':
	# 	print('Rank')
	# 	return jsonify({'code': 4, 'message': 'rank of this man', 'data': db.obtain_current_rank(uid)})
	#
	# if chart_type == 'isworking':
	# 	print("work or not")
	# 	return jsonify({'code':5, 'message': 'whether this man is working or not', 'data': db.real_time_monitor_info(uid)})

	if request.args.get('roomid') != None and request.args.get('roomid') != 'undefined':
		roomid = int(request.args.get('roomid'))
		print(roomid)
		if chart_type == 'message':
			print("ask for message of mid in a room")
			return jsonify({'code': 6, 'message': 'return message of a man in a room', 'data': db.get_man_messages(mid=uid, roomid=roomid)})

		if chart_type == 'room_info':
			print("Get room information")
			return jsonify({'code': 7, 'message': "return room message", 'data': db.build_room_chart(roomid=roomid)})
	else:
		print("No roomid provided")
		return jsonify({'code': -4, 'message': 'no roomid provided', 'data': []})

	print("Nothing obtained")
	return jsonify({'code': -1, 'message': "nothing returned",
	                'data': []})

if __name__ == '__main__':
	app.run(host='0.0.0.0')