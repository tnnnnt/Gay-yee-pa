"""
爬虫自定义函数
"""
import time
import requests
import urllib3.contrib
import winsound
from PIL import Image

timeout = 12.05  # 超时设置
sleep_time = 5


def is_valid(path):
    try:
        Image.open(path).load()
    except OSError:
        return False
    return True


def over_tip():
    duration = 1000  # 持续时间/ms
    frequency = 1000  # 频率/Hz
    winsound.Beep(frequency, duration)


def get_response(url, headers):
    t = 1
    while True:
        t += 1
        # noinspection PyBroadException
        try:
            urllib3.disable_warnings()
            urllib3.contrib.pyopenssl.inject_into_urllib3()
            requests.packages.urllib3.disable_warnings()
            requests.DEFAULT_RETRIES = 10
            requests.session().keep_alive = False
            response = requests.get(url, headers=headers, verify=False, timeout=timeout)
            response.close()
            return response
        except Exception as e:
            if t > 10:
                print('url: ' + url)
                print(e)
                over_tip()
            time.sleep(sleep_time)


def get_html(url, headers):
    return get_response(url, headers).text
