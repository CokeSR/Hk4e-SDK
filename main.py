import os
import sys
import time
import base64
import src.tools.repositories        as rep

from flask                           import Flask
from src.tools.loadconfig            import loadConfig
from src.tools.action.dbRebuild      import initializeDatabase
from src.tools.logger.system         import logger              as sys_log
from src.tools.logger.dispatch       import logger              as dispatch_log
from src.tools.logger.user           import logger              as user_log
from src.tools.logger.cdkservice     import logger              as cdk_log
from src.tools.check.dispatchConnect import dispatchConn
from src.tools.check.muipConnect     import muipStatus
from src.tools.check.rsaVerify       import rsakeyVerify
from src.tools.check.sslConfig       import checkSSLCertificate
from src.tools.check.databaseConnect import (
    checkDatabaseExists, checkMysqlConnect, checkRedisConnect,
)
from src.tools.check.configExists import (
    checkGateserver, checkRegionConfig, checkConfigYaml,
    checkDispatch, checkMuipservice, checkConfigYamlExists,
)

# flask 资源引导
app = Flask(
    __name__, 
    template_folder="data/static/templates/", 
    static_folder="data/static/",
)
app.secret_key = base64.b64encode(os.urandom(24))   # flask 模板文件用

# logger record
loggers = [sys_log, user_log, dispatch_log, cdk_log]
for log_msg in loggers:
    log_msg.info(f"{log_msg} | Latest launcher time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")


from src.main import *
from src.tools import *


# 系统检查
def isSystemAlready() -> bool:
    # 基本配置 检查失败后阻塞启动
    envCheckDict = {
        checkConfigYaml     : "Config文件校验失败",
        checkMysqlConnect   : "Mysql连接失败",
        checkRedisConnect   : "Redis连接失败",
        checkDatabaseExists : "Mysql库查询失败",
        checkRegionConfig   : "Region读取失败",
        checkDispatch       : "Dispatch读取失败",
        checkGateserver     : "Gateserver读取失败",
        checkMuipservice    : "Muipserver读取失败",
    }
    
    for checkFunc, err_msg in envCheckDict.items():
        if not checkFunc():
            sys_log.error(f"#=====================[{err_msg}]=====================#")
            return False

    # 基本配置完成后的其他检查 不阻塞启动
    [checkFunc() for checkFunc in [rsakeyVerify, muipStatus, dispatchConn]]

    # 如果启用了SSL模式
    config = loadConfig()["Setting"]
    if config["ssl"]:
        if not checkSSLCertificate(rep.SSL_PEM_PATH, config["ssl_self_signed"]):
            sys_log.error("加载并验证 SSL 证书失败")
            return False

    return True


# 数据库重建
def rebuildDatabase() -> None:
    if not checkConfigYaml():
        sys_log.error("Config文件校验失败!")
    if checkMysqlConnect():
        initializeDatabase()
    else:
        sys_log.error("Mysql连接失败!")


# 检查服务配置
def handleCheck() -> bool:
    if isSystemAlready() :
        sys_log.info(f"基础服务配置加载成功")
        return True
    else:
        sys_log.error(f"服务配置加载失败")
        return False


# 说明书
def handleBook() -> None:
    print(
        "# Hk4e-SDK(ver 1.4.3) 参数说明\n"
        + f"1.serve: 需要在 Config 中将 debug 模式设置为 true\n"
        + f"2.initdb: 初始化数据库(账号管理库、CDK系统库、公告系统库)\n"
        + f"3.check: 检查运行前所需的设置"
    )


# 执行主函
def launch() -> None:
    config = loadConfig()["Setting"]
    if isSystemAlready():
        if config["ssl"]:
            sys_log.info(f'服务已在 https://{config["listen"]}:{config["port"]} 运行')
            app.run(
                host=config["listen"],
                port=config["port"],
                debug=config["debug"],
                use_reloader=config["reload"],
                threaded=config["threaded"],
                ssl_context=(rep.SSL_PEM_PATH, rep.SSL_KEY_PATH)
            )
        else:
            sys_log.info(f'服务已在 http://{config["listen"]}:{config["port"]} 运行')
            app.run(
                host=config["listen"],
                port=config["port"],
                debug=config["debug"],
                use_reloader=config["reload"],
                threaded=config["threaded"],
            )


# 入口
def main(command) -> None:
    if not checkConfigYamlExists():
        sys_log.error("Config文件校验失败!")
    handlers = {
        "serve": launch,
        "initdb": rebuildDatabase,
        "check": handleCheck,
        "help": handleBook
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
