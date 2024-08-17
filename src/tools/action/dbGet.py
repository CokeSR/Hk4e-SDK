import redis
import pymysql

from flask import g
from src.tools.loadconfig import load_config

# ===================== 数据库连接 ===================== #


def get_redis():
    db = getattr(g, "_redis", None)
    if db is None:
        config = load_config()["Database"]["redis"]
        db = redis.StrictRedis(
            host=config["host"],
            port=config["port"],
            password=config["password"],
            db=0,
            decode_responses=True,
        )
        g._redis = db
    return db


def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        config = load_config()["Database"]["mysql"]
        db = g._database = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            database=config["account_library_name"],
            cursorclass=pymysql.cursors.DictCursor,
        )
    return db


def get_db_cdk():
    db = getattr(g, "_database", None)
    if db is None:
        config = load_config()["Database"]["mysql"]
        db = g._database = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            database=config["exchcdk_library_name"],
            cursorclass=pymysql.cursors.DictCursor,
        )
    return db


def get_db_ann():
    db = getattr(g, "_database", None)
    if db is None:
        config = load_config()["Database"]["mysql"]
        db = g._database = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            database=config["announce_library_name"],
            cursorclass=pymysql.cursors.DictCursor,
        )
    return db
