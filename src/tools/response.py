try:
    from __main__ import app
except ImportError:
    from main import app

import json
import requests
import src.tools.repositories       as repositories

from functools  import wraps
from flask      import Response, abort, request


# ===================== 创建回应 ===================== #
# 错误处理
@app.errorhandler(404)
@app.errorhandler(405)
def page_not_found(e):
    return jsonRspCommon(repositories.RES_FAIL, f"{e.description}")


# 自定义json响应
def jsonRsp(code, data):
    return Response(
        json.dumps({"retcode": code} | data, separators=(",", ":")),
        mimetype="application/json",
    )


def jsonRspWithMsg(code, msg, data):
    return Response(
        json.dumps({"retcode": code, "message": msg} | data, separators=(",", ":")),
        mimetype="application/json",
    )


def jsonRspCommon(code, msg):
    return Response(
        json.dumps({"retcode": code, "message": msg}), mimetype="application/json"
    )

# 白名单准入
def whiteListIP(allowed_ips):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if request.remote_addr not in allowed_ips:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator


# 信息处理
def forwardRequest(request, url):
    return requests.get(
        url, headers={"miHoYoCloudClientIP": request.remote_addr}
    ).content
