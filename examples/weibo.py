import time

import requests
from selenium import webdriver
from PIL import Image

from sina.cookies.verify import Yundama

USERNAME = 'Germey'

PASSWORD = '940629cqc'

APP_ID = '3372'

APP_KEY = '1b586a30bfda5c7fa71c881075ba49d0'

API_URL = 'http://api.yundama.com/api.php'

MAX_RETRY = 20

ydm = Yundama(USERNAME, PASSWORD, APP_ID, APP_KEY)

account = {
    'username': 'rgaotumxm547689@163.com',
    'password': '1diae6zkjf'
}
browser = webdriver.Chrome()
browser.get('https://weibo.cn/login/')
username = browser.find_element_by_name("mobile")
username.send_keys(account['username'])
psd = browser.find_element_by_xpath('//input[@type="password"]')
psd.send_keys(account['password'])

try:
    code = browser.find_element_by_name("code")
    code.clear()
    img = browser.find_element_by_xpath('//form[@method="post"]/div/img[@alt="请打开图片显示"]')
    src = img.get_attribute('src')
    response = requests.get(src)
    result = ydm.identify(stream=response.content)
    code.send_keys(result)
    submit = browser.find_element_by_name("submit")
    submit.click()
    time.sleep(2)

    html = browser.page_source

    if "验证码错误" in html or '登录名及密码不得为空' in html or '登录名或密码错误' in html:
        print('登录失败')
    if '未激活微博' in html:
        print('账号未开通微博')
    browser.get('http://weibo.cn/')



    if "我的首页" in browser.title:
        print(browser.get_cookies())
        cookies = {}
        for cookie in browser.get_cookies():
            cookies[cookie["name"]] = cookie["value"]

        print(cookies)

except Exception as e:
    pass
