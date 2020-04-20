# -*- coding: utf-8 -*-

#!/usr/bin/python3
import json
import requests

class DingMsg:
    def send(self, msg):
        url = 'https://oapi.dingtalk.com/robot/send?access_token=39474549996bad7e584523a02236d69b68be8963e2937274e4e0c57fbb629477'
        program = {
            "msgtype": "text",
            "text": {"content": json.dumps(msg, ensure_ascii=False, indent=4)},
        }
        headers = {'Content-Type': 'application/json'}
        f = requests.post(url, data=json.dumps(program), headers=headers)
