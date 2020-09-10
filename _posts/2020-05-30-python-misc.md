---
title: "Python 杂录"
categories: Language
updated: 2020-09-09
comments: true
mathjax: true
---

## @property

2020/8/31

> If you want private attributes and methods you can implement the **class** using *setters, getters* methods otherwise you will implement using the normal way.

参考

- [Python @property: How to Use it and Why? - Programiz](https://www.programiz.com/python-programming/property)
- [Property vs. Getters and Setters in Python - DataCamp](https://www.datacamp.com/community/tutorials/property-getters-setters)

<!-- more -->

## @classmethod and @staticmethod

2020/8/28

作用是在类实例化前提供 method 用以交互. 在下面的参考链接中给出的用例是用 staticmethod 检验输入, 用 classmethod 对不同类型的输入进行初始化.

参考
[Python's @classmethod and @staticmethod Explained](https://stackabuse.com/pythons-classmethod-and-staticmethod-explained/)

## 字典和列表

2020/7/17

字典: 哈希表, 开放寻址. 3.6 开始有新的改变.

列表: 动态数组

参考
- [为什么Python 3.6以后字典有序并且效率更高？](https://zhuanlan.zhihu.com/p/73426505)
- [How are Python's Built In Dictionaries Implemented?](https://stackoverflow.com/questions/327311/how-are-pythons-built-in-dictionaries-implemented)
- [How is Python's List Implemented?](https://stackoverflow.com/questions/3917574/how-is-pythons-list-implemented)
- [Implementation of Dynamic Array in Python](https://www.tutorialspoint.com/implementation-of-dynamic-array-in-python)

## 多线程和多进程

2020/7/15

You can use `threading` if your program is network or IO bound, and `multiprocessing` if it's CPU bound.

Without multiprocessing, Python programs have trouble maxing out your system's specs because of the GIL (Global Interpreter Lock). Python wasn't designed considering that personal computers might have more than one core, so the GIL is necessary because Python is not thread-safe and there is a globally enforced lock when accessing a Python object. Though not perfect, it's a pretty effective mechanism for memory management. 

Multiprocessing allows you to create programs that can run concurrently (bypassing the GIL) and use the entirety of your CPU core. The multiprocessing library gives each process its own Python interpreter and each their own GIL. Because of this, the usual problems associated with threading (such as data corruption and deadlocks) are no longer an issue. Since the processes don't share memory, they can't modify the same memory concurrently.

参考
- [Multiprocessing vs. Threading in Python: What you need to know.](https://timber.io/blog/multiprocessing-vs-multithreading-in-python-what-you-need-to-know/)
- [Intro to Threads and Processes in Python \| by Brendan Fortuner \| Medium](https://medium.com/@bfortuner/python-multithreading-vs-multiprocessing-73072ce5600b)

## `+=`

2020/6/9

```python
>>> x = y = [1, 2, 3, 4]
>>> x += [4]
>>> x
[1, 2, 3, 4, 4]
>>> y
[1, 2, 3, 4, 4]
```

```python
>>> x = y = [1, 2, 3, 4]
>>> x = x + [4]
>>> x
[1, 2, 3, 4, 4]
>>> y
[1, 2, 3, 4]
```

其中 `+=` 调用了可变对象的 `__iadd__` method, 原地操作, 对不可变对象来说依然是 `__add__`, 而 `+` 则是 `__add__`, 创建了新对象. 

对于 list 而言, `+=` 几乎等价于 `extend`, 只是后者是一次函数调用.

一个 corner case (2020/9/9)

```python
>>> t = (0, [1, 2])
>>> t[1] += [3]
'''
Traceback (most recent call last):
  File "<pyshell#2>", line 1, in <module>
    t[1] += [3]
TypeError: 'tuple' object does not support item assignment
'''
>>> t
(0, [1, 2, 3])
>>> dis.dis('t[1] += [3]')
'''
  1           0 LOAD_NAME                0 (t)
              2 LOAD_CONST               0 (1)
              4 DUP_TOP_TWO
              6 BINARY_SUBSCR
              8 LOAD_CONST               1 (3)
             10 BUILD_LIST               1
             12 INPLACE_ADD
             14 ROT_THREE
             16 STORE_SUBSCR
             18 LOAD_CONST               2 (None)
             20 RETURN_VALUE
'''
```

关键在于这并不是一个原子操作, 先对列表原地做完扩充后, 还有一个赋值动作 `STORE_SUBSCR`, 此处报错. 如果换成 extend 就没有这个赋值动作, 不会报错.

参考
- [python - Different behaviour for `list.__iadd__` and `list.__add__` - Stack Overflow](https://stackoverflow.com/questions/9766387/different-behaviour-for-list-iadd-and-list-add)
- [python - Concatenating two lists - difference between '+=' and extend() - Stack Overflow](https://stackoverflow.com/questions/3653298/concatenating-two-lists-difference-between-and-extend)
- Ramalho, L. (2015). *Fluent python: Clear, concise, and effective programming*. " O'Reilly Media, Inc.". pp. 40-42.

## UnboundLocalError

```python
a, b = 0, 1

def f(n):
    for _ in range(n):
        a, b = b, a + b
        return a

print(f(7))
# UnboundLocalError: local variable 'b' referenced before assignment
```

当函数中有赋值操作时, 那个变量就视为局部变量. 解决方法是用 `global`.

参考
[python - Don't understand why UnboundLocalError occurs (closure) - Stack Overflow](https://stackoverflow.com/questions/9264763/dont-understand-why-unboundlocalerror-occurs-closure)

## 当参数默认值为空列表

```python
def f(*args, a=[]):
    a += args
    return a

x = f(1)
y = f(2)
print(x, y)
# [1, 2] [1, 2]
```

```python
def g(*args, a=None):
    if not a:
        a = []
    a += args
    return a

x = g(1)
y = g(2)
print(x, y)
# [1] [2]
```

原因在于函数是一等公民, 参数就像是它的 member data, 随着函数调用而改变.

参考
[python - "Least Astonishment" and the Mutable Default Argument - Stack Overflow](https://stackoverflow.com/questions/1132941/least-astonishment-and-the-mutable-default-argument)

## Late Binding

```python
a = []
for i in range(3):
    def func(x): return x * i
    a.append(func)
for f in a:
    print(f(2))
'''
4
4
4
'''

for f in [lambda x: x*i for i in range(3)]:
    print(f(2))
'''
4
4
4
'''
```

> Python is actually behaving as defined. **Three separate functions** are created, but they each have the **closure of the environment** they're defined in - in this case, the global environment (or the outer function's environment if the loop is placed inside another function). This is exactly the problem, though - in this environment, **i is mutated**, and the closures all **refer to the same i**.

```python
a = []
for i in range(3):
    def funcC(j):
        def func(x): return x * j
        return func
    a.append(funcC(i))
for f in a:
    print(f(2))

for f in [lambda x, i=i: x*i for i in range(3)]:
    print(f(2))

for f in [lambda x, j=i: x*j for i in range(3)]:
    print(f(2))

# lazy evaluation
for f in (lambda x: x*i for i in range(3)):
    print(f(2))
```

参考
- [python - How do lexical closures work? - Stack Overflow](https://stackoverflow.com/questions/233673/how-do-lexical-closures-work)
- [Python中后期绑定(late binding)是什么意思？ - 知乎](https://www.zhihu.com/question/29483144)
- [lambda - lazy evaluation and late binding of python? - Stack Overflow](https://stackoverflow.com/questions/46210957/lazy-evaluation-and-late-binding-of-python/46213048#46213048)

## 小整数

```python
>>> a = 256
>>> b = 256
>>> a is b
True
>>> a = 257
>>> b = 257
>>> a is b
False    
```

Python 储存了 -5~256 的整数, 当在这个范围内创建整数时, 都会得到先前存在的对象的引用.

参考
[python - "is" operator behaves unexpectedly with integers - Stack Overflow](https://stackoverflow.com/questions/306313/is-operator-behaves-unexpectedly-with-integers)


## `super`

2020/5/30

当子类的 method 和父类同名时, 可以直接显式地调用父类的 method, 但更好的是用 `super` 来调用, 最常见的就是 `__init__`.

事实上上一句话并不对, `super` 的调用是根据 MRO (Method Resolution Order) 进行的, 并非调用它的父类, 在涉及多重继承时会有区别. 

**例**

```python
class First():
    def __init__(self):
        print("First(): entering")
        super().__init__()
        print("First(): exiting")

class Second():
    def __init__(self):
        print("Second(): entering")
        super().__init__()
        print("Second(): exiting")

class Third(First, Second):
    def __init__(self):
        print("Third(): entering")
        super().__init__()
        print("Third(): exiting")

Third()

'''
Third(): entering
First(): entering
Second(): entering
Second(): exiting
First(): exiting
Third(): exiting
'''
```

First 和 Second 没有父子关系, 但是在定义 `class Third(First, Second)` 时, MRO 是 [Third, First, Second], 于是 First 的 `super` 会调用 Second 的 method.

**例**

```python
class First():
    def __init__(self):
        print("First(): entering")
        super().__init__()
        print("First(): exiting")

class Second(First):
    def __init__(self):
        print("Second(): entering")
        super().__init__()
        print("Second(): exiting")

class Third(First):
    def __init__(self):
        print("Third(): entering")
        super().__init__()
        print("Third(): exiting")

class Fourth(Second, Third):
    def __init__(self):
        print("Fourth(): entering")
        super().__init__()
        print("Fourth(): exiting")

Fourth()

'''
Fourth(): entering
Second(): entering
Third(): entering
First(): entering
First(): exiting
Third(): exiting
Second(): exiting
Fourth(): exiting
'''
```

MRO 为 [Fourth, Second, Third, First], 规则是子类必须出现在父类之前.

**例**

```python
class First():
    def __init__(self):
        print("First(): entering")

class Second(First):
    def __init__(self):
        print("Second(): entering")
        # difference
        First.__init__(self)

class Third(First):
    def __init__(self):
        print("Third(): entering")
        super().__init__()

class Fourth(First):
    def __init__(self):
        print("Fourth(): entering")
        super().__init__()

class A(Second, Fourth):
    def __init__(self):
        print("A(): entering")
        super().__init__()

class B(Third, Fourth):
    def __init__(self):
        print("B(): entering")
        super().__init__()

A()
B()

'''
A(): entering
Second(): entering
First(): entering
B(): entering
Third(): entering
Fourth(): entering
First(): entering
'''
```

Second 显式地调用父类方法, 而 Third 通过 `super` 调用 MRO 下一个类的方法.

**例**

```python
class First():
    def __init__(self):
        print("First(): entering")
        super().__init__()
        print("First(): exiting")

class Second(First):
    def __init__(self):
        print("Second(): entering")
        super().__init__()
        print("Second(): exiting")

class Third(First, Second):
    def __init__(self):
        print("Third(): entering")
        super().__init__()
        print("Third(): exiting")

Third()
'''
TypeError: Cannot create a consistent method resolution
order (MRO) for bases First, Second
'''
```

这里 Second 是 First 的子类, 而 `Third(First, Second)` 却想让 MRO 为 [Third, First, Second], 产生矛盾, 抛出错误.

参考 
- [How does Python's `super()` work with multiple inheritance? - Stack Overflow](https://stackoverflow.com/questions/3277367/how-does-pythons-super-work-with-multiple-inheritance)
- [Understanding Python `super()` with `__init__()` methods - Stack Overflow](https://stackoverflow.com/questions/576169/understanding-python-super-with-init-methods)

## 装饰器

关键在于函数是 Python 的一等公民, 它可以作为参数被传递, 被 return, 被赋值到一个变量.

当函数嵌套时, 内层函数可以使用外层函数的临时变量.

### 闭包

闭包 (closure): 嵌套函数内层函数用了外层函数的变量, 并且外层函数 return 了内层函数. 见下例.

```python
def print_msg(msg):
    '''outer enclosing function'''

    def printer():
        '''nested function'''
        print(msg)

    return printer

another = print_msg("Hello")
another()
# Hello

'''
This technique by which some data ("Hello") gets attached 
to the code is called closure in Python.

This value in the enclosing scope is remembered 
even when the variable goes out of scope 
or the function itself is removed from the current namespace.
'''
```

用数学类比, 记 `print_msg` 为 $f$, 参数 `msg` 为 $\theta$, 内层 `printer` 为 $g$, 则 `print_msg` 可以理解为

$$
f\colon \theta \mapsto g_\theta(\cdot).
$$

### 装饰器

```python
# baisc example
def uppercase_decorator(function):
    def wrapper():
        func = function()
        make_uppercase = func.upper()
        return make_uppercase
    return wrapper

def say_hi():
    return 'hello there'

decorate = uppercase_decorator(say_hi)
decorate()
# 'HELLO THERE'

# general example
def some_decorator(function):
    def wrapper(*args, **kwargs):
        print('The positional arguments are', args)
        print('The keyword arguments are', kwargs)
        function(*args, **kwargs)
    return wrapper

@some_decorator
def printer(a, b, c):
    print(a, b, c)

printer(1, 2, c=3)

'''
The positional arguments are (1, 2)
The keyword arguments are {'c': 3}
1 2 3
'''
```

类似地, 记 `some_decorator` 为 $f$, `function` 为 $h$, `wrapper` 为 $g$, 则

$$
f \colon h\mapsto g_h(\cdot).
$$

在例子中 $h$ 为 `printer`, $x$ 为 `(a, b, c)`. 装饰器 $f$ 将原本的 $h(x)$ 变成了 $(f(h))(x) = g_h(x)$.

```python
# further example
def n_times(n):
    def some_decorator(function):
        def wrapper(*args, **kwargs):
            for _ in range(n):
                function(*args, **kwargs)
        return wrapper
    return some_decorator

@n_times(2)
def printer(a, b, c):
    print(a, b, c)

'''
1 2 3
1 2 3
'''

'''
若不用装饰器则等价于 n_times(2)(printer)(1, 2, c=3)
注意写成 n_times(2)(printer(1, 2, c=3)) 是错误的,
因为 n_times(2) 是记录了 n(=2) 的 some_decorator,
而 printer(1, 2, c=3) 返回的是 None,
传入 some_decorator 之后什么都不会发生,
除了之前调用 printer(1, 2, c=3) 时打印一次 123.
'''
```


参考
- [Python Closures: How to use it and Why?](https://www.programiz.com/python-programming/closure)
- [Decorators in Python - DataCamp](https://www.datacamp.com/community/tutorials/decorators-python?utm_source=adwords_ppc&utm_campaignid=9942305733&utm_adgroupid=100189364546&utm_device=c&utm_keyword=&utm_matchtype=b&utm_network=g&utm_adpostion=&utm_creative=229765585183&utm_targetid=aud-392016246653:dsa-929501846124&utm_loc_interest_ms=&utm_loc_physical_ms=2040&gclid=CjwKCAjwiMj2BRBFEiwAYfTbCvBXjtEwVscpKtssLQKAbKlUvi2hpbYpUreB4VIPGmmeiJVGv59j7RoCsSgQAvD_BwE)

## 垃圾回收

Garbage collection 的主要机制是 reference counts, 引用数归零则回收. 这个机制无法被关闭.

```python
import sys
a = 'my-string'
b = [a]
print(sys.getrefcount(a))
# 4
```

这里 4 来自: 
- 创建 `a`
- `b`
- `sys.getrefcount`
- `print`

### 循环引用

```python
class MyClass():
    pass
a = MyClass()
a.obj = a
del a
```

删除了实例后, Python 无法再访问它, 但是其实例依然在内存. 因为它有一个指向自己的引用, 所以引用数不是零.

这类问题叫做 reference cycle, 需要 generational garbage collector 来解决, 在标准库中的 `gc` 模块中, 它可以检测循环引用.

### 分代回收

垃圾回收器追踪内存中的所有对象, 一共分为 3 代, 新对象从第 1 代开始. 如果触发了垃圾回收之后对象存活 (没有被回收), 则移动到下一代. 有三个阈值来决定何时触发垃圾回收, 当那个代的对象数量超过了对应的阈值则触发.

但总得来说平时不太需要关心垃圾回收的问题.

参考 
- [Python Garbage Collection: What It Is and How It Works](https://stackify.com/python-garbage-collection/)
- [Garbage collection in Python: things you need to know \| Artem Golubin](https://rushter.com/blog/python-garbage-collector/)

## Docstring Formats

See [coding style - What is the standard Python docstring format? - Stack Overflow](https://stackoverflow.com/questions/3898572/what-is-the-standard-python-docstring-format)