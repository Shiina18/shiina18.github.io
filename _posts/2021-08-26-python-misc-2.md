---
title: "Python 杂录 2: 最佳实践"
categories: Tech
updated: 2022-04-07
comments: true
mathjax: false
---

由于历史遗留原因, 第一篇 [Python 杂录](https://shiina18.github.io/language/2020/05/30/python-misc/) 放在了 Language 类别下. 第二篇 Python 杂录更偏重 best practices.

<!-- more -->

## import

推荐文章 [The Definitive Guide to Python import Statements](https://chrisyeh96.github.io/2017/08/08/definitive-guide-python-imports.html), 下面是一些摘录.

- `import` statements search through the list of paths in `sys.path`.
- `sys.path` always includes the path of the script invoked on the command line and is agnostic to the working directory on the command line.
- importing a package is conceptually the same as importing that package’s `__init__.py` file. 一些例子: [`scikit-learn/sklearn/linear_model/__init__.py`](https://github.com/scikit-learn/scikit-learn/blob/main/sklearn/linear_model/__init__.py), 在 linear_model 文件夹中定义了很多私有 py 文件, 最后将 linear_model 作为模块导入, 把要用的东西塞在 init 文件里供调用.

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

补充 (2021/9/13) : Python 3.4 的 enum 好像也能做到类似的事情, 参考 [http.HTTPStatus 的实现](https://github.com/python/cpython/blob/3.9/Lib/http/__init__.py), 非常巧妙. 注意到 [enum 的源码](https://github.com/python/cpython/blob/3.9/Lib/enum.py#L792) 中有这么一段, http 的实现里是在类中定义 `_value_` 最后再以 `value` 访问.

```python
@DynamicClassAttribute
def name(self):
    """The name of the Enum member."""
    return self._name_

@DynamicClassAttribute
def value(self):
    """The value of the Enum member."""
    return self._value_
```

补充 (2022/4/7): namedtuple 的优势见 [data-classes-vs-typing-namedtuple-primary-use-cases](https://stackoverflow.com/questions/51671699/data-classes-vs-typing-namedtuple-primary-use-cases)

其他可参考的文章: [Configuration Files in Python using dataclasses \| True Analytics Tech](https://tech.trueanalytics.ai/posts/dataconf-at-tdg/)

## logging

主要参考 [Good logging practice in Python](https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/), 现在自用的代码也基本抄的这个. 此外, [Python logging 较佳实践](https://zhuanlan.zhihu.com/p/275706374) 这篇也可以. 基础从略.

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

其中 `logging.getLogger(name=__name__)` 表示获取 **名 (name)** 为 `__name__` 的 logger. 对于 my_module.py, `__name__` 为 utils.my_module (等价于 `logging.getLogger('utils.my_module')`), 对应 formatter 中的 %(name)s, 而 %(module)s 则为 my_module.

上面的配置定义了名为 root 和 utils 的 logger. 不同的 logger 之间存在树状的层级关系, 根部名为 root, 名字形如 utils.my_module 的 logger (上面没有定义, 但可以定义) 的父结点是名为 utils 的 logger, 而 utils 的父结点是 root. 如果 utils 的 propagate 为 true, 则除了这个 utils logger 配置的 handlers, 它还会把信息交给 (propagate, 默认为 true) 父结点 root logger 的 handlers, 详情参见 [logger 和 handler 的关系](https://docs.python.org/3/howto/logging.html#logging-flow). 

> Child loggers propagate messages up to the handlers associated with their ancestor loggers. Because of this, it is unnecessary to define and configure handlers for all the loggers an application uses. It is sufficient to configure handlers for a top-level logger and create child loggers as needed.

对于 my_module 而言, `logging.getLogger(__name__)` 获取名为 utils.my_module 的 logger. 因为没有配置同名 logger,  propagate 默认为 true, 所以将信息交给父结点 utils logger 的 handlers. 由于 utils 的 propagate 为 false, utils logger 的 handlers 处理完之后并不会把信息再交给父结点 root logger 的 handlers.

原始帖子里的 root logger 的 console handler 会输出 debug 信息, 而有些第三方模块的 debug 信息太多了, 所以上面把 console handler 的级别改成了 info. 上面定义的 utils logger 只会输出自己 utils 文件夹中模块定义的 debug 信息, 而不会输出第三方库的 debug 信息 (除非第三方库的名字恰好可以 propagate 到自己定义的 logger). 

比如 [kafka.producer.kafka 的源码](https://kafka-python.readthedocs.io/en/master/_modules/kafka/producer/kafka.html#KafkaProducer) 和 [kafka.conn 的源码](https://github.com/dpkp/kafka-python/blob/f19e4238fb47ae2619f18731f0e0e9a3762cfa11/kafka/conn.py), 在开头定义 `log = logging.getLogger(__name__)`, 可以参考它正文的 log 写法.

另外有篇巨长的文章 [Python Logging Guide – Best Practices and Hands-on Examples](https://coralogix.com/blog/python-logging-best-practices-tips/) 还没读.

### 更多自定义

2021/9/25

根据日志格式要求自定义, 在一堆以竖线分隔的信息最后, 用 JSON 格式输出其他信息, 例如

```
2021-09-25 12:06:42.736|INFO|MainProcess-10960|7|module_dir.random_module:{"message": "Json format"}
2021-09-25 12:06:42.737|ERROR|MainProcess-10960|21|__main__:
{"message": "233", "exc_info": "Traceback (most recent call last):\n  File \"D:\\PycharmProjects\\DemoLogger\\main.py\", line 19, in <module>\n    1 / 0\nZeroDivisionError: division by zero"}
```

```python
# configs/__init__.py
import json
import logging


class JsonMessageFormatter(logging.Formatter):
    def format(self, record):
        message_dict = {'message': record.getMessage()}
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        if record.exc_info:
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            message_dict['exc_info'] = record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            message_dict['stack_info'] = self.formatStack(record.stack_info)
        return s + json.dumps(message_dict)
```

配置方法参考 [官方文档](https://docs.python.org/3/library/logging.config.html#user-defined-objects). 在配置文件的 formatters 中加入

```json
"json": {
  "()": "configs.JsonMessageFormatter",
  "format": "%(asctime)s.%(msecs)03d|%(levelname)s|%(processName)s-%(process)d|%(lineno)s|%(name)s:",
  "datefmt": "%Y-%m-%d %H:%M:%S"
}
```

在 handlers 中需要的地方将 formatter 替换为 "json". 在主程序中 `import configs`, 详见 [示例](https://github.com/Shiina18/DemoLogger).

下面是一些暂时没有用到的自定义例子.

- Masnun. (2015, Nov 4). [Python: writing custom log handler and formatter](https://masnun.com/2015/11/04/python-writing-custom-log-handler-and-formatter.html) [Blog post]. *Abu Ashraf Masnun*.
- Ward. B. (2018, Sep 1). [Python Custom Logging Handler Example](https://dzone.com/articles/python-custom-logging-handler-example). *DZone*.

此外还有一个专门的库 [python-json-logger](https://github.com/madzak/python-json-logger), 不过这次用不到.

## pytest and assert

2022/3/15

比原生的 unittest 方便.

遇到 ModuleNotFoundError, 可以尝试在 tests 目录下加上 `__init__.py`, 参考 [这个回答](https://stackoverflow.com/questions/54895002/modulenotfounderror-with-pytest). 我自己是参考 [sklearn 的格式](https://github.com/scikit-learn/scikit-learn/blob/1fc86b6aacd89da44a3b4e8abf7c3e2ba4336ffe/sklearn/datasets/tests/test_samples_generator.py) 写的.

注意 assert 在平时的代码中是可以 disable 掉的, 参考 [RealPython 的介绍](https://realpython.com/python-assert-statement/#disabling-assertions-in-production-for-performance), 因此在代码中也不应该 except AssertionError.
