import requests

from src.tools.logger.system         import logger              as sys_log
from src.tools.loadconfig            import loadConfig


# ===================== Dispatch 访问校验 ===================== #
def dispatchConn():
    dispatch_url = loadConfig()["Dispatch"]["list"]
    for region, url in dispatch_url.items():
        if "https://" in url:
            sys_log.warning(f"Dispatch_url: {region} 存在 Https 标识，客户端可能会出现 4206 现象，跳过校验")
        elif "http://" in url:
            try:
                route = url + "/query_cur_region"
                status = requests.get(route, timeout=3)
                if status.status_code == 200:
                    if len(status.content.decode()) == 40 and status.content.decode().startswith("CAESGE5vdCBGb3VuZCB2ZXJzaW9u"):
                        sys_log.info(f"Dispatch_url: {region} / {url} 校验成功")
                    else:
                        sys_log.error(f"Dispatch_url: {region} / {url} 校验失败，请检查是否为 Dispatch 服务")
            except Exception:
                sys_log.error(f"Dispatch_url: {region} / {url} 访问失败")
        else:
            sys_log.error(f"Dispatch_url: {region} 访问失败，错误的URL: {url}")
