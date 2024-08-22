try:
    from __main__ import app
except ImportError:
    from main import app

import src.tools.repositories as repositories

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_limiter.errors import RateLimitExceeded
from src.tools.response import json_rsp_with_msg
from src.tools.loadconfig import load_config
from src.tools.action.dbGet import get_db, get_redis
from src.tools.action.getCountry import get_location

config = load_config()
# 初始化
limiter = Limiter(
    get_remote_address,
    app=app,
    # db 库默认 0
    storage_uri=f"redis://:{config['Database']['redis']['password']}@{config['Database']['redis']['host']}:{config['Database']['redis']['port']}/0",
    # 单IP 每分钟访问最多100次, 过了直接拉黑
    default_limits=[f"{config['Security']['access_limits']} per minute"],
)


# 黑名单检查
# 读取 mysql 是否有IP记录并缓存到 redis 有效期300秒
def is_ip_blacklisted(ip_address):
    if ip_address == "127.0.0.1":  # 防止本地主机被拉黑
        return False

    redis_client = get_redis()
    cached = redis_client.get(f"blacklist:{ip_address}")
    if cached is not None:
        return cached == "True"
    
    cursor = get_db().cursor()
    sql = "SELECT COUNT(*) as count FROM `t_ip_blacklist` WHERE ip_address = %s"
    cursor.execute(sql, (ip_address,))
    result = cursor.fetchone()
    if result and result["count"] > 0:
        redis_client.setex(f"blacklist:{ip_address}", 300, "True")
        return True
    else:
        redis_client.setex(f"blacklist:{ip_address}", 300, "False")
        return False


# 记录并拉黑IP
# 通过 is_ip_blacklisted 检查IP地址是否已在黑名单中
# 如果不在 将IP地址和相关信息插入 mysql 并更新 Redis 缓存
def blacklist_ip(ip_address):
    if ip_address == "127.0.0.1":  # 防止本地主机被拉黑
        return None

    if not is_ip_blacklisted(ip_address):
        cursor = get_db().cursor()
        city = get_location(ip_address)
        insert_sql = "INSERT INTO `t_ip_blacklist` (ip_address, city) VALUES (%s, %s)"
        cursor.execute(insert_sql, (ip_address, city))
        redis_client = get_redis()
        redis_client.setex(f"blacklist:{ip_address}", 300, "True")


# 访问单条路由的超出次数限制
@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    client_ip = get_remote_address()
    if not is_ip_blacklisted(client_ip):
        blacklist_ip(client_ip)
    return json_rsp_with_msg(
        repositories.RES_FAIL, "访问次数过多，请稍后重试", {"ip_address": client_ip}
    )


@app.before_request
def ip_blacklist_check():
    client_ip = get_remote_address()
    if client_ip == "127.0.0.1":  # 防止本地主机被拉黑
        return None
    if is_ip_blacklisted(client_ip):
        return json_rsp_with_msg(
            repositories.RES_FAIL,"你所在的IP已在黑名单中，禁止访问", {"ip_address": client_ip}
        )
