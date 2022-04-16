# coding=utf-8

from driver import load_driver
from app import create_app
from concurrent.futures import ThreadPoolExecutor

if __name__ == '__main__':
    driver = load_driver()
    pool = ThreadPoolExecutor(max_workers=10)  # 数量为 10 的线程池
    app = create_app(driver, pool)

    app.run(host='127.0.0.1', port=9997, debug=False)
