try:
    from __main__ import app
except ImportError:
    from main import app

import rsa
import src.tools.repositories                       as repositories
import src.proto.live.QueryCurrRegionHttpRsp_v2_pb2 as CurrRegion_Live

from flask                           import request
from base64                          import b64encode
from src.tools.action.rsaDecrypt     import chunked
from src.tools.action.getHotFixData  import getHotFixData
from src.tools.logger.dispatch       import logger                  as dispatch_log

rsa_sign_key = "MIIEpQIBAAKCAQEAxbbx2m1feHyrQ7jP+8mtDF/pyYLrJWKWAdEv3wZrOtjOZzeL\nGPzsmkcgncgoRhX4dT+1itSMR9j9m0/OwsH2UoF6U32LxCOQWQD1AMgIZjAkJeJv\nFTrtn8fMQ1701CkbaLTVIjRMlTw8kNXvNA/A9UatoiDmi4TFG6mrxTKZpIcTInvP\nEpkK2A7Qsp1E4skFK8jmysy7uRhMaYHtPTsBvxP0zn3lhKB3W+HTqpneewXWHjCD\nfL7Nbby91jbz5EKPZXWLuhXIvR1Cu4tiruorwXJxmXaP1HQZonytECNU/UOzP6GN\nLdq0eFDE4b04Wjp396551G99YiFP2nqHVJ5OMQIDAQABAoIBAQDEeYZhjyq+avUu\neSuFhOaIU4/ZhlXycsOqzpwJvzEz61tBSvrZPA5LSb9pzAvpic+7hDH94jX89+8d\nNfO7qlADsVNEQJBxuv2o1MCjpCRkmBZz506IBGU60Kt1j5kwdCEergTW1q375z4w\nl8f7LmSL2U6WvKcdojTVxohBkIUJ7shtmmukDi2YnMfe6T/2JuXDDL8rvIcnfr5E\nMCgPQs+xLeLEGrIJdpUy1iIYZYrzvrpJwf9EJL3D0e7jkpbvAQZ8EF9YhEizJhOm\ndzTqW4PgW2yUaHYd3q5QjiILy7AC+oOYoTZln3RfjPOxl+bYjeMOWlqkgtpPQkAE\n4I64w8RZAoGBAPLR44pEkmTdfIIF8ZtzBiVfDZ29bT96J0CWXGVzp8x6bSu5J5jl\ns7sP8DEcjGZ6vHsLGOvkcNxzcnR3l/5HOz6TIuvVuUm36b1jHltq1xZStjGeKZs1\nihhJSu2lIA+TrK8FCRnKARJ0ughXGNZFItgeM230Sgjp2RL4ISXJ724XAoGBANBy\nS2RwNpUYvkCSZHSFnQM/jq1jldxw+0p4jAGpWLilEaA/8xWUnZrnCrPFF/t9llpb\ndTR/dCI8ntIMAy2dH4IUHyYKUahyHSzCAUNKpS0s433kn5hy9tGvn7jyuOJ4dk9F\no1PIZM7qfzmkdCBbX3NF2TGpzOvbYGJHHC3ssVr3AoGBANHJDopN9iDYzpJTaktA\nVEYDWnM2zmUyNylw/sDT7FwYRaup2xEZG2/5NC5qGM8NKTww+UYMZom/4FnJXXLd\nvcyxOFGCpAORtoreUMLwioWJzkkN+apT1kxnPioVKJ7smhvYAOXcBZMZcAR2o0m0\nD4eiiBJuJWyQBPCDmbfZQFffAoGBAKpcr4ewOrwS0/O8cgPV7CTqfjbyDFp1sLwF\n2A/Hk66dotFBUvBRXZpruJCCxn4R/59r3lgAzy7oMrnjfXl7UHQk8+xIRMMSOQwK\np7OSv3szk96hy1pyo41vJ3CmWDsoTzGs7bcdMl72wvKemRaU92ckMEZpzAT8cEMC\ncWKLb8yzAoGAMibG8IyHSo7CJz82+7UHm98jNOlg6s73CEjp0W/+FL45Ka7MF/lp\nxtR3eSmxltvwvjQoti3V4Qboqtc2IPCt+EtapTM7Wo41wlLCWCNx4u25pZPH/c8g\n1yQ+OvH+xOYG+SeO98Phw/8d3IRfR83aqisQHv5upo2Rozzo0Kh3OsE="

rsa_private_key = {
    "2": "MIIEpAIBAAKCAQEAz/fyfozlDIDWG9e3Lb29+7j3c66wvUJBaBWP10rB9HTE6prj\nfcGMqC9imr6zAdD9q+Gr1j7egvqgi3Da+VBAMFH92/5wD5PsD7dX8Z2f4o65Vk2n\nVOY8Dl75Z/uRhg0Euwnfrved69z9LG6utmlyv6YUPAflXh/JFw7Dq6c4EGeR+Kej\nFTwmVhEdzPGHjXhFmsVt9HdXRYSf4NxHPzOwj8tiSaOQA0jC4E4mM7rvGSH5GX6h\nma+7pJnl/5+rEVM0mSQvm0m1XefmuFy040bEZ/6O7ZenOGBsvvwuG3TT4FNDNzW8\nDw9ExH1l6NoRGaVkDdtrl/nFu5+a09Pm/E0ElwIDAQABAoIBAQCtH17Cck+KJQYX\nj29xqG4qykNUDawbILiKCMkBE7553Wq/UcjmuuR4bVnML8ucS3mgR/BgHV3l8vUK\nnxvqRx/oGZkWNazbiuwL+ThAblLWqrEmYuZVCoQcAnvkT8tIqDWz7fhDEuZnnkMz\nZcATIZzgZUSa5IfP3u3rP+MrVbyaCdzJEeI0Yrv1XT+M5ddkKQrYgqC5kRiYi/Lj\nNcLJhqSVt8p37CdJx1PGHFjKKb4MZpANlNRgeTtWpGVfS0PJLzaiI1NyPSJv7xWZ\ngVhbK9+wQxqSG6KmZ4vpEvRI1zKiov5BsAFN+GfuD5mpn1Xo9CpzTfj/sO13VpHH\n+Mt80+yBAoGBAPYXVEcXug5zqkqXup4dp1S05saz1zWPhUhQm+CrbhgeTqpjngJJ\nEB79qMrGmyki0P/cGtbTcrHf8+i7gDlIGW0OMb4/jn4f5ACVD00iyvkHSGPn0Aim\nMoNOMbkGot7SkSnncwxXdawwDyTu2dofXuBr72+GYqgRAG52IuA0C0pRAoGBANhX\np/UyW/htB27frKch/rTKQKm12kBV20AkkRUQUibiiQyWueWKs+5bVaW5R5oDIhWx\nqftJtnEFWUvWaTHpHsB/bpjS3CJ6WknqNbpa3QIScpV1uw8V+Etz/K2/ftjyZzFo\nnqc+Jud5364xFdIlOsRj9gZnK83Wcui6EFxAer5nAoGBAJzTzzSjLUHqejqhKR98\nnFeCFZPJpjuO5AxqunvaJAYgwlcZtueT8j8dvgTDvrvfYTu85CnFhNFQfFrzqspW\nZUW3hwHL9R3xatboJ2Er7Bf5iSuJ3my0pXpCSbO1Q/QmUrZWtl3GGsqJsg0CXjkA\nRvFUN7ll9ddPRmwewykIYa2RAoGAcmKuWFNfE1O6WWIELH4p6LcDR3fyRI/gk+KB\nnyx48zxVkAVllrsmdYFvIGd9Ny4u6F9+a3HG960HULS1/ACxFMCL3lumrsgYUvp1\nm+mM7xqH4QRVeh14oZRa5hbY36YS76nMMMsI0Ny8aqJjUjADCXF81FfabkPTj79J\nBS3GeEMCgYAXmFIT079QokHjJrWz/UaoEUbrNkXB/8vKiA4ZGSzMtl3jUPQdXrVf\ne0ofeKiqCQs4f4S0dYEjCv7/OIijV5L24mj/Z1Q4q++S5OksKLPPAd3gX4AYbRcg\nPS4rUKl1oDk/eYN0CNYC/DYV9sAv65lX8b35HYhvXISVYtwwQu/+Yg==",
    "3": "MIIEpAIBAAKCAQEA02M1I1V/YvxANOvLFX8R7D8At40IlT7HDWpAW3t+tAgQ7sqj\nCeYOxiXqOaaw2kJhM3HT5nZll48UmykVq45Q05J57nhdSsGXLJshtLcTg9liMEoW\n61BjVZi9EPPRSnE05tBJc57iqZw+aEcaSU0awfzBc8IkRd6+pJ5iIgEVfuTluani\nzhHWvRli3EkAF4VNhaTfP3EkYfr4NE899aUeScbbdLFI6u1XQudlJCPTxaISx5Zc\nwM+nP3v242ABcjgUcfCbz0AY547WazK4bWP3qicyxo4MoLOoe9WBq6EuG4CuZQrz\nKnq8ltSxud/6chdg8Mqp/IasEQ2TpvY78tEXDQIDAQABAoIBAQC4uPsYk4AsSe75\n0Au6Dz7kSfIgdDhJ44AisvTmfLauMFZLtfxfjBDhCwTxuD7XnCZAxHm97Ty+AqSp\nKm/raQQsvtWalMhBqYanzjDYMRv2niJ1vGjm3WrQxBaEF+yOtvrZsK5fQTslqInI\nqknIQH7fgjazJ7Z28D18sYNj37qfFWSSymgFo+SoS/BKEr200lpRA/oaGXiHcyIO\njJidP6b7UGes7uhMXUvLrfozmCsSqslxXO5Uk5XN/fWl4LxCGX7mpNfPZIT5YBSj\nHliFkNlxIjyJg8ORLGi82M2cuyxp39r93F6uaCjLtb+rdwlGur7npgXUkKfWQJf9\nWE7uar6BAoGBAPXIuIuYFFUhqNz5CKU014jZu6Ql0z5ZA08V84cTJcfLIK4e2rqC\n8DFTldA0FtVfOGt0V08H/x2pRChGOvUwGG5nn9Dqqh6BjByUrW4z2hnXzT3ZuSDh\n6eapiCB1jl9meJ0snhF2Ps/hqWGL2b3SkCCe90qVTzOVOeLO6YUCIOq9AoGBANws\nfQkAq/0xw8neRGNTrnXimvbS+VXPIF38widljubNN7DY5cIFTQJrnTBWKbuz/t9a\nJ8QX6TFL0ci/9vhPJoThfL12vL2kWGYgWkWRPmqaBW3yz7Hs5rt+xuH3/7A5w5vm\nkEg1NZJgnsJ0rMUTu1Q6PM5CBg6OpyHY4ThBb8qRAoGAML8ciuMgtTm1yg3CPzHZ\nxZSZeJbf7K+uzlKmOBX+GkAZPS91ZiRuCvpu7hpGpQ77m6Q5ZL1LRdC6adpz+wkM\n72ix87d3AhHjfg+mzgKOsS1x0WCLLRBhWZQqIXXvRNCH/3RH7WKsVoKFG4mnJ9TJ\nLQ8aMLqoOKzSDD/JZM3lRWkCgYA8hn5Y2zZshCGufMuQApETFxhCgfzI+geLztAQ\nxHpkOEX296kxjQN+htbPUuBmGTUXcVE9NtWEF7Oz3BGocRnFrbb83odEGsmySXKH\nbUYbR/v2Ham638UOBevmcqZ3a2m6kcdYEkiH1MfP7QMRqjr1DI1qpfvERLLtOxGu\nxU5WAQKBgQCaVavyY6Slj3ZRQ7iKk9fHkge/bFl+zhANxRfWVOYMC8mD2gHDsq9C\nIdCp1Mg0tJpWLaGgyDM1kgChZYsff4jRxHC4czvAtoPSlxWXF2nL31qJ3vk2Zzzc\na4GSHAInodXBrKstav5SIKosWKT2YysxgHlA9Sm2f4n09GjFbslEHg==",
    "4": "MIIEpAIBAAKCAQEAyaxqjPJP5+Innfv5IdfQqY/ftS++lnDRe3EczNkIjESWXhHS\nOljEw9b9C+/BtF+fO9QZL7Z742y06eIdvsMPQKdGflB26+9OZ8AF4SpXDn3aVWGr\n8+9qpB7BELRZI/Ph2FlFL4cobCzMHunncW8zTfMId48+fgHkAzCjRl5rC6XT0Yge\n6+eKpXmF+hr0vGYWiTzqPzTABl44WZo3rw0yurZTzkrmRE4kR2VzkjY/rBnQAbFK\nKFUKsUozjCXvSag4l461wDkhmmyivpNkK5cAxuDbsmC39iqagMt9438fajLVvYOv\npVs9ci5tiLcbBtfB4Rf/QVAkqtTm86Z0O3e7DwIDAQABAoIBAQCyma226vTW35LE\nN5zXWuAg+hhcxk6bvofWMUMXKvGF/0vHPTMXlvuSkDeDNa4vBivneRthBNPMgb3q\nDuTWxrogQMOOI8ZdhY3DFexfDvcQD2anDJuSqSmg9Nd36q+yxk3xIoXB5Ilo23dd\nvTnJXHhsBNovv7zRLO134cAHFqDoKzt5EEHre0skUcn6HjHOek6c53jvpKr5LSrr\niwx5gMuY/7ZSIUDo9WGY70qbQFGY6bOlX9x8uNjcFF+7SztEVQ+vhJ/+7EvwqaJr\nysweo0l91TKM9WaMuwoucKeceVWuynEw6GGTw8UTLtltekLGe6bS8YxY8fVwnKkT\nRwJYwAJRAoGBAP2rhcfOA+1Ja37hUHKebfp9rHsex4+pGyt3Kdu7WdqOn4sexmya\nBuiHQcUchPDVla/ruQZ20+8LHgzBDo0m8sY7gpf715UV9NSVIRD0wu26SKRklOFz\nJ4HBOwU9hBGLSnRUJzyvVlt5O7E9hAv61SCrvWBEcow2YnKNQLwvjMVJAoGBAMuG\noSb3A/ulqtp2zpxVAclYe/bSItZZTOUWP6Vb4hOiHxIJ0n1H9ap6grOYkJ/Yn4gg\nyYzKm/noF1wXP7Rj/xOahnvMkzhGdmOabvE9LH5HwQTWxBBWTkZzgBbYtbg+J5MT\ncKqJaychSRjJj+xX+d90rtlSu/c27chlSRKAHXWXAoGAFTcIHDq9l1XBmL3tRXi8\nh+uExlM/q2MgM5VmucrEbAPrke4D+Ec1drMBLCQDdkTWnPzg34qGlQJgA/8NYX61\nZSDK/j0AvaY1cKX8OvfNaaZftuf2j5ha4H4xmnGXnwQAORRkp62eUk4kUOFtLrdO\npcnXL7rpvZI6z4vCszpi0okCgYEAp3lZEl8g/+oK9UneKfYpSi1tlGTGFevVwozU\nQpWhKta1CnraogycsnOtKWvZVi9C1xljwF7YioPY9QaMfTvroY3+K9DjM+OHd96U\nfB4Chsc0pW60V10te/t+403f+oPqvLO6ehop+kEBjUwPCkQ6cQ3q8xmJYpvofoYZ\n4wdZNnECgYBwG8Vrv7Z+kX9Zuh1FvcRoY57bYLU0cWW92SA3Nvi8pZOIEaLHrQyZ\npvvaLIicR1m9+KsOAmii7ru0zL7KsrGW+5migQsaDi4gzahKQpad/R7MLKi/L53r\nYmo0aZKARLHW82GbomQ0zxdRoo9vaqfGNpXkxyyt3k3GGDunmrskYw==",
    "5": "MIIEpAIBAAKCAQEAsJbFp3WcsiojjdQtVnTuvtawL2m4XxK93F6lCnFwcZqUP39t\nxFGGlrogHMqreyawIUN7E5shtwGzigzjW8Ly5CryBJpXP3ehNTqJS7emb+9LlC19\nOxa1eQuUQnatgcsd16DPH7kJ5JzN3vXnhvUyk4Qficdmm0uk7FRaNYFi7EJs4xyq\nFTrp3rDZ0dzBHumlIeK1om7FNt6Nyivgp+UybO7kl0NLFEeSlV4S+7ofitWQsO5x\nYqKAzSzz+KIRQcxJidGBlZ1JN/g5DPDpx/ztvOWYUlM7TYk6xN3focZpU0kBzAw/\nrn94yW9z8jpXfzk+MvWzVL/HAcPy4ySwkay0NwIDAQABAoIBADzKWpawbVYEHaM4\nlLb7oCjAPXzE9zx7djLDvisfLCdfoINPedkoe52ty1o+BtRpWB7LXTY9pFic1FLE\n5wvyy6zyf8hH3ZsysqNhWFxhh4FnLmx/UGokAir+anaK5mYVJ1vQtxzjlV1HAbQs\nkRyrklKoHDdRFqiFXOwiib97oDNWhD+RxfyGwwJnynZZSXdLbLSiz/QHQNr/+Ufk\nKRBaxt0CfU7mOLZxoy6fNAxHdBcBJPHCyh+aDvEbix7nSncSU8Ju/48YJ8DrglbZ\nsXCYoA5Uz8NMDuaEMgoNWCFQVoEcRkEUoaH7BlWd3UUFRPnDZ1B4BmkrVoRE8a58\n3OqSwakCgYEA19wQUISXtpnmCrEZfbyZ6IwOy8ZCVaVUtbTjVa8UyfNglzzJG3yz\ncXU3X35v5/HNCHaXbG2qcbQLThnHBA+obW3RDo+Q49V84Zh1fUNH0ONHHuC09kB/\n/gHqzn/4nLf1aJ2O0NrMyrZNsZ0ZKUKQuVCqWjBOmTNUitcc8RpXZ8sCgYEA0W09\nPOM/It7RoVGI+cfbbgSRmzFo9kzSp5lP7iZ81bnvUMabu2nv3OeGc3Pmdh1ZJFRw\n6iDM6VVbG0uz8g+f8+JT32XdqM7MJAmgfcYfTVBMiVnh330WNkeRrGWqQzB2f2Wr\n+0vJjU8CAAcOWDh0oNguJ1l1TSyKxqdL8FsA38UCgYEAudt1AJ7psgOYmqQZ+rUl\nH6FYLAQsoWmVIk75XpE9KRUwmYdw8QXRy2LNpp9K4z7C9wKFJorWMsh+42Q2gzyo\nHHBtjEf4zPLIb8XBg3UmpKjMV73Kkiy/B4nHDr4I5YdO+iCPEy0RH4kQJFnLjEcQ\nLT9TLgxh4G7d4B2PgdjYYTkCgYEArdgiV2LETCvulBzcuYufqOn9/He9i4cl7p4j\nbathQQFBmSnkqGQ+Cn/eagQxsKaYEsJNoOxtbNu/7x6eVzeFLawYt38Vy0UuzFN5\neC54WXNotTN5fk2VnKU4VYVnGrMmCobZhpbYzoZhQKiazby/g60wUtW9u7xXzqOd\nM/428YkCgYBwbEOx1RboH8H+fP1CAiF+cqtq4Jrz9IRWPOgcDpt2Usk1rDweWrZx\nbTRlwIaVc5csIEE2X02fut/TTXr1MoXHa6s2cQrnZYq44488NsO4TAC26hqs/x/H\nbVOcX13gT26SYngAHHeh7xjWJr/KgIIwvcvgvoVs6lu7a8aLUvrOag=="
}

client_sign_key = rsa.PrivateKey.load_pkcs1(
    f"-----BEGIN RSA PRIVATE KEY-----\n{rsa_sign_key}\n-----END RSA PRIVATE KEY-----".encode()
)

with open(repositories.DISPATCH_SEED, "rb") as f:
    dispatch_seed = f.read()

# 签名
def hotFixString(serializeString: bytes, client_private_key: bytes) -> str:
    decrypted = b""
    for chunk in chunked(245, serializeString):
        decrypted += rsa.encrypt(chunk, client_private_key)

    return b64encode(decrypted).decode(), b64encode(rsa.sign(serializeString, client_sign_key, 'SHA-256')).decode()

# 返回客户端提示
def hotFixDataNotFound(client_private_key: bytes, msg: str) -> dict:
    error_msg_config = CurrRegion_Live.QueryCurrRegionHttpRsp_v2()
    error_msg_config.retcode = -1
    error_msg_config.msg = msg
    error_msg_config.client_secret_key = dispatch_seed
    error_msg_string = error_msg_config.SerializeToString()

    content, sign = hotFixString(error_msg_string, client_private_key)

    return {"content": f"{content}", "sign": f"{sign}"}

# 自解析热更
# http://localhost:21000/query_cur_region?version=CNRELWin2.8.0&lang=2&platform=3&binary=1&time=628&channel_id=1&sub_channel_id=1&account_type=1&dispatchSeed=7057eb3d64a1c0e2
@app.route("/query_cur_region", methods=["GET"])
def query_cur_region():
    client_key_id  = request.args.get("key_id")
    client_version = request.args.get("version")

    # 客户端首次进入时会提前访问 此时无参
    if not client_version and not client_key_id:
        return ''

    # 无版本标识 默认2
    if not client_key_id:
        client_key_id = "2"

    if not client_version:
        dispatch_log.error(f"主机 {request.remote_addr} 访问 hot fix 服务失败: 无配置信息")
        return hotFixDataNotFound(client_private_key, "Not found version config")

    # 获取客户端私钥
    client_private_key = rsa.PrivateKey.load_pkcs1(
        f"-----BEGIN RSA PRIVATE KEY-----\n{rsa_private_key[client_key_id]}\n-----END RSA PRIVATE KEY-----".encode()
    )

    # 获取热更配置信息
    hot_fix_data   = getHotFixData(client_version)
    if len(hot_fix_data) == 0:
        dispatch_log.warning(f"主机 {request.remote_addr} 访问 hot fix 服务失败: 版本标识: {client_version} KeyID: {client_key_id}")
        return hotFixDataNotFound(client_private_key, "Not found hot fix config")

    hot_fix_config = CurrRegion_Live.QueryCurrRegionHttpRsp_v2()
    hot_fix_config.retcode                                           = 11
    hot_fix_config.msg                                               = ""
    hot_fix_config.region_info.res_version_config.relogin            = True
    hot_fix_config.client_secret_key                                 = dispatch_seed
    hot_fix_config.stop_server.stop_end_time                         = 2051193600   # 2035-01-01
    hot_fix_config.stop_server.stop_begin_time                       = 1640966400   # 2022-01-01
    hot_fix_config.region_info.data_url                              = hot_fix_data['DataUrl']
    hot_fix_config.region_info.area_type                             = hot_fix_data['AreaType']
    hot_fix_config.region_info.resource_url                          = hot_fix_data['ResourceUrl']
    hot_fix_config.region_info.client_data_md5                       = hot_fix_data['ClientDataMd5']
    hot_fix_config.region_info.client_data_version                   = hot_fix_data['ClientDataVersion']
    hot_fix_config.region_info.client_silence_data_md5               = hot_fix_data['ClientSilenceDataMd5']
    hot_fix_config.region_info.client_silence_data_version           = hot_fix_data['ClientSilenceDataVersion']
    hot_fix_config.region_info.res_version_config.md5                = hot_fix_data['ResVersionConfig']['Md5']
    hot_fix_config.region_info.res_version_config.version            = hot_fix_data['ResVersionConfig']['Version']
    hot_fix_config.region_info.res_version_config.release_total_size = hot_fix_data['ResVersionConfig']['ReleaseTotalSize']
    hot_fix_config.region_info.res_version_config.version_suffix     = hot_fix_data['ResVersionConfig']['VersionSuffix']
    hot_fix_config.region_info.res_version_config.branch             = hot_fix_data['ResVersionConfig']['Branch']
    hot_fix_config.region_info.client_version_suffix                 = hot_fix_data['ClientVersionSuffix']
    hot_fix_config.region_info.client_silence_version_suffix         = hot_fix_data['ClientSilenceVersionSuffix']
    # hot_fix_config.stop_server.url                                 = "https://www.cokeserver.com"
    hot_fix_config.stop_server.content_msg                           = '游戏资源下载完成，请重新登录以继续'

    host_fix_string = hot_fix_config.SerializeToString()
    content, sign = hotFixString(host_fix_string, client_private_key)

    dispatch_log.info(f"主机 {request.remote_addr} 访问 hot fix 服务成功: 版本标识: {client_version} KeyID: {client_key_id} 签名: {sign}")
    return {"content": f"{content}", "sign": f"{sign}"}
