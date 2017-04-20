import time
from multiprocessing import Process
from cookiepool.tester import *
from cookiepool.config import *


class Scheduler(object):
    def valid_cookie(cycle=VALID_CHECK_CYCLE):
        while True:
            print('Checking Cookies')
            for name, tester in TESTER_MAP.items():
                tester = eval(tester + '()')
                tester.run()
                time.sleep(cycle)

    def run(self):
        valid_process = Process(target=Scheduler.valid_cookie)
        valid_process.start()


if __name__ == '__main__':
    Scheduler().run()