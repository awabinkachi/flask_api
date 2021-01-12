#coding:utf-8
from flask import Flask, jsonify, request
import logging

app = Flask(__name__)

# JSONでの日本語文字化け対策
app.config['JSON_AS_ASCII'] = False

# log設定
LOGFILE = "test.log"
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
app.logger.setLevel(logging.DEBUG)
fh = logging.FileHandler(LOGFILE)
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
app.logger.addHandler(fh)

@app.route('/api/test')
def test():
    result = {
        "message": 'Hello, world'
    }
    logdata = 'test of Hello, world'
    app.logger.info(logdata)
    return jsonify(result), 200

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
    app.logger.warning('%s is posted', NAME)
    return jsonify(result), 400

if __name__ == '__main__':
    app.debug = True
    # app.run(host='localhost', port=4000)
    app.run()