# MysqlAlarm
mysql 报警
## 使用方法

```python
import json

from alarm.engine import DBUtil
from alarm.get_params import all_funcs
from handler.dingding.dingding import ding
from logger.logger import Logger

if __name__ == '__main__':
    my_logger = Logger(stream=True,file=True).get_logger()
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
                    alarm_handler=ding, tags=tags,logger=my_logger,
                    # funcs=my_func_dic
                    ) as client:
            client.run()


```
可以根据名称选择需要的监控参数
## Logger选择
可选择stream和file两种handler file handler 默认文件名为当前日期.log  
默认选择的default_logger选择的是stream handler  
如选择file handler
```python
from logger.logger import Logger
file_logger = Logger(stream=False,file=True).get_logger()
```
并将file_logger传入DBUtil中
## 扩展
### 通知
在handler中可以编写自己的通知函数，接收参数有(host, parameter, current, threshold, th_type,tags)
扩展参照dingding

### 添加监控参数
可以在get_params.py中添加自己需要的参数，示例如下：
```python
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
```
函数会自动进行调用
