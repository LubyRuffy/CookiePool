import json
from bs4 import BeautifulSoup
import requests
from requests.exceptions import ConnectionError
from cookiepool.db import *
from cookiepool.generator import WeiboCookiesGenerator


class ValidTester(object):
    def __init__(self, name='default'):
        self.name = name
        self.cookies_db = CookiesRedisClient(name=self.name)
        self.account_db = AccountRedisClient(name=self.name)

    def test(self, account, cookies):
        raise NotImplementedError

    def run(self):
        accounts = self.account_db.all()
        for account in accounts:
            username = account.get('username')
            cookies = self.cookies_db.get(username)
            self.test(account, cookies)


class WeiboValidTester(ValidTester):
    def __init__(self, name='weibo'):
        ValidTester.__init__(self, name)
        self.generator = WeiboCookiesGenerator(self.name, browser=DEFAULT_BROWSER)

    def test(self, account, cookies):
        print('Testing Account', account['username'])
        try:
            cookies = json.loads(cookies)
        except TypeError:
            # Cookie 格式不正确
            print('Invalid Cookies Value', account.get('username'))
            self.generator.set_cookies(account)
            return None
        try:
            response = requests.get('http://weibo.cn', cookies=cookies)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                title = soup.title.string
                if title == '我的首页':
                    print('Valid Cookies', account.get('username'))
                else:
                    # Cookie已失效
                    print('Invalid Cookies', account.get('username'))
                    self.generator.set_cookies(account)
        except ConnectionError:
            print('Invalid Cookies', account.get('username'))
            self.generator.set_cookies(account)


if __name__ == '__main__':
    tester = WeiboValidTester()
    tester.run()
