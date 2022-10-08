---
title: "Python 装饰器杂录"
categories: Tech
updated:
comments: true
mathjax: false
---

装饰器基础, 以及常用装饰器略了, 比如 `staticmethod`, `classmethod`, `property`, `functools.lru_cache`.

<!-- more -->

## Some builtin decorators

### typing.final

[官方文档](https://docs.python.org/3/library/typing.html#typing.final), New in version 3.8.

类似 C++ 或 Java 的 `final`.

> A decorator to indicate to type checkers that the decorated method cannot be overridden, and the decorated class cannot be subclassed.

比如 [pandas/core/groupby/groupby.py](https://github.com/pandas-dev/pandas/blob/main/pandas/core/groupby/groupby.py) 用到了, 很多其他库也会用到.

### typing.overload

[官方文档](https://docs.python.org/3/library/typing.html#typing.overload).

仅仅用来做 type hint. 严格使用 type annotation 时, 如果对不同的输入类型, 输出类型不同, 可以用这个装饰器. 用法参考 [Python Type Hints - How to Use @overload - Adam Johnson](https://adamj.eu/tech/2021/05/29/python-type-hints-how-to-use-overload/). 比如 [locust/user/task.py](https://github.com/locustio/locust/blob/master/locust/user/task.py#L44-L54) 用到了这个.

```python
@overload
def task(weight: TaskT) -> TaskT:
    ...


@overload
def task(weight: int) -> Callable[[TaskT], TaskT]:
    ...


def task(weight: Union[TaskT, int] = 1) -> Union[TaskT, Callable[[TaskT], TaskT]]:
    # 实际实现
```

如果真的要 "重载" Python 的函数, 可以参考 [The Correct Way to Overload Functions in Python](https://martinheinz.dev/blog/50), 用第三方 multipledispatch 库. 不过感觉没必要. Python 内置有 [`functools.singledispatch`](https://docs.python.org/3/library/functools.html#functools.singledispatch), 暂时没见到很好的用例.

## Write a decorator with optional arguments

目标是即可以写成 `@dec` 也可以写成 `@dec(param=...)`. 基本写法是

```python
import functools


def decorator(func=None, param=None):
    if func is None:
        return functools.partial(decorator, param=param)

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if param:
            pass
        result = func(*args, **kwargs)
        return result

    return wrapper
```

更完整的例子可以见我写的 [计时器装饰器](https://gist.github.com/Shiina18/fc61009bcc10b0b6d760352dfb4175e5). 参考了 

- Bob Belderbos. (2017). [How to Write a Decorator with an Optional Argument?](https://pybit.es/articles/decorator-optional-argument/)

很多库也会实现带参数的装饰器, 用到的 trick 也差不多.

## Some Pandas decorators

TODO.

见 [pandas/util/_decorators.py](https://github.com/pandas-dev/pandas/blob/main/pandas/util/_decorators.py), 选几个.

比如 `doc` 装饰器, 配合 [`textwrap.dedent`](https://docs.python.org/3/library/textwrap.html#textwrap.dedent) 可以让多行字符串更易读.

**其他**

- [你写过哪些真正生产可用的 Python 装饰器?](https://www.zhihu.com/question/350078061)