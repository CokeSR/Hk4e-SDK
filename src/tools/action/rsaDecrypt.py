import base64
import rsa
import base64
import src.tools.repositories as repositories

from rsa import PublicKey, transform, core
from src.tools.action.dbGet import get_db
from src.tools import repositories
from src.tools.action.dbGet import get_db


# ===================== 加密解密(暂时无用) ===================== #
def decrypt_sdk_authkey(message):
    with open(repositories.AUTHVERIFY_KEY_PATH, "rb") as f:
        return rsa.decrypt(
            base64.b64decode(message), rsa.PublicKey.load_pkcs1(f.read())
        ).decode()


# 密码rsa私钥解密
def decrypt_rsa_password(message):
    with open(repositories.PASSWDWORD_KEY_PATH, "rb") as f:
        return rsa.decrypt(
            base64.b64decode(message), rsa.PublicKey.load_pkcs1(f.read())
        ).decode()


# ===================== AuthKey解密返回信息 ===================== #
def decrypt(cipher, PUBLIC_KEY):
    public_key = PublicKey.load_pkcs1(PUBLIC_KEY)
    encrypted = transform.bytes2int(cipher)
    decrypted = core.decrypt_int(encrypted, public_key.e, public_key.n)
    text = transform.int2bytes(decrypted)

    if len(text) > 0 and text[0] == 1:
        pos = text.find(b"\x00")
        if pos > 0:
            return text[pos + 1 :]
        else:
            return b""


def chunked(size, source):
    for i in range(0, len(source), size):
        yield source[i : i + size]


def authkey(auth_key, auth_key_version):
    cursor = get_db().cursor()
    cursor.execute(
        f"SELECT * FROM `t_verifykey_config` WHERE `type` = 'authkey' AND `version` = {auth_key_version}"
    )
    rsa_key = cursor.fetchone()
    result = b""
    for chunk in chunked(256, base64.b64decode(auth_key)):
        result += decrypt(chunk, rsa_key["public_key"])
    return result.strip()
