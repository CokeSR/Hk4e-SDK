try:
    from __main__ import app
except ImportError:
    from main import app

import os
import src.tools.repositories as repositories

from flask                    import request, send_file
from src.tools.response       import jsonRspWithMsg
from src.tools.logger.system  import logger              as sys_log

# ===================== 支付模块 ===================== #
# 支付窗口-RMB
@app.route("/hk4e_cn/mdk/shopwindow/shopwindow/listPriceTier", methods=["POST"])
@app.route("/hk4e_cn/mdk/shopwindow/shopwindow/listPriceTierV2", methods=["POST"])
def price_tier_serve_cn():
    file_path = repositories.SHOPWINDOW_TIERS_PATH_CN
    sys_log.info(f'主机 {request.remote_addr} 获取资源文件: {file_path}')
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "Not found"


@app.route("/hk4e_global/mdk/shopwindow/shopwindow/getCurrencyAndCountryByIp", methods=["POST"])
def get_cur_country():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{})


# 支付窗口-美元
@app.route("/hk4e_global/mdk/shopwindow/shopwindow/listPriceTier", methods=["GET", "POST"])
@app.route("/hk4e_global/mdk/shopwindow/shopwindow/listPriceTierV2", methods=["GET", "POST"])
def price_tier_serve_os():
    file_path = repositories.SHOPWINDOW_TIERS_PATH_OS
    sys_log.info(f'主机 {request.remote_addr} 获取资源文件: {file_path}')
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "Not found"


# 支付平台展示1
@app.route("/plutus/api/v2/listPayPlat", methods=["GET"])
@app.route("/hk4e_cn/mdk/tally/tally/listPayPlat", methods=["POST"])
def price_pay_types_serve_2():
    file_path = repositories.SHOPWINDOW_PAY_TYPES_PATH_CN
    sys_log.info(f'主机 {request.remote_addr} 获取资源文件: {file_path}')
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "Not found"


# 支付平台展示2
@app.route("/hk4e_global/mdk/tally/tally/listPayPlat", methods=["POST"])
def price_pay_types_serve_1():
    file_path = repositories.SHOPWINDOW_PAY_TYPES_PATH_OS
    sys_log.info(f'主机 {request.remote_addr} 获取资源文件: {file_path}')
    if os.path.exists(file_path):
        return send_file(file_path)
    else:
        return "Not found"


# 支付确认
@app.route("/plutus/api/v2/check", methods=["GET"])
def charge_check():
    return jsonRspWithMsg(repositories.RES_SUCCESS, "OK", {"data": {"status": "CheckStatusInit"}})
