# 游戏内部兑换CDK功能
# Url示例：http://192.168.1.8:21000/common/api/exchangecdk?sign_type=2&auth_appid=apicdkey&authkey_ver=1
# 这里只写简易的兑换逻辑(无限兑换)，涉及加密解密的no leak!!! 而且我打算阉割掉authkey和passwdkey
# 孩子随便写写玩的 没完工

from __main__ import app
from flask import request
from settings.response import json_rsp
from settings.database import get_db_cdk

import time
import settings.repositories as repositories

current_timestamp = int(time.time())
@app.route('/common/api/exchangecdk',methods=['GET'])
def check_cdk_status():
    cursor = get_db_cdk().cursor()
    cdkey = request.args.get("cdkey")
    cursor.execute("SELECT * FROM t_cdk_redeem WHERE cdk_name = %s", (cdkey,))
    result = cursor.fetchone()
    if result is None:
        return json_rsp(repositories.RES_CDK_EXCHANGE_FAIL)
    cdk_name, open_time, expire_time, enabled, template_id, times = result
    # 将字符串类型的时间戳转换为整数类型
    current_timestamp = int(time.time())
    if expire_time < current_timestamp:
        return json_rsp(repositories.RES_CDK_EXCHANGE_FAIL, "兑换码已过期")
    # 还没到兑换时间
    elif open_time > current_timestamp:
        return json_rsp(repositories.RES_CDK_EXCHANGE_FAIL, "还未到兑换时间")
    # 0表示未启用兑换
    elif enabled == 0:
        return json_rsp(repositories.RES_CDK_EXCHANGE_FAIL, "尚未启用该兑换码")
    # 此CDK次数
    elif times < 1:
        return json_rsp(repositories.RES_CDK_EXCHANGE_FAIL, "兑换码已过期")
    else:
        return json_rsp(repositories.RES_CDK_EXCHANGE_SUCC)

def exchange_cdk():
    data = request.args.get('param_name')
    return 'Success'