try:
    from __main__ import app
except ImportError:
    from main import app

import re
import random
import string
import settings.repositories as repositories

from flask import request
from time import time as epoch
from flask_caching import Cache
from settings.database import get_db
from settings.loadconfig import get_config
from settings.response import json_rsp_with_msg
from settings.library import (
    request_ip,
    get_country_for_ip,
    password_verify,
    mask_string,
    mask_email,
    decrypt_rsa_password,
)

cache = Cache(app, config={"CACHE_TYPE": "simple"})
@app.context_processor
def inject_config():
    config = get_config()
    return {"config": config}

# =====================登录模块=====================#
def validate_user_format(user):
    phone_pattern = r"^\d{11}$"
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    name_pattern = r"^[\w_]+$"
    return (
        re.match(phone_pattern, user) is not None
        or re.match(email_pattern, user) is not None
        or re.match(name_pattern, user) is not None
    )

# CBT1-登录
# account=18343264056&password=546456456
@app.route("/sdk/login", methods=["GET"])
def cbt1_login():
    # 摆烂
    # uid 改变 你所在的游戏账号就会切换
    return json_rsp_with_msg(
        repositories.RES_SUCCESS,
        "OK",
        {
            "data": {
                "uid": 1001,
                "name": "mihoyo",
                "email": "cokeserver@qq.com",
                "token": "eVyrqDqAWdcvFGUUCCNsoQrAIwurecWf",
                "country": "CN",
                "area_code": None,
            }
        },
    )

@app.route('/sdk/token_login', methods = ['GET'])
def token_login_cbt1():
    # 摆烂
    # uid 改变 你所在的游戏账号就会切换
    return json_rsp_with_msg(
        repositories.RES_SUCCESS,
        "OK",
        {
            "data": {
                "uid": 1001,
                "name": "mihoyo",
                "email": "cokeserver@qq.com",
                "token": "eVyrqDqAWdcvFGUUCCNsoQrAIwurecWf",
                "country": "CN",
                "area_code": None,
            }
        },
    )

@app.route("/mdk/shield/api/login", methods=["POST"])
@app.route("/hk4e_cn/mdk/shield/api/login", methods=["POST"])
@app.route("/hk4e_global/mdk/shield/api/login", methods=["POST"])
def mdk_shield_api_login():
    try:
        cursor = get_db().cursor()
        if "account" not in request.json:
            return json_rsp_with_msg(repositories.RES_FAIL, "缺少登录凭据", {})
        account = request.json["account"]
        email_name_query = "SELECT * FROM `t_accounts` WHERE (`email` = %s OR `mobile` = %s OR `name` = %s ) AND `type` = %s"
        cursor.execute(email_name_query,(account, account, account, repositories.ACCOUNT_TYPE_NORMAL),)
        user = cursor.fetchone()
        if not validate_user_format(account):
            return json_rsp_with_msg(repositories.RES_FAIL, "错误的登录格式", {})
        if not user:
            return json_rsp_with_msg(repositories.RES_LOGIN_FAILED, "该账号未注册", {})
        if get_config()["Auth"]["enable_password_verify"]:
            if request.json["is_crypto"]:
                password = decrypt_rsa_password(request.json["password"])
            else:
                password = request.json["password"]
            if not password_verify(password, user["password"]):
                return json_rsp_with_msg(repositories.RES_LOGIN_FAILED, "用户名或密码不正确", {})
        token = "".join(random.choices(string.ascii_letters, k=get_config()["Security"]["token_length"]))
        device_id = request.headers.get("x-rpc-device_id")
        ip = request_ip(request)
        epoch_generated = int(epoch())
        insert_token_query = "INSERT INTO `t_accounts_tokens` (`uid`, `token`, `device`, `ip`, `epoch_generated`) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_token_query, (user["uid"], token, device_id, ip, epoch_generated))
        return json_rsp_with_msg(
            repositories.RES_SUCCESS,
            "OK",
            {
                "data": {
                    "account": {
                        "uid": str(user["uid"]),
                        "name": mask_string(user["name"]),
                        "email": mask_email(user["email"]),
                        "is_email_verify": get_config()["Login"]["email_verify"],
                        "token": token,
                        "country": get_country_for_ip(ip) or "CN",
                        "area_code": None,
                    },
                    "device_grant_required": get_config()["Login"][
                        "device_grant_required"
                    ],
                    "realname_operation": None,
                    "realperson_required": get_config()["Login"]["realperson_required"],
                    "safe_mobile_required": get_config()["Login"][
                        "safe_mobile_required"
                    ],
                }
            },
        )
    except Exception as err:
        print(f"处理登录事件时出现意外错误 {err=}，{type(err)=}")
        return json_rsp_with_msg(repositories.RES_FAIL, "系统错误，请稍后再试", {})


# 快速游戏
@app.route("/hk4e_cn/mdk/guest/guest/login", methods=["POST"])
@app.route("/hk4e_cn/mdk/guest/guest/v2/login", methods=["POST"])
@app.route("/hk4e_global/mdk/guest/guest/login", methods=["POST"])
@app.route("/hk4e_global/mdk/guest/guest/v2/login", methods=["POST"])
def mdk_guest_login():
    if not get_config()["Auth"]["enable_guest"]:
        return json_rsp_with_msg(repositories.RES_LOGIN_CANCEL, "游客模式已关闭", {})
    try:
        cursor = get_db().cursor()
        guest_query = "SELECT * FROM `t_accounts_guests` WHERE `device` = %s"
        cursor.execute(guest_query, (request.json["device"],))
        guest = cursor.fetchone()
        if not guest:
            insert_accounts_query = ("INSERT INTO `t_accounts` (`type`, `epoch_created`) VALUES (%s, %s)")
            cursor.execute(insert_accounts_query, (repositories.ACCOUNT_TYPE_GUEST, int(epoch())))
            user = {"uid": cursor.lastrowid, "type": repositories.ACCOUNT_TYPE_GUEST}
            insert_guests_query = ("INSERT INTO `t_accounts_guests` (`uid`, `device`) VALUES (%s, %s)")
            cursor.execute(insert_guests_query, (user["uid"], request.json["device"]))
        else:
            user_query = "SELECT * FROM `t_accounts` WHERE `uid` = %s AND `type` = %s"
            cursor.execute(user_query, (guest["uid"], repositories.ACCOUNT_TYPE_GUEST))
            user = cursor.fetchone()
            if not user:
                print(f"Found valid account_guest={guest['uid']} for device={guest['device']}, but no such account exists")
                return json_rsp_with_msg(repositories.RES_LOGIN_ERROR, "系统错误，请稍后再试", {})
        return json_rsp_with_msg(
            repositories.RES_SUCCESS,
            "OK",
            {"data": {"account_type": user["type"], "guest_id": str(user["uid"])}},
        )
    except Exception as err:
        print(f"处理游客登录事件时出现意外错误 {err=}, {type(err)=}")
        return json_rsp_with_msg(repositories.RES_FAIL, "系统错误，请稍后再试", {})
