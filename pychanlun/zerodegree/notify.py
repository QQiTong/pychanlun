# -*- coding: utf-8 -*-

import json
import requests
import traceback
import logging
import os

DING_TALK_WEB_HOOK = "https://oapi.dingtalk.com/robot/send?access_token=ed114ee425e559087807042af1d8e141c73b3bd37b0ff634a435959e9eb7e2f6"


def send_ding_message(content):
    # noinspection PyBroadException
    try:
        url = os.environ.get("DING_TALK_WEB_HOOK") if os.environ.get("DING_TALK_WEB_HOOK") is not None else DING_TALK_WEB_HOOK
        data = {
            "msgtype": "text",
            "text": {"content": content},
        }
        headers = {'Content-Type': 'application/json'}
        requests.post(url, data=json.dumps(data), headers=headers)
    except BaseException as e:
        logging.error("Error Occurred: {0}".format(traceback.format_exc()))
