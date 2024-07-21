try:
    from __main__ import app
except ImportError:
    from main import app
import os
import yaml
import time
import shutil
import atexit
import logging
import settings.repositories as repositories

from flask import request
from datetime import datetime

#======================log设置======================#
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'sdkserver-running.log')
logging.basicConfig(filename=log_file, level=logging.INFO,format='%(asctime)s|%(levelname)s|%(message)s')

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

logger = logging.getLogger()
logger.addHandler(console_handler)

def rename_log_file():
    logger.removeHandler(console_handler)
    logging.shutdown()
    console_handler.close()
    time.sleep(1)
    now = datetime.now()
    new_filename = now.strftime("sdkserver-%Y-%m-%d %H-%M-%S.0000")
    new_log_file = os.path.join(log_dir, new_filename)
    shutil.move(log_file, new_log_file)
atexit.register(rename_log_file)

# 加载配置文件
def load_config():
    with open(repositories.CONFIG_FILE_PATH, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

# 获取请求日志记录配置项
def get_request_logging_config():
    config = load_config()
    return config.get('Setting', {}).get('high_frequency_logs', True)

@app.before_request
def log_request_content():
    enable_request_logging = get_request_logging_config()
    if enable_request_logging:
        content = request.get_data(as_text=True)
        encoded_content = content.encode('utf-8')
        logging.info(f"[信息上报]: {encoded_content}")