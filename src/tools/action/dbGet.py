import redis
import pymysql

from flask                  import g
from src.tools.loadconfig   import loadConfig

# ===================== 数据库连接 ===================== #
def getRedisConn():
    db = getattr(g, "_redis", None)
    if db is None:
        config = loadConfig()["Database"]["redis"]
        db = redis.StrictRedis(
            host=config["host"],
            port=config["port"],
            password=config["password"],
            db=0,
            decode_responses=True,
        )
        g._redis = db
    return db


def getMysqlConn():
    db = getattr(g, "_database", None)
    if db is None:
        config = loadConfig()["Database"]["mysql"]
        db = g._database = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            database=config["account_library_name"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    return db


def getMysqlConn_cdk():
    db = getattr(g, "_database", None)
    if db is None:
        config = loadConfig()["Database"]["mysql"]
        db = g._database = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            database=config["exchcdk_library_name"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    return db


def getMysqlConn_ann():
    db = getattr(g, "_database", None)
    if db is None:
        config = loadConfig()["Database"]["mysql"]
        db = g._database = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            database=config["announce_library_name"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
    return db
