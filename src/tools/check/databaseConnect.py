import redis
import pymysql

from src.tools.logger.system         import logger              as sys_log
from src.tools.loadconfig            import loadConfig


# ===================== 数据库检查 ===================== #
def checkRedisConnect():
    config = loadConfig()["Database"]["redis"]
    try:
        redis_client = redis.StrictRedis(
            host=config["host"],
            port=config["port"],
            password=config["password"],
        )
        if redis_client.ping():
            return True
    except redis.ConnectionError:
        return False


# 检查连接
def checkMysqlConnect():
    config = loadConfig()["Database"]["mysql"]
    try:
        conn = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            charset="utf8",
            autocommit=True
        )
        conn.close()
        return True
    except pymysql.Error:
        return False


# 检查连接后是否存在库
def checkDatabaseExists():
    config = loadConfig()["Database"]["mysql"]
    try:
        conn = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            charset="utf8",
            autocommit=True
        )
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # 检查库是否存在 但不检查表
        found_account_library = False
        found_exchcdk_library = False
        found_announce_library = False

        for db in databases:
            if db[0] == config["account_library_name"]:
                found_account_library = True
            if db[0] == config["exchcdk_library_name"]:
                found_exchcdk_library = True
            if db[0] == config["announce_library_name"]:
                found_announce_library = True

        if found_account_library and found_exchcdk_library:
            return True
        elif not found_account_library:
            sys_log.error(f"未找到账号管理库")
        elif not found_exchcdk_library:
            sys_log.error(f"未找到CDK管理库")
        elif not found_announce_library:
            sys_log.error(f"未找到公告管理库")
        return False
    except pymysql.Error:
        return False
