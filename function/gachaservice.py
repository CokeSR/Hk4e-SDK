from __main__ import app
import json
import settings.repositories as repositories

from flask_caching import Cache
from settings.loadconfig import get_config
from flask import request,abort, render_template

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
@app.context_processor
def inject_config():
    config = get_config()
    return {'config': config}

#=====================抽卡模块=====================#
# 祈愿规则
@app.route('/gacha/info/<int:id>', methods=['GET'])
def gacha_info(id):

    schedule = {}
    textmap = {
        'title_map': {},
        'item_map': {}
    }
    language = request.args.get('lang') or 'en'
    try:
        f = open(f"{repositories.GACHA_SCHEDULE_PATH}/{id}.json")                  # 加载当前卡池祈愿规则
        schedule = json.load(f)
        f.close()
    except Exception as err:
        abort(
            404, description=f"Unexpected {err=}, {type(err)=} while loading gacha schedule data for {id=}")
    try:
        f = open(f"{repositories.GACHA_TEXTMAP_PATH}/{language}.json")            # 加载适配的语言
        textmap = json.load(f)
        f.close()
    except Exception as err:
        print(
            f"Unexpected {err=}, {type(err)=} while loading textmap for {language=}")
    return render_template("gacha/details.tmpl", schedule=schedule, textmap=textmap, id=id)

# 祈愿记录
@app.route('/gacha/record/<int:type>', methods=['GET'])
def gacha_log(type):
    return render_template("gacha/history.tmpl")