from alarm.alarm import DBUtil
from handler.dingding.dingding import ding
import json

if __name__ == '__main__':
    with open("config.json","r") as f:
        config = json.load(f)
    user = config.get("user")
    passwd = config.get("passwd")
    host = config.get("host")
    port = config.get("port")
    slaves = config.get("slaves")

    with DBUtil(user=user, passwd=passwd, host=host, port=port, slaves=slaves,
                alarm_handler=ding) as client:
        client.run()