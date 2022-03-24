import os
import json
from asyncio import sleep
from hoshino import aiorequests
from .api import toApi, getApi, checkApi
from .meta_data import gachaQueryTypeIds, gachaQueryTypeNames, gachaQueryTypeDict
from .UIGF_and_XLSX import convertUIGF, writeXLSX

data_path = os.path.join(os.path.dirname(os.path.dirname(__file__)),'user_data', 'gacha_log_data')

async def getGachaLogs(url, gachaTypeId):
    size = "20"
    # api限制一页最大20
    gachaList = []
    end_id = "0"
    for page in range(1, 9999):
        api = getApi(url, gachaTypeId, size, page, end_id)
        r = await aiorequests.get(api)
        s = (await r.content).decode("utf-8")
        j = json.loads(s)
        gacha = j["data"]["list"]
        if not len(gacha):
            break
        for i in gacha:
            gachaList.append(i)
        end_id = j["data"]["list"][-1]["id"]
        await sleep(0.5)

    return gachaList

def mergeDataFunc(localData, gachaData):

    for banner in gachaQueryTypeDict:
        bannerLocal = localData["gachaLog"][banner]
        bannerGet = gachaData["gachaLog"][banner]
        if bannerGet == bannerLocal:
            pass
        else:
            # print("合并", gachaQueryTypeDict[banner], end=": ", flush=True)
            flaglist = [1] * len(bannerGet)
            loc = [[i["time"], i["name"]] for i in bannerLocal]
            for i in range(len(bannerGet)):
                gachaGet = bannerGet[i]
                get = [gachaGet["time"], gachaGet["name"]]
                if get in loc:
                    pass
                else:
                    flaglist[i] = 0 

            tempData = []
            for i in range(len(bannerGet)):
                if flaglist[i] == 0:
                    gachaGet = bannerGet[i]
                    tempData.insert(0, gachaGet)
            # print("追加", len(tempData), "条记录", flush=True)
            for i in tempData:
                localData["gachaLog"][banner].insert(0, i)

    return localData


async def get_data(url):
    gachaData = {}
    gachaData["gachaLog"] = {}
    for gachaTypeId in gachaQueryTypeIds:
        gachaLog = await getGachaLogs(url, gachaTypeId)
        gachaData["gachaLog"][gachaTypeId] = gachaLog
    
    uid_flag = 1
    for gachaType in gachaData["gachaLog"]:
        for log in gachaData["gachaLog"][gachaType]:
            if uid_flag and log["uid"]:
                gachaData["uid"] = log["uid"]
                uid_flag = 0

    uid = gachaData["uid"]
    localDataFilePath = os.path.join(data_path, f"gachaData-{uid}.json")

    if os.path.isfile(localDataFilePath):
        with open(localDataFilePath, "r", encoding="utf-8") as f:
            localData = json.load(f)
        mergeData = mergeDataFunc(localData, gachaData)
    else:
        mergeData = gachaData
    mergeData["gachaType"] = gachaQueryTypeDict
    # 写入json
    with open(localDataFilePath, "w", encoding="utf-8") as f:
        json.dump(mergeData, f, ensure_ascii=False, sort_keys=False, indent=4)
    # 写入UIFG json
    with open(os.path.join(data_path, f"UIGF_gachaData-{uid}.json"), "w", encoding="utf-8") as f:
        UIGF_data = convertUIGF(mergeData['gachaLog'], uid)
        json.dump(UIGF_data, f, ensure_ascii=False, sort_keys=False, indent=4)
	# 写入xlsx
    writeXLSX(uid, mergeData['gachaLog'], gachaQueryTypeIds)
    
