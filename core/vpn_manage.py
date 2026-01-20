# 加载根目录下的 .env 文件
import os
import subprocess
import sys
from core.util import ensure_docker_engine, test_network


VPN_CONTAINER_NAME =  "easyconnect_vpn_charge"
class VpnManage:


    def __init__(self):
        pass

    def check_vpn_environment(self, proxy_config)->bool:
        try:
            return test_network(proxy_config)
        except Exception:
            return False

    def is_vpn_running(self) -> bool:
        try:
            # 使用 inspect 检查容器状态更准确
            out = subprocess.check_output(
                ["docker", "inspect", "-f", "{{.State.Running}}", VPN_CONTAINER_NAME],
                text=True, stderr=subprocess.DEVNULL
            )
            return "true" in out.lower()
        except Exception:
            return False

    def start_vpn(self, user, pwd):

        if not ensure_docker_engine():
            sys.exit(1)

        if self.is_vpn_running():
            print("🔗 VPN 已在后台运行。")
            return

        # 检查是否存在已停止的同名容器，如果有则先删除（防止 --name 冲突）
        subprocess.run(["docker", "rm", "-f", VPN_CONTAINER_NAME], capture_output=True)

        print("🚀 启动 EasyConnect VPN（Docker 静默模式）...")

        # 1. 从环境变量获取数据
        server = os.getenv("EC_SERVER_URL", "https://vpn.shiep.edu.cn")
        ver = os.getenv("EC_VER", "7.6.3")

        # 2. 构建镜像要求的 CLI_OPTS 字符串
        # 格式必须严格对应：-d [地址] -u [账号] -p [密码]
        cli_opts = f"-d {server} -u {user} -p {pwd}"

        # 3. 构建完整的 docker run 指令
        cmd = [
            "docker", "run", "-d",
            "--name", VPN_CONTAINER_NAME,
            "--rm",
            "--device", "/dev/net/tun",
            "--cap-add", "NET_ADMIN",
            "-p", "127.0.0.1:1080:1080",
            "-p", "127.0.0.1:8888:8888",
            "-e", f"EC_VER={ver}",
            "-e", f"CLI_OPTS={cli_opts}",
            "hagb/docker-easyconnect:cli"
        ]

        print(f"🚀 正在为用户 {user} 启动 VPN 容器...")
        try:
            # 使用 subprocess 运行
            subprocess.check_call(cmd)
            print("✅ 容器启动指令发送成功。")
        except subprocess.CalledProcessError as e:
            print(f"❌ 启动失败，请检查 Docker 是否运行或容器名是否冲突: {e}")

    @staticmethod
    def stop_vpn():
        """任务结束后调用此函数"""
        print("🔌 正在关闭并清理 VPN 容器...")
        # 只要执行 stop，因为启动时加了 --rm，容器会自动被删除
        subprocess.run(["docker", "stop", VPN_CONTAINER_NAME], capture_output=True)