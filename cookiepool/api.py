from flask import Flask, g
from cookiepool.config import *
from cookiepool.db import CookiesRedisClient

__all__ = ['app']

app = Flask(__name__)


@app.route('/')
def index():
    return '<h2>Welcome to Cookie Pool System</h2>'


def get_conn():
    """
    获取
    :return:
    """
    for name in GENERATOR_MAP:
        print(name)
        if not hasattr(g, name):
            setattr(g, name, eval('CookiesRedisClient' + '(name="' + name + '")'))
    return g


@app.route('/<name>/random')
def random(name):
    """
    获取随机的Cookie, 访问地址如 /weibo/random
    :return: 随机Cookie
    """
    g = get_conn()
    cookies = getattr(g, name).random()
    return cookies


@app.route('/<name>/count')
def count(name):
    """
    获取Cookies总数
    """
    g = get_conn()
    count = getattr(g, name).count()
    return str(int) if isinstance(count, int) else count


if __name__ == '__main__':
    app.run()
