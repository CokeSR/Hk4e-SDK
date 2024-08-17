import rsa
import pymysql
import src.tools.repositories as repositories

from src.tools.loadconfig import load_config


# ===================== 秘钥验证 ===================== #
def rsakey_verify():
    string = "COKESERVER2022"
    config = load_config()["Database"]["mysql"]
    # 这里是SDK启动验证阶段 故不使用 database.get_db()
    db = pymysql.connect(
        host=config["host"],
        user=config["user"],
        port=config["port"],
        password=config["password"],
        database=config["account_library_name"],
        cursorclass=pymysql.cursors.DictCursor,
        charset="utf8",
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

            print(f"{repositories.SDK_STATUS_SUCC}秘钥 {id}, 类型 {type} 验证成功")
        except rsa.VerificationError:
            print(f"{repositories.SDK_STATUS_WARING}秘钥 {id}, 类型 {type} 验证失败")
        except Exception as e:
            print(
                f"{repositories.SDK_STATUS_WARING}秘钥 {id}, 类型 {type} 加载错误: {e}"
            )
