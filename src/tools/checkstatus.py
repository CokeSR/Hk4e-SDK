import sys
import yaml
import redis
import pymysql
import src.tools.repositories as repositories
from src.tools.loadconfig import load_config
from src.tools.restoreconfig import recover_config

# ======================redis检查=====================#
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

# ======================mysql检查=====================#
# 检查连接
def check_mysql_connection():
    config = load_config()["Database"]["mysql"]
    try:
        conn = pymysql.connect(
            host=config["host"],
            user=config["user"],
            port=config["port"],
            password=config["password"],
            charset="utf8mb4",
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
            charset="utf8mb4",
        )
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        cursor.close()
        conn.close()
        found_account_library = False
        found_exchcdk_library = False
        for db in databases:
            if db[0] == config["account_library_name"]:
                found_account_library = True
            if db[0] == config["exchcdk_library_name"]:
                found_exchcdk_library = True
        if found_account_library and found_exchcdk_library:
            return True
        elif not found_account_library:
            print(">> [Error] 未找到账号管理库")
        elif not found_exchcdk_library:
            print(">> [Error] 未找到CDK管理库")
        return False
    except pymysql.Error:
        return False


# =====================Config检查完整性=====================#
def check_config_exists():
    try:
        with open(repositories.CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
            try:
                config = yaml.safe_load(file)
                return True
            except Exception as err:
                print(f"未知错误：{err}")
                return False
    except FileNotFoundError as err:
        print(
            "#=====================未检测到[Config]文件！运行失败=====================#"
        )
        select = input(">> 是否创建新的[Config]文件？(y/n):").strip().lower()
        if select == "y":
            recover_config()
            print(">> [Successful]-[Config]文件创建成功")
            sys.exit(1)
        elif select == "n":
            print(">> [Waring] 取消创建[Config]文件，停止运行...")
            sys.exit(1)
        else:
            print(">> [Error] 非法输入！停止运行...")
            sys.exit(1)


def check_config():
    config = load_config()
    required_settings = {
        "Setting": {
            "listen": str,
            "port": int,
            "reload": bool,
            "debug": bool,
            "threaded": bool,
            "high_frequency_logs": bool,
            "cdkexchange": bool,
            "secret_key": str,
        },
        "Database": {
            "mysql": {
                "host": str,
                "user": str,
                "port": int,
                "account_library_name": str,
                "exchcdk_library_name": str,
                "password": str,
            },
            "redis": {
                "host": str,
                "port": int,
                "password": str,
            },
        },
        "Login": {
            "disable_mmt": bool,
            "disable_regist": bool,
            "disable_email_bind_skip": bool,
            "enable_email_captcha": bool,
            "enable_ps_bind_account": bool,
            "email_bind_remind": bool,
            "email_verify": bool,
            "realperson_required": bool,
            "safe_mobile_required": bool,
            "device_grant_required": bool,
            "initialize_firebase": bool,
            "bbs_auth_login": bool,
            "fetch_instance_id": bool,
            "enable_flash_login": bool,
        },
        "Player": {
            "disable_ysdk_guard": bool,
            "enable_announce_pic_popup": bool,
            "protocol": bool,
            "qr_enabled": bool,
            "qr_bbs": bool,
            "qr_cloud": bool,
            "enable_user_center": bool,
            "guardian_required": bool,
            "realname_required": bool,
            "heartbeat_required": bool,
        },
        "Reddot": {
            "display": bool,
        },
        "Announce": {
            "remind": bool,
            "alert": bool,
            "extra_remind": bool,
        },
        "Security": {
            "access_limits": int,
            "verify_code_length": int,
            "token_length": int,
            "min_password_len": int,
        },
        "Auth": {
            "enable_password_verify": bool,
            "enable_guest": bool,
        },
        "Other": {
            "modified": bool,
            "serviceworker": bool,
            "new_register_page_enable": bool,
            "kcp_enable": bool,
            "enable_web_dpi": bool,
            "list_price_tierv2_enable": bool,
        },
        "Muipserver": [],
        "Dispatch": ["list"],
        "Region": [],
        "Gateserver": [],
        "Mail": {
            "ENABLE": bool,
            "MAIL_SERVER": str,
            "MAIL_PORT": int,
            "MAIL_USE_TLS": bool,
            "MAIL_USE_SSL": bool,
            "MAIL_USERNAME": str,
            "MAIL_PASSWORD": str,
            "MAIL_DEFAULT_SENDER": str,
        },
    }

    missing_keys = []
    invalid_type_keys = []
    # 递归检查
    def check_settings(config_section, required_settings_section, path):
        if isinstance(required_settings_section, dict):
            for key, expected_type in required_settings_section.items():
                if key not in config_section:
                    missing_keys.append(f"{path}.{key}")
                else:
                    if isinstance(expected_type, dict):
                        check_settings(config_section[key], expected_type, f"{path}.{key}")
                    else:
                        if not isinstance(config_section[key], expected_type):
                            invalid_type_keys.append(f"{path}.{key} (必须是{expected_type.__name__}类型)")
        elif isinstance(required_settings_section, list):
            for setting in required_settings_section:
                if setting not in config_section:
                    missing_keys.append(f"{path}.{setting}")
    # 细节
    for section, settings in required_settings.items():
        if section not in config:
            missing_keys.append(section)
        else:
            check_settings(config[section], settings, section)

    if missing_keys or invalid_type_keys:
        if missing_keys:
            print(">> [Error]-[Config]配置项缺失:\n" + "\n".join(missing_keys))
        if invalid_type_keys:
            print(">> [Error]-[Config]未知的配置:\n" + "\n".join(invalid_type_keys))
        return False
    return True

"""
try:
    if not check_config():
        print("Configuration check failed.")
except FileNotFoundError:
    print("Configuration file not found.")
except yaml.YAMLError as e:
    print(f"Error loading configuration: {e}")
"""

# 单独拎出来 检查region对不对
def check_region():
    try:
        for entry in load_config()["Region"]:
            if (
                "name" not in entry
                or not entry["name"]
                or "title" not in entry
                or not entry["title"]
                or "dispatchUrl" not in entry
                or not entry["dispatchUrl"]
            ):
                print(">> [Error]-[Region]配置表中有项为空或不完全")
                return False
    except:
            print(">> [Error]-[Region]配置项损坏或缺失")
            return False
    return True


# 检查 gateserver
def check_gate():
    try:
        for entry in load_config()["Gateserver"]:
            if ("ip" not in entry or not entry["ip"] or "port" not in entry):
                print(">> [Error]-[Gateserver]配置项损坏或缺失")
                return False
    except:
        print(">> [Error]-[Gateserver]配置表中有项为空或不完全")
        return False
    return True


# 检查dispatch_list 每个字段是不是空的 是空的你玩鸡毛
def check_dispatch():
    try:
        config = load_config()["Dispatch"]
        if "list" not in config or not isinstance(config["list"], dict):
            print(">> [Error]-[Dispatch]配置项损坏或缺失")
            return False
        for name, url in config["list"].items():
            if (
                not isinstance(name, str)
                or not isinstance(url, str)
                or not url.startswith("http" or "https")
            ):
                print(">> [Error]-[Disaptch]配置表中有项为空或无 Http 标识")
                return False
    except:
        print(">> [Error]-[Disaptch]配置表中有项为空")
        return False
    return True


# 检查Muipserver每个字段是不是空的 是空的你玩鸡毛
def check_muipserver():
    try:
        config = load_config()["Muipserver"]
        if not isinstance(config["address"], str) or not isinstance(config["port"], int):
            print(">> [Error]-[Muipserver]配置表中所设置的格式不正确(address:str|port:int)")
            return False
        if (
            not config["address"]
            or not config["region"]
            or not config["port"]
            or not config["sign"]
        ):
            print(">> [Error]-[Muipserver]配置表中有项为空")
            return False
    except:
        print(">> [Error]-[Muipserver]配置项损坏或缺失")
        return False
    return True

"""
if (
    "address" not in config
    or "region" not in config
    or "port" not in config
    or "sign" not in config
):
    print(">> [Error]-[Muipserver]配置项损坏或缺失")
    return False
"""