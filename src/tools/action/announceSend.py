import time

from src.tools import repositories
from src.tools.response import json_rsp_with_msg
from src.tools.action.dbGet import get_db_ann

# ===================== 公告分发 ===================== #
def announce_send(cmd):
    """
    - 从 config 表中取展示列
    - 从 list 表中取展示列中需要显示的公告内容
    - 从 content 表中获得公告主体内容
    ---
    取消了游戏内外的公告显示区分
    list 表中 type_id 外键 config type_id
    content 表中 ann_id 外键 list ann_id
    """
    cursor = get_db_ann().cursor()

    # 获取公告内容
    if cmd == "undefined":
        main = {"data": {"list": [], "total": 0, "pic_list": [], "pic_total": 0}}

        try:
            cursor.execute(f"SELECT * FROM `t_announce_content`")
            msg = cursor.fetchall()
        except Exception:
            return json_rsp_with_msg(
                repositories.RES_FAIL, "System error, please try again later.", {}
            )

        for config in msg:
            content = {
                "ann_id": config["ann_id"],
                "title": config["title"],
                "subtitle": config["subtitle"],
                "banner": config["banner"],
                "content": config["content"],
                "lang": "zh-cn",
            }
            main["data"]["list"].append(content)
        return json_rsp_with_msg(repositories.RES_SUCCESS, "OK", main)

    # 获取展示列
    else:
        main = {
            "data": {
                "list": [],
                "type_list": [],
                "total": 0,
                "alert": False,
                "alert_id": 0,
                "timezone": 8,
                "t": int(time.time() * 1000),
                "pic_list": [],
                "pic_total": 0,
                "pic_type_list": [],
                "pic_alert": False,
                "pic_alert_id": 0,
                "static_sign": "",
            }
        }
        # 获取公告类型列表
        try:
            cursor.execute("SELECT * FROM `t_announce_config` ORDER BY `id` ASC")
            config = cursor.fetchall()
        except:
            return json_rsp_with_msg(
                repositories.RES_FAIL, "System error, please try again later.", {}
            )

        type_list = []
        for type_entry in config:
            type_list.append(
                {
                    "id": type_entry["id"],
                    "name": type_entry["mi18n_name"],
                    "mi18n_name": type_entry["mi18n_name"],
                }
            )
        main["data"]["type_list"] = type_list

        # 获取客户端要展示的ID
        id_list = [type_id["id"] for type_id in config]

        for id in id_list:
            cursor.execute(f"SELECT * FROM `t_announce_list` WHERE `type_id` = {id}")
            msg = cursor.fetchall()
            type_data = {
                "list": [],
                "type_id": id,
                "type_label": msg[0]["desc"] if msg else "",
            }

            # 如果查询有结果，将内容添加到 type_data 的 list 中
            if msg:
                for config in msg:
                    content = {
                        "ann_id": config["ann_id"],
                        "banner": "",
                        "tag_icon": config["tag_icon"],
                        "login_alert": config["login_alert"],
                        "lang": "zh-cn",
                        "start_time": config["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "end_time": config["end_time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "type": 2,
                        "remind": 0,
                        "alert": 0,
                        "tag_start_time": config["start_time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "tag_end_time": config["end_time"].strftime("%Y-%m-%d %H:%M:%S"),
                        "remind_ver": 1,
                        "has_content": True,
                        "extra_remind": 0,
                    }
                    type_data["list"].append(content)
            main["data"]["list"].append(type_data)
        return json_rsp_with_msg(repositories.RES_SUCCESS, "OK", main)
