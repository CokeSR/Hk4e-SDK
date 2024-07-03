try:
    from __main__ import app
except ImportError:
    from main import app

import json
import settings.repositories as repositories
import data.proto.cbt.QueryRegionListHttpRsp_v1_pb2 as RegionList_CBT
import data.proto.live.QueryRegionListHttpRsp_v2_pb2 as RegionList_Live

from base64 import b64encode
from flask_caching import Cache
from settings.library import forward_request
from flask import Response, abort, request
from settings.library import check_config_exists

cache = Cache(app, config={'CACHE_TYPE': 'simple'})
@app.context_processor
def inject_config():
    config = check_config_exists()
    return {'config': config}

with open(repositories.DISPATCH_KEY, 'rb') as f:
    dispatch_key = f.read()
with open(repositories.DISPATCH_SEED, 'rb') as f:
    dispatch_seed = f.read()

#===================== Dispatch 配置 =====================#
# 实验性分区 Dispatch - CBT/Live
# ?version=CHNWINCB1.0.0&lang=1&platform=3&binary=1&time=431
# ?version=OVSWIN0.7.1&lang=1&platform=3&binary=1&time=429
# ?version=CNRELWin4.0.1&lang=2&platform=3&binary=1&time=291&channel_id=1 sub_channel_id=1
# ?version=OSRELWin2.8.0&lang=2&platform=3&binary=1&time=454&channel_id=1&sub_channel_id=1
@app.route('/query_region_list', methods=['GET'])
def query_dispatch():
    version = request.args.get('version', '')
    if version.startswith('CHN'):
        # CBT1
        response = {
            "region_list": [],
            "clientCustomConfig":"{\"visitor\": false, \"sdkenv\": \"2\", \"checkdevice\": false}"
        }

        gateservers = check_config_exists().get('Gateserver', [])
        for entry in gateservers:
            region_info = {
                "name": entry.get('name', ''),
                "title": entry.get('title', ''),
                "type": "DEV_PUBLIC",
                # 草 有坑
                "dispatchUrl": entry.get('dispatchUrl', '')
            }
            response["region_list"].append(region_info)

        json_response = json.dumps(response)
        return Response(json_response, content_type='text/plain')
    elif version.startswith('OVS'):
        # CBT2
        custom_config = '{"sdkenv": "2", "checkdevice": false, "showexception": false}'
        
        response = RegionList_CBT.QueryRegionListHttpRsp_v1()
        response.retcode = repositories.RES_SUCCESS
        gateservers = check_config_exists().get('Gateserver', [])
        
        for entry in gateservers:
            region_info = response.region_list.add()
            region_info.name = entry.get('name', '')
            region_info.title = entry.get('title', '')
            region_info.type = "DEV_PUBLIC"
            region_info.dispatch_url = entry.get('dispatchUrl', '')
        
        updated_region_list = RegionList_CBT.QueryRegionListHttpRsp_v1()
        updated_region_list.region_list.extend(response.region_list)
        updated_region_list.client_custom_config = custom_config
        
        serialized_data = updated_region_list.SerializeToString()
        base64_str = b64encode(serialized_data).decode()
        return Response(base64_str, content_type='text/plain')
    else:
        # CBT3 & live
        version_config = {
            'CNREL': '{"sdkenv":"0","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}',
            'OSREL': '{"sdkenv":"5","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}',
            'CNCB': '{"sdkenv":"6","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}',
            'OSCB': '{"sdkenv":"7","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
        }
        default_config = '{"sdkenv":"2","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
        
        response = RegionList_Live.QueryRegionListHttpRsp_v2()
        response.retcode = repositories.RES_SUCCESS
        gateservers = check_config_exists().get('Gateserver', [])
        
        for entry in gateservers:
            region_info = response.region_list.add()
            region_info.name = entry.get('name', '')
            region_info.title = entry.get('title', '')
            region_info.type = "PRODUCT"
            region_info.dispatch_url = entry.get('dispatchUrl', '')

        version = request.args.get('version', '')
        custom_config = version_config.get(version, default_config)
        encrypted_config = bytearray(ord(char) ^ dispatch_key[idx % len(dispatch_key)] for idx, char in enumerate(custom_config))
        
        updated_region_list = RegionList_Live.QueryRegionListHttpRsp_v2()
        updated_region_list.region_list.extend(response.region_list)
        updated_region_list.client_secret_key = dispatch_seed
        updated_region_list.client_custom_config_encrypted = bytes(encrypted_config)
        updated_region_list.enable_login_pc = True
        
        serialized_data = updated_region_list.SerializeToString()
        base64_str = b64encode(serialized_data).decode()
        return Response(base64_str, content_type='text/plain')

# 实验性解析QueryCurRegion(live版本服务端dispatchurl必须要填写sdk的地址，通过sdk来传递区服信息)
# version=OSRELWin2.8.0 lang=2 platform=3 binary=1 time=348 channel_id=1 sub_channel_id=1 account_type=1 dispatchSeed=caffbdd6d7460dff key_id=3
@app.route('/query_region/<name>', methods=['GET'])
def query_cur_region(name):
    try:
        return forward_request(request, f"{check_config_exists()['Dispatch']['list'][name]}/query_cur_region?{request.query_string.decode()}")
    except KeyError:
        print(f"未知的Region={name}")
        abort(404)
    except Exception as err:
        print(f"处理请求事件发生以外错误{err=}, {type(err)=}")
        abort(500)
