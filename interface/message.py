# 也可以进一步分组，使用嵌套类
from typing import Any


class MenuMessage:
    # ASCII 艺术字，可以用 http://patorjk.com/software/taag/ 生成
    BANNER = r"""
      _____  _    _  ______  _____  
     / ____|| |  | ||  ____||  __ \ 
    | (___  | |  | || |__   | |__) |
     \___ \ | |  | ||  __|  |  ___/ 
     ____) || |__| || |____ | |     
    |_____/  \____/ |______||_|     
           """
    SUBTITLE = "[bold cyan]上海电力大学 · 电费充值小助手[/]"
    FOOTER = "⚡ Stay Powered, Stay Awesome."
    TITLE = "👋 欢迎使用电费小助手"
    SELECT_HINT = "请使用上下键选择功能："

    # 选项
    OPT_INFO = "✏️ 信息管理"
    OPT_QUICK = "💰 快捷充值"
    OPT_CHANGE = "⚙️  本次更改后充值"
    OPT_RETURN = "🪄 回到上一级"
    OPT_EXIT = "❌ 退出程序"
    OPTS_LISTS = [OPT_INFO, OPT_QUICK, OPT_CHANGE, OPT_EXIT]


class VpnUserMessage:
    VPN_MODIFY = "✏️ 修改VPN账号信息"
    VPN_QUERY = "🔍 查看当前VPN账户"
    INPUT_USER = "🙍‍♂️ 请输入VPN账号:"
    INPUT_PASSWORD = "🫣 请输入VPN密码:"
    VPN_FAIL = "🌐 VPN连接失败，请检查网络设置"
    VPN_SUCCESS = "✅ VPN环境正常"


class PayerMessage:
    PAYER_MODIFY = "✏️ 修改付款账号信息"
    PAYER_QUERY = "🔍 查看当前付款账户"
    PAYER_USER = "🙍‍♂️ 请输入付款账号:"
    PAYER_PASS = "🫣 请输入付款密码:"


class ChargeMessage:

    INPUT_OK = "👉 确认充电？"
    INPUT_AMOUNT = "🪙 请输入充值度数(kwh):"
    RECHARGE = "🎉 充值请求已提交"
    CHARGE_MODIFY = "✏️ 修改当前默认充值配置"
    CHARGE_QUERY = "🔍 查看当前充值配置"
    INPUT_ROOM = "🚪 请输入你的房间号:"
    BUILDINGS_SELECT = "🏢 请选择你的楼栋"
    Buildings = ["一号学生公寓",
                 "二号学生公寓",
                 "三号学生公寓",
                 "四号学生公寓",
                 "五号学生公寓",
                 "六号学生公寓",
                 "七号学生公寓",
                 "八号学生公寓",
                 "九号学生公寓",
                 "留学生及教师公寓"]
    Buildings_code = ["C1",
                      "C2",
                      "C3",
                      "C4",
                      "C5",
                      "C6",
                      "C7",
                      "C8",
                      "C9",
                      "B6", ]

    @staticmethod
    def get_buildings_code(building_name: str) -> Any | None:
        """
        静态方法：根据楼栋名称获取对应的编码
        调用方式：ChargeMessage.get_buildings_code("一号学生公寓")
        """
        # 静态方法中直接用类名访问类属性，无需self/cls
        for name, code in zip(ChargeMessage.Buildings, ChargeMessage.Buildings_code):
            if name == building_name:
                return code
        return None

    @staticmethod
    def charge_success(time, amount):
        return f"✅ 充值成功! {time} , 花费: {amount}"


class Error:
    INFO_LESS = "⚠️ 信息不全"
    AUTH_FAIL = "🔐 登录失败，用户名或密码错误"
    UNKNOWN = "❓ 发生未知错误"

    @staticmethod
    def error_detail(err_msg):
        return f"❌ fail: {err_msg}"


class Success:
    LOGIN = "✅ 登录成功！"
    INFO_MODIFY = "✅ 信息保存成功"
    INFO_QUERY = "✅ 信息查询成功"
    INFO_DETECT = "✅ 信息检测通过"

    @staticmethod
    def success_info(self, content: str) -> str:
        return "✅success:" + content
