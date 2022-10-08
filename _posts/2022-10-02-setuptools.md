---
title: "Python setuptools 简要"
categories: Tech
updated: 
comments: true
mathjax: false
---

用 [setuptools](https://setuptools.pypa.io/en/latest/userguide/index.html)

<!-- more -->

## Quickstart

```shell
pip install --upgrade setuptools
pip install --upgrade build
```

代码结构

- 根目录
    - `setup.cfg`
    - `setup.py`
    - foo_package
        - `__init__.py` # 如果没有这个, 需要用 namespace packages, 见 [这里](https://setuptools.pypa.io/en/latest/userguide/package_discovery.html#custom-discovery)
        - 其他文件
        
```toml
# setup.cfg
[metadata]
# 项目名不一定和项目的源目录名相同. 比如 name = beautifulsoup4,
# 但是源目录名为 bs4; 因此 pip install beautifulsoup4, import bs4
name = foo_package
version = 0.0.2

[options]
# 只支持版本 <, >, <=, >=, == or != (常用 >=)
install_requires =
    requests
    pandas >= 1.2
```

```python
# setup.py
from setuptools import setup

if __name__ == '__main__':
    setup()
```

`setup.py` 也可以填写 metadata 参数, 但新规范更建议用 cfg 文件. 此外更新的规范有用 `pyproject.toml`.

### 代码写法

foo_package 下的代码建议写为绝对 import

```python
from foo_package.xxx import yyy
```

### 安装

```shell
python -m build
```

之后如果本地项目需要用到, 可以用

```shell
pip install -e path/to/foo_package
```

把 `path/to/foo_package` 加入 PYTHONPATH 里.

- [python - What is the use case for `pip install -e`? - Stack Overflow](https://stackoverflow.com/questions/42609943/what-is-the-use-case-for-pip-install-e)

更一般地可以用 wheel (.whl) 文件安装; 上传到 pypi 等.

## Package discovery

上例项目结构比较简单, setuptools 可以自动找到正确的目录. 对于复杂一些的结构

- 根目录
    - `setup.cfg`, `setup.py`
    - foo_package
    - bar_package

可以如下配置

```toml
[options]
packages = find:

[options.packages.find]
# where = . by default
# use `where = src` for src layout
include = foo_package*  # * by default
exclude = foo_package.tests*  # empty by default
```

`setuptools` walks through the directory specified in `where` (defaults to `.`) and filters the packages it can find following the `include` patterns (defaults to `*`), then it removes those that match the `exclude` patterns (defaults to empty) and returns a list of Python packages.
    
这样就只打包 foo_package. 之前的结构称为 flat-layout (如 pandas, sklearn 等大多数项目), 所谓 src-layout (如 transformers) 指如下结构

- 根目录
    - `setup.cfg`, `setup.py`
    - src
        - foo_package
        - bar_package
        
## Including data files

默认只封装 py 文件.

```toml
[options]
include_package_data = True

[options.exclude_package_data]
* =
    *.c
    *.h
```

其中 data files 放在 `MANIFEST.in` 文件中, 比如

```
include *.json
include *.txt
```

## Entry points

可以直接在 console 上使用的命令. An example of how this feature can be used in `pip`: it allows you to run commands like `pip install` instead of having to type `python -m pip install`.

```toml
[options.entry_points]
console_scripts =
    cli-name = foo_package.mymodule:some_func
```

When this project is installed, a `cli-name` executable will be created. `cli-name` will invoke the function `some_func` in the `foo_package/mymodule.py` file when called by the user.
 
## Keywords

只提几个, 例子来自 pandas.

```toml
[metadata]
long_description = file: README.md
long_description_content_type = text/markdown

license = BSD-3-Clause
license_files = LICENSE

classifiers =
    # 开发周期
    # 3 - Alpha
    # 4 - Beta
    # 5 - Production/Stable
    Development Status :: 5 - Production/Stable
    Environment :: Console
    # 目标用户
    Intended Audience :: Science/Research
    # 许可证
    License :: OSI Approved :: BSD License
    Operating System :: OS Independent
    Programming Language :: Cython
    Programming Language :: Python
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3 :: Only
    Programming Language :: Python :: 3.8
    Programming Language :: Python :: 3.9
    Programming Language :: Python :: 3.10
    # 类型
    Topic :: Scientific/Engineering
    
[options]
python_requires = >=3.8
zip_safe = False
```


- classifiers 来自 [这个列表](https://pypi.org/pypi?%3Aaction=list_classifiers)
- zip_safe: A boolean (True or False) flag specifying whether the project can be safely installed and run from a zip file. If this argument is not supplied, the bdist_egg command will have to analyze all of your project's contents for possible problems each time it builds an egg.

至于怎么写版本号

- Crista Perlton. (2022). [5 Best Practices for Versioning Your Python Packages](https://blog.inedo.com/python-best-practices-for-versioning-python-packages-in-the-enterprise)
- [语义化版本 2.0.0](https://semver.org/lang/zh-CN/)

TODO: [TECH ARTICLES BY BERNÁT GÁBOR](https://bernat.tech/posts/)
