import rsa
import base64

from rsa                             import PublicKey, transform, core
from src.tools.action.dbGet          import getMysqlConn
from src.tools.logger.system         import logger          as sys_log


# ===================== 密码解密 ===================== #
# 密码rsa私钥解密
def decrypt_rsa_password(message):
    try:
        cursor = getMysqlConn().cursor()
        cursor.execute(
            # 取最后一个rsakey
            "SELECT private_key FROM `t_verifykey_config` WHERE `type` = 'rsakey'"
        )
        password = cursor.fetchone()
        verify = rsa.decrypt(base64.b64decode(message), rsa.PublicKey.load_pkcs1(password['private_key'])).decode()
    except Exception as err:
        sys_log.error(f"密码解密时出现意外错误：{err}")
        verify = base64.b64decode(message)

    return verify


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
    cursor = getMysqlConn().cursor()
    cursor.execute(f"SELECT * FROM `t_verifykey_config` WHERE `type` = 'authkey' AND `version` = {auth_key_version}")
    rsa_key = cursor.fetchone()
    result = b""
    for chunk in chunked(256, base64.b64decode(auth_key)):
        result += decrypt(chunk, rsa_key["public_key"])
    return result.strip()
