import re
import time
import requests

from .config import settings


LOGIN_SINA_URL = "https://login.sina.com.cn/sso/login.php?url=https%3A%2F%2Fweibo.com%2F&_rand={}&gateway=1&service=miniblog&entry=miniblog&useticket=1&returntype=META&sudaref=https%3A%2F%2Flogin.sina.com.cn%2F&_client_version=0.6.36"
RE_REDIRECT_URL = re.compile(r"location.replace\((.*?)\)")
RE_COOKIE_SUB = re.compile(r"SUB=(.*?);")
COOKIE_ALC = "ALC={}"


def new_cookie_sub():
    res1 = requests.get(
        url=LOGIN_SINA_URL.format(str(time.time())),
        headers={
            "cookie": COOKIE_ALC.format(settings.cookie_alc)
        }
    )
    redirect_urls = RE_REDIRECT_URL.findall(res1.text)
    if not redirect_urls:
        raise Exception("LOGIN_SINA_URL failed")
    redirect_url = redirect_urls[0]
    res2 = requests.get(url=redirect_url.replace("'", '').replace('"', ''))
    redirect_urls = RE_REDIRECT_URL.findall(res2.text)
    if not redirect_urls:
        raise Exception("LOGIN_SINA_URL failed")
    redirect_url = redirect_urls[0]
    res3 = requests.get(url=redirect_url.replace("'", '').replace('"', ''))
    if len(res3.history) < 1:
        raise Exception("LOGIN_SINA_URL failed")
    cookies = res3.history[0].headers.get("set-cookie")
    cookie_sub = RE_COOKIE_SUB.findall(cookies)
    if not cookie_sub:
        raise Exception("LOGIN_SINA_URL failed")
    return cookie_sub[0]
