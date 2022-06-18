---
title: "Python 第三方库杂录"
categories: Tech
updated: 2022-05-30
comments: true
mathjax: false
---

大多是常用第三方库.

## Pandas

### Cookbook

2020/5/30

pipeline, 临时列 等

- peter. (2022). [Cookbook](https://www.zhihu.com/question/289788451/answer/2495499460)

### groupby 默认会排序

2022/4/25

> sort : bool, default True
>
> Sort group keys. Get better performance by turning this off. Note this does not influence the order of observations within each group. Groupby preserves the order of rows within each group.

见 [这个问题](https://stackoverflow.com/questions/35511350/preserve-row-order-when-doing-operations-across-multiple-dataframes-in-pandas) 和 [文档](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.groupby.html). 我因为忽视这一点遇到了微妙的 bug. 把这个关掉还能提升性能.

<!-- more -->

### Pandas 1.1 `isin` bug

2022/3/24

```python
import pandas as pd

a = pd.Series([42])
b = pd.Series(['42'])
a.isin(b)  # True in 1.1
b.isin(a)  # False in 1.1
# Both are False since 1.2
```

> Strings and integers are distinct and are therefore not comparable

这句话从 1.2 版本才出现在 [文档](https://pandas.pydata.org/pandas-docs/version/1.2/reference/api/pandas.Series.isin.html) 中, 相关 issue 见 [Pandas doesn't always cast strings to int consistently when using .isin()](https://github.com/pandas-dev/pandas/issues/24918).

### Pandas 1.3 inconsistent `where`

2022/3/24

Pandas 1.2

```python
>>> import pandas as pd
>>> import numpy as np
>>> df = pd.DataFrame([0.5, np.nan])
>>> df.where(pd.notnull(df), None)
     0
0  0.5
1  None
```

Pandas 1.3

```python
>>> import pandas as pd
>>> import numpy as np
>>> df = pd.DataFrame([0.5, np.nan])
>>> df.where(pd.notnull(df), None)
     0
0  0.5
1  NaN
```

See the issue [https://github.com/pandas-dev/pandas/issues/42423](https://github.com/pandas-dev/pandas/issues/42423)

### Inplace is harmful

时间和空间都没优势, 反而不能 chaining methods.

Ref: [python - In pandas, is inplace = True considered harmful, or not? - Stack Overflow](https://stackoverflow.com/questions/45570984/in-pandas-is-inplace-true-considered-harmful-or-not)

### datetime, Timestamp, and datetime64

真的很搞.

Ref: [python - Converting between datetime, Timestamp and datetime64 - Stack Overflow](https://stackoverflow.com/questions/13703720/converting-between-datetime-timestamp-and-datetime64)

## Numpy

### `np.nan`

- `np.nan == np.nan` returns False.
- `np.nan` is a floating point constant.

Ref: [Python NumPy For Your Grandma - 3.5 nan](https://www.gormanalysis.com/blog/python-numpy-for-your-grandma-3-5-nan)

## SQLAlchemy

### Close connection with pandas

用 with 包住 connection 后, 好像不需要 [dispose](https://docs.sqlalchemy.org/en/14/core/connections.html#engine-disposal)?

- [python - Does pandas need to close connection? - Stack Overflow](https://stackoverflow.com/questions/42034373/does-pandas-need-to-close-connection/42034432)

### Streaming

读取大查询.

- Turner-Trauring, I. (2021, Oct 1). [Loading SQL data into Pandas without running out of memory](https://pythonspeed.com/articles/pandas-sql-chunking/).

## schedule

定时任务包 [schedule](https://schedule.readthedocs.io/en/stable/)

### How it works

设置定时后, 每次调用 `run_pending` 时检测当前时刻是否超过任务下次 (由上次运行决定) 运行时刻, 是则执行. 如果两次 `run_pending` 间隔太久, 中间错过的任务 (本来应该执行多次的) 会且仅会执行一次. 这点很重要却没在文档中说明, 只有注释

```python
# schedule/__init__.py#L88-L100
def run_pending(self) -> None:
    """
    Run all jobs that are scheduled to run.
    Please note that it is *intended behavior that run_pending()
    does not run missed jobs*. For example, if you've registered a job
    that should run every minute and you only call run_pending()
    in one hour increments then your job won't be run 60 times in
    between but only once.
    """
    runnable_jobs = (job for job in self.jobs if job.should_run)
    for job in sorted(runnable_jobs):
        self._run_job(job)
```

```python
# schedule/__init__.py#L637-L642
def should_run(self) -> bool:
    """
    :return: ``True`` if the job should be run now.
    """
    assert self.next_run is not None, "must run _schedule_next_run before"
    return datetime.datetime.now() >= self.next_run
```

## statsmodels

真的贼难用

### 有趣实践: 用更宽松的方式判断传入参数

以前读源码看到一个有趣的地方, [statsmodels.tsa.seasonal.seasonal_decompose](https://www.statsmodels.org/dev/generated/statsmodels.tsa.seasonal.seasonal_decompose.html) 这个函数的参数为 `model: {"additive", "multiplicative"}, optional`, [源码](https://www.statsmodels.org/dev/_modules/statsmodels/tsa/seasonal.html#seasonal_decompose) 写的是 `if model.startswith("m"):`.