---
title: "Python 的 web 相关库杂录"
categories: Tech
updated: 2022-10-24
comments: true
mathjax: false
---

随手找的一些模型部署简单例子.

- [Flask+Gunicorn+Service Streamer](https://zhuanlan.zhihu.com/p/460235764)
- [Flask+Gunicorn](https://blog.csdn.net/nuohuang3371/article/details/113061659)
- [Flask+gevent](https://zhuanlan.zhihu.com/p/143678340)
- [Tornado](https://mp.weixin.qq.com/s/Axkti1PXDh6o2bx6MMvnKQ)

<!-- more -->

## uWSGI

> uWSGI, pronounced "mu wiz gee" (u or $\mu$ whiskey), is a Web Server Gateway Interface (WSGI) server implementation that is typically used to run Python web applications.

可以参考 [uWSGI - Full Stack Python](https://www.fullstackpython.com/uwsgi.html) 收集的资源. Full Stack Python 是很好的资源站.

## Gunicorn

> Green Unicorn, commonly shortened to "Gunicorn", is a Web Server Gateway Interface (WSGI) server implementation that is commonly used to run Python web applications.

- [Green Unicorn (Gunicorn) - Full Stack Python](https://www.fullstackpython.com/green-unicorn-gunicorn.html)

> Use Gunicorn, unless you are deploying on Windows, in which case use mod_wsgi.

uWSGI 很多功能与 Nginx 等部件重复, 文档也很杂乱 (开发者承认很难写). Gunicorn 简单效果好.

- Antonis Christofides. (2020). [Which WSGI server should I use?](https://medium.com/django-deployment/which-wsgi-server-should-i-use-a70548da6a83)

## gevent

> gevent is a coroutine-based Python networking library that uses greenlet to provide a high-level synchronous API on top of the libev or libuv event loop.

- [gevent introduction](http://www.gevent.org/intro.html)
- [gevent For the Working Python Developer](https://sdiehl.github.io/gevent-tutorial/)

> A monkey patch (also spelled monkey-patch, MonkeyPatch) is a way to extend or modify the runtime code of dynamic languages (e.g. Smalltalk, JavaScript, Objective-C, Ruby, Perl, Python, Groovy, etc.) without altering the original source code.

- 罗辑. (2018). [有哪些应用场景适合用 python 的 gevent 来完成?](https://www.zhihu.com/question/26671162/answer/38614017)
- 罗辑. (2018). [Python 黑魔法: greenlet](https://www.zhihu.com/question/29995881/answer/83152937)

## Ngnix

> Nginx, pronounced "engine-X", is the second most common web server among the top 100,000 websites. Nginx also functions well as a reverse proxy to handle requests and pass back responses for Python WSGI servers or even other web servers such as Apache.

- [Nginx - Full Stack Python](https://www.fullstackpython.com/nginx.html)

## Flask

> Flask is a Python web framework built with a small core and easy-to-extend philosophy.

基本用法没什么好说的. 此外有个自动生成 Swagger UI 的包 [Flask-RESTX](https://flask-restx.readthedocs.io/en/latest/). Flask-RESTX is a community driven fork of Flask-RESTPlus (后者很久没维护了, 前者也有一段时间不怎么维护了).

- [一个并发的网站, Tornado 与 Flask 应该选哪一个?](https://www.zhihu.com/question/27316652/answer/299186589)
- [Flask - Full Stack Python](https://www.fullstackpython.com/flask.html)
- [python - What is an 'endpoint' in Flask? - Stack Overflow](https://stackoverflow.com/questions/19261833/what-is-an-endpoint-in-flask)

## 其他

### Flask-RESTX demo

需要注意的是, 如果开了 `.expect(validate=True)`, 发送不合法的请求后, Swagger UI 上不会有任何提示. 这是 Swagger UI 的一个 "bug", 见这个 [issue](https://github.com/python-restx/flask-restx/issues/472).

```python
import flask
import flask_restx
from flask import request
from flask_restx import fields

app = flask.Flask(__name__)
api = flask_restx.Api(app=app, title='app title', version='2.3.3', description='app desc')

CONFERENCES_DESC = """
Conference operations

Markdown is supported.
"""
ns_conf = api.namespace(name='conferences', description=CONFERENCES_DESC)
model_conf_input = ns_conf.model(
    name='my_model',
    model={
        'name': fields.String(
            example='C7', description='name whatever', title='field title',
            min_length=1, max_length=10, pattern=r'[A-Z][0-9]', required=True
        ),
        # the default example is the first element of the enum argument ('A' in this case)
        'type': fields.String(enum=['A', 'B', 'C']),
        'nums': fields.List(
            fields.Integer(min=0, max=100),
            min_items=0, max_items=10, description='list of integers'
        ),
        'bool': fields.Boolean(),
    },
    strict=True
)
model_conf_response = ns_conf.model(name='response', model={
    'name': fields.String(description='haha'),
    'nums': fields.List(fields.Integer())
})


@ns_conf.route("/")
class ConferenceList(flask_restx.Resource):
    # `.doc(body=...)` or `.expect(...)` for input
    # `.doc(model=...)` for response
    @ns_conf.expect(model_conf_input, validate=True)
    @ns_conf.param('payload', 'some description goes here', _in='body')
    @ns_conf.response(200, 'Success', model_conf_response)
    @ns_conf.response(400, 'Validation Error')
    def post(self):
        """
        random example

        **markdown is also supported in docstring**
        """
        name = request.json.get('name')
        nums = request.json.get('nums')
        return {
            'name': name,
            'nums': nums
        }


@ns_conf.route("/<int:id>")
class Conference(flask_restx.Resource):
    @ns_conf.doc(params={'id': 'An ID'})
    def get(self, id):
        return id


if __name__ == '__main__':
    app.run(debug=True)
```

### Memo

- Exadel AI Team. (2020). [Deploying Multiple Machine Learning Models on a Single Server](https://exadel.com/news/deploying-multiple-machine-learning-models-on-a-single-server/)
- [模型压测: Locust](https://zhuanlan.zhihu.com/p/475826716) (很简单)
- 测试工具 wrk
