import hashlib
import requests
import urllib.parse

from src.tools.loadconfig import load_config

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
    http_sign = query_sha256_sign(command, load_config()["Muipserver"]["sign"])
    ssl = load_config()["Muipserver"]["is_ssl"]
    header = "https://" if ssl else "http://"
    request = (
        header
        + load_config()["Muipserver"]["address"]
        + ":"
        + str(load_config()["Muipserver"]["port"])
        + "/api?"
        + query
        + "&sign="
        + http_sign
    )
    response = requests.get(request)
    return response.text.strip()
