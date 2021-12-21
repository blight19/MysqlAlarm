import pymysql
from alarm.get_params import all_funcs
from alarm.threshold import SLAVE_CHECK_PARAMS, CHECK_PARAMS
from logger import default_logger
import sys
import traceback


class Alarmer:
    def __init__(self, user=None, passwd=None, host=None, port=None, tags=None,
                 slaves=None, alarm_handler=print,
                 funcs=all_funcs, logger=default_logger,
                 **kwargs):
        if slaves is None:
            self.slaves = []
        else:
            self.slaves = slaves
        self.user = user
        self.passwd = passwd
        self.host = host
        self.port = int(port)
        self.tags = tags
        self._conn = None
        self._cursor = None
        self.params = {}
        self.alarm_params = {}
        self.check_params = CHECK_PARAMS
        self.alarm_handler = alarm_handler
        self.funcs = funcs
        self.logger = logger

    def __enter__(self):
        try:
            self._conn = pymysql.connect(host=self.host, port=self.port,
                                         user=self.user, passwd=self.passwd,connect_timeout=10)
        except pymysql.err.OperationalError:
            self.logger.error(f"Connect Error:{self.host}:{self.user}")
            self.alarm(handler=self.alarm_handler, key="connection", current="offline",
                       th="online", th_type="eq", tag=self.tags)
        except Exception as e:
            self.logger.error(f"Connect Error:{self.host}:{self.user}")
            self.alarm(handler=self.alarm_handler, key="connection", current=e,
                       th="online", th_type="eq", tag=self.tags)
        self._cursor = self._conn.cursor()
        self.dict_cursor = self._conn.cursor(pymysql.cursors.DictCursor)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
        self._conn = None

    # def get_mysql_undo_log(self):
    #     # 8版本没有
    #     pass

    def get_mysql_slave_status(self):
        # 获取slave状态

        for slave in self.slaves:
            with Slave(user=self.user, passwd=self.passwd,
                       host=slave, port=3306, tags=self.tags, funcs=self.funcs,
                       master_host=self.host, alarm_handler=self.alarm_handler,logger=self.logger) as slave_client:

                if self.params.get("Slaves") is None:
                    self.params.update({"Slaves": []})
                self.params.get("Slaves").append(slave_client.run())

    def get_all_params(self):
        # funcs = filter(lambda m: m.startswith("get_mysql") and callable(getattr(self, m)), dir(self))

        for name, func in self.funcs.items():
            self.logger.debug(f"{self.host}--{name}--getting")
            func(self)
        self.get_mysql_slave_status()

    def run(self):
        self.get_all_params()
        self.logger.info(f"{self.host} ALL INFO :{self.params}")
        self.check_threshold()

    def th_run(self):
        self.__enter__()
        try:
            self.run()
        except Exception as e:
            exc_type, exc_value, exc_obj = sys.exc_info()
            s = traceback.format_tb(exc_obj)
            self.logger.error(f"{self.host} {s} {e} {exc_type}")
        self.__exit__(None, None, None)

    def check_threshold(self):
        # slave参数检查和报警在子类中单独处理
        if "Slaves" in self.params:
            self.params.pop("Slaves")

        for k, v in self.check_params.items():
            if k not in self.params:
                continue
            current_value = self.params.get(k)
            th_value = v.get("value")
            check_type = v.get("type")
            alarm_flag = ""
            if check_type == "skip":
                pass
            elif check_type == "gt":
                if current_value > th_value:
                    alarm_flag = check_type
            elif check_type == "lt":
                if current_value < th_value:
                    alarm_flag = check_type
            elif check_type == "eq":
                if current_value == th_value:
                    alarm_flag = check_type
            elif check_type == "uneq":
                if current_value != th_value:
                    alarm_flag = check_type
            else:
                self.logger.error("Check Type Not Exist:", check_type, self.host)
            if alarm_flag != "":
                self.alarm(self.alarm_handler, k, current_value,
                           th_value, alarm_flag, self.tags)

    def alarm(self, handler, key, current, th, th_type, tag):
        self.logger.debug(f"{tag}-{self.host}, {key}, {current}, {th}, {th_type}")
        if isinstance(handler, list):
            for h in handler:
                h(self.host, key, current, th, th_type, tag, self.logger)
        else:
            handler(self.host, key, current, th, th_type, tag, self.logger)


class Slave(Alarmer):
    def __init__(self, user=None, passwd=None, host=None, port=None,
                 master_host=None, tags=None, alarm_handler=print, funcs=all_funcs, logger=None):
        super(Slave, self).__init__(user=user, passwd=passwd, host=host, port=port, tags=tags,
                                    alarm_handler=alarm_handler, funcs=funcs, logger=logger)
        self.master_host = master_host
        self.check_params = SLAVE_CHECK_PARAMS

    def get_mysql_slave_status(self):
        self.dict_cursor.execute("show slave status")
        results = self.dict_cursor.fetchall()
        result = {}
        if len(results) > 1:
            for x in results:
                if x.get("Master_Host") == self.master_host:
                    result = x
        else:
            result = results[0]

        self.params.update({"Slave_IO_Running": result.get("Slave_IO_Running"),
                            "Slave_SQL_Running": result.get("Slave_SQL_Running"),
                            "Seconds_Behind_Master": result.get("Seconds_Behind_Master"),
                            })

    def run(self):
        self.get_all_params()
        self.logger.info(f"{self.host} ALL INFO :{self.params}")
        self.check_threshold()
        return self.params
