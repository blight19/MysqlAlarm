import json

from alarm.engine import DBUtil
from handler.dingding.dingding import ding

if __name__ == '__main__':
    with open("config.json","r",encoding="utf-8") as f:
        config = json.load(f)
    user = config.get("user")
    passwd = config.get("passwd")
    host = config.get("host")
    port = config.get("port")
    slaves = config.get("slaves")
    tags = config.get("tags")

    with DBUtil(user=user, passwd=passwd, host=host, port=port, slaves=slaves,
                alarm_handler=ding,tags=tags) as client:
        client.run()