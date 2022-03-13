import json
import urllib
import requests
from asyncio import sleep
import time
import os
import hoshino,os
from hoshino import R,MessageSegment,aiorequests,logger,Service

sv = Service('原神抽卡记录导出')

def checkApi(url) -> bool:
    if not url:
        #print("url为空")
        return "url为空"
    if "getGachaLog" not in url:
        #print("错误的url，检查是否包含getGachaLog")
        return "错误的url，检查是否包含getGachaLog"
    try:
        r = requests.get(url)
        s = r.content.decode("utf-8")
        j = json.loads(s)
    except Exception as e:
        #print("API请求解析出错：" + str(e))
        return "API请求解析出错：" + str(e)

    if not j["data"]:
        if j["message"] == "authkey valid error":
            return "authkey错误"
        else:
            return "数据为空，错误代码：" + j["message"]
    return "OK"

def getApi(url: str, gachaType: str, size: str, page: int, end_id="") -> str:
    parsed = urllib.parse.urlparse(url)
    querys = urllib.parse.parse_qsl(parsed.query)
    param_dict = dict(querys)
    param_dict["size"] = size
    param_dict["gacha_type"] = gachaType
    param_dict["page"] = page
    param_dict["lang"] = "zh-cn"
    param_dict["end_id"] = end_id
    param = urllib.parse.urlencode(param_dict)
    path = url.split("?")[0]
    api = path + "?" + param
    return api


async def getGachaLogs(url: str, gachaTypeId: str, gachaTypeDict: dict) -> list:
    size = "20"
    # api限制一页最大20
    gachaList = []
    gachaList_temp = []
    end_id = "0"
    c = 0
    for page in range(1, 9999):
        #print(f"正在获取 {gachaTypeDict[gachaTypeId]} 第 {page} 页", flush=True)
        api = getApi(url, gachaTypeId, size, page, end_id)
        r = requests.get(api)
        s = r.content.decode("utf-8")
        j = json.loads(s)
        gacha = j["data"]["list"]
        if not len(gacha):
            break
        for i in gacha:
            gachaList_temp.append(i)
        end_id = j["data"]["list"][-1]["id"]
        await sleep(0.3)
    if gachaList_temp:
        gachaList.append({'uid':gachaList_temp[0]['uid']})
    gachaList_temp.reverse()
    for i in gachaList_temp:
        c += 1
        if i['rank_type'] == "5":
            fivechar = {}
            fivechar['name'] = i['name']
            fivechar['item_type'] = i['item_type']
            fivechar['count'] = c
            c = 0
            gachaList.append(fivechar)
    gachaList.append({'未出货':c})
    return gachaList

# def getGachaTypes(url: str) -> list:
#     tmp_url = url.replace("getGachaLog", "getConfigList")
#     parsed = urllib.parse.urlparse(tmp_url)
#     querys = urllib.parse.parse_qsl(parsed.query)
#     param_dict = dict(querys)
#     param_dict["lang"] = "zh-cn"
#     param = urllib.parse.urlencode(param_dict)
#     path = tmp_url.split("?")[0]
#     tmp_url = path + "?" + param
#     r = requests.get(tmp_url)
#     s = r.content.decode("utf-8")
#     configList = json.loads(s)
#     return configList["data"]["gacha_type_list"]

# def mergeDataFunc(localData: dict, gachaData: dict) -> dict:
#     gachaTypes = gachaData["gachaType"]
#     gachaTypeIds = [banner["key"] for banner in gachaTypes]
#     gachaTypeNames = [banner["name"] for banner in gachaTypes]
#     gachaTypeDict = dict(zip(gachaTypeIds, gachaTypeNames))

#     for banner in gachaTypeDict:
#         bannerLocal = localData["gachaLog"][banner]
#         bannerGet = gachaData["gachaLog"][banner]
#         if bannerGet == bannerLocal:
#             pass
#         else:
#             #print("合并", gachaTypeDict[banner])
#             flaglist = [1] * len(bannerGet)
#             loc = [[i["time"], i["name"]] for i in bannerLocal]
#             for i in range(len(bannerGet)):
#                 gachaGet = bannerGet[i]
#                 get = [gachaGet["time"], gachaGet["name"]]
#                 if get in loc:
#                     pass
#                 else:
#                     flaglist[i] = 0

#             print("获取到", len(flaglist), "条记录")
#             tempData = []
#             for i in range(len(bannerGet)):
#                 if flaglist[i] == 0:
#                     gachaGet = bannerGet[i]
#                     tempData.insert(0, gachaGet)
#             print("追加", len(tempData), "条记录")
#             for i in tempData:
#                 localData["gachaLog"][banner].insert(0, i)

#     return localData

@sv.on_prefix('原神抽卡记录导出')
async def get_gacha_record(bot,ev):
    url = ev.message.extract_plain_text().strip()
    spliturl = url.split("?")
    spliturl[0] = "https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog"
    url = "?".join(spliturl)
    checkApimsg = checkApi(url)
    if checkApimsg == 'OK':
        await bot.send(ev,'获取抽卡记录中，请稍候...',at_sender=True)
        gachaTypes = {'200': '常驻祈愿', '301': '角色活动祈愿', '302': '武器活动祈愿'}
        gachaData = {}
        gachaData["gachaLog"] = {}

        for gachaType in gachaTypes.items():
            gachaLog = await getGachaLogs(url, gachaType[0], gachaTypes)
            gachaData["gachaLog"][gachaType[1]] = gachaLog

        uid_flag = 1
        for gachaType in gachaData["gachaLog"]:
            for log in gachaData["gachaLog"][gachaType]:
                if uid_flag and log["uid"]:
                    gachaData["uid"] = log["uid"]
                    uid_flag = 0


        #gen_path = os.path.dirname(os.path.realpath(sys.argv[0]))
        uid = gachaData["uid"]
        mergeData = gachaData
        msg = f'你的抽卡记录如下\nuid: {uid}\n'
        for gachaType in gachaTypes.values():
            if gachaType in mergeData['gachaLog']:
                msg += gachaType +': '
                if len(mergeData['gachaLog'][gachaType]) <= 2:
                    msg += '没有五星记录'
                else:
                    for role in mergeData['gachaLog'][gachaType]:
                        if 'name' in role:
                            msg += f"{role['name']}({role['count']}) "
                msg += '\n'
        await bot.send(ev,msg,at_sender=True)
    else:
        await bot.send(ev,checkApimsg,at_sender=True)