try:
    from __main__ import app
except ImportError:
    from main import app

import json
import random
import string
import src.tools.repositories    as repositories

from flask                       import request
from time                        import time as epoch
from src.tools.action.dbGet      import getMysqlConn
from src.tools.action.getCountry import getLocation
from src.tools.action.msgSafe    import mask_identity, mask_email, mask_string
from src.tools.logger.user       import logger              as user_log
from src.tools.logger.system     import logger              as sys_log
from src.tools.loadconfig        import loadConfig
from src.tools.response          import jsonRsp, jsonRspWithMsg


# ===================== 校验模块 ===================== #
# 账号校验(t_sdk_config)
@app.route("/inner/account/verify", methods=["POST"])
def inner_account_verify():
    try:
        data   = json.loads(request.data)
        sys_log.info(f"gameserver {request.remote_addr} 尝试账号校验, 服务端传入: {data}")
        cursor = getMysqlConn().cursor()
        
        token_query = "SELECT * FROM `t_combo_tokens` WHERE `token` = %s AND `uid` = %s"
        cursor.execute(token_query, (data["combo_token"], data["open_id"]))
        
        token = cursor.fetchone()
        if not token:
            user_log.error(f"gameserver {request.remote_addr} 账号校验失败: 无token引入")
            return jsonRsp(repositories.RES_SDK_VERIFY_FAIL, {})
        
        user_query = "SELECT * FROM `t_accounts` WHERE `uid` = %s"
        cursor.execute(user_query, (token["uid"],))
        user = cursor.fetchone()
        
        if not user:
            user_log.error(f"gameserver {request.remote_addr} 账号校验失败: UID: {token['uid']} 寻到有效的 combo token: {token['token']} 但在数据库中未曾找到此用户")
            return jsonRsp(repositories.RES_SDK_VERIFY_FAIL, {})
        
        is_guest = True if user["type"] == repositories.ACCOUNT_TYPE_GUEST else False
        
        user_log.info(f'gameserver {request.remote_addr} 账号校验成功: UID: {token["uid"]} 类型: {user["type"]}  访客身份: {is_guest}')
        return jsonRsp(repositories.RES_SDK_VERIFY_SUCC,{
                "data": {
                    "guest": is_guest,
                    "account_type": user["type"],
                    "account_uid": str(token["uid"]),
                    "ip_info": {
                        "country_code": getLocation(token["ip"]) or "CN"
                    },
                }
            },
        )
    except Exception as err:
        sys_log.error(f"处理账号校验事件时出现意外错误{err=}, {type(err)=}")
        return jsonRsp(repositories.RES_SDK_VERIFY_FAIL, {})


# 账号风险验证
@app.route("/account/risky/api/check", methods=["POST"])
def account_risky_api_check():
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "id": "none",
                "action": repositories.RISKY_ACTION_NONE,
                "geetest": None,
            }
        },
    )


# 验证account_id和combo_token
@app.route("/hk4e_cn/combo/granter/login/beforeVerify", methods=["POST"])
@app.route("/hk4e_global/combo/granter/login/beforeVerify", methods=["POST"])
def combo_granter_login_verify():
    return jsonRspWithMsg(
        repositories.RES_SUCCESS,"OK",{
            "data": {
                "is_guardian_required": loadConfig()["Player"]["guardian_required"],  # 未满14周岁阻止登录
                "is_heartbeat_required": loadConfig()["Player"]["heartbeat_required"],
                "is_realname_required": loadConfig()["Player"]["realname_required"],  # 实名认证请求
            }
        },
    )


# 二次登录校验
@app.route("/combo/granter/login/login", methods=["POST"])
@app.route("/hk4e_cn/combo/granter/login/v2/login", methods=["POST"])
@app.route("/hk4e_global/combo/granter/login/v2/login", methods=["POST"])
def combo_granter_login_v2_login():
    try:
        cursor = getMysqlConn().cursor()
        data = json.loads(request.json["data"])
        sys_log.info(f"主机 {request.remote_addr} 客户端数据: {data}")
        
        if data["guest"]:
            guest_query = ("SELECT * FROM `t_accounts_guests` WHERE `device` = %s AND `uid` = %s")
            cursor.execute(guest_query, (request.json["device"], data["uid"]))
            guest = cursor.fetchone()
            if not guest:
                user_log.error(f'主机 {request.remote_addr} 登录二检失败: UID {data["uid"]} 在访客模式中无缓存信息')
                return jsonRspWithMsg(repositories.RES_LOGIN_FAILED, "游戏账号信息缓存错误", {})
            
            user_query = "SELECT * FROM `t_accounts` WHERE `uid` = %s AND `type` = %s"
            cursor.execute(user_query, (data["uid"], repositories.ACCOUNT_TYPE_GUEST))
            user = cursor.fetchone()
            
            if not user:
                user_log.error(f"主机 {request.remote_addr} 登录二检失败: 无头部信息")
                return jsonRspWithMsg(repositories.RES_LOGIN_ERROR, "系统错误，请稍后再试", {})

        else:
            token_query = ("SELECT * FROM `t_accounts_tokens` WHERE `token` = %s AND `uid` = %s")
            cursor.execute(token_query, (data["token"], data["uid"]))
            token = cursor.fetchone()
            
            if not token:
                user_log.error(f'主机 {request.remote_addr} 登录二检失败: UID {data["uid"]} 在常规模式中无缓存信息')
                return jsonRspWithMsg(repositories.RES_LOGIN_FAILED, "游戏账号信息缓存错误", {})
            
            user_query = "SELECT * FROM `t_accounts` WHERE `uid` = %s AND `type` = %s"
            cursor.execute(user_query, (token["uid"], repositories.ACCOUNT_TYPE_NORMAL))
            user = cursor.fetchone()
            
            if not user:
                user_log.error(f"主机 {request.remote_addr} 登录二检失败: 无头部信息")
                return jsonRspWithMsg(repositories.RES_LOGIN_ERROR, "系统错误，请稍后再试", {})
        
        
        combo_token       = "".join(random.choices("0123456789abcdef", k=loadConfig()["Security"]["token_length"]))
        device            = request.json["device"]
        request_ip        = request.remote_addr
        epoch_generated   = int(epoch())
        
        combo_token_query = "INSERT INTO `t_combo_tokens` (`uid`, `token`, `device`, `ip`, `epoch_generated`) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE `token` = VALUES(`token`), `device` = VALUES(`device`), `ip` = VALUES(`ip`), `epoch_generated` = VALUES(`epoch_generated`)"
        cursor.execute(combo_token_query, (user["uid"], combo_token, device, request_ip, epoch_generated))
        
        user_log.info(f'主机 {request.remote_addr} 登录二检成功: 设备码: {device} UID: {user["uid"]} combo token: {combo_token} epoch: {epoch_generated}')
        return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
                "data": {
                    "combo_id": 0,
                    "account_type": user["type"],
                    "data": json.dumps({"guest": True if data["guest"] else False},separators=(",", ":"),),
                    "fatigue_remind": {
                        "nickname": "旅行者",
                        "reset_point": 14400,
                        "durations": [180, 240, 300],
                    },
                    "heartbeat": loadConfig()["Player"]["heartbeat_required"],
                    "open_id": str(data["uid"]),
                    "combo_token": combo_token,
                }
            },
        )
    except Exception as err:
        sys_log.error(f"处理 combo 登录事件时出现意外错误 {err=}，{type(err)=}")
        return jsonRspWithMsg(repositories.RES_FAIL, "系统错误，请稍后再试", {})


@app.route("/combo/granter/login/genAuthKey", methods=["GET", "POST"])
def getAuthkey():
    auth_key_version = request.args.get("app_id", "")
    if auth_key_version is None:
        return jsonRspWithMsg(repositories.RES_FAIL,"系统错误, 请稍后再试",{"data": None},)
    
    else:
        try:
            cursor = getMysqlConn().cursor()
            cursor.execute(f"SELECT public_key, private_key FROM `t_verifykey_config` WHERE `type` = 'authkey' AND `version` = {auth_key_version}")
            key = cursor.fetchone()
        except Exception as err:
            sys_log.error(f"处理 genAuthkey 事件出现错误：{err=}")
            return jsonRspWithMsg(repositories.RES_FAIL,"系统错误, 请稍后再试",{"data": None},)
        return jsonRspWithMsg(repositories.RES_SUCCESS, "OK", {"data": key})


# 二次登录校验 CBT1专用
# uid=1001&token=eVyrqDqAWdcvFGUUCCNsoQrAIwurecWf
@app.route("/sdk/token_login", methods=["GET"])
def cbt1_token_login():
    try:
        cursor = getMysqlConn().cursor()
        uid    = request.args.get("uid", "")
        token  = request.args.get("token", "")
        sys_log.info(f"主机 {request.remote_addr} (CBT)客户端数据: UID: {uid} token: {token}")
        
        msg_query   = cursor.execute(f"SELECT * FROM `t_accounts_tokens` WHERE `uid`='{uid}' AND `token`='{token}'")
        token_query = "SELECT * FROM `t_accounts` WHERE (`uid` = %s) AND `type` = %s"
        cursor.execute(token_query, (uid, repositories.ACCOUNT_TYPE_NORMAL))
        user = cursor.fetchone()
        
        if not msg_query:
            user_log.error(f"主机 {request.remote_addr} (CBT)登录二检失败: 无token")
            return jsonRspWithMsg(repositories.RES_LOGIN_FAILED, "游戏账号信息缓存错误", {})
        
        if not user:
            user_log.error(f"主机 {request.remote_addr} (CBT)登录二检失败: 无头部信息")
            return jsonRspWithMsg(repositories.RES_LOGIN_ERROR, "系统错误，请稍后再试", {})
        
        user_log.info(f'主机 {request.remote_addr} (CBT)登录二检成功: UID: {user["uid"]} name: {user["name"]} email: {user["email"]} token: {token}')
        return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
                "data": {
                    "uid": user["uid"],
                    "name": mask_string(user["name"]),
                    "email": mask_email(user["email"]),
                    "token": token,
                    "country": getLocation(request.remote_addr) or "CN",
                    "area_code": None,
                }
            },
        )
    except Exception as err:
        sys_log.error(f"处理登录事件时出现意外错误 {err=}，{type(err)=}")
        return jsonRspWithMsg(repositories.RES_FAIL, "系统错误，请稍后再试", {})


# 游戏账号信息缓存校验
@app.route("/mdk/shield/api/verify", methods=["POST"])
@app.route("/hk4e_cn/mdk/shield/api/verify", methods=["POST"])
@app.route("/hk4e_global/mdk/shield/api/verify", methods=["POST"])
def mdk_shield_api_verify():
    try:
        cursor = getMysqlConn().cursor()
        sys_log.info(f'主机 {request.remote_addr} 客户端数据: UID: {request.json["uid"]} token: {request.json["token"]}')
        
        token_query = ("SELECT * FROM `t_accounts_tokens` WHERE `token` = %s AND `uid` = %s")
        cursor.execute(token_query, (request.json["token"], request.json["uid"]))
        token = cursor.fetchone()
        
        if not token:
            user_log.error(f"主机 {request.remote_addr} 登录缓存校验失败: 无token记录")
            return jsonRspWithMsg(repositories.RES_LOGIN_FAILED, "游戏账号信息缓存错误", {})
        
        if token["device"] != request.headers.get("x-rpc-device_id"):
            user_log.error(f"主机 {request.remote_addr} 登录缓存校验失败: 请求头失效(x-rpc-device_id)")
            return jsonRspWithMsg(repositories.RES_LOGIN_FAILED, "登录态失效，请重新登录", {})
        
        user_query = "SELECT * FROM `t_accounts` WHERE `uid` = %s AND `type` = %s"
        cursor.execute(user_query, (token["uid"], repositories.ACCOUNT_TYPE_NORMAL))
        user = cursor.fetchone()
        
        if not user:
            user_log.error(f"主机 {request.remote_addr} 登录缓存校验失败: UID: {token['uid']} 寻到有效的 combo token: {token['token']} 但在数据库中未曾找到此用户")
            return jsonRspWithMsg(repositories.RES_LOGIN_ERROR, "系统错误，请稍后再试", {})
        
        cursor.execute("SELECT * FROM `t_accounts_realname` WHERE `account_id` = %s",(user["uid"],),)  # 刷新实名信息
        
        identity = cursor.fetchone()
        if identity is None:
            name = ""
            card = ""
        else:
            name = mask_identity(identity["name"])
            card = mask_identity(identity["identity_card"])
        
        user_log.info(f'主机 {request.remote_addr} 登录缓存校验成功: UID: {str(user["uid"])} token: {token["token"]} name: {user["name"]} email: {user["email"]} 实名: {name} 身份证号: {card}')
        return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
                "data": {
                    "account": {
                        "uid": str(user["uid"]),
                        "name": mask_string(user["name"]),
                        "email": mask_email(user["email"]),
                        "is_email_verify": loadConfig()["Login"]["email_verify"],
                        "realname": name,
                        "identity_card": card,
                        "token": token["token"],
                        "country": getLocation(request.remote_addr) or "CN",
                        "area_code": None,
                    }
                }
            },
        )
    except Exception as err:
        sys_log.error(f"处理 MDK Shield API 验证时出现意外错误 {err=}，{type(err)=}")
        return jsonRspWithMsg(repositories.RES_FAIL, "系统错误，请稍后再试", {})


# 实名认证 - 创建票据
# {"action_type":"bind_realname","account_id":"1","game_token":"mlRnIgYzMrPKnqDkTBROXdCNOytAVvso"}
@app.route("/hk4e_cn/mdk/shield/api/actionTicket", methods=["POST"])
def actionTicket():
    try:
        cursor      = getMysqlConn().cursor()
        action_type = request.json["action_type"]
        account_id  = request.json["account_id"]
        sys_log.info(f"主机 {request.remote_addr} 客户端数据: 账号ID: {account_id} 操作类型: {action_type}")
        
        ticket = "".join(random.choices(string.ascii_letters, k=loadConfig()["Security"]["ticket_length"]))
        
        # 检查实名信息是否存在 若不存在插入新的 ticket 并返回
        cursor.execute("SELECT * FROM `t_accounts_realname` WHERE `account_id` = %s", (account_id))
        get_ticket = cursor.fetchone()
        if get_ticket is None:
            cursor.execute(
                "INSERT INTO `t_accounts_realname` (`account_id`, `action_type`, `ticket`, `epoch_created`) VALUES (%s, %s, %s, %s)",
                (account_id, action_type, ticket, int(epoch())),
            )
            cursor.execute(
                "SELECT * FROM `t_accounts_realname` WHERE `account_id` = %s",
                (account_id),
            )
            get_ticket = cursor.fetchone()
            user_log.warning(f"主机 {request.remote_addr} 账号实名认证: {account_id} 实名信息不存在，创建新的 ticket({ticket}) 并记录")

        # cursor.execute("UPDATE `t_accounts_realname` SET `ticket` = %s, `epoch_created` = %s WHERE `account_id` = %s", (ticket, int(epoch()), account_id))
        user_log.info(f'主机 {request.remote_addr} 账号实名认证: 账号ID: {account_id} ticket: {get_ticket["ticket"]}')
        return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
            "data": {
                "ticket": get_ticket["ticket"]
            }},
        )
    except Exception as err:
        sys_log.error(f"处理实名认证时出现意外错误 {err}")
        return jsonRspWithMsg(repositories.RES_FAIL, "系统错误，请稍后再试", {})


# 2.8 后续版本身份信息加密 该功能失效
# {"ticket":"qKsHzVThGqCbMNakMfEBzHneXAmWldtXUfoiWRWU","realname":"??????","identity":"??????","is_crypto":true}
@app.route("/account/auth/api/bindRealname", methods=["POST"])
@app.route("/hk4e_cn/mdk/shield/api/bindRealname", methods=["POST"])
def bindRealName():
    try:
        cursor = getMysqlConn().cursor()
        ticket = request.json["action_ticket"]
        name   = request.json["realname"]
        card   = request.json["identity_card"]
        sys_log.info(f"主机 {request.remote_addr} 客户端数据: 实名者: {name} 身份证号: {card} ticket: {ticket}")
        
        cursor.execute("SELECT * FROM `t_accounts_realname` WHERE `identity_card` = %s", (card,))
        existing_card = cursor.fetchone()
        
        if existing_card:
            user_log.error(f"主机 {request.remote_addr} 账号实名认证失败: 相同的实名信息已存在")
            return jsonRspWithMsg(repositories.RES_FAIL, "该身份证号已被绑定，请使用其他身份证号", {})
        
        cursor.execute("SELECT * FROM `t_accounts_realname` WHERE `ticket` = %s", (ticket,))
        status = cursor.fetchone()
        if status:
            cursor.execute("UPDATE `t_accounts_realname` SET `name` = %s, `identity_card` = %s WHERE `ticket` = %s",(name, card, ticket),)
            cursor.execute("SELECT * FROM `t_accounts_realname` WHERE `ticket` = %s", (ticket,))
            result = cursor.fetchone()
            
            user_log.info(f"主机 {request.remote_addr} 账号实名认证成功: 实名者: {name} 身份证号: {card} ticket: {ticket}")
            return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{
                    "data": {
                        "realname_operation": "updated",
                        "identity_card": mask_identity(result["identity_card"]),
                        "realname": mask_identity(result["name"]),
                    }
                },
            )
        else:
            user_log.error(f"主机 {request.remote_addr} 账号实名认证失败: 连接超时")
            return jsonRspWithMsg(repositories.RES_FAIL, "无效的 Ticket, 请重新登录", {})
    except Exception as err:
        sys_log.error(f"处理实名认证时出现意外错误 {err=}, {type(err)=}")
        return jsonRspWithMsg(repositories.RES_FAIL, "系统错误，请稍后再试", {})
