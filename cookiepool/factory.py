from cookiepool.generator import WeiboCookiesGenerator
from cookiepool.config import *


class CookiesFactory():
    def __init__(self):
        """
        初始化操作, 定义工厂模式调用映射
        """
        self.map = GENERATOR_MAP

    def produce(self, name, browser=DEFAULT_BROWSER):
        """
        动态产生Generator, 生产Cookie, 保存到 Redis
        :param name:
        :param browser:
        :return:
        """
        code = self.map.get(name) + '(browser="' + browser + '")'
        generator = eval(code)
        print('Using generator', generator)
        generator.run()


if __name__ == '__main__':
    factory = CookiesFactory()
    factory.produce('weibo', browser='Chrome')
