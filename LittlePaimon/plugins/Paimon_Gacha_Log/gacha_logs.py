from asyncio import sleep
from pathlib import Path

from LittlePaimon.utils import aiorequests
from LittlePaimon.utils.files import load_json, save_json
from .UIGF_and_XLSX import convertUIGF, writeXLSX
from .api import getApi
from .meta_data import gachaQueryTypeIds, gachaQueryTypeDict

data_path = Path() / 'data' / 'LittlePaimon' / 'user_data' / 'gacha_log_data'


async def getGachaLogs(url, gachaTypeId):
    size = "20"
    # api限制一页最大20
    gachaList = []
    end_id = "0"
    for page in range(1, 9999):
        api = getApi(url, gachaTypeId, size, page, end_id)
        resp = await aiorequests.get(url=api)
        j = resp.json()
        gacha = j["data"]["list"]
        if not len(gacha):
            break
        gachaList.extend(iter(gacha))
        end_id = j["data"]["list"][-1]["id"]
        await sleep(0.5)

    return gachaList


def mergeDataFunc(localData, gachaData):
    for banner in gachaQueryTypeDict:
        bannerLocal = localData["gachaLog"][banner]
        bannerGet = gachaData["gachaLog"][banner]
        if bannerGet != bannerLocal:
            flaglist = [1] * len(bannerGet)
            loc = [[i["time"], i["name"]] for i in bannerLocal]
            for i in range(len(bannerGet)):
                gachaGet = bannerGet[i]
                get = [gachaGet["time"], gachaGet["name"]]
                if get not in loc:
                    flaglist[i] = 0
            tempData = []
            for i in range(len(bannerGet)):
                if flaglist[i] == 0:
                    gachaGet = bannerGet[i]
                    tempData.insert(0, gachaGet)
            for i in tempData:
                localData["gachaLog"][banner].insert(0, i)
    return localData


async def get_data(url):
    gachaData = {"gachaLog": {}}
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
    localDataFilePath = data_path / f"gachaData-{uid}.json"

    if localDataFilePath.is_file():
        localData = load_json(localDataFilePath)
        mergeData = mergeDataFunc(localData, gachaData)
    else:
        mergeData = gachaData
    mergeData["gachaType"] = gachaQueryTypeDict
    # 写入json
    save_json(mergeData, localDataFilePath)
    # 写入UIGF、json
    UIGF_data = convertUIGF(mergeData['gachaLog'], uid)
    save_json(UIGF_data, data_path / f"UIGF_gachaData-{uid}.json")
    # 写入xlsx
    writeXLSX(uid, mergeData['gachaLog'], gachaQueryTypeIds)
    return uid
