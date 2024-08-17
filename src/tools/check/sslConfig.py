import os
import src.tools.repositories as repositories

from OpenSSL import crypto
from datetime import datetime
from src.tools.action.sslSigned import ssl_self_signed


# ===================== SSL 证书检查 ===================== #
def load_cert(cert_path, self_signed):
    """加载证书文件，若路径不存在则尝试生成自签名证书。"""
    if not os.path.exists(cert_path):
        if self_signed:
            # 尝试生成自签名证书
            if ssl_self_signed():
                print(f"{repositories.SDK_STATUS_SUCC}自签名证书已生成")
                return load_cert(cert_path, False)
            else:
                print(f"{repositories.SDK_STATUS_FAIL}自签名证书生成失败")
                return None
        else:
            print(f"{repositories.SDK_STATUS_FAIL}未找到证书文件: {cert_path}")
            return None

    try:
        with open(cert_path, "rb") as f:
            cert_data = f.read()
            cert = crypto.load_certificate(crypto.FILETYPE_PEM, cert_data)
            return cert
    except Exception as e:
        print(f"{repositories.SDK_STATUS_FAIL}加载证书失败: {e}")
        return None


def check_cert_validity(cert):
    """检查证书的有效性并打印相关信息。"""
    try:
        not_before = datetime.strptime(
            cert.get_notBefore().decode("ascii"), "%Y%m%d%H%M%SZ"
        )
        not_after = datetime.strptime(
            cert.get_notAfter().decode("ascii"), "%Y%m%d%H%M%SZ"
        )
        now = datetime.utcnow()

        if not_before <= now <= not_after:
            print(f"{repositories.SDK_STATUS_SUCC}该 SSL 证书有效")
        else:
            print(f"{repositories.SDK_STATUS_FAIL}该 SSL 证书无效")
            if now < not_before:
                print(f"{repositories.SDK_STATUS_WARING}该 SSL 证书尚未生效，将在 {not_before} 后生效")
            elif now > not_after:
                print(f"{repositories.SDK_STATUS_WARING}该证书已于 {not_after} 过期")
    except Exception as e:
        print(f"{repositories.SDK_STATUS_FAIL}检查证书有效性时出错: {e}")


def check_self_signed(cert):
    """检查证书是否为自签名。"""
    return cert.get_subject() == cert.get_issuer()


def check_ssl_certificate(cert_path, self_signed):
    """检查 SSL 证书是否存在、是否有效，以及是否为自签名证书。"""
    cert = load_cert(cert_path, self_signed)
    if cert:
        check_cert_validity(cert)
        if check_self_signed(cert):
            print(f"{repositories.SDK_STATUS_WARING}该 SSL 证书是自签名")
        else:
            print(f"{repositories.SDK_STATUS_SUCC}该 SSL 证书是由受信任的 CA 签发的")
        return True
    else:
        return False
