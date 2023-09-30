import yaml
import settings.repositories as repositories

from flask import g

#=====================读取Config=====================#
def load_config():
    with open(repositories.CONFIG_FILE_PATH, encoding='utf-8') as file:
        return yaml.safe_load(file)

def get_config():
    config = getattr(g, '_config', None)
    if config is None:
        with open(repositories.CONFIG_FILE_PATH, encoding='utf-8'):
            config = g._config = load_config()
    return config