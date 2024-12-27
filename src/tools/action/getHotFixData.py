from flask                      import request
from src.tools.logger.system    import logger              as sys_log

import re
import json
import src.tools.repositories   as rep

def getHotFixData(client_version: str) -> dict:
    try:
        # 示例: CNREL2.8.0 -> CNREL
        type_pattern    = re.sub(r"(WIN|Win|Android|IOS|ios|AndroidMi).*$", "", client_version)
        version_pattern = re.sub(r"(CN|OS)(REL|CB)(Win|WIN|iOS|Android)", "", client_version)

        if "Win" or "WIN" in client_version:
            client_pattern = "Win"
        elif "iOS" in client_version:
            client_pattern = "iOS"
        elif "Android" in client_version:
            client_pattern = "Android"
        else:
            sys_log.error(f"主机 {request.remote_addr} 获取热更资源失败: {err}")
            return {}

        sys_log.info(f"{type_pattern} | {client_pattern} | {version_pattern}")

        with open(f"{rep.HOT_FIX_MAIN_PATH}{type_pattern}/{client_pattern}/{version_pattern}.json", 'r', encoding="UTF-8") as file:
            data = json.loads(file.read())
        
        sys_log.info(f"主机 {request.remote_addr} 获取热更新资源成功: 版本标识: {client_version}, 详情信息: {data['regionInfo']}")
        return data['regionInfo']

    except Exception as err:
        sys_log.error(f"主机 {request.remote_addr} 获取热更资源失败: {err}")
        return {}
