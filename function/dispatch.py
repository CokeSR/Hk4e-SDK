try:
    from __main__ import app
except ImportError:
    from main import app

import re
import json
import settings.repositories as repositories
import data.proto.cbt.QueryRegionListHttpRsp_v1_pb2 as RegionList_CBT
import data.proto.live.QueryRegionListHttpRsp_v2_pb2 as RegionList_Live

from base64 import b64encode
from flask_caching import Cache
from settings.library import forward_request
from flask import Response, abort, request
from settings.library import check_config_exists

cache = Cache(app, config={"CACHE_TYPE": "simple"})


@app.context_processor
def inject_config():
    config = check_config_exists()
    return {"config": config}


with open(repositories.DISPATCH_KEY, "rb") as f:
    dispatch_key = f.read()
with open(repositories.DISPATCH_SEED, "rb") as f:
    dispatch_seed = f.read()


# ===================== Dispatch 配置 =====================#
# 实验性分区 Dispatch - CBT/Live
@app.route("/query_region_list", methods=["GET"])
def query_dispatch():
    gateservers = check_config_exists().get("Gateserver", [])

    # 创建版本库标识
    def create_client_version():
        version = ["OVSWIN", "CHNWINCB", "CHNiOSCB"]
        client_type = ["Win", "Android", "IOS"]
        region_type = ["CHN", "OVS", "CNREL", "OSREL", "CNCB", "OSCB"]
        for region in region_type:
            for client in client_type:
                ver = region + client
                version.append(ver)
        return version

    # dispatch 请求
    def cbt1_dispatch(custom_config):
        for entry in gateservers:
            region_info = {
                "name": entry.get("name", ""),
                "title": entry.get("title", ""),
                "type": "DEV_PUBLIC",
                "dispatchUrl": entry.get("dispatchUrl", ""),
            }
            custom_config["region_list"].append(region_info)
        json_response = json.dumps(custom_config)
        # 纯 JSON 形式
        return json_response

    def cbt2_dispatch(custom_config):
        response = RegionList_CBT.QueryRegionListHttpRsp_v1()
        response.retcode = repositories.RES_SUCCESS

        for entry in gateservers:
            region_info = response.region_list.add()
            region_info.name = entry.get("name", "")
            region_info.title = entry.get("title", "")
            region_info.type = "DEV_PUBLIC"
            region_info.dispatch_url = entry.get("dispatchUrl", "")

        updated_region_list = RegionList_CBT.QueryRegionListHttpRsp_v1()
        updated_region_list.region_list.extend(response.region_list)
        updated_region_list.client_custom_config = custom_config
        # 序列化
        serialized_data = updated_region_list.SerializeToString()
        base64_str = b64encode(serialized_data).decode()
        return Response(base64_str, content_type="text/plain")

    def live_dispatch(custom_config):
        # 包含 CBT3
        response = RegionList_Live.QueryRegionListHttpRsp_v2()
        response.retcode = repositories.RES_SUCCESS

        for entry in gateservers:
            region_info = response.region_list.add()
            region_info.name = entry.get("name", "")
            region_info.title = entry.get("title", "")
            region_info.type = "PRODUCT"
            region_info.dispatch_url = entry.get("dispatchUrl", "")

        encrypted_config = bytearray(
            ord(char) ^ dispatch_key[idx % len(dispatch_key)]
            for idx, char in enumerate(custom_config)
        )
        updated_region_list = RegionList_Live.QueryRegionListHttpRsp_v2()
        updated_region_list.region_list.extend(response.region_list)
        updated_region_list.client_secret_key = dispatch_seed
        updated_region_list.client_custom_config_encrypted = bytes(encrypted_config)
        updated_region_list.enable_login_pc = True
        # 序列化
        serialized_data = updated_region_list.SerializeToString()
        base64_str = b64encode(serialized_data).decode()
        return Response(base64_str, content_type="text/plain")

    def output(client):
        if client == "CHN":  # CBT1
            custom_config = {
                "region_list": [],
                "clientCustomConfig": '{"visitor": false, "sdkenv": "2", "checkdevice": false}',
            }
            return cbt1_dispatch(custom_config)
        elif client == "OVS":  # CBT2
            custom_config = (
                '{"sdkenv": "2", "checkdevice": false, "showexception": false}'
            )
            return cbt2_dispatch(custom_config)
        elif client == "CNREL":  # CBT3-Live
            custom_config = '{"sdkenv":"0","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
            return live_dispatch(custom_config)
        elif client == "OSREL":
            custom_config = '{"sdkenv":"5","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
            return live_dispatch(custom_config)
        elif client == "CNCB":
            custom_config = '{"sdkenv":"6","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
            return live_dispatch(custom_config)
        elif client == "OSCB":
            custom_config = '{"sdkenv":"7","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0"}'
            return live_dispatch(custom_config)
        else:
            return Response(
                f"Error client type: {client}", content_type="text/plain", status=400
            )

    # 外部获取版本标识名称并与版本库标识对比
    version = create_client_version()
    get = request.args.get("version", "")
    ver = get[:-5]
    client = re.sub(r"(WIN|Win|Android|IOS|ios).*$", "", get)
    if ver not in version:
        return Response("CP///////////wE=", content_type="text/plain")
    else:
        return output(client)


# 解析 QueryCurRegion
@app.route("/query_region/<name>", methods=["GET"])
def query_cur_region(name):
    try:
        return forward_request(
            request,
            f"{check_config_exists()['Dispatch']['list'][name]}/query_cur_region?{request.query_string.decode()}",
        )
    except KeyError:
        print(f"Unknow Region={name}")
        abort(404)
    except Exception as err:
        print(
            f"Errors other than the occurrence of the processing request event: {err=}, {type(err)=}"
        )
        abort(500)
