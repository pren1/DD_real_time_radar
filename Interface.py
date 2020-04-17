from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import *
import pdb
from update_data import update_data
data_updater = update_data(update_rank_list=False)
data_updater.begin_update_data_periodically()
'interface to front end'
app = Flask(__name__)
CORS(app, supports_credentials=True)
@app.route('/processjson', methods=['POST'])
def processjson():
	# print(request.args)
	if request.args.get('uid') == None or request.args.get('uid') == 'undefined':
		# print("UID undefined!")
		return jsonify({'code': -2, 'message': "Undefined uid",
		                'data': []})

	if request.args.get('chart_type') == None or request.args.get('chart_type') == 'undefined':
		# print("chart type undefined!")
		return jsonify({'code': -3, 'message': "Undefined chart type", 'data': []})

	uid = int(request.args.get('uid'))
	chart_type = request.args.get('chart_type')

	# print(uid)
	# print(chart_type)

	if chart_type == 'ladder':
		# print("ladder")
		return jsonify({'code': 0, 'message': 'return initialize rank_list', 'data': data_updater.total_rank_list})

	if chart_type == 'pie':
		return jsonify({'code': 1, 'message': 'pie data','data': data_updater.message_room_persentage_dict[uid]})

	if chart_type == 'bar':
		return jsonify({'code': 2, 'message': 'bar whole data', 'data': data_updater.man_chart_dict[uid]})

	if chart_type == 'man_status':
		# print("get the status of this person")
		return jsonify({'code': 3, 'message': '[danmaku counts, rank of this man, whether this man is working or not, face, sign]',
		                'data': data_updater.man_status_dict[uid]})

	if chart_type == 'radar':
		# print("Radar!")
		return jsonify({'code': 4, 'message': 'radar map',
		                'data': data_updater.radar_dict[uid]
		                })

	if chart_type == 'monitor':
		# print('monitor!')
		return jsonify({'code': 5, 'message': 'monitor',
		                'data': data_updater.huolonglive_tracker
		                })

	if chart_type == 'danmaku':

		return jsonify({'code': 8, 'message': 'danmaku',
		                'data': data_updater.get_total_message(uid)
		                })

	'For the room related part, I do not save those things yet'
	if request.args.get('roomid') != None and request.args.get('roomid') != 'undefined':
		roomid = int(request.args.get('roomid'))
		# print(roomid)
		if chart_type == 'message':
			# print("ask for message of mid in a room")
			return jsonify({'code': 6, 'message': 'return message of a man in a room', 'data': data_updater.db.get_man_messages(mid=uid, roomid=roomid)})

		if chart_type == 'room_info':
			# print("Get room information")
			return jsonify({'code': 7, 'message': "return room message", 'data': data_updater.db.build_room_chart(roomid=roomid)})
	else:
		# print("No roomid provided")
		return jsonify({'code': -4, 'message': 'no roomid provided', 'data': []})

	print("Nothing obtained")
	return jsonify({'code': -1, 'message': "nothing returned",
	                'data': []})

if __name__ == '__main__':
	app.run(host='0.0.0.0')