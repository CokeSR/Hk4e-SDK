import sys
import time
import rsa
import yaml
import base64
import bcrypt
import hashlib
import datetime
import requests
import urllib.parse
import geoip2.database
import settings.repositories as repositories

from functools import wraps
from flask import abort, request
from rsa import PublicKey, transform, core
from settings.restoreconfig import recover_config
from settings.loadconfig import get_json_config

#=====================函数库=====================#
# 检查[Config]文件是否存在并告知是否创建
# database dispatch 读取的是这里
def check_config_exists():
   config = None
   try:
      with open(repositories.CONFIG_FILE_PATH, encoding='utf-8') as file:
         config = yaml.safe_load(file)
   except FileNotFoundError:
      print("#=====================未检测到[Config]文件！运行失败=====================#")
      select = input(">> 是否创建新的[Config]文件？(y/n):")
      if select == 'y' or select == 'Y':
         recover_config()
         print(">> [Successful]-[Config]文件创建成功")
         sys.exit(1)
      elif select == 'n' or select == 'N':
         print(">> [Waring] 取消创建[Config]文件，停止运行...")
         sys.exit(1)
      else:
         print(">> [Error] 非法输入！停止运行...")
         sys.exit(1)
   return config

# 通过IP来检查是哪个国家
def get_country_for_ip(ip):
   with geoip2.database.Reader(repositories.GEOIP2_DB_PATH) as reader:
      try:
         return reader.country(ip).country.iso_code
      except geoip2.errors.AddressNotFoundError:
         pass
      except geoip2.errors.GeoIP2Error as err:
         print(f"Unexpected {err=} while resolving country code for {ip=}")
         pass
   return None

# 白名单准入
def ip_whitelist(allowed_ips):
   def decorator(func):
      @wraps(func)
      def wrapper(*args, **kwargs):
         if request.remote_addr not in allowed_ips:
            abort(403)
         return func(*args, **kwargs)
      return wrapper
   return decorator

# 信息处理
def forward_request(request, url):
   return requests.get(url, headers={"miHoYoCloudClientIP": request_ip(request)}).content
def forward_request_database(request, url, data):
   return requests.post(url, headers={"miHoYoCloudClientIP": request_ip(request)}, data=data)  
def request_ip(request):
   return request.remote_addr
def chunked(size, source):
   for i in range(0, len(source), size):
      yield source[i:i+size]

# 密码保存
def password_hash(password):
   h = hashlib.new('sha256')
   h.update(password.encode())
   return bcrypt.hashpw(h.hexdigest().encode(), bcrypt.gensalt())

# 密码验证
def password_verify(password, hashed):
   h = hashlib.new('sha256')
   h.update(password.encode())
   return bcrypt.checkpw(h.hexdigest().encode(), hashed.encode())

# 信息安全(脱敏)
def mask_string(text):
   if len(text) < 4:
      return "*" * len(text)                          # 如果源小于4个字符，则将其全部屏蔽
   else:
      start_pos = 2 if len(text) >= 10 else 1         # 根据总长度，显示1或2个第一个字符
      end_post = 2 if len(text) > 5 else 1            # 显示最后2个字符，但前提是总长度大于5个字符
      return f"{text[0:start_pos]}****{text[len(text)-end_post:]}"
def mask_email(email):
   text = email.split('@')
   return f"{mask_string(text[0])}@{text[1]}"

#=====================加密解密(暂时无用)=====================#
# Auth_key解密
def decrypt_sdk_authkey(message):
   with open(repositories.AUTHVERIFY_KEY_PATH,"rb") as f:
      return rsa.decrypt(base64.b64decode(message), rsa.PublicKey.load_pkcs1(f.read())).decode()

# 密码rsa私钥解密
def decrypt_rsa_password(message):
   with open(repositories.PASSWDWORD_KEY_PATH,"rb") as f:
      return rsa.decrypt(base64.b64decode(message), rsa.PublicKey.load_pkcs1(f.read())).decode()

#=====================AuthKey解密返回信息=====================#
def decrypt(cipher, PUBLIC_KEY):
   public_key = PublicKey.load_pkcs1(PUBLIC_KEY)
   encrypted = transform.bytes2int(cipher)
   decrypted = core.decrypt_int(encrypted, public_key.e, public_key.n)
   text = transform.int2bytes(decrypted)

   if len(text) > 0 and text[0] == 1:
      pos = text.find(b'\x00')
      if pos > 0:
         return text[pos+1:]
      else:
         return b""

def authkey(auth_key, auth_key_version):
   public_key = get_json_config()["crypto"]["rsa"]["authkey"][auth_key_version]
   result = b""
   for chunk in chunked(256, base64.b64decode(auth_key)):
      result += decrypt(chunk, public_key)
   return result.strip()

#=====================Muip签名计算与配置=====================#
def send(uid, content):
   def query_sha256_sign(query, sign):
      querys = query.split("&")
      sort_querys = [q for q in querys if q.split("=")[1] != ""]
      sort_querys.sort()
      ready_sign_query = "&".join(sort_querys)
      http_sign = sha256_encode(ready_sign_query + sign)
      return http_sign

   def query_escape(query):
      querys = query.split("&")
      new_querys = ["=".join([key_and_value[0], urllib.parse.quote(
         key_and_value[1])]) for key_and_value in (q.split("=") for q in querys)]
      return "&".join(new_querys)

   def sha256_encode(data):
      sha256 = hashlib.sha256()
      sha256.update(data.encode('utf-8'))
      return sha256.hexdigest()

   command = f"cmd=1005&uid={uid}&{content}" + "&ticket=" + "COKESERVER@" + str(time.mktime(datetime.datetime.now().timetuple())).split('.')[0]
   query = query_escape(command)
   http_sign = query_sha256_sign(command, check_config_exists()["Muipserver"]["sign"])
   request = "http://" + check_config_exists()["Muipserver"]["address"] + ":" + str(check_config_exists()["Muipserver"]["port"]) + "/api?" + query + "&sign=" + http_sign
   response = requests.get(request)
   return response.text.strip()