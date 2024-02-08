try:
    from __main__ import app
except ImportError:
    from main import app
import sys
import pymysql
import settings.database as database

from flask import g
from settings.library import check_config_exists
from settings.checkstatus import check_mysql_connection

#=====================数据库创建=====================#
# 在原有的基础上直接cv 懒得思考了
# 重置数据库的时候账号管理连着CDK配置一起扬了
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        config = check_config_exists()['Database']
        db = g._database = pymysql.connect(
            host=config['host'],
            user=config['user'],
            port=config['port'],
            password=config['password'],
            database=config['account_library_name'],
            cursorclass=pymysql.cursors.DictCursor
        )
    return db

def get_db_cdk():
    db = getattr(g, '_database', None)
    if db is None:
        config = check_config_exists()['Database']
        db = g._database = pymysql.connect(
            host=config['host'],
            user=config['user'],
            port=config['port'],
            password=config['password'],
            database=config['exchcdk_library_name'],
            cursorclass=pymysql.cursors.DictCursor
        )
    return db

# 账号管理库
def init_db(auto_create = check_config_exists()['Database']['autocreate']):
    config = check_config_exists()['Database']
    conn = pymysql.connect(
        host=config['host'],
        user=config['user'],
        port=config['port'],
        password=config['password'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    if auto_create:
        cursor.execute("CREATE DATABASE IF NOT EXISTS `{}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(config['account_library_name']))
    cursor.execute("USE `{}`".format(config['account_library_name']))
    cursor.execute("DROP TABLE IF EXISTS `t_accounts`")
    cursor.execute("DROP TABLE IF EXISTS `t_accounts_tokens`")
    cursor.execute("DROP TABLE IF EXISTS `t_accounts_guests`")
    cursor.execute("DROP TABLE IF EXISTS `t_accounts_events`")
    cursor.execute("DROP TABLE IF EXISTS `t_accounts_thirdparty`")
    cursor.execute("DROP TABLE IF EXISTS `t_thirdparty_tokens`")
    cursor.execute("DROP TABLE IF EXISTS `t_combo_tokens`")
    
    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_accounts` (
                     `uid` INT AUTO_INCREMENT PRIMARY KEY COMMENT '玩家UID',
                     `name` VARCHAR(255) UNIQUE COMMENT '用户名',
                     `mobile` VARCHAR(255) UNIQUE COMMENT '手机号',
                     `email` VARCHAR(255) UNIQUE COMMENT '电子邮件',
                     `password` VARCHAR(255) COMMENT '哈希密码',
                     `type` INT NOT NULL COMMENT '类型',
                     `epoch_created` INT NOT NULL COMMENT '时间戳'
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT='玩家账号信息表'
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_accounts_tokens` (
                     `uid` INT NOT NULL COMMENT '玩家UID',
                     `token` VARCHAR(255) NOT NULL COMMENT '登录Token',
                     `device` VARCHAR(255) NOT NULL COMMENT '设备ID',
                     `ip` VARCHAR(255) NOT NULL COMMENT '登录IP',
                     `epoch_generated` INT NOT NULL COMMENT '时间戳',
                     PRIMARY KEY(`uid`,`token`)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT='账号登录token'
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_accounts_guests` (
                     `uid` INT NOT NULL COMMENT '玩家UID',
                     `device` VARCHAR(255) NOT NULL COMMENT '设备ID',
                     PRIMARY KEY(`uid`,`device`)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT='游客登录信息表'
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_accounts_events` (
                     `uid` INT NOT NULL COMMENT '玩家UID',
                     `method` VARCHAR(255) NOT NULL COMMENT '登录方式',
                     `account_type` INT NOT NULL COMMENT '账号类型',
                     `account_id` INT NOT NULL COMMENT '账号ID',
                     `platform` INT NOT NULL COMMENT '平台',
                     `region` VARCHAR(255) NOT NULL COMMENT '区服信息',
                     `biz_game` VARCHAR(255) NOT NULL,
                     `epoch_created` INT NOT NULL COMMENT '时间戳',
                     PRIMARY KEY(`epoch_created`)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT='账号活动记录表 由GameServer控制'
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_accounts_thirdparty` (
                     `uid` INT NOT NULL COMMENT '玩家UID',
                     `type` INT NOT NULL COMMENT '类型',
                     `external_name` VARCHAR(255) NOT NULL COMMENT '标识名称',
                     `external_id` INT NOT NULL COMMENT '标识ID',
                     PRIMARY KEY(`uid`,`type`)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT='第三方账号登录信息表'
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_thirdparty_tokens` (
                     `uid` INT NOT NULL COMMENT '玩家UID',
                     `type` INT NOT NULL COMMENT '类型',
                     `token` VARCHAR(255) NOT NULL COMMENT '登录Token'
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT='第三方账号登录token'
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_combo_tokens` (
                     `uid` INT NOT NULL COMMENT '玩家UID',
                     `token` VARCHAR(255) NOT NULL COMMENT '登录Token',
                     `device` VARCHAR(255) NOT NULL COMMENT '设备ID',
                     `ip` VARCHAR(255) NOT NULL COMMENT '登录IP',
                     `epoch_generated` INT NOT NULL COMMENT '时间戳',
                     PRIMARY KEY(`uid`)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT='设备信息token'
    """)
    conn.commit()
    conn.close()

# CDK管理库
def init_db_cdk(auto_create = check_config_exists()['Database']['autocreate']):
    config = check_config_exists()['Database']
    conn = pymysql.connect(
        host=config['host'],
        user=config['user'],
        port=config['port'],
        password=config['password'],
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    if auto_create:
        cursor.execute("CREATE DATABASE IF NOT EXISTS `{}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci".format(config['exchcdk_library_name']))
    cursor.execute("USE `{}`".format(config['exchcdk_library_name']))
    cursor.execute("DROP TABLE IF EXISTS `t_cdk_record`")
    cursor.execute("DROP TABLE IF EXISTS `t_cdk_redeem`")
    cursor.execute("DROP TABLE IF EXISTS `t_cdk_template`")

    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_cdk_record` (
                    `cdk_name` varchar(255) NOT NULL COMMENT '使用的CDK',
                    `uid` INT NOT NULL COMMENT '玩家UID',
                    `account_type` varchar(255) NOT NULL COMMENT '账号类型',
                    `account_uid` INT NOT NULL COMMENT '账号ID',
                    `region` varchar(255) NOT NULL COMMENT '所在区服',
                    `game` varchar(255) NOT NULL COMMENT 'cn/global',
                    `platform` varchar(255) NOT NULL COMMENT '客户端平台',
                    `used_time` INT NOT NULL COMMENT '使用时间'
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT '玩家CDK兑换记录'
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_cdk_redeem` (
                    `cdk_name` varchar(255) NOT NULL COMMENT 'CDK配置',
                    `open_time` INT NOT NULL COMMENT '启用时间',
                    `expire_time` INT NOT NULL COMMENT '过期时间',
                    `enabled` INT NOT NULL COMMENT '1启用0不启用',
                    `template_id` INT NOT NULL COMMENT '与CDK邮件配置相对应',
                    `times` INT NOT NULL COMMENT '使用次数',
                    PRIMARY KEY (`cdk_name`)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT 'CDK配置'
    """)
    cursor.execute("""CREATE TABLE IF NOT EXISTS `t_cdk_template` (
                    `cdk_template_id` int NOT NULL COMMENT '与CDK配置相对应',
                    `title` varchar(255) NOT NULL COMMENT '邮件标头',
                    `sender` varchar(255) NOT NULL COMMENT '署名',
                    `content` varchar(255) NOT NULL COMMENT '邮件内容',
                    `importance` INT NOT NULL COMMENT '是否是星标邮件(0/1)',
                    `is_collectible` varchar(255) NOT NULL COMMENT '是否纳入收藏夹(true/false)',
                    `item_list` varchar(255) NOT NULL COMMENT '物品id:数量 逗号分隔',
                    PRIMARY KEY (`cdk_template_id`)
                  ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
                  COMMENT 'CDK邮件配置'
    """)
    conn.commit()
    conn.close()
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.commit()
        db.close()

# 重置数据库
def initialize_database():
    print(">> [Waring] 正在初始化数据库结构(清空数据)...")
    database.init_db()
    database.init_db_cdk()
    print(">> [Successful] 初始化数据库完成")