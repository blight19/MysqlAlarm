#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:yanshushuang
# datetime:2021/9/26
# 参数为报警参数
CHECK_PARAMS = {
    "Size": {"type": "skip", "value": None},
    "Threads_connected": {"type": "gt", "value": 250},
    "Table_open_cache_hits_precent": {"type": "lt", "value": 80},
    "Innodb_buffer_hint_precent": {"type": "lt", "value": 80},
    "Trans_time": {"type": "gt", "value": 60},
    "Innodb_buffer_pool_wait_free": {"type": "gt", "value": 0},
    "Lock_waits": {"type": "gt", "value": 0},
}

SLAVE_CHECK_PARAMS = {
    "Size": {"type": "skip", "value": None},
    "Threads_connected": {"type": "gt", "value": 250},
    "Table_open_cache_hits_precent": {"type": "lt", "value": 80},
    "Innodb_buffer_hint_precent": {"type": "lt", "value": 80},
    "Trans_time": {"type": "gt", "value": 60},
    "Innodb_buffer_pool_wait_free": {"type": "gt", "value": 0},
    # "Lock_waits": {"type": "gt", "value": 0},#从节点不需要检测
    "Slave_IO_Running": {"type": "uneq", "value": 'Yes'},
    "Slave_SQL_Running": {"type": "uneq", "value": 'Yes'},
    "Seconds_Behind_Master": {"type": "gt", "value": 60},
}
