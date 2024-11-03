try:
    from __main__ import app
except ImportError:
    from main import app

import re
import random
import string
import src.tools.repositories        as repositories

from flask                           import request
from time                            import time as epoch
from src.tools.loadconfig            import loadConfig
from src.tools.response              import jsonRspWithMsg
from src.tools.action.dbGet          import getMysqlConn
from src.tools.action.getCountry     import getLocation
from src.tools.action.passwordManage import password_verify
from src.tools.action.msgSafe        import mask_identity, mask_email, mask_string
from src.tools.action.rsaDecrypt     import decrypt_rsa_password
from src.tools.logger.user           import logger              as user_log
from src.tools.logger.system         import logger              as sys_log


# ===================== 登录模块 ===================== #
def validate_user_format(user):
    phone_pattern = r"^\d{11}$"
    email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    # name_pattern = r"^[\w_]+$"
    return (
        re.match(phone_pattern, user) is not None
        or re.match(email_pattern, user) is not None
        # or re.match(name_pattern, user) is not None
    )


# CBT1-登录
# account=18343264056&password=546456456
@app.route("/sdk/login", methods=["GET"])
def cbt1_login():
    try:
        cursor = getMysqlConn().cursor()
        userName = request.args.get("account", "")
        user_log.info(f"(CBT)账号登录数据: 用户名: {userName}")
        
        if not userName:
            user_log.error(f"(CBT)账号登录失败: 缺少头部信息")
            return jsonRspWithMsg(repositories.RES_FAIL, "缺少登录凭据", {})
        else:
            login_query = "SELECT * FROM `t_accounts` WHERE (`email` = %s OR `mobile` = %s) AND `type` = %s"
            cursor.execute(login_query, (userName, userName, repositories.ACCOUNT_TYPE_NORMAL))
            
            user = cursor.fetchone()
            if not validate_user_format(userName):
                user_log.error(f"(CBT)账号登录失败: 用户 {userName} 格式非法")
                return jsonRspWithMsg(repositories.RES_FAIL,"错误的登录格式,仅可用手机号或邮箱进行登录",{},)
            
            if not user:
                user_log.error(f"(CBT)账号登录失败: 用户 {userName} 未注册")
                return jsonRspWithMsg(repositories.RES_LOGIN_FAILED, "该账号未注册", {})
            
            if loadConfig()["Auth"]["enable_password_verify"]:
                if request.args.get("is_crypto", ""):
                    password = decrypt_rsa_password(request.args.get("password", ""))
                else:
                    password = request.args.get("password", "")
                
                if not password_verify(password, user["password"]):
                    return jsonRspWithMsg(repositories.RES_LOGIN_FAILED, "账号或密码不正确", {})
            
            token = "".join(random.choices(string.ascii_letters, k=loadConfig()["Security"]["token_length"]))
            
            device_id = ""  # CBT1 没有返回设备ID 故留空
            ip = request.remote_addr
            epoch_generated = int(epoch())
            insert_token_query = "INSERT INTO `t_accounts_tokens` (`uid`, `token`, `device`, `ip`, `epoch_generated`) VALUES (%s, %s, %s, %s, %s)"
            cursor.execute(insert_token_query, (user["uid"], token, device_id, ip, epoch_generated))
            
            user_log.info(f'(CBT)账号登录成功: 用户 {userName} UID: {str(user["uid"])} token: {token}')
            return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
                    "data": {
                        "uid": str(user["uid"]),
                        "name": mask_string(user["name"]),
                        "email": mask_email(user["email"]),
                        "token": token,
                        "country": getLocation(ip) or "CN",
                        "area_code": None,
                    }
                },
            )
    except Exception as err:
        sys_log.error(f"处理登录事件时出现意外错误 {err=}，{type(err)=}")
        return jsonRspWithMsg(repositories.RES_FAIL, "系统错误，请稍后再试", {})


@app.route("/mdk/shield/api/login", methods=["POST"])
@app.route("/hk4e_cn/mdk/shield/api/login", methods=["POST"])
@app.route("/hk4e_global/mdk/shield/api/login", methods=["POST"])
def mdk_shield_api_login():
    try:
        cursor = getMysqlConn().cursor()
        sys_log.info(f"主机 {request.remote_addr} 客户端数据: {request.json}")
        
        if "account" not in request.json:
            sys_log.error(f"主机 {request.remote_addr} 尝试登录失败: 缺少登录凭据")
            return jsonRspWithMsg(repositories.RES_FAIL, "缺少登录凭据", {})
        
        # 国内登录正式化 不进行用户名登录 "OR `name` = %s"
        userName = request.json["account"]
        login_query = "SELECT * FROM `t_accounts` WHERE (`email` = %s OR `mobile` = %s) AND `type` = %s"
        cursor.execute(login_query, (userName, userName, repositories.ACCOUNT_TYPE_NORMAL))
        
        user = cursor.fetchone()
        if not validate_user_format(userName):
            user_log.error(f"主机 {request.remote_addr} 用户 {userName} 登录失败: 格式非法")        
            return jsonRspWithMsg(repositories.RES_FAIL, "错误的登录格式,仅可用手机号或邮箱进行登录", {})
        
        if not user:
            user_log.error(f"主机 {request.remote_addr} 用户 {userName} 登录失败: 未注册")    
            return jsonRspWithMsg(repositories.RES_LOGIN_FAILED, "该账号未注册", {})
        
        if loadConfig()["Auth"]["enable_password_verify"]:
            if request.json["is_crypto"]:
                password = decrypt_rsa_password(request.json["password"])
            else:
                password = request.json["password"]
            
            if not password_verify(password, user["password"]):
                user_log.error(f"主机 {request.remote_addr} 用户 {userName} 登录失败: 密码错误")
                return jsonRspWithMsg(repositories.RES_LOGIN_FAILED, "账号或密码不正确", {})
        
        cursor.execute("SELECT * FROM `t_accounts_realname` WHERE `account_id` = %s",(user["uid"],),)  # 刷新实名信息
        identity = cursor.fetchone()
        
        if identity is None:
            name = ""
            card = ""
        else:
            name = mask_identity(identity["name"])
            card = mask_identity(identity["identity_card"])
            
        token      = "".join(random.choices(string.ascii_letters, k=loadConfig()["Security"]["token_length"]))
        device_id  = request.headers.get("x-rpc-device_id")
        request_ip = request.remote_addr
        epoch_generated = int(epoch())
        insert_token_query = "INSERT INTO `t_accounts_tokens` (`uid`, `token`, `device`, `ip`, `epoch_generated`) VALUES (%s, %s, %s, %s, %s)"
        cursor.execute(insert_token_query, (user["uid"], token, device_id, request_ip, epoch_generated))
        
        user_log.info(f'主机 {request.remote_addr} 用户 {userName} 登录成功: UID: {str(user["uid"])} token: {token}')
        return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
                "data": {
                    "account": {
                        "uid": str(user["uid"]),
                        "name": mask_string(user["name"]),
                        "mobile": mask_string(user["mobile"]),
                        "email": mask_email(user["email"]),
                        "is_email_verify": loadConfig()["Login"]["email_verify"],
                        "realname": name,
                        "identity_card": card,
                        "token": token,
                        "safe_mobile": "",
                        "facebook_name": "",
                        "google_name": "",
                        "twitter_name": "",
                        "game_center_name": "",
                        "apple_name": "",
                        "sony_name": "",
                        "tap_name": "",
                        "country": getLocation(request_ip) or "CN",
                        "reactivate_ticket": "",
                        "area_code": "",
                        "device_grant_ticket": "",
                        "steam_name": "",
                        "unmasked_email": "",
                        "unmasked_email_type": 0,
                        "cx_name": "",
                    },
                    "device_grant_required": loadConfig()["Login"]["device_grant_required"],
                    "realname_operation": None,
                    "realperson_required": loadConfig()["Login"]["realperson_required"],
                    "safe_mobile_required": loadConfig()["Login"]["safe_mobile_required"],
                    "reactivate_required": loadConfig()["Login"]["safe_mobile_required"],
                }
            },
        )
    except Exception as err:
        sys_log.error(f"处理登录事件时出现意外错误 {err=}，{type(err)=}")
        return jsonRspWithMsg(repositories.RES_FAIL, "系统错误，请稍后再试", {})


# 快速游戏
@app.route("/hk4e_cn/mdk/guest/guest/login", methods=["POST"])
@app.route("/hk4e_cn/mdk/guest/guest/v2/login", methods=["POST"])
@app.route("/hk4e_global/mdk/guest/guest/login", methods=["POST"])
@app.route("/hk4e_global/mdk/guest/guest/v2/login", methods=["POST"])
def mdk_guest_login():
    if not loadConfig()["Auth"]["enable_guest"]:
        user_log.warning(f"主机 {request.remote_addr} 游客登录失败: 功能已关闭")
        return jsonRspWithMsg(repositories.RES_LOGIN_CANCEL, "游客模式已关闭", {})
    try:
        cursor = getMysqlConn().cursor()
        guest_query = "SELECT * FROM `t_accounts_guests` WHERE `device` = %s"
        cursor.execute(guest_query, (request.json["device"],))
        guest = cursor.fetchone()
        
        # 检查是否存在预留信息
        if not guest:
            insert_accounts_query = ("INSERT INTO `t_accounts` (`type`, `epoch_created`) VALUES (%s, %s)")
            cursor.execute(insert_accounts_query, (repositories.ACCOUNT_TYPE_GUEST, int(epoch())))
            
            user = {"uid": cursor.lastrowid, "type": repositories.ACCOUNT_TYPE_GUEST}
            
            insert_guests_query = ("INSERT INTO `t_accounts_guests` (`uid`, `device`) VALUES (%s, %s)")
            cursor.execute(insert_guests_query, (user["uid"], request.json["device"]))
            user_log.info(f'主机 {request.remote_addr} 游客账号注册成功: UID: {user["uid"]} 设备码: {request.json["device"]}')
        else:
            user_query = "SELECT * FROM `t_accounts` WHERE `uid` = %s AND `type` = %s"
            cursor.execute(user_query, (guest["uid"], repositories.ACCOUNT_TYPE_GUEST))
            user = cursor.fetchone()
            
            if not user:
                user_log.error(f"主机 {request.remote_addr} 游客登录失败: 为 UID: {guest['uid']} 找到了有效的设备码: {guest['device']} 但在数据库中未曾找到此用户")
                return jsonRspWithMsg(repositories.RES_LOGIN_ERROR, "系统错误，请稍后再试", {})
        
        user_log.info(f'主机 {request.remote_addr} 游客登录成功: ID: {str(user["uid"])} 平台类型: {user["type"]} 设备码: {guest["device"]}')
        return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "account_type": user["type"], 
                "guest_id": str(user["uid"])
            }},
        )
    except Exception as err:
        sys_log.error(f"处理游客登录事件时出现意外错误 {err=}, {type(err)=}")
        return jsonRspWithMsg(repositories.RES_FAIL, "系统错误，请稍后再试", {})
