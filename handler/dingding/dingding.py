import base64
import hashlib
import hmac
import json
import time
import urllib.parse
from pathlib import Path

import requests

file_path = Path(__file__).parent

with open(file_path.joinpath("conf.json"), 'rb') as f:
    conf = json.load(f)

headers = {
    'Content-type': 'application/json'
}

secret = conf.get("secret")
url_prefix = conf.get("url")


def ding(host, parameter, current, threshold, th_type,tag):
    timestamp = str(round(time.time() * 1000))
    secret_enc = secret.encode('utf-8')
    string_to_sign = '{}\n{}'.format(timestamp, secret)
    string_to_sign_enc = string_to_sign.encode('utf-8')
    hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
    sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
    url = f"{url_prefix}&timestamp={timestamp}&sign={sign}"

    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": "报警信息",
            "text": f"#### 报警信息 \n > "
                    f"##### Tag:{tag}\n >"
                    f"##### Host:{host}\n >"
                    f"##### Param:{parameter}\n >"
                    f"##### Current Value:{current}\n >"
                    f"##### Alarm Threshold: {th_type} {threshold}\n >"
                    f"##### Time: {time.strftime('%m-%d %H:%M:%S')}\n >"
            # "> ![screenshot](https://img.alicdn.com/tfs/TB1NwmBEL9TBuNjy1zbXXXpepXa-2400-1218.png)\n"

        },
        "at": {
            # "atMobiles": [],
            # "atUserIds": [],
            "isAtAll": False
        }
    }

    requests.post(url, data=json.dumps(data), headers=headers)


if __name__ == '__main__':
    host = "1.1.1.1"
    parameter = "Table_open_cache_hits_precent"
    current = "58.59"
    threshold = "80"
    th_type = "lt "
    ding(host, parameter, current, threshold, th_type=th_type)
