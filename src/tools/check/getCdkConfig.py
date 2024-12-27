import pymysql

from src.tools.loadconfig    import loadConfig
from src.tools.logger.system import logger


def cdkServiceStatus() -> None:
    config = loadConfig()["Database"]["mysql"]
    conn = pymysql.connect(
        host=config["host"],
        user=config["user"],
        port=config["port"],
        password=config["password"],
        database=config["exchcdk_library_name"],
        charset="utf8",
    ).cursor()

    # 0-5 | 兑换码配置
    template_list = []
    conn.execute("SELECT * FROM `t_cdk_redeem`")    
    if conn.fetchall() == ():
        logger.info(f"兑换码预期配置: null")
    else:
        # 为什么无法引用上面的查询?
        conn.execute("SELECT * FROM `t_cdk_redeem`")
        for data in conn.fetchall():
            cdk_name, is_enable  = data[0], data[3]
            start_time, end_time = data[1], data[2]
            template_id, times   = data[4], data[5]
            template_list.append(template_id)
            logger.info(f"兑换码预期配置: 模板id: {template_id} 名称: {cdk_name} 启用时间: {start_time} 结束时间: {end_time} 是否启用: {is_enable} 剩余次数: {times}")

    # 0-5 | 邮件模板配置
    for template_id in template_list:
        conn.execute(f"SELECT * FROM `t_cdk_template` WHERE `cdk_template_id` = {template_id}")
        if conn.fetchall() == ():
            logger.info(f"兑换码模板配置: id: {template_id} config: null")
        else:
            # 为什么无法引用上面的查询?
            conn.execute(f"SELECT * FROM `t_cdk_template` WHERE `cdk_template_id` = {template_id}")
            for data in conn.fetchall():
                title, sender, content        = data[1], data[2], data[3]
                importance, is_collect, items = data[4], data[5], data[6]
                logger.info(f"兑换码模板配置: 模板id: {template_id} 邮件标题: {title} 发送者: {sender} 邮件内容: {content} 是否星标: {importance} 玩家是否收藏: {is_collect} 奖励物品: {items}")

    return None
