try:
    from __main__ import app
except ImportError:
    from main import app
import json

from flask import Response, render_template


# =====================创建回应=====================#
# 错误处理
@app.errorhandler(404)
def page_not_found(e):
    print(f"ErrorHandler: {e=}, {e.description}")
    return render_template("404.tmpl"), 404


# 自定义json响应
def json_rsp(code, data):
    return Response(
        json.dumps({"retcode": code} | data, separators=(",", ":")),
        mimetype="application/json",
    )


def json_rsp_with_msg(code, msg, data):
    return Response(
        json.dumps({"retcode": code, "message": msg} | data, separators=(",", ":")),
        mimetype="application/json",
    )


def json_rsp_common(code, msg):
    return Response(
        json.dumps({"retcode": code, "message": msg}), mimetype="application/json"
    )
