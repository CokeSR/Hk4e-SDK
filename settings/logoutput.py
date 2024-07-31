try:
    from __main__ import app
except ImportError:
    from main import app

import os
import logging
import atexit

from flask import request
from datetime import datetime
from settings.loadconfig import load_config
from logging.handlers import RotatingFileHandler


# ====================== Log 设置 ====================== #
log_dir = "logs"
log_file = os.path.join(log_dir, "sdkserver.log")
os.makedirs(log_dir, exist_ok=True)

def setup_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Rotating file handler
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_formatter = logging.Formatter("|%(levelname)s|%(message)s|")
    file_handler.setFormatter(file_formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter("|%(levelname)s|%(message)s|")   # %(asctime)s|%(levelname)s|%(message)s
    console_handler.setFormatter(console_formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

logger = setup_logger()

# Log file rename on exit
def rename_log_file():
    try:
        now = datetime.now()
        new_filename = now.strftime("sdkserver_%Y%m%d%H%M%S.log")
        new_log_file = os.path.join(log_dir, new_filename)
        os.rename(log_file, new_log_file)
    except Exception as e:
        print(f"Failed to rename log file: {e}")


atexit.register(rename_log_file)

# 获取请求日志记录配置项
def get_request_logging_config():
    config = load_config()
    return config.get("Setting", {}).get("high_frequency_logs", True)

@app.before_request
def log_request_content():
    content = request.get_data(as_text=True)
    enable_request_logging = get_request_logging_config()
    if enable_request_logging:
        if content == "":
            pass
        else:
            logger.info(f"[Client-Report]{content}")
