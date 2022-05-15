# coding=utf-8

from flask import Flask, g, request
from selenium import webdriver
from driver import create_instance, goto_login_url, quit_driver
from concurrent.futures import ThreadPoolExecutor


def create_app(driver, pool):
    app = Flask(__name__)

    @app.before_request
    def inject_middleware():  # 注入一些全局变量
        # 自动切换当前窗口
        print("切换窗口")
        try:
            print(driver.window_handles)
            driver.switch_to.window(driver.window_handles[0])  # 切换到第一个窗口
        except Exception as e:
            print(f'切换窗口失败, err: {e}')
            errmsg = str(e)
            if 'chrome not reachable' in errmsg:
                # 重新启动 driver，这里可以做一个 reload driver func,单例 driver
                pass
        # 注入 selenium driver
        g.driver = driver
        g.pool = pool

    init_router(app)
    # init_custom_router(app)

    return app


def init_router(app: Flask):
    @app.route("/")
    def hello_world():
        return "<p>Hello, World!</p>"

    @app.route('/login')
    def login_website():
        # 登录网站
        driver: webdriver.Chrome = g.driver
        pool: ThreadPoolExecutor = g.pool
        pool.submit(goto_login_url, driver=driver)  # 不需要获取结果
        # goto_login_url(driver)

        return 'login OK'

    @app.route('/buy', methods=['GET', 'POST'])
    def buy():
        # 通用抢票 api， 需要传入 ticketId 以及 event
        # 可选项: cron_time 表示是否定时
        # example: ?event=123&ticketId=456
        driver: webdriver.Chrome = g.driver
        pool: ThreadPoolExecutor = g.pool
        ticketId = request.args.get('ticketId')
        event = request.args.get('event')
        if ticketId == "" or event == "":
            return 'ERROR' 
        ticketNum = request.args.get('ticketNum')
        if ticketNum == None or ticketNum == "":
            ticketNum = 1
        else:
            ticketNum = ticketNum
        print('ticketNum = ',ticketNum)
        cron_time = request.args.get('cron_time')
        if cron_time == "":
            cron = False
        else:
            cron = True
        print(f'cron_time is {cron_time}, 是否是定时配置: {cron}')

        if not cron:
            pool.submit(create_instance, driver, ticketId, event, ticketNum)
        else:
            pool.submit(create_instance, driver, ticketId, event, ticketNum,cron_time)

        return 'buy OK'

    @app.route('/quit')
    def quit_website():
        # 退出
        driver: webdriver.Chrome = g.driver
        quit_driver(driver)

        return '关闭 driver OK'
