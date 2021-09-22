import pymysql
import logging

logger = logging.getLogger("Alarm Logger")
formatter = logging.Formatter("%(asctime)s - %(levelname)s: %(message)s")
sh = logging.StreamHandler()
sh.setFormatter(formatter)
logger.addHandler(sh)
logger.setLevel(logging.INFO)

# 参数为报警参数
CHECK_PARAMS = {
    "Size": {"type": "skip", "value": None},
    "Threads_connected": {"type": "gt", "value": 80},
    "Table_open_cache_hits_precent": {"type": "lt", "value": 80},
    "Innodb_buffer_hint_precent": {"type": "lt", "value": 80},
}

SLAVE_CHECK_PARAMS = {
    "Size": {"type": "skip", "value": None},
    "Threads_connected": {"type": "gt", "value": 80},
    "Table_open_cache_hits_precent": {"type": "lt", "value": 80},
    "Innodb_buffer_hint_precent": {"type": "lt", "value": 80},
    "Slave_IO_Running": {"type": "uneq", "value": 'Yes'},
    "Slave_SQL_Running": {"type": "uneq", "value": 'Yes'},
    "Seconds_Behind_Master": {"type": "gt", "value": 20},
}


class DBUtil:
    def __init__(self, user=None, passwd=None, host=None, port=None, tags=None, slaves=None, alarm_handler=print,
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

    def __enter__(self):
        self._conn = pymysql.connect(host=self.host, port=self.port, user=self.user, passwd=self.passwd)
        self._cursor = self._conn.cursor()
        self._dict_cursor = self._conn.cursor(pymysql.cursors.DictCursor)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
        self._conn = None

    def get_mysql_disk(self):
        # 占用空间
        self._dict_cursor.execute(
            "select TABLE_SCHEMA, concat(truncate(sum(data_length)/1024/1024,2)) as data_size,concat(truncate(sum("
            "index_length)/1024/1024,2)) as index_size from information_schema.tables group by TABLE_SCHEMA,"
            "data_length,index_length order by data_length desc;")
        res = self._dict_cursor.fetchall()
        data_size = sum([float(x["data_size"]) for x in res if x["data_size"] is not None])
        index_size = sum([float(x["index_size"]) for x in res if x["index_size"] is not None])
        self.params.update({"Size": round((data_size + index_size), 2)})

    def get_mysql_thread_connect(self):
        # 连接数
        self._dict_cursor.execute("show global status like 'Threads_connected'")
        threads_connected = int(self._dict_cursor.fetchone().get("Value"))
        self.params.update({"Threads_connected": threads_connected})

    def get_mysql_table_open_cache_hits_precent(self):
        # 查询命中率
        self._dict_cursor.execute("show global status like 'table_open_cache_hits'")
        table_open_cache_hits = int(self._dict_cursor.fetchone().get("Value"))

        self._dict_cursor.execute("show global status like 'table_open_cache_misses'")
        table_open_cache_misses = int(self._dict_cursor.fetchone().get("Value"))

        table_open_cache_hits_precent = table_open_cache_hits / (table_open_cache_misses + table_open_cache_hits)
        self.params.update({"Table_open_cache_hits_precent": round(table_open_cache_hits_precent * 100, 2)})

    def get_mysql_undo_log(self):
        # 8版本没有
        pass

    def get_mysql_slave_status(self):
        # 获取slave状态

        for slave in self.slaves:
            with Slave(user=self.user, passwd=self.passwd, host=slave, port=3306,
                       master_host=self.host, alarm_handler=self.alarm_handler) as slave_client:

                if self.params.get("Slaves") is None:
                    self.params.update({"Slaves": []})
                self.params.get("Slaves").append(slave_client.run())

    def get_mysql_innodb_buffer_hint_precent(self):
        # 查询命中率

        self._dict_cursor.execute("show global status like 'innodb_buffer_pool_reads'")
        innodb_buffer_pool_reads = int(self._dict_cursor.fetchone().get("Value"))

        self._dict_cursor.execute("show global status like 'innodb_buffer_pool_read_requests'")
        buffer_pool_read_requests = int(self._dict_cursor.fetchone().get("Value"))

        innodb_buffer_hint_precent = (buffer_pool_read_requests - innodb_buffer_pool_reads) / buffer_pool_read_requests
        self.params.update({"Innodb_buffer_hint_precent": round(innodb_buffer_hint_precent * 100, 2)})

    def get_all_params(self):
        funcs = filter(lambda m: m.startswith("get_mysql") and callable(getattr(self, m)), dir(self))
        for i in funcs:
            getattr(self, i)()

    def run(self):
        self.get_all_params()
        self.check_threshold()

    def check_threshold(self):
        # slave参数检查和报警在子类中单独处理
        if "Slaves" in self.params:
            self.params.pop("Slaves")

        for k, v in self.check_params.items():
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
                logger.error("Check Type Not Exist:", check_type)
            if alarm_flag != "":
                self.alarm(self.alarm_handler, k, current_value, th_value, alarm_flag)

    def alarm(self, handler, key, current, th, th_type):
        handler(self.host, key, current, th, th_type)


class Slave(DBUtil):
    def __init__(self, user=None, passwd=None, host=None, port=None, master_host=None, tags=None, alarm_handler=print):
        super(Slave, self).__init__(user=user, passwd=passwd, host=host, port=port, tags=tags,
                                    alarm_handler=alarm_handler)
        self.master_host = master_host
        self.check_params = SLAVE_CHECK_PARAMS

    def get_mysql_slave_status(self):
        self._dict_cursor.execute("show slave status")
        results = self._dict_cursor.fetchall()
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
        self.check_threshold()
        return self.params


def my_handler(host, key, current, th, th_type):
    logger.warning(f"-----[{host} {key} current value:{current},already {th_type} {th}]")

