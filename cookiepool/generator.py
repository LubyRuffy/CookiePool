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
        self.ydm = Yundama(YUNDAMA_USERNAME, YUNDAMA_PASSWORD, YUNDAMA_APP_ID, YUNDAMA_APP_KEY)

    def new_cookies(self, username, password):
        """
        生成Cookies
        :param username: 用户名
        :param password: 密码
        :return: 用户名和Cookies
        """
        print('Generating Cookies of', username)
        self.browser.get('https://weibo.cn/login/')
        self.browser.delete_all_cookies()

        try:
            user = self.browser.find_element_by_name("mobile")
            user.send_keys(username)
            psd = self.browser.find_element_by_xpath('//input[@type="password"]')
            psd.send_keys(password)
            code = self.browser.find_element_by_name("code")
            code.clear()
            img = self.browser.find_element_by_xpath('//form[@method="post"]/div/img[@alt="请打开图片显示"]')
            src = img.get_attribute('src')
            response = requests.get(src)
            result = self.ydm.identify(stream=response.content)
            if not result:
                print('验证码识别失败, 跳过识别')
                return
            code.send_keys(result)
            submit = self.browser.find_element_by_name("submit")
            submit.click()
            time.sleep(2)
            html = self.browser.page_source

            if "验证码错误" in html or '登录名及密码不得为空' in html or '登录名或密码错误' in html:
                print('登录失败')
                return
            if '未激活微博' in html:
                print('账号未开通微博')
                return
            self.browser.get('http://weibo.cn/')

            if "我的首页" in self.browser.title:
                print(self.browser.get_cookies())
                cookies = {}
                for cookie in self.browser.get_cookies():
                    cookies[cookie["name"]] = cookie["value"]

                return (username, json.dumps(cookies))
        except ConnectionError as e:
            print(e.args)
            print('验证码获取失败, 跳过')
        except WebDriverException as e:
            print(e.args)


if __name__ == '__main__':
    generator = WeiboCookiesGenerator()
    generator.run()
