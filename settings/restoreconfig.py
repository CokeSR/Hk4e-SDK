import yaml
import settings.repositories as repositories

#=====================[Config]恢复=====================#
# 对于在根目录下没有config或破损的留一个模板来创建
def recover_config():
    config = {
            'Setting': {
                'listen': '{{%YOUR_SDK_ADDRESS%}}',
                'port': '{{%YOUR_SDK_PORT%}}',
                'reload': False,
                'debug': False,
                'threaded': False,
                'high_frequency_logs': False,
                'cdkexchange': False,
                'secret_key': 'cokeserver2022'
            },
            'Database': {
                'host': '{{%SDK_ADDRESS%}}',
                'user': '{{%YOUR_MYSQL_USER%}}',
                'port': '{{%YOUR_MYSQL_PORT%}}',
                'autocreate': False,
                'account_library_name': 'hk4e-accounts-cokeserver',
                'exchcdk_library_name': 'hk4e-cdk-cokeserver',
                'password': '{{%YOUR_MYSQL_PASSWD%}}'
            },
            'Login': {
                'disable_mmt': False,
                'disable_regist': False,
                'disable_email_bind_skip': False,
                'enable_email_captcha': False,
                'enable_ps_bind_account': False,
                'email_bind_remind': False,
                'email_verify': False,
                'realperson_required': False,
                'safe_mobile_required': False,
                'device_grant_required': False,
                'initialize_firebase': False,
                'bbs_auth_login': False,
                'fetch_instance_id': False,
                'enable_flash_login': False
            },
            'Player': {
                'disable_ysdk_guard': False,
                'enable_announce_pic_popup': False,
                'protocol': False,
                'qr_enabled': False,
                'qr_bbs': False,
                'qr_cloud': False,
                'enable_user_center': False,
                'guardian_required': False,
                'realname_required': False,
                'heartbeat_required': False
            },
            'Reddot': {
                'display': False
            },
            'Announce': {
                'remind': False,
                'alert': False,
                'extra_remind': False
            },
            'Security': {
                'token_length': 32,
                'min_password_len': 8
            },
            'Auth': {
                'enable_password_verify': False,
                'enable_guest': False
            },
            'Other': {
                'modified': False,
                'serviceworker': False,
                'new_register_page_enable': False,
                'kcp_enable': False,
                'enable_web_dpi': False,
                'list_price_tierv2_enable': False
            },
            'Muipserver':{
                'address': '{{%MUIP_IP%}}',
                'region': '{{%SERVER_REGION%}}',
                'port': '{{%MUIP_PORT%}}',
                'sign': '{{%MUIP_SIGN%}}'
            },
            'Dispatch': {
                'list': {
                    'dev_docker': 'http://{{%DISPATCH_ADDRESS%}}:{{%DISPATCH_PORT%}}',
                    'dev_client': 'http://{{%DISPATCH_ADDRESS%}}:{{%DISPATCH_PORT%}}',
                    'dev_common': 'http://{{%DISPATCH_ADDRESS%}}:{{%DISPATCH_PORT%}}'
                }
            },
            'Gateserver': [
                {
                    'name': 'dev_docker',
                    'title': 'live-FormalChannel',
                    'dispatchUrl': 'http://{{%SDK_ADDRESS%}}:{{%YOUR_SDK_PORT%}}/query_region/dev_docker'
                },
                {
                    'name': 'dev_client',
                    'title': 'Dev-TestChannel-1',
                    'dispatchUrl': 'http://{{%SDK_ADDRESS%}}:{{%YOUR_SDK_PORT%}}/query_region/dev_client'
                },
                {
                    'name': 'dev_common',
                    'title': 'Dev-TestChannel-2',
                    'dispatchUrl': 'http://{{%SDK_ADDRESS%}}:{{%YOUR_SDK_PORT%}}/query_region/dev_common'
                }
            ],
            'Mail': {
                'ENABLE': False,
                'MAIL_SERVER': 'smtp.qq.com',
                'MAIL_PORT': 587,
                'MAIL_USE_TLS': False,
                'MAIL_USE_SSL': False,
                'MAIL_USERNAME': '{{%EMAIL_ADDRESS%}}',
                'MAIL_PASSWORD': '{{%EMAIL_STMP_PASSWORD%}}',
                'MAIL_DEFAULT_SENDER': '{{%EMAIL_SENDER%}}'
            }
        }
    config_file_path = repositories.CONFIG_FILE_PATH
    with open(config_file_path, 'wb') as f:         # 使用二进制写入模式 让文件编排原封不动
        yaml.dump(config, f, encoding='utf-8', sort_keys=False)