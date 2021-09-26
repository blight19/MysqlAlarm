import json

from alarm.engine import DBUtil
from alarm.get_params import all_funcs
from handler.dingding.dingding import ding

if __name__ == '__main__':
    with open("config.json", "r", encoding="utf-8") as f:
        configs = json.load(f)['databases']
    for config in configs:
        user = config.get("user")
        passwd = config.get("passwd")
        host = config.get("host")
        port = config.get("port")
        slaves = config.get("slaves")
        tags = config.get("tags")
        my_functions = ["disk"]
        my_func_dic = {name: all_funcs.get(name) for name in my_functions}
        with DBUtil(user=user, passwd=passwd, host=host, port=port, slaves=slaves,
                    alarm_handler=ding, tags=tags,funcs=my_func_dic) as client:
            client.run()
