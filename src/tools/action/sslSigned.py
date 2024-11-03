import os
import datetime
import src.tools.repositories as repositories
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

from src.tools.loadconfig import loadConfig


# ===================== = 自签生成 ===================== #
# 生成证书
def ssl_self_signed():
    host = loadConfig()["Setting"]["listen"]
    select = (
        input(f"是否使用 {host} 作为证书？[y/n]")
        .strip()
        .lower()
    )
    if select == "y":
        # 生成私钥
        key = rsa.generate_private_key(
            public_exponent=65537, key_size=2048, backend=default_backend()
        )

        csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(
                x509.Name(
                    [
                        x509.NameAttribute(NameOID.COMMON_NAME, host),
                    ]
                )
            )
            .sign(key, hashes.SHA256(), default_backend())
        )

        # 自签
        subject = issuer = csr.subject
        cert = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.utcnow())
            .not_valid_after(
                # 有效期为一年
                datetime.datetime.utcnow()
                + datetime.timedelta(days=365)
            )
            .sign(key, hashes.SHA256(), default_backend())
        )

        key_file_path = f"data/key/ssl/server.key"
        pem_file_path = f"data/key/ssl/server.pem"

        try:
            os.makedirs(f"data/key/ssl", exist_ok=True)
            with open(key_file_path, "wb") as key_file:
                key_file.write(
                    key.private_bytes(
                        encoding=serialization.Encoding.PEM,
                        format=serialization.PrivateFormat.TraditionalOpenSSL,
                        encryption_algorithm=serialization.NoEncryption(),
                    )
                )
            with open(pem_file_path, "wb") as pem_file:
                pem_file.write(cert.public_bytes(serialization.Encoding.PEM))
            print(f"生成证书和密钥文件: {host} 操作完成")
            return True
        except Exception as err:
            print(f"创建文件或文件夹失败: {err}")
            return False
    else:
        print(f"操作取消.")
        return False
