---
title: "Python 并发基础"
categories: Tech
updated: 
comments: true
mathjax: false
---

并发 (concurrency) 和并行 (parallelism) 是两个概念. 这两个术语的使用还有争议, 下面依照书上的说法, 并行是并发的子集. 

> A modern laptop with 4 CPU cores is routinely running more than 200 processes at any given time under normal, casual use. To execute 200 tasks in parallel, you'd need 200 cores. So, in practice, most computing is concurrent and not parallel.

<!-- more -->

## 一些基础

**协程 (coroutine)**: A function that can suspend itself and resume later. *Native coroutines* are defined with `async def`. Python coroutines usually run within a **single thread** under the supervision of an **event loop**, also in the same thread. Coroutines support **cooperative multitasking**: each coroutine must explicitly cede control with the `yield` or `await` keyword, so that another may proceed concurrently (but not in parallel). This means that any blocking code in a coroutine blocks the execution of the event loop and all other coroutines—in contrast with the **preemptive multitasking** supported by processes and threads. On the other hand, each coroutine consumes less resources than a thread or process doing the same job.

Processes allow **preemptive multitasking**: the OS scheduler preempts—i.e., suspends—each running process periodically to allow other processes to run. This means that a frozen process can't freeze the whole system—in theory.

**GIL**

- Each instance of the Python interpreter is a process. The Python interpreter uses a single thread to run the user's program and the memory garbage collector. 
- Access to object reference counts and other internal interpreter state is controlled by a lock, the Global Interpreter Lock (GIL). **Only one Python thread can hold the GIL at any time.** This means that only one thread can execute Python code at any time, regardless of the number of CPU cores.
- To prevent a Python thread from holding the GIL indefinitely, Python's bytecode interpreter pauses the current Python thread every 5ms by default, releasing the GIL.
- Every Python standard library function that makes a syscall 5 releases the GIL. This includes all functions that perform disk I/O, network I/O, and  `time.sleep()`. Particularly because sleep always releases the GIL, so Python may switch to another thread even if you sleep for 0s.

## 基本用法

```python
from concurrent import futures


def func(n: int) -> int:
    ...


with futures.ThreadPoolExecutor() as executor:
    res = executor.map(func, [0, 1, 2, 3])
```

其中 `map` 方法和通常的 `map(func, [0, 1, 2, 3])` 类似, 返回的都是生成器. **Although the tasks are executed asynchronously, the results are iterated in the order of the iterable** provided to the `map()` function, the same as the built-in `map()` function.

退出上下文管理器时会调用 `.shutdown(wait=True)`: Clean-up the resources associated with the Executor. If wait is True then shutdown will not return until all running futures have finished executing and the resources used by the executor have been reclaimed. 如果不 shutdown, 则退出 Python 时才会释放资源, 参考 [这个](https://stackoverflow.com/questions/28417525/what-is-the-difference-between-using-the-method-threadpoolexecutor-shutdownwait).

要多进程可以直接把 `futures.ThreadPoolExecutor()` 换为 `futures.ProcessPoolExecutor()`, 他们都实现了 `Executor` 接口. `Executor` 会自己调度资源, 无需用户操心.

## Futures

Executor 有个 `submit` method: Submits and schedules a callable to be executed with the given arguments. Returns a `Future` instance representing the execution of the callable.

上述过程的底层用到的对象叫 `Future`, 它能提供更灵活的用法.

> An important thing to know about futures is that you and I should not create them: they are meant to be instantiated exclusively by the concurrency framework, be it `concurrent.futures` or `asyncio`. Here is why: a `Future` represents something that will eventually run, therefore it must be scheduled to run, and that's the job of the framework.
>
> Application code is not supposed to change the state of a future: the concurrency framework changes the state of a future when the computation it represents is done, and we can't control when that happens.

### Methods

部分方法

- `done`: Nonblocking. Return True if the future was cancelled or finished executing.
- `add_done_callback`: Attaches a callable that will be called when the future finishes (completes or is cancelled). Instead of repeatedly asking whether a future is done, client code usually asks to be notified.
- `cancel`: Cancel the future if possible. Returns True if the future was cancelled, False otherwise. A future cannot be cancelled if it is running or has already completed.
- `result`: Return the result of the call that the future represents. In a `concurrency.futures.Future` instance, invoking `f.result()` will block the caller's thread until the result is ready.
- `as_completed`: 入参是 Future 的序列, 返回 an iterator that yields the given Futures as they complete (finished or cancelled).

```python
with futures.ThreadPoolExecutor() as executor:
    future2n = {executor.submit(func, n): n for n in [0, 1, 2, 3]}
    for future in futures.as_completed(future2n):
        n = future2n[future]
        res = future.result()
        ...
```

比 `map` 方法更灵活之处是, 可以 submit 不同的函数, 最后 as_completed 中可以传来源不同的 Futures (比如同时有 ThreadPoolExecutor 和 ProcessPoolExecutor 的). 常见写法是建一个字典, key 是 Future, value 是相关的便于后续处理的值, 比如官方文档的 [例子](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor-example).

## TODO

- [SuperFastPython](https://superfastpython.com/) 写得好像还可以.
- 异步编程: 协程. 多进程多线程重构起来都相当简单, 外面套一层就行; 但协程写起来比较麻烦, 得把涉及到的函数都调整一遍 (所以 gevent 是神).
- Fossen. [python asyncio的设计晦涩难懂，一点也不python，是做毁了吗？](https://www.zhihu.com/question/451397804/answer/2193074474)

