import yaml
import json
import src.tools.repositories as repositories

from flask import g


# =====================读取Config=====================#
def load_config():
    with open(repositories.CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
        return yaml.safe_load(file)


def get_config():
    config = getattr(g, "_config", None)
    if config is None:
        with open(repositories.CONFIG_FILE_PATH, encoding="utf-8"):
            config = g._config = load_config()
    return config


def load_json_config():
    with open(repositories.CONFIG_FILE_JSON_PATH) as file:
        return json.load(file)

"""
def get_json_config():
    config = getattr(g, "_config", None)
    if config is None:
        with open(repositories.CONFIG_FILE_JSON_PATH):
            config = g._config = load_json_config()
    return config
"""