---
title: "Python 杂录 2: 最佳实践"
categories: Tech
updated: 
comments: true
mathjax: false
---

由于历史遗留原因, 第一篇 [Python 杂录](https://shiina18.github.io/language/2020/05/30/python-misc/) 放在了 Language 类别下. 第二篇 Python 杂录更偏重 best practices.

<!-- more -->

## import

推荐文章 [The Definitive Guide to Python import Statements](https://chrisyeh96.github.io/2017/08/08/definitive-guide-python-imports.html), 下面是一些摘录.

- `import` statements search through the list of paths in `sys.path`.
- `sys.path` always includes the path of the script invoked on the command line and is agnostic to the working directory on the command line.
- importing a package is conceptually the same as importing that package’s `__init__.py` file. 一些例子: [`scikit-learn/sklearn/linear_model/__init__.py`](https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/linear_model/__init__.py)

关于从别的文件夹导入

- The only acceptable syntax for relative imports is `from .[module] import name`. All import forms not starting with . are interpreted as absolute imports.
- If we do not modify `PYTHONPATH` and avoid modifying `sys.path` programmatically, then the following is a major limitation of Python imports: **When running a script directly, it is impossible to import anything from its parent directory.**
- My approach is to avoid writing scripts that have to import from the parent directory. In cases where this must happen, the preferred workaround is to modify `sys.path`.

## 用 pathlib 替换 os.path

虽然 `pathlib` 相比 `os.path` 并没有更简洁, 但是参考 [这里](https://zhuanlan.zhihu.com/p/87940289) 下面的评论, 它

> 提供了对资源路径和资源命名结构的通用抽象, 把文件系统接口从 os 模块中隔离出来, 打开了从应用层配置文件系统的大门. 换句话说, Path 这个接口代表的可以不仅是 os 的资源路径, 还可以是 HDFS 的资源路径, RESTful API 的资源路径, 某种内存文件系统的资源路径等等.
>
>设想你的应用完全合理地基于 Path 的接口来写, 然后某天你需要把应用存储迁移到 HDFS 上去, 结果你发现几乎只要把 from pathlib import Path 换成 from myhdfslib import Path, 业务代码不用变就可以工作.

一个迁移 cheatsheet: [Migrating from OS.PATH to PATHLIB Module in Python](https://amitness.com/2019/12/migrating-to-pathlib/)

## 用 dataclass 写配置文件

最佳实践参考了 [Best Practices for Working with Configuration in Python Applications](https://tech.preferred.jp/en/blog/working-with-configuration-in-python/).

下面是习见的读取配置文件参数的方式.

```python
start_server(port=os.environ.get("PORT", 80))  # wrong type if PORT is present

server_timeout_ms = config["timeout"] * 1000  # let's hope it's not a string

database_timeout = config["timeout"]  # reuse config key in different context

if has_failed() and config["vrebose"]:  # typo will show only on failure
    logger.warning("something has failed")
```

要解决上述问题, 配置文件应当

- It should use identifiers rather than string keys to access configuration values. 避免拼写错误, IDE 还可以方便地提醒我们有哪些参数可用. 比如用 dataclasses.dataclass, 由 3.7 正式引入, [3.6 可以 pip 安装](https://pypi.org/project/dataclasses/). 参考 [Data Classes in Python 3.7+ (Guide)](https://realpython.com/python-data-classes/) (注意比较 [namedtuple](https://dbader.org/blog/writing-clean-python-with-namedtuples)), 其中这个网站 Real Python 提供了许多高质量的 Python 介绍. 
- Its values should be statically typed. For example, when you have a configuration entry referencing a file, use a `pathlib.Path` rather than `str` and avoid having to deal with strings that are not valid file names.
    - One additional thing to consider, in particular when dealing with physical dimensions like duration, weight, distance, speed etc., is to abstract away the concrete unit and work with the dimension instead. For example, rather than declaring a configuration entry like, say, `check_interval_s: float` or `check_interval_ms: int`, declare it like `check_interval: datetime.timedelta`. You can then write most of your code in terms of these dimensions, calculate with them on an abstract level, and only convert them into a concrete value when working with external libraries, for example when calling `time.sleep(check_interval.total_seconds())`.
- It should be validated early. I would advise to validate the configuration as soon as possible after program startup, and exit immediately if it is found to be invalid.
- It should be declared close to where it is used.

另外顺便一提, 关于项目组织结构, 当年给我启蒙的是 [Cookiecutter Data Science](https://drivendata.github.io/cookiecutter-data-science/). 虽然没有用它的包, 但是大致结构参考了它的.

## logging

主要参考 [Good logging practice in Python](https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/), 现在自用的代码也基本抄的这个. 此外, [Python logging 较佳实践](https://zhuanlan.zhihu.com/p/275706374) 这篇也可以.

配置文件 `log_config.json`

```json
{
  "version": 1,
  "disable_existing_loggers": false,
  "formatters": {
    "simple": {
      "format": "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    }
  },
  "handlers": {
    "console": {
      "class": "logging.StreamHandler",
      "level": "INFO",
      "formatter": "simple",
      "stream": "ext://sys.stdout"
    },
    "info_file_handler": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "INFO",
      "formatter": "simple",
      "filename": "info.log",
      "maxBytes": 1000000,
      "backupCount": 1,
      "encoding": "utf8"
    },
    "error_file_handler": {
      "class": "logging.handlers.RotatingFileHandler",
      "level": "ERROR",
      "formatter": "simple",
      "filename": "errors.log",
      "maxBytes": 1000000,
      "backupCount": 1,
      "encoding": "utf8"
    },
    "debug_console": {
      "class": "logging.StreamHandler",
      "level": "DEBUG",
      "formatter": "simple",
      "stream": "ext://sys.stdout"
    }
  },
  "loggers": {
    "utils": {
      "level": "NOTSET",
      "handlers": [
        "debug_console",
        "info_file_handler",
        "error_file_handler"
      ],
      "propagate": false
    }
  },
  "root": {
    "level": "NOTSET",
    "handlers": [
      "console",
      "info_file_handler",
      "error_file_handler"
    ]
  }
}
```

在主程序导入配置, 定义模块级变量 logger.

```python
with open(pathlib.Path('configs/log_config.json')) as f:
    logging.config.dictConfig(json.load(f))
logger = logging.getLogger(__name__)
```

在其他被导入的子模块同样定义模块级的 `logger = logging.getLogger(__name__)`.

假设文件结构为

```
- main.py
- utils
    - my_module.py
```

其中 `logging.getLogger(name=__name__)` 表示获取名为 `__name__` 的 logger. 对于 my_module.py, `__name__` 为 utils.my_module, 对应 formatter 中的 %(name)s, 而 %(module)s 则为 my_module.

上面的配置定义了名为 root 和 utils 的 logger. 不同的 logger 之间存在树状的层次关系, 根部名为 root, 形如 utils.my_module 的 logger (上面没有定义, 但可以定义) 的父节点是 utils, 而 utils 的父节点是 root. 如果 utils 的 propagate 为 true, 则除了这个 utils logger 配置的 handlers, 它还会把信息交给父节点 root logger 配置的 handlers, 详情参见 [logger 和 handler 的关系](https://docs.python.org/3/howto/logging.html#logging-flow). 

对于 my_module 而言, `logging.getLogger(name=__name__)` 获取名为 utils.my_module 的 logger, 因为没有配置, 所以将信息交给父节点 utils logger 的 handlers, 由于 utils 的 propagate 为 false, utils logger 的 handlers 处理完之后并不会把信息再交给 root logger 的 handlers.

原始帖子里的 root logger 的 console handler 会输出 debug 信息, 而有些第三方模块的 debug 信息太多了, 所以上面把 console handler 的级别改成了 info. 上面定义的 utils logger 只会输出自己定义的 debug 信息, 而不会输出第三方库的 debug 信息 (除非第三方库的名字恰好可以 propagate 到自己定义的 logger). 

比如 [kafka.producer.kafka 的源码](https://kafka-python.readthedocs.io/en/master/_modules/kafka/producer/kafka.html#KafkaProducer), 在开头定义 `log = logging.getLogger(__name__)`, 可以参考它正文的 log 写法.

另外有篇巨长的文章 [Python Logging Guide – Best Practices and Hands-on Examples](https://coralogix.com/blog/python-logging-best-practices-tips/) 还没读.