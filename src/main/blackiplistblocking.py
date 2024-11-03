try:
    from __main__ import app
except ImportError:
    from main import app

import src.tools.repositories as repositories

from flask_limiter               import Limiter
from flask_limiter.util          import get_remote_address
from flask_limiter.errors        import RateLimitExceeded
from src.tools.response          import jsonRspWithMsg
from src.tools.loadconfig        import loadConfig
from src.tools.action.dbGet      import getMysqlConn, getRedisConn
from src.tools.action.getCountry import getLocation
from src.tools.logger.system     import logger              as sys_log

# 初始化
config = loadConfig()
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

    redis_client = getRedisConn()
    cached = redis_client.get(f"blacklist:{ip_address}")
    if cached is not None:
        return cached == "True"
    
    cursor = getMysqlConn().cursor()
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
        cursor = getMysqlConn().cursor()
        city = getLocation(ip_address)
        insert_sql = "INSERT INTO `t_ip_blacklist` (ip_address, city) VALUES (%s, %s)"
        cursor.execute(insert_sql, (ip_address, city))
        redis_client = getRedisConn()
        redis_client.setex(f"blacklist:{ip_address}", 300, "True")
        sys_log.info(f"目标主机: {ip_address} 访问过于频繁 暂停访问")


# 访问单条路由的超出次数限制
@app.errorhandler(RateLimitExceeded)
def ratelimit_handler(e):
    client_ip = get_remote_address()
    if not is_ip_blacklisted(client_ip):
        blacklist_ip(client_ip)
    sys_log.info(f"目标主机: {client_ip} 访问超过预定峰值 暂停访问")
    return jsonRspWithMsg(repositories.RES_FAIL, "访问次数过多，请稍后重试", {"ip_address": client_ip})


@app.before_request
def ip_blacklist_check():
    client_ip = get_remote_address()
    if client_ip == "127.0.0.1":  # 防止本地主机被拉黑
        return None
    if is_ip_blacklisted(client_ip):
        sys_log.info(f"目标主机: {client_ip} 已在黑名单 禁止访问")
        return jsonRspWithMsg(repositories.RES_FAIL,"你所在的IP已在黑名单中，禁止访问", {"ip_address": client_ip})
