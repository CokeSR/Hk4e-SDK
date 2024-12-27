import sys
import yaml
import src.tools.repositories        as repositories

from src.tools.logger.system         import logger              as sys_log
from src.tools.loadconfig            import loadConfig
from src.tools.action.configRebuild  import recover_config


# ===================== Config检查完整性 ===================== #
def checkConfigYamlExists():
    try:
        with open(repositories.CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
            try:
                config = yaml.safe_load(file)
                for index, key in config.items():
                    sys_log.info(f"加载配置 {index}: {key}")
                return True
            except Exception as err:
                print(f"未知错误: {err}")
                return False
    except FileNotFoundError as err:
        print("#===================== 未检测到 Config 文件 =====================#")
        select = (input(f"是否创建新的 Config 文件？(y/n):").strip().lower())
        if select == "y":
            recover_config()
            print(f"Config 文件创建成功")
            sys.exit(1)
        elif select == "n":
            print(f"取消创建 Config 文件，停止运行...")
            sys.exit(1)
        else:
            print(f"非法输入！停止运行...")
            sys.exit(1)


def checkConfigYaml():
    config = loadConfig()
    required_settings = {
        "Setting": {
            "ssl": bool,
            "ssl_self_signed": bool,
            "listen": str,
            "port": int,
            "reload": bool,
            "debug": bool,
            "threaded": bool,
            "high_frequency_logs": bool,
            "cdkexchange": bool,
        },
        "Database": {
            "mysql": {
                "host": str,
                "user": str,
                "port": int,
                "account_library_name": str,
                "exchcdk_library_name": str,
                "announce_library_name": str,
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
        "Muipserver": {
            "is_ssl": bool,
            "address": str,
            "region": str,
            "port": int,
            "sign": str,
        },
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
            sys_log.error(f"Config 配置项缺失: " + "\n".join(missing_keys))
        if invalid_type_keys:
            sys_log.error(f"Config 未知的配置: " + "\n".join(invalid_type_keys))
        return False
    return True


# 单独拎出来 检查region对不对
def checkRegionConfig():
    try:
        for entry in loadConfig()["Region"]:
            if (
                "name" not in entry
                or not entry["name"]
                or "title" not in entry
                or not entry["title"]
                or "dispatchUrl" not in entry
                or not entry["dispatchUrl"]
            ):
                sys_log.error(f"[Region]配置表中有项为空或不完全")
                return False
    except:
        sys_log.error(f"[Region]配置项损坏或缺失")
        return False
    return True


# 检查 gateserver
def checkGateserver():
    try:
        for entry in loadConfig()["Gateserver"]:
            if "ip" not in entry or not entry["ip"] or "port" not in entry:
                sys_log.error(f"[Gateserver]配置项损坏或缺失")
                return False
    except:
        sys_log.error(f"[Gateserver]配置表中有项为空或不完全")
        return False
    return True


# 检查dispatch_list 每个字段是不是空的 是空的你玩鸡毛
def checkDispatch():
    try:
        config = loadConfig()["Dispatch"]
        if "list" not in config or not isinstance(config["list"], dict):
            sys_log.error(f"[Dispatch]配置项损坏或缺失")
            return False
        for name, url in config["list"].items():
            if (not isinstance(name, str) or not isinstance(url, str) or not url.startswith("http" or "https")):
                sys_log.error(f"[Disaptch]配置表中有项为空或无 Http 标识")
                return False
    except:
        sys_log.error(f"[Disaptch]配置表中有项为空")
        return False
    return True


# 检查Muipserver每个字段是不是空的 是空的你玩鸡毛
def checkMuipservice():
    try:
        config = loadConfig()["Muipserver"]
        if not isinstance(config["address"], str) or not isinstance(config["port"], int):
            sys_log.error(f"[Muipserver]配置表中所设置的格式不正确(address:str|port:int)")
            return False
        if (not config["address"] or not config["region"] or not config["port"] or not config["sign"]):
            sys_log.error(f"[Muipserver]配置表中有项为空")
            return False
    except:
        sys_log.error(f"[Muipserver]配置项损坏或缺失")
        return False
    return True
