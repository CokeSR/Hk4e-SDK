from flask import Flask

app = Flask(__name__)
import sys
import codecs
from function import *
from settings import *
from settings.checkstatus import *
from settings.logoutput import *
from settings.database import initialize_database
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


def create_app():
    config = load_config()
    app.secret_key = config["Setting"]["secret_key"]
    app.debug = config["Setting"]["debug"]
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    mail_config = config.get("Mail", {})
    enable_mail = mail_config.get("ENABLE", True)
    if enable_mail:
        app.config.update(mail_config)
        mail = Mail(app)
        app.extensions["Mail"] = mail

    return app


def start_flask_server():
    app = create_app()
    config = load_config()
    if config["Setting"].get("debug", False):
        app.run(
            host=config["Setting"]["listen"],
            port=config["Setting"]["port"],
            debug=config["Setting"]["debug"],
            use_reloader=config["Setting"]["reload"],
            threaded=config["Setting"]["threaded"],
        )
    else:
        raise RuntimeError("Should not use start_flask_server() in production")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise Exception("请提供命令行参数: serve 或 initdb")

    command = sys.argv[1]

    if command == "serve":
        if not check_config():
            print(
                "#=====================[Config]文件校验失败！请检查服务配置=====================#"
            )
            sys.exit(1)
        if not check_mysql_connection():
            print(
                "#======================[Mysql]连接失败！请检查服务配置======================#"
            )
            sys.exit(1)
        if not check_database_exists():
            print(
                "#======================[Mysql]库查询失败！请检查服务配置======================#"
            )
            sys.exit(1)
        if not check_region():
            print(
                "#=====================[Region]读取失败！请检查[Config]配置=====================#"
            )
            sys.exit(1)
        if not check_dispatch():
            print(
                "#=====================[Dispatch]读取失败！请检查[Config]配置=====================#"
            )
            sys.exit(1)
        if not check_muipserver():
            print(
                "#=====================[Muipserver]读取失败！请检查[Config]配置=====================#"
            )
            sys.exit(1)
        start_flask_server()
    elif command == "initdb":
        if not check_config():
            print(
                "#=====================[Config]文件校验失败！请检查服务配置=====================#"
            )
            sys.exit(1)
        if not check_mysql_connection():
            print(
                "#======================[Mysql]连接失败！请检查服务配置======================#"
            )
        else:
            initialize_database()
    else:
        raise Exception("未知的操作！必须是以下命令: serve 或 initdb")
