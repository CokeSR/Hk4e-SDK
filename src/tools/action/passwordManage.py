import bcrypt
import hashlib


# ===================== 密码相关 ===================== #
def password_hash(password):
    h = hashlib.new("sha256")
    h.update(password.encode())
    return bcrypt.hashpw(h.hexdigest().encode(), bcrypt.gensalt())


# 密码验证
def password_verify(password, hashed):
    h = hashlib.new("sha256")
    h.update(password.encode())
    return bcrypt.checkpw(h.hexdigest().encode(), hashed.encode())
