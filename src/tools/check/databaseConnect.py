import pymysql
import redis
import src.tools.repositories as repositories

from src.tools.loadconfig import load_config


# ===================== 数据库检查 ===================== #
def check_redis_connection():
    config = load_config()["Database"]["redis"]
    try:
        redis_client = redis.StrictRedis(
            host=config["host"],
            port=config["port"],
            password=config["password"],
            # db=0,
        )
        if redis_client.ping():
            return True
    except redis.ConnectionError:
        return False


# 检查连接
def check_mysql_connection():
    config = load_config()["Database"]["mysql"]
    try:
        conn = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            charset="utf8",
        )
        conn.close()
        return True
    except pymysql.Error:
        return False


# 检查连接后是否存在库
def check_database_exists():
    config = load_config()["Database"]["mysql"]
    try:
        conn = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            charset="utf8",
        )
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        cursor.close()
        conn.close()
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
            print(f"{repositories.SDK_STATUS_FAIL} 未找到账号管理库")
        elif not found_exchcdk_library:
            print(f"{repositories.SDK_STATUS_FAIL} 未找到CDK管理库")
        elif not found_announce_library:
            print(f"{repositories.SDK_STATUS_FAIL} 未找到公告管理库")
        return False
    except pymysql.Error:
        return False
