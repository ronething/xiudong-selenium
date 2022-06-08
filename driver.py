import time

from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from sendEmail import sendMail

wait_time = 3  # 提前三秒开始抢


def load_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('log-level=3')
    options.add_argument('--window-size=400,700')
    # options.add_argument('--proxy-server=127.0.0.1:8888') # 本地代理
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option(
        "mobileEmulation", {"deviceName": "Nexus 5"})
    # DONE: 根据平台判断加载的 driver
    import platform
    os_info = platform.system()
    if os_info == "Linux":
        executable_path = "./chromedriver_linux"
    elif os_info == "Windows":
        executable_path = "./chromedriver.exe"
    else:  # mac or other
        executable_path = "./chromedriver"

    driver = webdriver.Chrome(executable_path=executable_path, options=options)

    # js 注入 过环境检测
    with open('./js/stealth.min.js') as f:
        inject_js = f.read()

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": inject_js
    })

    return driver


def goto_login_url(driver: webdriver.Chrome):
    # 前往登录页面
    login_url = "https://wap.showstart.com/pages/passport/login/login?redirect=%2Fpages%2FmyHome%2FmyHome"
    driver.get(login_url)
    WebDriverWait(driver, 100).until(EC.title_is(u"我的"))  # 最多等待 100s

    return


def goto_confirm_url(driver, confirm_ticket_url):
    driver.get(confirm_ticket_url)

    select_user(driver)
    payBtn = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.payBtn')))

    # DONE: 如果不是立即支付，需要进行刷新
    # payBtn <selenium.webdriver.remote.webelement.WebElement
    # (session="1244164329c3e2743132313082fd0416", element="36634b86-15bf-45a2-90d8-db69c3e60f6e")>
    # print(f'点击按钮的文字', payBtn.text)  # 已售罄/ 立即支付 ¥160.00
    if '立即支付' in payBtn.text:
        return payBtn
    else:
        # 不断刷新
        time.sleep(0.001)
        return goto_confirm_url(driver, confirm_ticket_url)


def confirm_ticket(payBtn):
    b = payBtn
    while True:
        try:
            b.click()  # click 本身会占用时间，不 sleep 了
            # time.sleep(interval)

            # 发送邮件通知
            content = '也有可能没抢到，反正打开秀动看看吧...'
            subject = '抢到啦，快看看手机吧'
            receivers = ['xxx@qq.com']
            sendMail(subject, content, receivers)
        except ElementClickInterceptedException as e:
            print(f'点击支付按钮发生异常，可能是已经抢票成功, 请查看手机 但是先不要退出 {e}')
            continue
        except Exception as e:
            # 其他异常直接忽略并返回
            # argument of type 'ElementClickInterceptedException' is not iterable
            errmsg = str(e)  # exception not iterable, 需要通过 str 转一下
            print(f'errmsg is {errmsg}')

            return


def quit_driver(driver):
    try:
        driver.quit()
    except Exception as e:
        print(f'quit err: {e}')


def create_instance(chrome_driver, ticketId: str, event: str, ticketNum: str, start_time: str = None):
    # TODO: 多窗口操作
    # 获取支付按钮 这里不能直接 goto，应该是由 driver 新开标签页或者新窗口然后进行句柄的轮询，
    # 看看能不能给对应窗口或者标签页一个 tag 进行标记
    # 标记时间，如果时间已到达则可以点击 否则不点击
    confirm_url = f"https://wap.showstart.com/pages/order/activity/confirm/confirm" \
                  f"?sequence={event}&ticketId={ticketId}&ticketNum={ticketNum}" \
                  f"&ioswx=1&terminal=app&from=singlemessage&isappinstalled=0"
    pay_btn = goto_confirm_url(chrome_driver, confirm_url)

    if start_time is None:  # 直接抢
        print(f'开始抢票')
        confirm_ticket(pay_btn)
    else:
        # 处理时间
        # start_time = "2021 07 19 20 00 00"
        t1 = time.mktime(time.strptime(start_time, "%Y %m %d %H %M %S"))
        while True:
            if t1 - time.time() < float(wait_time):
                break
            time.sleep(0.001)  # 休眠一下防止 cpu 占用飙升

        print(f'开始抢票')
        confirm_ticket(pay_btn)

    # quit(chrome_driver) 抢不到也不要自己退出 手动抢

# 选择观演人
def select_user(driver):

    # 打开身份证列表
    pleaseSelect = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.link-item>.rr>.tips')))
    if pleaseSelect is None:
        return
    pleaseSelect.click()

    # 选择第一个身份证
    checkBox = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.uni-checkbox-wrapper:nth-child(1)')))
    checkBox.click()

    # 确认
    confirm = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, '.pop-box>.pop-head>uni-view:nth-child(2)')))
    confirm.click()
