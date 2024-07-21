import yaml
import pymysql
from settings.loadconfig import load_config

#======================mysql检查=====================#
# 检查连接
def check_mysql_connection():
    config = load_config()['Database']
    try:
        conn = pymysql.connect(
            host=config['host'],
            user=config['user'],
            port=config['port'],
            password=config['password'],
            charset='utf8mb4'
        )
        conn.close()
        return True
    except pymysql.Error:
        return False

# 检查连接后是否存在库
def check_database_exists():
    config = load_config()['Database']
    try:
        conn = pymysql.connect(
            host=config['host'],
            user=config['user'],
            port=config['port'],
            password=config['password'],
            charset='utf8mb4'
        )
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = cursor.fetchall()
        cursor.close()
        conn.close()
        found_account_library = False
        found_exchcdk_library = False
        for db in databases:
            if db[0] == config['account_library_name']:
                found_account_library = True
            if db[0] == config['exchcdk_library_name']:
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

#=====================Config检查完整性=====================#
def check_config():
    try:
        config = load_config()
        required_settings = {
            'Setting': ['listen', 'port', 'reload', 'debug', 'threaded', 'high_frequency_logs', 'cdkexchange','secret_key'],
            'Database': ['host', 'user', 'port', 'autocreate','account_library_name','exchcdk_library_name','password'],
            'Login': ['disable_mmt', 'disable_regist', 'disable_email_bind_skip', 'enable_email_captcha', 'enable_ps_bind_account', 'email_bind_remind', 'email_verify', 'realperson_required', 'safe_mobile_required', 'device_grant_required', 'initialize_firebase', 'bbs_auth_login', 'fetch_instance_id', 'enable_flash_login'],
            'Player': ['disable_ysdk_guard', 'enable_announce_pic_popup', 'protocol', 'qr_enabled', 'qr_bbs', 'qr_cloud', 'enable_user_center', 'guardian_required', 'realname_required', 'heartbeat_required'],
            'Announce': ['remind', 'alert', 'extra_remind'],
            'Security': ['token_length', 'min_password_len'],
            'Auth': ['enable_password_verify', 'enable_guest'],
            'Other': ['modified', 'serviceworker', 'new_register_page_enable', 'kcp_enable', 'enable_web_dpi', 'list_price_tierv2_enable'],
            'Muipserver': ['address','region','port','sign'],
            'Dispatch': ['list'],
            'Mail': ['ENABLE', 'MAIL_SERVER', 'MAIL_PORT', 'MAIL_USE_TLS', 'MAIL_USE_SSL', 'MAIL_USERNAME', 'MAIL_PASSWORD', 'MAIL_DEFAULT_SENDER']
        }
        for section, settings in required_settings.items():
            if section not in config:
                return False
            for setting in settings:
                if setting not in config[section]:
                    return False
        return True
    except FileNotFoundError:
        return False
    except yaml.YAMLError:
        return False

# 单独拎出来 检查region对不对
def check_region():
    for entry in load_config()['Gateserver']:
        if ('name' not in entry or not entry['name'] or
            'title' not in entry or not entry['title'] or
            'dispatchUrl' not in entry or not entry['dispatchUrl']):
            print(">> [Error]-[Gateserver]配置表中有项为空或不完全")
            return False
    return True

# 检查dispatch_list 每个字段是不是空的 是空的你玩鸡毛
def check_dispatch():
    config = load_config()['Dispatch']
    if ('list' not in config or not isinstance(config['list'], dict)):
        print(">> [Error]-[Dispatch]配置项损坏")
        return False
    for name, url in config['list'].items():
        if not isinstance(name, str) or not isinstance(url, str) or not url.startswith('http' or 'https'):
            print(">> [Error]-[Disaptch]配置表中有项为空")
            return False
    return True

# 检查Muipserver每个字段是不是空的 是空的你玩鸡毛
def check_muipserver():
    config = load_config()['Muipserver']
    if ('address' not in config or 'region' not in config or 'port' not in config or 'sign' not in config):
        print(">> [Error]-[Muipserver]配置项损坏")
        return False
    if (not isinstance(config['address'], str) or
        not isinstance(config['port'], int)):
        print(">> [Error]-[Muipserver]配置表中所设置的格式不正确(address:str|port:int)")
        return False
    if (not config['address'] or not config['region'] or not config['port']):
        print(">> [Error]-[Muipserver]配置表中有项为空")
        return False
    return True