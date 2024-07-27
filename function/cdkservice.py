# Url示例：http://192.168.1.8:21000/common/api/exchangecdk?sign_type=2&auth_appid=apicdkey&authkey_ver=1
# Gameserver 与 Multiserver 邮件产出设置
# <ItemOutputLimit>
#   <Item item_id="201" reward_limit="1000" drop_limit="1000" mail_limit="1000"/>
#   <Item item_id="223" reward_limit="100" drop_limit="100" mail_limit="100" />
#   <Item item_id="224" reward_limit="100" drop_limit="100" mail_limit="100" />
# </ItemOutputLimit>
try:
    from __main__ import app
except ImportError:
    from main import app
from flask import request
from settings.database import get_db_cdk
from settings.library import authkey, send
from settings.loadconfig import get_config
from settings.response import json_rsp_common

import time
import json
import datetime as dt
import settings.repositories as repositories

# 时间计算 用于提供邮件过期时间
server_time = dt.datetime.now()
current_time = int(time.time())
delta_30_days = dt.timedelta(days=30)
after_30_days = server_time + delta_30_days
unixt_30_days = str(time.mktime(after_30_days.timetuple())).split(".")[0]


# ===========================游戏内部兑换CDK功能===========================#
@app.route("/common/api/exchangecdk", methods=["GET"])
def cdk_verify():
    if get_config()["Setting"]["cdkexchange"]:
        # Auth解密来获取兑换者数据,计入数据库
        cdkey = request.args.get("cdkey")
        auth_key = request.args.get("authkey")
        authkey_ver = request.args.get("authkey_ver")

        keys = authkey(auth_key, authkey_ver)
        message = json.loads(keys)
        uid = message.get("uid")
        game = message.get("game")
        region = message.get("region")
        account_uid = message.get("account_uid")
        account_type = message.get("ext").get("account_type")
        platform_type = message.get("ext").get("platform_type")

        # 检查请求的CDK内容合法性
        cursor = get_db_cdk().cursor()
        cursor.execute("SELECT * FROM `t_cdk_redeem` WHERE `cdk_name` = %s", cdkey)
        cdk_status = cursor.fetchone()
        if cdk_status is None:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "无效的CDK")

        # 检查CDK状态
        times = cdk_status.get("times")
        enabled = cdk_status.get("enabled")
        cdk_name = cdk_status.get("cdk_name")
        open_time = cdk_status.get("open_time")
        expire_time = cdk_status.get("expire_time")
        template_id = cdk_status.get("template_id")

        if open_time > current_time:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "CDK尚未启用")
        elif expire_time < current_time:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "CDK已过期")
        elif enabled == 0:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "CDK尚未启用")
        elif times <= 0:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "CDK已被使用")

        # 检查对应的CDK中是否有兑换者的信息
        cursor.execute(
            "SELECT * FROM `t_cdk_record` WHERE `cdk_name` = %s AND `uid` = %s",
            (cdkey, uid),
        )
        record = cursor.fetchone()
        if record is not None:
            return json_rsp_common(
                repositories.RES_CDK_EXCHANGE_FAIL, "你已经兑换过这个CDK了"
            )

        # 查询与 CDK 相关的邮件模板 有则拼接邮件内容发出去
        cursor.execute(
            "SELECT * FROM `t_cdk_template` WHERE `cdk_template_id` = %s", template_id
        )
        templates = cursor.fetchone()
        if templates is None:
            return json_rsp_common(
                repositories.RES_CDK_EXCHANGE_FAIL, "邮件模板不存在！CDK发送失败"
            )

        expire_time = unixt_30_days
        title = templates.get("title")
        sender = templates.get("sender")
        content = templates.get("content")
        item_list = templates.get("item_list")
        importance = templates.get("importance")
        is_collectible = templates.get("is_collectible")
        region = get_config()["Muipserver"]["region"]
        content = f"title={title}&sender={sender}&content={content}&expire_time={expire_time}&importance={importance}&is_collectible={is_collectible}&item_list={item_list}&region={region}"
        mail = send(uid, content)

        # 如果邮件功能寄掉了
        if mail is None:
            return json_rsp_common(
                repositories.RES_CDK_EXCHANGE_FAIL, "邮件功能错误！CDK发送失败"
            )
        # 将兑换者的信息计入数据库
        cursor.execute(
            "INSERT INTO `t_cdk_record` (`cdk_name`, `uid`, `account_type`, `account_uid`,`region`, `game`, `platform`, `used_time`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);",
            (
                cdk_name,
                uid,
                account_type,
                account_uid,
                region,
                game,
                platform_type,
                current_time,
            ),
        )
        # 刷新该CDK的使用次数
        times -= 1
        cursor.execute(
            "UPDATE t_cdk_redeem SET times = %s WHERE cdk_name = %s", (times, cdk_name)
        )
        return json_rsp_common(repositories.RES_CDK_EXCHANGE_SUCC, "SEND MAIL SUCC")
    else:
        return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "邮件系统已关闭")
