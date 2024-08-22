import requests
import src.tools.repositories as repositories

# ===================== IP获取地区 ===================== #
def get_location(ip):
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
            print(f"{repositories.SDK_STATUS_FAIL}在线查询信息失败：HTTP 状态码: {response.status_code}")
            return result
    except requests.RequestException as err:
        print(f"{repositories.SDK_STATUS_FAIL}地址：{ip} 获取信息失败：{err}")
        return result
