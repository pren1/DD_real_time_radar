from flask import Flask
from flask import jsonify
from flask import request
from flask_cors import *
import pdb

'interface to front end'
app = Flask(__name__)
CORS(app, supports_credentials=True)
@app.route('/processjson', methods=['POST'])
def processjson():
	print(request.args)
	uid = request.args.get('uid')
	chart_type = request.args.get('chart_type')
	print(uid)
	print(chart_type)
	return jsonify({'code': -1, 'message': "room id not exist",
	                'result': []})

if __name__ == '__main__':
	app.run(host='0.0.0.0')