try:
    from __main__ import app
except ImportError:
    from main import app

import json
import src.tools.repositories   as repositories

from flask                      import request, abort, render_template
from src.tools.logger.system    import logger       as sys_log

# ===================== 抽卡模块 ===================== #
# 祈愿规则
@app.route("/gacha/info/<int:id>", methods=["GET"])
def gacha_info(id):

    schedule = {}
    textmap = {"title_map": {}, "item_map": {}}
    language = request.args.get("lang") or "en"
    try:
        f = open(f"{repositories.GACHA_SCHEDULE_PATH}/{id}.json")  # 加载当前卡池祈愿规则
        schedule = json.load(f)
        f.close()
    except Exception as err:
        abort(
            404,
            description=f"Unexpected {err=}, {type(err)=} while loading gacha schedule data for {id=}",
        )
    try:
        f = open(f"{repositories.GACHA_TEXTMAP_PATH}/{language}.json")  # 加载适配的语言
        textmap = json.load(f)
        f.close()
    except Exception as err:
        sys_log.info(f"Unexpected {err=}, {type(err)=} while loading textmap for {language=}")
    return render_template("gacha/details.tmpl", schedule=schedule, textmap=textmap, id=id)


# 祈愿记录
@app.route("/gacha/record/<int:type>", methods=["GET"])
def gacha_log(type):
    return render_template("gacha/history.tmpl")
