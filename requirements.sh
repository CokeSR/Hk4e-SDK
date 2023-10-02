#!/bin/bash
#-*-coding:utf8-*-
apt update && apt upgrade -y
apt install python-is-python3 python3-pip -y
pip install --no-cache-dir werkzeug==2.2.3 flask==2.2.4 flask_mail Flask-Caching==2.0.2 requests rsa geoip2 bcrypt pyyaml pymysql protobuf  hashes cryptography Flask-Limiter -i https://pypi.tuna.tsinghua.edu.cn/simple
echo "所需环境下载完成"