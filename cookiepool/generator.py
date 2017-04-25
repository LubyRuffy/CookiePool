import json
import requests
import time
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.common.exceptions import WebDriverException
from cookiepool.db import CookiesRedisClient, AccountRedisClient
from cookiepool.verify import Yundama
from cookiepool.config import *
from requests.exceptions import ConnectionError


class CookiesGenerator(object):
    def __init__(self, name='default', browser=DEFAULT_BROWSER):
        """
        父类, 初始化一些对象
        :param name: 名称
        :param browser: 浏览器, 若不使用浏览器则可设置为 None
        """
        self.name = name
        self.cookies_db = CookiesRedisClient(name=self.name)
        self.account_db = AccountRedisClient(name=self.name)
        self._init_browser(browser=browser)

    def _init_browser(self, browser):
        """
        通过browser参数初始化全局浏览器供模拟登录使用
        :param browser: 浏览器 PhantomJS/ Chrome
        :return:
        """
        if browser == 'PhantomJS':
            caps = DesiredCapabilities.PHANTOMJS
            caps[
                "phantomjs.page.settings.userAgent"] = "Mozilla/5.0 (Linux; U; Android 2.3.6; en-us; Nexus S Build/GRK39F) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1"
            self.browser = webdriver.PhantomJS(desired_capabilities=caps)
        elif browser == 'Chrome':
            self.browser = webdriver.Chrome()

    def new_cookies(self, username, password):
        raise NotImplementedError

    def set_cookies(self, account):
        """
        根据账户设置新的Cookies
        :param account:
        :return:
        """
        results = self.new_cookies(account.get('username'), account.get('password'))
        if results:
            username, cookies = results
            print('Saving Cookies to Redis', username, cookies)
            self.cookies_db.set(username, cookies)

    def run(self):
        """
        运行, 得到所有账户, 然后顺次模拟登录
        :return:
        """
        accounts = self.account_db.all()
        print('Getting', len(accounts), ' from Redis')
        for account in accounts:
            print('Getting Cookies of ', self.name, account.get('username'), account.get('password'))
            self.set_cookies(account)

    def __del__(self):
        if hasattr(self, 'browser'):
            self.browser.quit()


class WeiboCookiesGenerator(CookiesGenerator):
    def __init__(self, name='weibo', browser=DEFAULT_BROWSER):
        """
        初始化操作, 微博需要声明一个云打码引用
        :param name: 名称微博
        :param browser: 使用的浏览器
        """
        CookiesGenerator.__init__(self, name, browser)
        self.name = name
        # self.ydm = Yundama(YUNDAMA_USERNAME, YUNDAMA_PASSWORD, YUNDAMA_APP_ID, YUNDAMA_APP_KEY)

    def new_cookies(self, username, password):
        """
        生成Cookies
        :param username: 用户名
        :param password: 密码
        :return: 用户名和Cookies
        """
        print('Generating Cookies of', username)

        url = 'https://passport.weibo.cn/sso/login'
        data = {
            'username': username,
            'password': password,
            'savestate': '1',
            'r': 'http://weibo.cn/',
            'ec': '0',
            'pagerefer': 'http://weibo.cn/pub/',
            'entry': 'mweibo',
            'mainpageflag': '1'
        }
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,ja;q=0.4,zh-TW;q=0.2',
            'Connection': 'keep-alive',
            'Content-Length': '210',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'passport.weibo.cn',
            'Origin': 'https://passport.weibo.cn',
            'Referer': 'https://passport.weibo.cn/signin/login?entry=mweibo&r=http%3A%2F%2Fweibo.cn%2F&backTitle=%CE%A2%B2%A9&vt=',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
        }
        try:
            s = requests.Session()
            response = s.post(url, data=data, headers=headers)
            result = json.loads(response.text)
            if result.get('retcode') == 20000000:
                return (username, dict(s.cookies))
            else:
                print(result.get('msg'))
                print(result)
        except ConnectionError:
            print('登录失败，跳过登录')


if __name__ == '__main__':
    generator = WeiboCookiesGenerator()
    cookies = generator.new_cookies('13467553219', 'trbnbl199')
    print(cookies)
