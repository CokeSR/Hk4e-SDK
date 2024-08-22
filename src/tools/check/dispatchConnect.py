import requests
import src.tools.repositories as repositories

from src.tools.loadconfig import load_config


# ===================== Dispatch 访问校验 ===================== #

def dispatchConn():
    dispatch_url = load_config()["Dispatch"]["list"]
    for region, url in dispatch_url.items():
        if "https://" in url:
            print(f"{repositories.SDK_STATUS_WARING}Dispatch_url: {region} 存在 Https 标识，客户端可能会出现 4206 现象，跳过校验")
        elif "http://" in url:
            try:
                route = url + "/query_cur_region"
                status = requests.get(route, timeout=3)
                if status.status_code == 200:
                    if (
                        status.content.decode()
                        == "CAESGE5vdCBGb3VuZCB2ZXJzaW9uIGNvbmZpZw=="
                    ):
                        print(f"{repositories.SDK_STATUS_SUCC}Dispatch_url: {region} 校验成功")
                    else:
                        print(f"{repositories.SDK_STATUS_FAIL}Dispatch_url: {region} 校验失败，请检查是否为 Dispatch 服务")
            except Exception:
                print(f"{repositories.SDK_STATUS_FAIL}Dispatch_url: {region} 访问失败")
        else:
            print(f"{repositories.SDK_STATUS_FAIL}Dispatch_url: {region} 访问失败，错误的URL：{url}")
