import os
import socket
import subprocess
import sys
import time
from datetime import date
import socks  # 需先 pip install PySocks

import requests
from bs4 import BeautifulSoup
from requests import HTTPError

from core import auth, electricity
from core.electricity import RechargeInfo


class AuthServiceError(Exception):
    """当未登陆或登陆失败时引发此异常。"""

    pass


class VPNError(Exception):
    """当疑似未开启 VPN 时引发此异常。"""

    pass


def test_network(timeout: float = 0.5) -> bool:
    ip_addrs = [
        "http://10.50.2.206",
        "http://10.166.18.114",
        "http://10.166.19.26",
        "http://10.168.103.76",
    ]

    ok = 0
    for url in ip_addrs:
        try:
            requests.get(url, timeout=timeout)
            ok += 1
        except Exception:
            print("can't connect to %s" % url)
            pass

    return ok / len(ip_addrs) >= 0.5


def semester_week() -> int:
    """获取当前教学周。

    特别地，`-1` 表示暑假，`-2` 表示寒假。
    """
    jwc_url = "https://jwc.shiep.edu.cn/"
    response = requests.get(jwc_url)
    response.raise_for_status()
    dom = BeautifulSoup(response.text, features="html.parser")

    semeter_start = date.fromisoformat(dom.select("div#semester_start")[0].text)
    semeter_end = date.fromisoformat(dom.select("div#semester_end")[0].text)
    if (date.today() - semeter_start).days < 0 or (date.today() - semeter_end).days > 0:
        return -1 if date.today().month > 5 else -2
    else:
        return (date.today() - semeter_start).days // 7

def get_resource_path(relative_path):
    """ 获取资源的绝对路径，兼容开发环境和打包后的环境 """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller 会创建一个临时文件夹 _MEIPASS 来存放解压后的文件
        base_path = sys._MEIPASS
    else:
        # 开发环境或者未打包的情况
        base_path = os.path.abspath("..") # 或者 os.path.dirname(__file__)
    return os.path.join(base_path, relative_path)

def login_service(username, password, site = "http://10.50.2.206:80/"):

    """执行登陆，然后返回service对象"""

    # service 必须与下面一行所展示的精确相符，都为 22 个字符！
    service = auth.AuthService(username, password, service=site, renew="true")
    # 是否需要输入验证码？
    if service.need_captcha():
        # 获取并保存验证码:
        with open("captcha.jpg", "wb") as captcha_image:
            captcha_image.write(service.get_captcha_image())
        # 填写验证码:
        service.set_captcha_code("验证码")
    # 登陆:
    try:
        service.login()
    except HTTPError as e:
        print(e)
    return service

def pay_electricity(service, building_code, room, amount, delay)->RechargeInfo:
    """根据房间号和金额充值电费以及用户service直接进行充值，并返回充值信息"""
    time.sleep(delay)
    em = electricity.ElectricityManagement(service.session)
    # 充值电费
    em.recharge(building_code, room, amount)
    # 获取历次的电表充值账单：
    all_payments = list(em.recharge_info)
    service.logout()
    return all_payments[0]

def setup_global_proxy():
    # 强制所有底层 socket 走 SOCKS5 代理
    socks.set_default_proxy(socks.SOCKS5, "127.0.0.1", 1080)
    socket.socket = socks.socksocket
    print("✅ 全局 Socket 代理已配置")

def ensure_docker_engine():
    """检查 Docker Engine 是否启动，若未启动则尝试唤醒 Docker Desktop"""
    try:
        # 尝试运行一个简单的 docker 命令
        subprocess.run(["docker", "info"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ 检测到 Docker 未启动，请先唤醒 Docker Desktop...")
        # 常见的 Docker Desktop 安装路径
        return False



__all__ = (
    "AuthServiceError",
    "VPNError",
    "test_network",
    "semester_week",
    "get_resource_path",
    "login_service",
    "pay_electricity",
    "setup_global_proxy",
    "ensure_docker_engine"
)