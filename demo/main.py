import json

from alarm.engine import Alarmer
from alarm.get_params import all_funcs
from handler import dingding_handler, mail_handler
from logger.logger import Logger

if __name__ == '__main__':
    my_logger = Logger(stream=True, file=True).get_logger()
    with open("config.json", "r", encoding="utf-8") as f:
        configs = json.load(f)['databases']
    for config in configs:
        user = config.get("user")
        passwd = config.get("passwd")
        host = config.get("host")
        port = config.get("port")
        slaves = config.get("slaves")
        tags = config.get("tags")
        my_functions = ["disk", "thread_connect", "innodb_buffer_hint_precent"]
        my_func_dic = {name: all_funcs.get(name) for name in my_functions}
        with Alarmer(user=user, passwd=passwd, host=host, port=port, slaves=slaves,
                     alarm_handler=[mail_handler, dingding_handler], tags=tags, logger=my_logger,
                     funcs=my_func_dic
                     ) as client:
            client.run()
