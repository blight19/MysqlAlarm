#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:yanshushuang
# datetime:2021/9/26

def get_mysql_disk(db):
    # 占用空间
    db.dict_cursor.execute(
        "select TABLE_SCHEMA, concat(truncate(sum(data_length)/1024/1024,2)) as data_size,concat(truncate(sum("
        "index_length)/1024/1024,2)) as index_size from information_schema.tables group by TABLE_SCHEMA,"
        "data_length,index_length order by data_length desc;")
    res = db.dict_cursor.fetchall()
    data_size = sum([float(x["data_size"]) for x in res if x["data_size"] is not None])
    index_size = sum([float(x["index_size"]) for x in res if x["index_size"] is not None])
    db.params.update({"Size": round((data_size + index_size), 2)})


get_mysql_disk.name = "disk"


def get_mysql_thread_connect(db):
    # 连接数
    db.dict_cursor.execute("show global status like 'Threads_connected'")
    threads_connected = int(db.dict_cursor.fetchone().get("Value"))
    db.params.update({"Threads_connected": threads_connected})


get_mysql_thread_connect.name = "thread_connect"


def get_mysql_table_open_cache_hits_precent(db):
    # 表缓存命中率
    db.dict_cursor.execute("show global status like 'table_open_cache_hits'")
    table_open_cache_hits = int(db.dict_cursor.fetchone().get("Value"))

    db.dict_cursor.execute("show global status like 'table_open_cache_misses'")
    table_open_cache_misses = int(db.dict_cursor.fetchone().get("Value"))

    table_open_cache_hits_precent = table_open_cache_hits / (table_open_cache_misses + table_open_cache_hits)
    db.params.update({"Table_open_cache_hits_precent": round(table_open_cache_hits_precent * 100, 2)})


get_mysql_table_open_cache_hits_precent.name = "table_open_cache_hits_precent"


def get_mysql_innodb_buffer_hint_precent(db):
    # buffer缓冲命中率

    db.dict_cursor.execute("show global status like 'innodb_buffer_pool_reads'")
    innodb_buffer_pool_reads = int(db.dict_cursor.fetchone().get("Value"))

    db.dict_cursor.execute("show global status like 'innodb_buffer_pool_read_requests'")
    buffer_pool_read_requests = int(db.dict_cursor.fetchone().get("Value"))

    innodb_buffer_hint_precent = (buffer_pool_read_requests - innodb_buffer_pool_reads) / buffer_pool_read_requests
    db.params.update({"Innodb_buffer_hint_precent": round(innodb_buffer_hint_precent * 100, 2)})


get_mysql_innodb_buffer_hint_precent.name = "innodb_buffer_hint_precent"


def get_mysql_trans_time(db):
    # 事务运行时间
    db.dict_cursor.execute("SELECT TIME_TO_SEC(timediff( now(), trx_started )) AS "
                           "'trans_time' FROM information_schema.innodb_trx "
                           "ORDER BY TIME_TO_SEC(timediff( now(), trx_started )) DESC;")
    trans = db.dict_cursor.fetchone()
    if trans:
        db.params.update({"Trans_time": trans.get("trans_time")})
    else:
        db.params.update({"Trans_time": 0})


get_mysql_trans_time.name = "trans_time"


def get_mysql_innodb_buffer_pool_wait_free(db):
    # 缓冲池等待空闲页的次数
    db.dict_cursor.execute("show global status  LIKE 'Innodb_buffer_pool_wait_free';")
    value = db.dict_cursor.fetchone().get("Value")
    db.params.update({"Innodb_buffer_pool_wait_free": int(value)})


get_mysql_innodb_buffer_pool_wait_free.name = "innodb_buffer_pool_wait_free"


def get_mysql_innodb_lock_waits(db):
    # 数据库锁等待
    db.dict_cursor.execute("select version();")
    version = db.dict_cursor.fetchone().get("version()").split(".")[0]
    if version == "8":
        db.dict_cursor.execute("select COUNT(locked_table) as 'lock_waits' "
                               "from sys.innodb_lock_waits where blocking_lock_id is not null;")
        value = db.dict_cursor.fetchone().get("lock_waits")
    elif version == "5":
        db.dict_cursor.execute("SELECT count(*) as 'lock_waits' FROM information_schema.innodb_lock_waits w "
                               "INNER JOIN information_schema.innodb_trx b  "
                               "ON b.trx_id = w.blocking_trx_id INNER JOIN information_schema.innodb_trx r "
                               "ON r.trx_id = w.requesting_trx_id INNER JOIN information_schema.innodb_locks bl "
                               "ON bl.lock_id = w.blocking_lock_id INNER JOIN information_schema.innodb_locks rl "
                               "ON rl.lock_id = w.requested_lock_id; ")
        value = db.dict_cursor.fetchone().get('lock_waits')
    else:
        raise Exception("Version is neither 5 nor 8")
    db.params.update({"Lock_waits": int(value)})


get_mysql_innodb_lock_waits.name = "lock_waits"

all_funcs = {globals()[name].name: globals()[name] for name in globals() if name.startswith("get_mysql")}
