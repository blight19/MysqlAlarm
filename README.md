# MysqlAlarm
mysql 报警
## 使用方法

```python
from alarm.alarm import DBUtil
from handler.dingding.dingding import ding
import json

if __name__ == '__main__':
    with open("config.json", "r") as f:
        config = json.load(f)
    user = config.get("user")
    passwd = config.get("passwd")
    host = config.get("host")
    port = config.get("port")
    slaves = config.get("slaves")

    with DBUtil(user=user, passwd=passwd, host=host, port=port, slaves=slaves,
                alarm_handler=ding) as client:
        client.run()
```
## 扩展
### 通知
在handler中可以编写自己的通知函数，接收参数有(host, parameter, current, threshold, th_type)
参照dingding
### 添加监控参数
可继承类DBUtil以后添加自己的方法，方法名需要以get_mysql为开头，
并在函数中将获取到的参数update到self.params
在__init__中初始化update所需要的函数阈值
