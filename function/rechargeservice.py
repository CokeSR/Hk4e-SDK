try:
    from __main__ import app
except ImportError:
    from main import app
import os
import settings.repositories as repositories

from flask import send_file
from flask_caching import Cache
from settings.loadconfig import get_config
from settings.response import json_rsp_with_msg

cache = Cache(app, config={"CACHE_TYPE": "simple"})


@app.context_processor
def inject_config():
    config = get_config()
    return {"config": config}


# =====================支付模块=====================#
# 支付窗口-RMB
@app.route("/hk4e_cn/mdk/shopwindow/shopwindow/listPriceTier", methods=["POST"])
@app.route("/hk4e_cn/mdk/shopwindow/shopwindow/listPriceTierV2", methods=["POST"])
def price_tier_serve_cn():
    file_path = repositories.SHOPWINDOW_TIERS_PATH_CN
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "Not found"


@app.route(
    "/hk4e_global/mdk/shopwindow/shopwindow/getCurrencyAndCountryByIp", methods=["POST"]
)
def get_cur_country():
    return json_rsp_with_msg(repositories.RES_SUCCESS)


# 支付窗口-美元
@app.route("/hk4e_global/mdk/shopwindow/shopwindow/listPriceTier", methods=["POST"])
@app.route("/hk4e_global/mdk/shopwindow/shopwindow/listPriceTierV2", methods=["POST"])
def price_tier_serve_os():
    file_path = repositories.SHOPWINDOW_TIERS_PATH_OS
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "Not found"


# 支付平台展示1
@app.route("/plutus/api/v2/listPayPlat", methods=["GET"])
@app.route("/hk4e_cn/mdk/tally/tally/listPayPlat", methods=["POST"])
def price_pay_types_serve_2():
    file_path = repositories.SHOPWINDOW_PAY_TYPES_PATH_CN
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "Not found"


# 支付平台展示2
@app.route("/hk4e_global/mdk/tally/tally/listPayPlat", methods=["POST"])
def price_pay_types_serve_1():
    file_path = repositories.SHOPWINDOW_PAY_TYPES_PATH_OS
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "Not found"


# 支付确认
@app.route("/plutus/api/v2/check", methods=["GET"])
def charge_check():
    return json_rsp_with_msg(
        repositories.RES_SUCCESS, "OK", {"data": {"status": "CheckStatusInit"}}
    )
