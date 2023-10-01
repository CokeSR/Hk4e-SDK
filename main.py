from flask import Flask
app = Flask(__name__)
import sys
import codecs
import settings.logoutput
import function.dispatch
import function.apiservice
import function.safeservice
import function.gachaservice
import function.otherservice
import function.announcement
import function.loginservice
import function.accountverify
import function.accountrecover
import function.accountregister
import function.rechargeservice
import function.cdkservice

from flask_mail import Mail
from werkzeug.serving import run_simple
from settings.loadconfig import load_config
from settings.database import initialize_database
from werkzeug.middleware.proxy_fix import ProxyFix
from settings.checkstatus import check_region , check_dispatch , check_config , check_mysql_connection , check_database_exists,check_muipserver
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

#======================Falsk(main)======================#
def start_flask_server(config):
    app.secret_key = config["Setting"]["secret_key"]
    app.debug = config["Setting"]["debug"]
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)
    mail_config = config.get('Mail', {})
    enable_mail = mail_config.get('ENABLE', True)
    if enable_mail:
        app.config.update(mail_config)
        mail = Mail(app)
        app.extensions['Mail'] = mail
    run_simple(
        config["Setting"]["listen"],
        config["Setting"]["port"],
        app,
        # use_reloader= config["Setting"]["reload"],    # 热重载1 按照config配置文件来设置
        # use_debugger= config["Setting"]["debug"],
        # threaded= config["Setting"]["threaded"]
        use_reloader=True,                              # 热重载2 快捷设置 方便debug
        use_debugger=False,
        threaded=True                                   # 多线程模式 默认开启
    )

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise Exception("请提供命令行参数: serve 或 initdb")
    config = load_config()
    command = sys.argv[1]
    if command == "serve": 
        if not check_config():
            print("#=====================[Config]文件校验失败！请检查服务配置=====================#")
            sys.exit(1)
        if not check_mysql_connection():
            print("#======================[Mysql]连接失败！请检查服务配置======================#")
            sys.exit(1)
        if not check_database_exists():
            print("#======================[Mysql]库查询失败！请检查服务配置======================#")
            sys.exit(1)
        if not check_region():
            print("#=====================[Region]读取失败！请检查[Config]配置=====================#")
            sys.exit(1)
        if not check_dispatch():
            print("#=====================[Dispatch]读取失败！请检查[Config]配置=====================#")
            sys.exit(1)
        if not check_muipserver():
            print("#=====================[Muipserver]读取失败！请检查[Config]配置=====================#")
            sys.exit(1)
        start_flask_server(config)
    elif command == "initdb":
        initialize_database()
    else:
        raise Exception("未知的操作！必须是以下命令: serve 或 initdb")