---
title: "SQLAlchemy 简要"
categories: Tech
updated: 
comments: true
mathjax: false
---

```python
import urllib.parse

import sqlalchemy

password = ...
# escaping special characters such as @ signs
password = urllib.parse.quote_plus(password)
url = f'dialect+driver://username:{password}@host:port/database'
engine = sqlalchemy.create_engine(url)  # Engine object

with engine.connect() as conn:
    results = conn.execute('SELECT * FROM students')
    for row in results:
        print(row)
```

<!-- more -->

根据 [官方文档](https://docs.sqlalchemy.org/en/14/core/connections.html#basic-usage), The Engine is **not** synonymous to the DBAPI connect function, which represents just one connection resource - the Engine is most efficient when created just once at the module level of an application, not per-object or per-function call.

>  The `Engine` is a *factory* for connections as well as a *pool* of connections, not the connection itself. When you say `conn.close()`, the connection is *returned to the connection pool within the Engine*, not actually closed.

`engine.dispose()` 参考 [官方文档](https://docs.sqlalchemy.org/en/14/core/connections.html#engine-disposal).

`engine.connect()` 返回一个 `Connection` 对象.

```python
# engine/base.py

class Connection(Connectable):
    def __exit__(self, type_, value, traceback):
        self.close()
```

关于 `engine.execute(...)`, `engine.connect()`, `Session` 的区别, 参考 [这里](https://stackoverflow.com/questions/34322471/sqlalchemy-engine-connection-and-session-difference). 

- `engine.execute(...)` 其实内部先创建 `engine.connect()`, 执行完后再关闭. 不过 pandas 的 `read_sql` 内部不会关闭, 参考 [这里](https://stackoverflow.com/questions/42034373/does-pandas-need-to-close-connection/42034432).
- `Session` 用来做 Object Relationship Management (ORM).

ORM 是用面向对象的方式操作数据库, 使得对所有支持的数据库类型都能用相同的代码. 教程参考 [官方文档](https://docs.sqlalchemy.org/en/14/orm/tutorial.html) (但总体而言官方文档写得太长了, 见 [为什么很多人都喜欢 Django 的 ORM 而不是 SQLAlchemy](https://www.zhihu.com/question/19959765/answer/28233183)), 稳定版是 1.4, 最近已经有 2.0 beta 了, 只保留了核心操作. (我没看过)

参考

- [How to Execute Raw SQL in SQLAlchemy \| Tutorial by Chartio](https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/)
- [How to close sqlalchemy connection in MySQL - Stack Overflow](https://stackoverflow.com/questions/8645250/how-to-close-sqlalchemy-connection-in-mysql)
- [python - SQLAlchemy Core Connection Context Manager - Stack Overflow](https://stackoverflow.com/questions/17497614/sqlalchemy-core-connection-context-manager)
