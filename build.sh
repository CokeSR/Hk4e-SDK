#!/bin/bash
#-*-coding:utf8-*-
apt update && apt upgrade -y
apt install python-is-python3 python3-pip -y
pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
echo "所需环境下载完成"