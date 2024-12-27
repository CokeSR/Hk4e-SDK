import json
import hashlib
import requests
import urllib.parse

from src.tools.loadconfig         import loadConfig
from src.tools.logger.system      import logger              as sys_log

# ===================== Muip签名计算与配置 ===================== #
def calMuipSign(command):
    def query_sha256_sign(query, sign):
        querys = query.split("&")
        sort_querys = [q for q in querys if q.split("=")[1] != ""]
        sort_querys.sort()
        ready_sign_query = "&".join(sort_querys)
        http_sign = sha256_encode(ready_sign_query + sign)
        return http_sign

    def query_escape(query):
        querys = query.split("&")
        new_querys = [
            "=".join([key_and_value[0], urllib.parse.quote(key_and_value[1])])
            for key_and_value in (q.split("=") for q in querys)
        ]
        return "&".join(new_querys)

    def sha256_encode(data):
        sha256 = hashlib.sha256()
        sha256.update(data.encode("utf-8"))
        return sha256.hexdigest()

    query = query_escape(command)
    http_sign = query_sha256_sign(command, loadConfig()["Muipserver"]["sign"])
    ssl = loadConfig()["Muipserver"]["is_ssl"]
    header = "https://" if ssl else "http://"
    request = (
        header
        + loadConfig()["Muipserver"]["address"]
        + ":"
        + str(loadConfig()["Muipserver"]["port"])
        + "/api?"
        + query
        + "&sign="
        + http_sign
    )
    try:
        response = requests.get(request)
        data = response.text.strip()
        sys_log.info(f"尝试交互 Muipserver 成功: URL: {request} 目标回应: {data}")
        return data
    except Exception as err:
        data = {
            "retcode": -1,
            "msg": "loading muipserver failed"
        }
        sys_log.info(f"尝试交互 Muipserver 失败: URL: {request} 错误信息: {err}")
        return json.dumps(data)

