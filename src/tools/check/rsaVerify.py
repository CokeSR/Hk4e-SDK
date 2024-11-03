import rsa
import pymysql

from src.tools.logger.system         import logger              as sys_log
from src.tools.loadconfig            import loadConfig


# ===================== 秘钥验证 ===================== #
def rsakeyVerify():
    string = "COKESERVER2022"
    config = loadConfig()["Database"]["mysql"]
    # 这里是SDK启动验证阶段 故不使用 database.getMysqlConn()
    db = pymysql.connect(
        host=config["host"],
        user=config["user"],
        port=config["port"],
        password=config["password"],
        database=config["account_library_name"],
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8",
        autocommit=True
    )
    cursor = db.cursor()
    cursor.execute("SELECT id, type, public_key, private_key FROM `t_verifykey_config`")
    keys = cursor.fetchall()
    for key in keys:
        id = key["id"]
        type = key["type"]
        public_key = key["public_key"]
        private_key = key["private_key"]
        try:
            if not public_key.startswith("-----BEGIN"):
                public_key = f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"

            if not private_key.startswith("-----BEGIN"):
                private_key = f"-----BEGIN PRIVATE KEY-----\n{private_key}\n-----END PRIVATE KEY-----"

            pubkey = rsa.PublicKey.load_pkcs1(public_key.encode("utf-8"))
            privkey = rsa.PrivateKey.load_pkcs1(private_key.encode("utf-8"))
            signature = rsa.sign(string.encode("utf-8"), privkey, "SHA-256")
            rsa.verify(string.encode("utf-8"), signature, pubkey)

            public_key_cleaned = public_key.replace('\n', '')
            private_key_cleaned = private_key.replace('\n', '')
            sys_log.info(f"秘钥 {id} 公钥: {public_key_cleaned} 私钥: {private_key_cleaned} 类型 {type} 验证成功")

        except rsa.VerificationError:
            sys_log.error(f"秘钥 {id} 公钥: {private_key} 私钥: {private_key} 类型 {type} 验证失败")
        except Exception as err:
            sys_log.error(f"秘钥 {id} 类型 {type} 加载错误: {err}")
