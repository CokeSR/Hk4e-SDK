import requests
import src.tools.repositories as repositories

from src.tools.loadconfig import load_config


# ===================== Muip 验证 ===================== #
def muip_status():
    config = load_config()["Muipserver"]
    ssl, address, port = config["is_ssl"], config["address"], config["port"]
    http_proto = "https://" if ssl else "http://"
    url = f"{http_proto}{address}:{port}"
    try:
        status = requests.get(url).status_code
        (
            print(f"{repositories.SDK_STATUS_SUCC}Muip_url: {url} 通信成功")
            if status == 200
            else print(f"{repositories.SDK_STATUS_WARING}Muip_url: {url} 通信失败")
        )
    except Exception:
        print(f"{repositories.SDK_STATUS_WARING}Muip_url: {url} 连接超时")
