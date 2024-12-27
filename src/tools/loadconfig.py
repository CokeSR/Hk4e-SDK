import yaml
import src.tools.repositories        as repositories

# ===================== 读取Config ===================== #
def loadConfig():
    with open(repositories.CONFIG_FILE_PATH, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
        return data


""" 废弃
def getConfig():
    config = getattr(g, "_config", None)
    if config is None:
        with open(repositories.CONFIG_FILE_PATH, encoding="utf-8"):
            config = g._config = loadConfig()
    return config
  
def load_json_config():
    with open(repositories.CONFIG_FILE_JSON_PATH) as file:
        return json.load(file)
        
def get_json_config():
    config = getattr(g, "_config", None)
    if config is None:
        with open(repositories.CONFIG_FILE_JSON_PATH):
            config = g._config = load_json_config()
    return config
"""
