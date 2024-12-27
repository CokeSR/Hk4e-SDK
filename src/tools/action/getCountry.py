import requests

from src.tools.logger.system         import logger              as sys_log

# ===================== IP获取地区 ===================== #
def getLocation(ip):
    result = "Not Found"
    try:
        # 该时区获取并不准确 仅供参考
        response = requests.get(f'http://ipinfo.io/{ip}/json')
        if response.status_code == 200:
            data = response.json()
            country = data.get('country')
            region = data.get('region')
            city = data.get('city')
            if country == None:
                return result
            else:
                result = f"{country}/{region}-{city}"
            return result
        else:
            sys_log.error(f"在线查询信息失败: HTTP 状态码: {response.status_code}")
            return result
    except requests.RequestException as err:
        sys_log.error(f"地址: {ip} 获取信息失败: {err}")
        return result
