import platform
import bcrypt
import hashlib
from src.tools.logger.system         import logger              as sys_log

# ===================== 密码相关 ===================== #
def passwordHash(password):
    sys_platfrom = platform.system()
    
    # 如果是 Windows 平台部署 不进行加密
    if sys_platfrom == "Windows":
        sys_log.warning(f"Windows 平台不进行加密, 存入原密码 {password}")
        return password
    
    h = hashlib.new("sha256")
    h.update(password.encode())
    data = bcrypt.hashpw(h.hexdigest().encode(), bcrypt.gensalt())
    sys_log.info(f"加密平台: {sys_platfrom} 加密值: {data.decode()}")
    return data


# 密码验证
def password_verify(password, hashed):
    h = hashlib.new("sha256")
    h.update(password.encode())
    data = bcrypt.checkpw(h.hexdigest().encode(), hashed.encode())
    sys_log.info(f"传入的密码: {password} 哈希值: {hashed} 校验结果: {data}")
    return data
