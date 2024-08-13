try:
    from __main__ import app
except ImportError:
    from main import app

import re
import json
import src.tools.repositories as repositories
import src.proto.cbt.QueryRegionListHttpRsp_v1_pb2 as RegionList_CBT
import src.proto.live.QueryRegionListHttpRsp_v2_pb2 as RegionList_Live

from base64 import b64encode
from flask_caching import Cache
from src.tools.library import forward_request
from flask import Response, abort, request
from src.tools.loadconfig import load_config
from src.tools.response import json_rsp_with_msg

cache = Cache(app, config={"CACHE_TYPE": "simple"})

with open(repositories.DISPATCH_KEY, "rb") as f:
    dispatch_key = f.read()
with open(repositories.DISPATCH_SEED, "rb") as f:
    dispatch_seed = f.read()


# 新路由（4.0）
@app.route("/dispatch/dispatch/getGateAddress", methods=["GET"])
def get_gatesrip():
    gateserver = load_config()["Gateserver"]
    gate_info = {"address_list":[],}
    for address in gateserver:
        ip_list = {
            "ip": address.get("ip", ""),
            "port": address.get("port", ""),
        }
        gate_info["address_list"].append(ip_list)
    return json_rsp_with_msg( repositories.RES_SUCCESS, "OK", {"data": gate_info})


# ===================== Dispatch 配置 =====================#
# 实验性分区 Dispatch - CBT/Live
@app.route("/query_region_list", methods=["GET"])
def query_dispatch():
    regions = load_config()["Region"]

    # dispatch 请求
    def cbt1_dispatch(custom_config):
        for entry in regions:
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

        for entry in regions:
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

        for entry in regions:
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

    def output_region(client):
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
                "CAESGE5vdCBGb3VuZCB2ZXJzaW9uIGNvbmZpZw==", content_type="text/plain"
            )

    # 外部获取版本标识名称并与版本库标识对比
    get = request.args.get("version")
    if get is None:
        return Response(
            '{"retcode":"-1", "msg":"system error"}', content_type="text/plain"
        )
    if get == "":
        return Response(
            "CAESGE5vdCBGb3VuZCB2ZXJzaW9uIGNvbmZpZw==", content_type="text/plain"
        )
    else:
        # 假识别 就是版本标识 + x.x.x 版本号
        version_pattern = re.compile(r"(WIN|Win|Android|IOS|ios).*\d+\.\d+\.\d+$")
        if not version_pattern.search(get):
            return Response(
                "CAESGE5vdCBGb3VuZCB2ZXJzaW9uIGNvbmZpZw==", content_type="text/plain"
            )
        else:
            client = re.sub(r"(WIN|Win|Android|IOS|ios).*$", "", get)
            return output_region(client)


# 解析 QueryCurRegion
@app.route("/query_region/<name>", methods=["GET"])
def query_cur_region(name):
    try:
        return forward_request(
            request,
            f"{load_config()['Dispatch']['list'][name]}/query_cur_region?{request.query_string.decode()}",
        )
    except KeyError:
        print(f"Unknow Region={name}")
        abort(404)
    except Exception as err:
        print(
            f"Errors other than the occurrence of the processing request event: {err=}, {type(err)=}"
        )
        abort(500)
