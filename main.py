from flask import Flask

app = Flask(
    __name__, 
    template_folder="data/static/templates/", 
    static_folder="data/static/",
)

import sys
import codecs
from src.tools.checkstatus import *
from src.tools.library import initialize_database
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

# 防报错 / 优先级
try:
    from src.main import *
    from src.tools import *
except Exception as err:
    print(f"导入模块时出现错误：{err}")

try:
    app.secret_key = load_config()["Setting"]["secret_key"]
except Exception:
    app.secret_key = "cokeserver2022"

"""服务的两种启动方式"""
# 正式环境
def launch():
    config = load_config()
    app.debug = config["Setting"]["debug"]
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    """
    mail_config = config.get("Mail", {})
    enable_mail = mail_config.get("ENABLE", True)
    if enable_mail:
        app.config.update(mail_config)
        mail = Mail(app)
        app.extensions["Mail"] = mail
    """
    return app


# 开发环境
def flak_server_debug():
    import src.tools.logoutput
    config = load_config()
    try:
        if config["Setting"]['debug']:
            app.run(
                host=config["Setting"]["listen"],
                port=config["Setting"]["port"],
                debug=config["Setting"]["debug"],
                use_reloader=config["Setting"]["reload"],
                threaded=config["Setting"]["threaded"],
            )
        else:
            raise RuntimeError("Should not use flak_server_debug() in production")
    except Exception as err:
        host = config["Setting"]["listen"]
        port = config["Setting"]["port"]
        print(
            f"DEBUG 模式已关闭，请启用 DEBUG 模式或使用生产环境命令运行本程序\n"
            + f"命令如下：gunicorn -w 4 -b {host}:{port} 'main:launch()' "
            + "--access-logfile logs/sdkserver.log --error-logfile logs/sdkserver-error.log"
        )

"""系统处理"""
def print_error(message):
    print(f"#=====================[{message}]=====================#")
    sys.exit(1)

def check_all_required_conditions():
    if not check_config():
        print_error("Config文件校验失败！请检查服务配置")
    elif not check_mysql_connection():
        print_error("Mysql连接失败！请检查服务配置")
    elif not check_redis_connection():
        print_error("Redis连接失败！请检查服务配置")
    elif not check_database_exists():
        print_error("Mysql库查询失败！请检查服务配置")
    elif not check_region():
        print_error("Region读取失败！请检查[Config]配置")
    elif not check_dispatch():
        print_error("Dispatch读取失败！请检查[Config]配置")
    elif not check_gate():
        print_error("Gateserver读取失败！请检查[Config]配置")
    elif not check_muipserver():
        print_error("Muipserver读取失败！请检查[Config]配置")
    else:
        return True

# 开发模式
def handle_serve():
    check_all_required_conditions()
    flak_server_debug()


# 数据库重建
def handle_initdb():
    if not check_config():
        print_error("Config文件校验失败！请检查服务配置")
    if check_mysql_connection():
        initialize_database()
    else:
        print_error("Mysql连接失败！请检查服务配置")

# 检查服务配置
def handle_check():
    print("执行检查操作...")
    status = check_all_required_conditions()
    if status :
        print("服务配置加载成功")
        return True
    else:
        print("服务配置加载失败")
        return False

# 说明书
def handle_book():
    print("# Hk4e-SDK(ver 1.1.9) 参数说明\n"
          + f"serve: 测试环境用 需要在 Config 中将 debug 模式设置为 true\n"
          + f"initdb: 初始化数据库（账号管理库、CDK系统库）\n"
          + f"check: 检查运行前所需的设置\n"
          + f"{'*'*13} 额外说明 {'*'*13}\n"
          + f"使用适用于生产环境的命令：\n"
          + f"gunicorn -w 4 -b $host:$port 'main:launch()' --access-logfile logs/sdkserver.log --error-logfile logs/sdkserver-error.log\n"
          + f"此命令仅适用于 Linux 平台\n"
          + f"使用该命令时，需要先 check 检查配置"
    )

# 入口
def main(command):
    if not check_config_exists():
        print_error("Config文件校验失败！请检查服务配置")
    handlers = {
        "serve": handle_serve,
        "initdb": handle_initdb,
        "check": handle_check,
        "help": handle_book
    }

    if command in handlers:
        handlers[command]()
    else:
        print(f"未知的参数: {command}\n请输入 help 参数以获取帮助")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("参数有误 请输入 python main.py help 以获取帮助")
    else:
        main(sys.argv[1])
