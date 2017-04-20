from cookiepool.api import app
from cookiepool.scheduler import Scheduler

def main():
    s = Scheduler()
    s.run()
    app.run()

if __name__ == '__main__':
    main()