#coding:utf-8
from flask import Flask, jsonify, request

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # JSONでの日本語文字化け対策

@app.route('/api/test')
def test():
	result = {
		"message": 'Hello, world'
	}
	return jsonify(result)

@app.route('/api/fr', methods=['POST'])
def fr():
	json = request.get_json()  # POSTされたJSONを取得
	NAME = json['first']
	result = {
		"data": {
			"id": 1,
			"name": NAME
		}
	}
	return jsonify(result)

if __name__ == '__main__':
	app.debug = True
	# app.run(host='localhost', port=4000)
	app.run()