import time

from core.electricity import RechargeInfo, pay_electricity
from core.user_info_manage import InfoManger
from core.util import  setup_global_proxy
from core.vpn_manage import VpnManage
from interface.message import MenuMessage, VpnUserMessage, PayerMessage, ChargeMessage, Success, Error
import questionary


def get_input_val(message):
    v = input(message)
    return v


def select_buildings():
    choice = questionary.select(
        ChargeMessage.BUILDINGS_SELECT,
        choices=ChargeMessage.Buildings
    ).ask()
    return choice


class Terminal:

    def __init__(self):

        self.info_manager = InfoManger()
        self.vpn_manager = VpnManage()
        self.proxy_config = None  # 存储代理配置

    def electricity_ok_info(self):
        return (f"使用{self.info_manager.payer_info.username}账户付费\n"
                f"给{self.info_manager.charge_info.building_name, self.info_manager.charge_info.room},充值{self.info_manager.charge_info.amount}度电")

    def electricity_ok(self):
        print(self.electricity_ok_info())
        choice = questionary.confirm(
            ChargeMessage.INPUT_OK
        ).ask()
        return choice

    def main_menu(self):
        """主菜单"""
        choice = questionary.select(
            MenuMessage.TITLE,
            choices=MenuMessage.OPTS_LISTS,
        ).ask()

        if choice == MenuMessage.OPT_INFO:
            self.manage_info()
        elif choice == MenuMessage.OPT_QUICK:
            self.charge_quick()
            self.main_menu()
        elif choice == MenuMessage.OPT_EXIT:
            print("拜拜！")
            VpnManage.stop_vpn()
            exit(0)
        else:
            self.charge_after_modify()
            self.main_menu()



    def manage_info(self):
        """信息管理"""
        choice = questionary.select(
            "✏️ 信息修改与查看",
            choices=[VpnUserMessage.VPN_QUERY,
                     VpnUserMessage.VPN_MODIFY,
                     PayerMessage.PAYER_QUERY,
                     PayerMessage.PAYER_MODIFY,
                     ChargeMessage.CHARGE_QUERY,
                     ChargeMessage.CHARGE_MODIFY,
                     MenuMessage.OPT_RETURN]
        ).ask()

        if choice == VpnUserMessage.VPN_QUERY:
            self.query_vpn_info()
        elif choice == VpnUserMessage.VPN_MODIFY:
            self.modify_vpn_info()
        elif choice == PayerMessage.PAYER_QUERY:
            self.query_payer_info()
        elif choice == PayerMessage.PAYER_MODIFY:
            self.modify_payer_info()
        elif choice == ChargeMessage.CHARGE_QUERY:
            self.query_charge_info()
        elif choice == ChargeMessage.CHARGE_MODIFY:
            self.modify_charge_info()

        if choice == MenuMessage.OPT_RETURN:
            self.main_menu()
        else:
            self.manage_info()

    def charge_quick(self):
        """按照默认配置快速充电"""
        if self.electricity_ok():
            print(ChargeMessage.RECHARGE)
            result:RechargeInfo = pay_electricity(self.info_manager.payer_info.username, self.info_manager.payer_info.password,
                                              self.info_manager.charge_info.building_code, self.info_manager.charge_info.room,
                                              self.info_manager.charge_info.amount, self.proxy_config)
            print(ChargeMessage.charge_success(result.time, result.money))




    def charge_after_modify(self):
        """首先输入楼栋号、房间号、充值数，然后充值"""
        building_name = select_buildings()
        building_code = ChargeMessage.get_buildings_code(building_name)
        room = get_input_val(ChargeMessage.INPUT_ROOM)
        amount = get_input_val(ChargeMessage.INPUT_AMOUNT)
        if self.electricity_ok():
            print(ChargeMessage.RECHARGE)
            result: RechargeInfo = pay_electricity(self.info_manager.payer_info.username,
                                               self.info_manager.payer_info.password,
                                               building_code,
                                               room,
                                               int(amount),
                                               self.proxy_config)
            print(ChargeMessage.charge_success(result.time, result.money))


    def modify_vpn_info(self):
        """输入 username, password"""
        print("填写VPN信息：\n")
        vpn_user = get_input_val(VpnUserMessage.INPUT_USER)
        password = get_input_val(VpnUserMessage.INPUT_PASSWORD)
        self.info_manager.modify_info(2, vpn_user, password)
        print(Success.INFO_MODIFY)

    def modify_payer_info(self):
        """输入 username, password"""
        print("填写付费账户信息\n")
        payer_user = get_input_val(PayerMessage.PAYER_USER)
        payer_password = get_input_val(PayerMessage.PAYER_PASS)
        self.info_manager.modify_info(3, payer_user, payer_password)
        print(Success.INFO_MODIFY)

    def modify_charge_info(self):
        """输入 building, room, amount"""
        print("填充值相关信息\n")

        building_name = select_buildings()
        building_code = ChargeMessage.get_buildings_code(building_name)
        room = get_input_val(ChargeMessage.INPUT_ROOM)
        amount = get_input_val(ChargeMessage.INPUT_AMOUNT)
        self.info_manager.modify_info(1, building_name, building_code, room, amount)
        print(Success.INFO_MODIFY)

    def query_vpn_info(self):
        print(Success.INFO_QUERY)
        print(self.info_manager.query_info(1))


    def query_charge_info(self):
        print(Success.INFO_QUERY)
        print(self.info_manager.query_info(3))

    def query_payer_info(self):
        print(Success.INFO_QUERY)
        print(self.info_manager.query_info(2))

    def write_all_info(self, vpn_info_check, charge_info_check, payer_info_check):
        print(Error.INFO_LESS)
        if vpn_info_check:
            self.modify_vpn_info()
        if payer_info_check:
            self.modify_payer_info()
        if charge_info_check:
            self.modify_charge_info()

    def run(self):
        """
        1.检查配置信息
        2.登陆VPN
        3.检查VPN
        """
        print(MenuMessage.BANNER)
        print(MenuMessage.SUBTITLE)
        print(MenuMessage.FOOTER)
        while self.info_manager.check_info_empty():
            self.write_all_info(self.info_manager.vpn_info.check_info_empty(), self.info_manager.charge_info.check_info_empty(), self.info_manager.payer_info.check_info_empty())
        else:
            print(Success.INFO_DETECT)

        self.vpn_manager.start_vpn(self.info_manager.vpn_info.username, self.info_manager.vpn_info.password)
        self.proxy_config = setup_global_proxy()
        time.sleep(5)

        while not self.vpn_manager.check_vpn_environment(self.proxy_config):
            print(VpnUserMessage.VPN_FAIL)
            choice = questionary.select(
                "选择处理方式",
                choices=["刷新等待", "更改VPN登陆信息", "退出"]
            ).ask()
            if choice == "更改VPN登陆信息":
                self.modify_vpn_info()
                VpnManage.stop_vpn()
                time.sleep(2)
                self.vpn_manager.start_vpn(self.info_manager.vpn_info.username, self.info_manager.vpn_info.password)
            elif choice == "刷新等待":
                time.sleep(2)
            else:
                VpnManage.stop_vpn()
                exit(1)
        else:
            print(VpnUserMessage.VPN_SUCCESS)

        self.main_menu()





