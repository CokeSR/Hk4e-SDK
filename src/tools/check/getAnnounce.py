import pymysql

from src.tools.loadconfig    import loadConfig
from src.tools.logger.system import logger


def announceStatus() -> None:
    config = loadConfig()["Database"]["mysql"]
    conn = pymysql.connect(
        host=config["host"],
        user=config["user"],
        port=config["port"],
        password=config["password"],
        database=config["announce_library_name"],
        charset="utf8",
    ).cursor()

    # 0-1 | 公告展示栏
    config_id = []
    conn.execute("""SELECT * FROM `t_announce_config` ORDER BY `id` ASC""")
    for mi18n in conn.fetchall():
        id, mi18n_name = mi18n[0], mi18n[1]
        config_id.append(id)
        logger.info(f"公告展示设置: id: {id} mi18n: {mi18n_name}")

    # 0-6 | 公告展示配置
    ann_id = []
    for id in config_id:
        conn.execute(f"SELECT * FROM `t_announce_list` WHERE `type_id` = {id}")
        if conn.fetchall() == ():
            logger.info(f"公告显示配置: id: {id} config: null")
        else:
            # 为什么无法引用上面的查询?
            conn.execute(f"SELECT * FROM `t_announce_list` WHERE `type_id` = {id}")
            for data in conn.fetchall():
                id, tag_icon          = data[1], data[4]
                start_time, end_time  = data[2], data[3]
                login_alert, desc     = data[5], data[6]
                
                ann_id.append(id)
                ann_desc = "null" if len(desc) == 0 else desc
                
                logger.info(f"公告显示配置: id: {id} config: 公告ID: {id} 启用时间: {start_time} 结束时间: {end_time} 图标: {tag_icon} 红点显示: {login_alert} 备注: {ann_desc}")

    # 0-5 | 公告展示内容
    for id in ann_id:
        conn.execute(f"SELECT * FROM `t_announce_content` WHERE `ann_id` = {id}")
        if conn.fetchall() == ():
            logger.info(f"公告内容配置: id: {id} config: null")
        else:
            # 为什么无法引用上面的查询?
            conn.execute(f"SELECT * FROM `t_announce_content` WHERE `ann_id` = {id}")
            for data in conn.fetchall():
                desc = data[5]
                subtitle, title = data[1], data[2]
                img_url, content = data[3], data[4]

                banner   = "null" if len(img_url) == 0 else img_url
                ann_desc = "null" if len(desc) == 0 else desc

                logger.info(f"公告内容配置: id: {id} 左侧显示: {subtitle} 首页标题: {title} 背景图: {banner} 文本内容: {content} 备注: {ann_desc}")
    
    return None
