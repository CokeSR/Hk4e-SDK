import json
import requests
import src.tools.repositories as repositories

from src.tools.loadconfig import load_config
from src.tools.action.calMuipSign import calMuipSign


# ===================== Muip 验证 ===================== #
def muip_status():
    config = load_config()["Muipserver"]
    ssl, address, port = config["is_ssl"], config["address"], config["port"]
    http_proto = "https://" if ssl else "http://"
    url = f"{http_proto}{address}:{port}"
    try:
        status = requests.get(url, timeout=3).status_code
        if status == 200:
            print(f"{repositories.SDK_STATUS_SUCC}Muip_url: {url} 通信成功")

            # Muip 签名校验
            command = "cmd=1101"
            content = json.loads(calMuipSign(command))

            if (
                "data" in content
                and "msg" in content
                and "retcode" in content
                and "ticket" in content
            ):
                if content["msg"] == "succ":
                    print(f"{repositories.SDK_STATUS_SUCC}Muip_url: {url} 签名校验成功")
                if content["msg"] == "verify sign error":
                    print(f"{repositories.SDK_STATUS_WARING}Muip_url: {url} 签名校验失败")
            else:
                print(f"{repositories.SDK_STATUS_WARING}Muip_url: {url} 校验失败，请检查是否为 Muipserver 服务")
        else:
            print(f"{repositories.SDK_STATUS_WARING}Muip_url: {url} 通信失败")
    except Exception:
        print(f"{repositories.SDK_STATUS_WARING}Muip_url: {url} 连接超时")
