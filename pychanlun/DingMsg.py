# -*- coding: utf-8 -*-

#!/usr/bin/python3
import json
import requests

class DingMsg:
    def send(self, msg):
        url = 'https://oapi.dingtalk.com/robot/send?access_token=b53f9ce8d050ced9658be2bb5fb378e46a723debda17b8a7bc8d5cdb6991d651'
        program = {
            "msgtype": "text",
            "text": {"content": json.dumps(msg, ensure_ascii=False, indent=4)},
        }
        headers = {'Content-Type': 'application/json'}
        f = requests.post(url, data=json.dumps(program), headers=headers)
