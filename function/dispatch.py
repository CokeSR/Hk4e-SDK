from __main__ import app
import sys
import settings.repositories as repositories
import data.proto.QueryRegionListHttpRsp_pb2 as RegionList

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

#=====================Dispatch配置=====================#
# 实验性分区 Dispatch
# version=CNRELWin4.0.1 lang=2 platform=3 binary=1 time=291 channel_id=1 sub_channel_id=1
# version=OSRELWin2.8.0 lang=2 platform=3 binary=1 time=454 channel_id=1 sub_channel_id=1
@app.route('/query_region_list', methods=['GET'])
def query_dispatch():
    response = RegionList.QueryRegionListHttpRsp()
    response.retcode = repositories.RES_SUCCESS
    for entry in check_config_exists()['Gateserver']:
        if ('name' not in entry or not entry['name'] or
            'title' not in entry or not entry['title'] or
            'dispatchUrl' not in entry or not entry['dispatchUrl']):
            print("#=====================Region读取失败！请检查[Config]配置=====================#")       # 客户端请求的时候再检查一下 如果不符合就原地抛锚
            sys.exit(1)
        region_info = response.region_list.add()
        region_info.name = entry['name']
        region_info.title = entry['title']
        region_info.type = "PRODUTC"
        region_info.dispatch_url = entry['dispatchUrl']
        version = request.args.get('version')
    if version.startswith('CNREL'):
        custom_config = '{"sdkenv":"0","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
    elif version == 'CNCB':
        custom_config = '{"sdkenv":"6","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
    elif version == 'OSCB':
        custom_config = '{"sdkenv":"7","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
    else:
        custom_config = '{"sdkenv":"2","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
    encrypted_config = bytearray()
    for coke in range(len(custom_config)):
        encrypted_config.append(ord(custom_config[coke]) ^ dispatch_key[coke % len(dispatch_key)])
    updated_region_list = RegionList.QueryRegionListHttpRsp()
    updated_region_list.region_list.extend(response.region_list)
    updated_region_list.client_secret_key = dispatch_seed
    updated_region_list.client_custom_config_encrypted = bytes(encrypted_config)
    updated_region_list.enable_login_pc = True      # 试过了 无论是否都没用 但是必须要存在 :)
    # 序列化
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