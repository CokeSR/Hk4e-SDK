try:
    from __main__ import app
except ImportError:
    from main import app

import re
import json
import src.tools.repositories                       as repositories
import src.proto.cbt.QueryRegionListHttpRsp_v1_pb2  as RegionList_CBT
import src.proto.live.QueryRegionListHttpRsp_v2_pb2 as RegionList_Live

from flask                           import Response, abort, request
from base64                          import b64encode
from src.tools.response              import forwardRequest, jsonRspCommon
from src.tools.loadconfig            import loadConfig
from src.tools.response              import jsonRspWithMsg
from src.tools.logger.system         import logger                  as sys_log
from src.tools.logger.dispatch       import logger                  as dispatch_log

with open(repositories.DISPATCH_KEY, "rb") as f:
    dispatch_key = f.read()
with open(repositories.DISPATCH_SEED, "rb") as f:
    dispatch_seed = f.read()


# 新路由（4.0）
@app.route("/dispatch/dispatch/getGateAddress", methods=["GET"])
def get_gatesrip():
    gateserver = loadConfig()["Gateserver"]
    gate_info = {"address_list":[],}
    for address in gateserver:
        ip_list = {
            "ip": address.get("ip", ""),
            "port": address.get("port", ""),
        }
        gate_info["address_list"].append(ip_list)
    return jsonRspWithMsg( repositories.RES_SUCCESS, "OK", {"data": gate_info})


# ===================== Dispatch 配置 ===================== #
# 实验性分区 Dispatch - CBT/Live
@app.route("/query_region_list", methods=["GET"])
def query_dispatch():
    regions = loadConfig()["Region"]

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

    def output_region(client, version):
        sdk_env_common = {"CNREL": "0", "CN": "0", "CNIN": "0", "OSREL": "5", "CNCB": "6", "OSCB": "7"}
        # CBT1
        if client == "CHN":
            custom_config = {
                "region_list": [],
                "clientCustomConfig": '{"visitor": false, "sdkenv": "2", "checkdevice": false}',
            }
            dispatch_log.info(f"主机 {request.remote_addr} 访问 dispatch (CBT1) 成功: 版本类型: {client}")
            return cbt1_dispatch(custom_config)
        # CBT2
        elif client == "OVS":
            custom_config = '{"sdkenv": "2", "checkdevice": false, "showexception": false}'
            dispatch_log.info(f"主机 {request.remote_addr} 访问 dispatch (CBT2) 成功: 版本类型: {client} 环境: {custom_config}")
            return cbt2_dispatch(custom_config)
        # CBT3 - Live
        elif client in sdk_env_common:
            video_keys = {
                "common":"0",
                "2.0.0":"1946182291478952",
                "2.1.0":"8578639302762988",
                "2.2.0":"8986874010832568",
                "2.3.0":"4206600976229209",
                "2.4.0":"7630808905721825",
                "2.5.0":"4614952043623735",
                "2.6.0":"5578228838233776",
                "2.7.0":"5750031464064937"
            }

            if version not in video_keys:
                video_key = video_keys['common']
                dispatch_log.info(f"{version} 版本中获取到的 video key: {video_key}")
            else:
                video_key = video_keys[version]
                dispatch_log.info(f"{version} 版本暂无存取的 video key")

            custom_config = {"sdkenv": f"{sdk_env_common[client]}","checkdevice":"false","loadPatch":"false","showexception":"false","regionConfig":"pm|fk|add","downloadMode":"0","videoKey":f"{video_key}"}
            dispatch_log.info(f"主机 {request.remote_addr} 访问 dispatch (LIVE) 成功: 版本类型: {client} 环境: {custom_config}")
            return live_dispatch(json.dumps(custom_config))
        else:
            dispatch_log.error(f"主机 {request.remote_addr} 访问 dispatch 失败: 未知的版本类型: {client}")
            return Response("CAESGE5vdCBGb3VuZCB2ZXJzaW9uIGNvbmZpZw==", content_type="text/plain")

    # 外部获取版本标识名称并与版本库标识对比
    get = request.args.get("version")
    sys_log.info(f"获取到的版本: {get}")
    if get is None:
        dispatch_log.error(f"主机 {request.remote_addr} 访问 dispatch 失败: 无配置参数")
        return jsonRspCommon(repositories.RES_FAIL, "system error")
    if get == "":
        dispatch_log.error(f"主机 {request.remote_addr} 访问 dispatch 失败: 缺少必要的配置参数")
        return jsonRspCommon(repositories.RES_FAIL, "system error")
    else:
        # 假识别 就是版本标识 + x.x.x 版本号 | 小米演示服适配
        version_pattern = re.compile(r"(WIN|Win|Android|iOS|AndroidMi).*\d+\.\d+\.\d+$")
        if not version_pattern.search(get):
            dispatch_log.error(f"主机 {request.remote_addr} 访问 dispatch 失败: 未知的版本标识: {get}")
            return jsonRspCommon(repositories.RES_FAIL, "system error")
        else:
            client = re.sub(r"(WIN|Win|Android|iOS|AndroidMi).*$", "", get)
            version = re.sub(r"(CNREL|OSREL|CNCB|OSCB|CN|CNIN)", "", re.sub(r"(WIN|Win|Android|iOS|AndroidMi)", "", get))
            return output_region(client, str(version))


# 解析 QueryCurRegion
@app.route("/query_region/<name>", methods=["GET"])
def query_region(name):
    try:
        region = loadConfig()['Dispatch']['list'][name]
        dispatch_log.info(f"主机 {request.remote_addr} 将目标 {name} 转发至 dispatch 服务: {region}")
        return forwardRequest(request, f"{region}/query_cur_region?{request.query_string.decode()}",)
    except KeyError:
        dispatch_log.error(f"主机 {request.remote_addr} 访问 dispatch 服务失败: 未知的区域类型: {name}")
        abort(404)
    except Exception as err:
        sys_log.error(f"处理解析 dispatch 服务发生意外错误: {err=}, {type(err)=}")
        abort(500)
