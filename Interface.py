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
	if request.args.get('uid') == 'undefined':
		print("Undefined!")
		return jsonify({'code': -2, 'message': "Undefined uid",
		                'result': []})

	uid = int(request.args.get('uid'))
	chart_type = request.args.get('chart_type')
	print(uid)
	print(chart_type)

	if chart_type == 'ladder':
		return jsonify({'code': 0, 'message': 'return initialize rank_list', 'data': db.find_total_rank()})

	if chart_type == 'pie':
		return jsonify({'code': 1, 'message': 'pie data','data': db.build_message_room_persentage(uid)})

	if chart_type == 'bar':
		return jsonify({'code': 2, 'message': 'bar whole data', 'data': db.build_man_chart(uid)})

	return jsonify({'code': -1, 'message': "nothing returned",
	                'result': []})

if __name__ == '__main__':
	app.run(host='0.0.0.0')