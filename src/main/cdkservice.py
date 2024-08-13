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
from src.tools.database import get_db_cdk
from src.tools.library import authkey, datetime_to_timestamp, send
from src.tools.loadconfig import load_config
from src.tools.response import json_rsp_common

import json
import datetime as dt
import src.tools.repositories as repositories

server_time = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 当前服务器时间
after_30_days = datetime_to_timestamp(
    (dt.datetime.now() + dt.timedelta(minutes=30)).strftime("%Y-%m-%d %H:%M:%S")
)  # 计算30天后的时间-邮件过期


# ===========================游戏内部兑换CDK功能===========================#
@app.route("/common/api/exchangecdk", methods=["GET"])
def cdk_verify():
    def get_request_args():
        cdkey = request.args.get("cdkey")
        auth_key = request.args.get("authkey")
        authkey_ver = request.args.get("authkey_ver")
        return cdkey, auth_key, authkey_ver

    def decrypt_auth_key(auth_key, authkey_ver):
        keys = authkey(auth_key, authkey_ver)
        message = json.loads(keys)
        return message

    def fetch_cdk_status(cdkey):
        db_name = load_config()['Database']['mysql']['exchcdk_library_name']
        cursor = get_db_cdk().cursor()
        cursor.execute("USE `{}`".format(db_name))
        cursor.execute("SELECT * FROM `t_cdk_redeem` WHERE `cdk_name` = %s", cdkey)
        return cursor.fetchone()

    def check_cdk_validity(cdk_status):
        if cdk_status is None:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "无效的兑换码")
        return None  # No error

    def get_cdk_details(cdk_status):
        keys = [
            "times",
            "enabled",
            "cdk_name",
            "open_time",
            "expire_time",
            "template_id",
        ]
        return [cdk_status.get(key) for key in keys]

    def is_cdk_expired(open_time, expire_time, current_time):
        if open_time > current_time:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "兑换码尚未启用")
        elif expire_time < current_time:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "兑换码已过期")
        elif enabled == 0:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "兑换码尚未启用")
        elif times <= 0:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "兑换码已被使用")
        return None  # No error

    def has_already_redeemed(cdkey, uid):
        cursor = get_db_cdk().cursor()
        cursor.execute(
            "SELECT * FROM `t_cdk_record` WHERE `cdk_name` = %s AND `uid` = %s",
            (cdkey, uid),
        )
        return cursor.fetchone() is not None

    def fetch_mail_template(template_id):
        cursor = get_db_cdk().cursor()
        cursor.execute(
            "SELECT * FROM `t_cdk_template` WHERE `cdk_template_id` = %s", template_id
        )
        return cursor.fetchone()

    def send_mail(uid, templates):
        expire_time = after_30_days
        title = templates.get("title")
        sender = templates.get("sender")
        content = templates.get("content")
        item_list = templates.get("item_list")
        importance = templates.get("importance")
        is_collectible = templates.get("is_collectible")
        region = load_config()["Muipserver"]["region"]
        content = (
            f"title={title}&sender={sender}&content={content}"
            + f"&expire_time={expire_time}&importance={importance}"
            + f"&is_collectible={is_collectible}&item_list={item_list}"
            + f"&region={region}"
        )
        return send(uid, content)

    def insert_redeem_record(
        cdk_name,
        uid,
        account_type,
        account_uid,
        region,
        game,
        platform_type,
        server_time,
    ):
        cursor = get_db_cdk().cursor()
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
                server_time,
            ),
        )

    def update_cdk_times(cdk_name, times):
        cursor = get_db_cdk().cursor()
        cursor.execute(
            "UPDATE t_cdk_redeem SET times = %s WHERE cdk_name = %s", (times, cdk_name)
        )

    if not request.args:
        return json_rsp_common(repositories.RES_FAIL,"环境错误")

    # 保证基本参数
    required_params = ['cdkey','sign_type', 'auth_appid', 'authkey_ver','authkey']
    if not all(param in request.args for param in required_params):
        return json_rsp_common(repositories.RES_FAIL,"参数错误")

    # 如果启用CDK
    if load_config()["Setting"]["cdkexchange"]:
        cdkey, auth_key, authkey_ver = get_request_args()
        
        # 尝试解密
        try:
            message = decrypt_auth_key(auth_key, authkey_ver)
        except Exception:
            return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "系统错误")

        uid = message.get("uid")
        game = message.get("game")
        region = message.get("region")
        account_uid = message.get("account_uid")
        account_type = message.get("ext").get("account_type")
        platform_type = message.get("ext").get("platform_type")

        cdk_status = fetch_cdk_status(cdkey)
        error = check_cdk_validity(cdk_status)
        if error:
            return error

        times, enabled, cdk_name, open_time, expire_time, template_id = get_cdk_details(
            cdk_status
        )
        current_time = datetime_to_timestamp(server_time)
        open_time = datetime_to_timestamp(open_time)
        expire_time = datetime_to_timestamp(expire_time)

        cdk_expired = is_cdk_expired(open_time, expire_time, current_time)
        if cdk_expired:
            return cdk_expired

        if has_already_redeemed(cdkey, uid):
            return json_rsp_common(
                repositories.RES_CDK_EXCHANGE_FAIL, "你已经兑换过这个CDK了"
            )

        templates = fetch_mail_template(template_id)
        if templates is None:
            return json_rsp_common(
                repositories.RES_CDK_EXCHANGE_FAIL, "邮件模板不存在！兑换码发送失败"
            )

        mail = send_mail(uid, templates)
        if mail is None:
            return json_rsp_common(
                repositories.RES_CDK_EXCHANGE_FAIL, "邮件功能错误！兑换码发送失败"
            )

        insert_redeem_record(
            cdk_name,
            uid,
            account_type,
            account_uid,
            region,
            game,
            platform_type,
            server_time,
        )

        times -= 1
        update_cdk_times(cdk_name, times)
        return json_rsp_common(repositories.RES_CDK_EXCHANGE_SUCC, {})
    else:
        return json_rsp_common(repositories.RES_CDK_EXCHANGE_FAIL, "邮件系统已关闭")
