#coding:utf-8
from flask import Flask, jsonify, request
import logging
import requests
import json

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

PII_MODULE_URL_JP = "http://35.243.95.2:8001/todo/api/v1.0/detect_pii"
PII_MODULE_URL_US = "http://35.190.230.167:8000/todo/api/v1.0/detect_pii"
PII_MODULE_URL_TW = "http://34.84.102.217:8002/todo/api/v1.0/detect_pii"

# データのチェック
def validate(json_data):
    # TODO 後でconfig化
    NAME_COUNTRY = "country"
    NAME_ID = "id"
    NAME_CONTENT = "content"
    NOT_NULL_STR = "フィールドが必須です"
    LEN_COUNTRY = 2
    VALUES_COUNTRY = ["jp", "us", "tw"]
    LEN_ID = 100
    LEN_CONTENT = 2000

    msg_list = []
    for record in json_data:
        # 必須チェック
        if not record[NAME_COUNTRY]:
            msg_list.append('%s %s', NAME_COUNTRY, NOT_NULL_STR)
            break
        if not record[NAME_ID]:
            msg_list.append('%s %s', NAME_ID, NOT_NULL_STR)
            break
        if not record[NAME_CONTENT]:
            msg_list.append('%s %s', NAME_CONTENT, NOT_NULL_STR)
            break

        # 内容チェック
        if len(record[NAME_COUNTRY]) != LEN_COUNTRY:
            msg_list.append('%s フィールドが %d 桁以外は禁止です。', NAME_COUNTRY, LEN_COUNTRY)
            break
        if not record[NAME_COUNTRY] in VALUES_COUNTRY:
            msg_list.append('%s フィールドの内容が [%s] 以外の値は禁止です', NAME_COUNTRY, ",".join(VALUES_COUNTRY))
            break
        if len(record[NAME_ID]) > LEN_ID:
            msg_list.append('%s フィールドが %d 桁以上は禁止です。', NAME_ID, LEN_ID)
            break
        if len(record[NAME_CONTENT]) > LEN_CONTENT:
            msg_list.append('%s フィールドが %d 桁以上は禁止です。', NAME_CONTENT, LEN_CONTENT)
            break

    return msg_list

#マスキングAPIの呼び出し
def get_masking_data(one_data):
    url = PII_MODULE_URL_JP

    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}

    timeout_seconds = 300
    wait_seconds = 30
    retry_times = 3

    for i in range(retry_times):
        try:
            response = requests.post(url, json=one_data, headers=headers, timeout=timeout_seconds)
            # print(response)
            # print(response.headers)
            # print(response.status_code)
            # print(response.content)

            response_json = response.json()
            # print(response_json)

            if len(one_data['raw_str']) == len(response_json['mask_info']) or len(response_json['mask_info']) > 0:
                return response_json

        except Exception as e:
            import time
            app.logger.error(str(i + 1) + "回目のリトライ：PII MODULEの呼び出しが失敗になりなした。エラー情報は以下となる。")
            app.logger.error(e)
            app.logger.error("リクエスト用のJSONデータ：")
            app.logger.error(json.dumps(one_data))

            if i < (retry_times - 1):
                timeout_seconds += 20
                wait_seconds += 20
                # app.logger.info(str(wait_seconds) + "秒以降再度呼び出しを試す。")

            else:
                app.logger.error("PII MODULEの呼び出しが失敗になりなした。PII MODULEが動いていないあるいは接続できない状態になる可能性が高い")
                raise e
            time.sleep(wait_seconds)

    return None

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
    # POSTされたJSONを取得
    json = request.get_json()
    # リクエストデータのチェック
    msg_list = validate(json)
    if len(msg_list) > 0:
        result = {
            "message": msg_list[0]
        }
        return jsonify(result), 400
    else:
        value = {}
        for data in json:
            value[data['country'] + data['id']] = data['content'] # TODO valueのidの設定
            app.logger.info('country: %s , id: %s', data['country'], data['id'])

        request_data = {"raw_str": value}
        result = get_masking_data(request_data)
        return jsonify(result), 200

if __name__ == '__main__':
    app.debug = True
    # app.run(host='localhost', port=4000)
    app.run()