try:
    from __main__ import app
except ImportError:
    from main import app
import yaml
import settings.repositories as repositories

from flask_caching import Cache
from settings.loadconfig import get_config
from flask import send_from_directory, render_template
from settings.response import json_rsp, json_rsp_with_msg

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
@app.context_processor
def inject_config():
    config = get_config()
    return {'config': config}

def json_rsp(code, message, data=None):
    response = {
        "code": code,
        "message": message
    }
    if data is not None:
        response["data"] = data
    return response
#====================SDKServer====================#
# 首页
@app.route('/')
@app.route('/sandbox/index.html', methods=['GET'])
def account_index():
    return render_template("account/index.tmpl")

# 检查SDK配置(https://testing-abtest-api-data-sg.mihoyo.com) 不知道什么用 不写config
@app.route('/data_abtest_api/config/experiment/list', methods=['GET', 'POST'])
def abtest_config_experiment_list():
    return json_rsp_with_msg(repositories.RES_SUCCESS, "OK", {
        "data": [{
		"code": 1000,
		"type": 2,
		"config_id": "246",
		"period_id": "5147_328",
		"version": "2",
		"configs": {
			"cardType": "native",
			"cashierId": "34b2b997-b1c7-412b-b5f2-eeef09a03d92"
		}}, {
		"code": 1000,
		"type": 2,
		"config_id": "245",
		"period_id": "5145_536",
		"version": "1",
		"configs": {
			"foldOther": "true"             # 简化界面？
		}}, {
		"code": 1000,
		"type": 2,
		"config_id": "244",
		"period_id": "5144_535",
		"version": "1",
		"configs": {
			"expandMixedQRcode": "true"     # 二维码
		}}, {
		"code": 1010,
		"type": 2,
		"config_id": "243",
		"period_id": "",
		"version": "",
		"configs": {
			"disableMarket": "false"        # 市场？
		}}]
    })

#=====================状态收集=====================#
# log收集
@app.route('/log', methods=['POST'])
@app.route('/h5/upload',methods=['POST'])
@app.route('/log/sdk/upload', methods=['POST'])
@app.route('/crash/dataUpload', methods=['POST'])
@app.route('/client/event/dataUpload', methods = ['POST'])
@app.route('/sdk/dataUpload', methods=['POST'])
@app.route('/common/h5log/log/batch', methods=['POST'])
def sdk_log():
    return json_rsp(repositories.RES_SUCCESS, {})

# 红点配置 一般infos为空 特别写的
@app.route('/hk4e_cn/combo/red_dot/list', methods=['POST'])
@app.route('/hk4e_global/combo/red_dot/list', methods=['POST'])
def red_dot():
    return json_rsp(repositories.RES_SUCCESS, "ok", {
        "infos": []
    })
"""
def red_dot():
    return json_rsp(define.RES_SUCCESS, "ok", {
        "infos": [
            {
                "red_point_type": 2201,
                "content_id": 184,
                "display": get_config()["Reddot"]["display"]
            }
        ]
    })
"""
#======================mi18n======================#
@app.route('/admin/mi18n/plat_cn/m2020030410/m2020030410-version.json', methods=['GET'])
@app.route('/admin/mi18n/plat_oversea/m202003049/m202003049-version.json',methods=['GET'])
@app.route('/admin/mi18n/plat_oversea/m2020030410/m2020030410-version.json', methods=['GET'])
def mi18n_version():
    return json_rsp(repositories.RES_SUCCESS, {"version": 79})
@app.route('/admin/mi18n/plat_os/m09291531181441/m09291531181441-version.json',methods=['GET'])
def min18_os_version():
    return json_rsp(repositories.RES_SUCCESS, {"version": 16})
@app.route('/admin/mi18n/plat_cn/m2020030410/m2020030410-<language>.json', methods=['GET'])
@app.route('/admin/mi18n/plat_oversea/m2020030410/m2020030410-<language>.json', methods=['GET'])
def mi18n_serve(language):
    return send_from_directory(repositories.MI18N_PATH, f"{language}.json")

#================cokeserver-config================#
@app.route('/hk4e_cn/developers/config.yaml',methods=['GET'])
@app.route('/hk4e_global/developers/config.yaml',methods=['GET'])
def view_config():
    config_path = repositories.CONFIG_FILE_PATH
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        return config_data
    except FileNotFoundError:
        return "Config file not found"
    except Exception as e:
        return f"Error reading config file: {str(e)}"

@app.route('/hk4e_cn/developers/keys/authverify.pem',methods=['GET'])
@app.route('/hk4e_global/developers/keys/authverify.pem',methods=['GET'])
def view_authverify_key():
    config_path = repositories.AUTHVERIFY_KEY_PATH
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        return config_data
    except FileNotFoundError:
        return "Config file not found"
    except Exception as e:
        return f"Error reading config file: {str(e)}"

@app.route('/hk4e_cn/developers/keys/password.pem',methods=['GET'])
@app.route('/hk4e_global/developers/keys/password.pem',methods=['GET'])
def view_password_key():
    config_path = repositories.PASSWDWORD_KEY_PATH
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        return config_data
    except FileNotFoundError:
        return "Config file not found"
    except Exception as e:
        return f"Error reading config file: {str(e)}"