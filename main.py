from flask import Flask

app = Flask(__name__)
import sys
import codecs
from function import *
from settings import *
from settings.checkstatus import *
from settings.logoutput import *
from settings.checkstatus import check_config_exists
from settings.library import initialize_database
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

app.secret_key = load_config()["Setting"]["secret_key"]

"""服务的两种启动方式"""
# 正式环境
def launch():
    config = load_config()
    app.debug = config["Setting"]["debug"]
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    mail_config = config.get("Mail", {})
    enable_mail = mail_config.get("ENABLE", True)
    if enable_mail:
        app.config.update(mail_config)
        mail = Mail(app)
        app.extensions["Mail"] = mail
    return app


# 开发环境
def flak_server_debug():
    # app = create_app()
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
    except:
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

# 入口
def main(command):
    check_config_exists()
    handlers = {
        "serve": handle_serve,
        "initdb": handle_initdb,
        "check": handle_check
    }
    
    if command in handlers:
        handlers[command]()
    else:
        raise Exception("未知的操作！必须是以下命令: serve 或 initdb")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("请提供命令行参数: serve 或 initdb")
    else:
        main(sys.argv[1])
