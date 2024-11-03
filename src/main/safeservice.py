try:
    from __main__ import app
except ImportError:
    from main import app

import json

import src.tools.repositories as repositories

from time                            import time                as epoch
from flask                           import abort, request
from src.tools.action.dbGet          import getMysqlConn
from src.tools.response              import jsonRsp, jsonRspWithMsg
from src.tools.logger.system         import logger              as sys_log
from src.tools.action.passwordManage import password_verify

# ===================== GameServer请求处理 ===================== #
# 玩家登入
@app.route("/bat/game/gameLoginNotify", methods=["POST"])
@app.route("/inner/bat/game/gameLoginNotify", methods=["POST"])
# @whiteListIP(['192.168.1.8'])
def player_login():
    cursor = getMysqlConn().cursor()
    player_info = json.loads(request.data.decode())
    sys_log.info(f"来自 gameserver 的玩家登入记录: {player_info}")
    uid          = player_info["uid"]
    account_type = player_info["account_type"]
    account      = player_info["account"]
    platform     = player_info["platform"]
    # 低版本真端没有 region 和 biz_game?
    try:
        region = player_info["region"]
        biz_game = player_info["biz_game"]
    except Exception:
        region, biz_game = "Not Found Region", "Not Found BIZ"
    cursor.execute(
        "INSERT INTO `t_accounts_events` (`uid`, `method`, `account_type`, `account_id`, `platform`, `region`, `biz_game`, `epoch_created`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (uid, "LOGIN", account_type, account, platform, region, biz_game, int(epoch())),
    )
    return jsonRsp(repositories.RES_SUCCESS, {})


# 玩家登出
@app.route("/bat/game/gameLogoutNotify", methods=["POST"])
@app.route("/inner/bat/game/gameLogoutNotify", methods=["POST"])
def player_logout():
    cursor = getMysqlConn().cursor()
    player_info = json.loads(request.data.decode())
    sys_log.info(f"来自 gameserver 的玩家登出记录: {player_info}")
    uid = player_info["uid"]
    account_type = player_info["account_type"]
    account = player_info["account"]
    platform = player_info["platform"]
    # 低版本真端没有 region 和 biz_game?
    try:
        region = player_info["region"]
        biz_game = player_info["biz_game"]
    except Exception as err:
        region, biz_game = "Not Found Region", "Not Found BIZ"
    cursor.execute(
        "INSERT INTO `t_accounts_events` (`uid`, `method`, `account_type`, `account_id`, `platform`, `region`, `biz_game`, `epoch_created`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
        (
            uid,
            "LOGOUT",
            account_type,
            account,
            platform,
            region,
            biz_game,
            int(epoch()),
        ),
    )
    return jsonRsp(repositories.RES_SUCCESS, {})

# sdk登出（4.8新版本）
# {"aid":"1","token":{"token":"HbiTUFl....","token_type":1}}
# {"retcode":0,"message":"OK","data":{}}
@app.route('/account/ma-cn-session/app/logout',methods = ['POST'])
def sdk_logout():
    # return {"retcode":0,"message":"OK","data":{}}
    sys_log.info(f"主机 {request.remote_addr} 客户端登出")
    return jsonRspWithMsg(repositories.RES_SUCCESS,"OK",{})

# 心跳包
@app.route("/bat/game/gameHeartBeatNotify", methods=["POST"])
@app.route("/inner/bat/game/gameHeartBeatNotify", methods=["POST"])
def player_heartbeat():
    sys_log.info(f"来自 gameserver 的监听心跳: {request.data.decode()}")
    try:
        return jsonRsp(repositories.RES_SUCCESS, {})
    except Exception as err:
        sys_log.error(f"处理心跳包时出现意外错误{err=}, {type(err)=}")
        abort(500)


# 配置验证
@app.route("/config/verify", methods=["GET"])
@app.route("/perf/config/verify", methods=["GET"])
def config_verify():
    return jsonRsp(repositories.RES_SUCCESS, {"code": 0})


# Data上传
@app.route("/dataUpload", methods=["POST"])
@app.route("/perf/dataUpload", methods=["POST"])
def data_upload():
    return jsonRsp(repositories.RES_SUCCESS, {"code": 0})


# 账号验证 (dev)
# http://127.0.0.1:21000/account/verify?name=Coke&mobile=18423458894&password=genshinimpactoffline2022
@app.route('/hk4e_cn/user/account/verify', methods = ['GET'])
@app.route('/hk4e_global/user/account/verify', methods = ['GET'])
def UserVerify():
    user_name   = request.args.get("name")
    user_mobile = request.args.get("mobile")
    user_passwd = request.args.get("password")
    
    # 保证基本参数
    required_params = ["name", "mobile", "password"]

    if not all(param in request.args for param in required_params):
        sys_log.error(f"主机 {request.remote_addr} 尝试账号验证失败: 无效数据")
        return jsonRspWithMsg(repositories.RES_FAIL, "Not found user config", {})
    else:
        sys_log.info(f"主机 {request.remote_addr} 尝试账号验证: 用户名: {user_name} 手机: {user_mobile} 密码: {user_passwd}")
        cursor = getMysqlConn().cursor()
        cursor.execute("SELECT * FROM `t_accounts` WHERE `name` = %s AND `mobile` = %s",(user_name, user_mobile))
        # 检查用户数据
        data = cursor.fetchone()
        if data:
            passwd_hash = data["password"]
            is_verify = password_verify(user_passwd, passwd_hash)
            if is_verify:
                user_msg = {
                    "data": {
                        "account_uid": data["uid"],
                        "account_user": data["name"],
                        "account_mobile": data["mobile"],
                        "account_email": data["email"],
                        "account_type": data["type"],
                        "account_epoch": data["epoch_created"],
                    }
                }
                sys_log.error(f"主机 {request.remote_addr} 尝试账号验证成功: 数据: {user_msg}")
                return jsonRspWithMsg(repositories.RES_SUCCESS, "OK", user_msg)
            else:
                sys_log.error(f"主机 {request.remote_addr} 尝试账号验证失败: 密码错误")
                return jsonRspWithMsg(repositories.RES_FAIL, f"User {user_mobile} verify failed.", {})
        else:
            sys_log.error(f"主机 {request.remote_addr} 尝试账号验证失败: 未记录该用户")
            return jsonRspWithMsg(repositories.RES_FAIL, f"User {user_mobile} not found", {})
