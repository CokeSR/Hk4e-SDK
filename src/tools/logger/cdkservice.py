import os
import logging
import time

if not os.path.exists('logs'):
    os.mkdir('logs')

start_time = time.time()

def get_runtime() -> float:
    return time.time() - start_time

formatter = logging.Formatter('|SDKSERVER|%(asctime)s|%(levelname)s|%(filename)s|%(message)s')

class RuntimeFilter(logging.Filter):
    def filter(self, record):
        record.runtime = f"{get_runtime():.2f}"
        return True

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

flask_log = logging.getLogger('werkzeug')
flask_log.disabled = True

console_hander = logging.StreamHandler()
console_hander.setLevel(logging.DEBUG)

file_hander = logging.FileHandler('logs/hk4e-sdkserver-cdk.log', mode="w", encoding="UTF-8")
file_hander.setLevel(logging.DEBUG)

console_hander.setFormatter(formatter)
file_hander.setFormatter(formatter)

logger.addFilter(RuntimeFilter())

logger.addHandler(console_hander)
logger.addHandler(file_hander)
