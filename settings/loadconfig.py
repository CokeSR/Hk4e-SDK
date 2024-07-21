import yaml
import json
import settings.repositories as repositories

from flask import g

#=====================读取Config=====================#
# config = getattr(g, '_config', None)
def load_config():
    with open(repositories.CONFIG_FILE_PATH, encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def get_config():
    config = None
    if config is None:
        with open(repositories.CONFIG_FILE_PATH, encoding='utf-8'):
            config = g._config = load_config()
    return config

def get_json_config():
    config = None
    with open(repositories.CONFIG_FILE_JSON_PATH) as file:
        msg = json.load(file)
    if config is None:
      with open(repositories.CONFIG_FILE_JSON_PATH):
        config = g._config = msg
    return config
