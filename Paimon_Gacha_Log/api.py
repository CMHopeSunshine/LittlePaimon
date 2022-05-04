import json
from urllib import parse
from aiohttp import ClientSession


def toApi(url):
    spliturl = str(url).split("?")
    if "webstatic-sea" in spliturl[0] or "hk4e-api-os" in spliturl[0]:
        spliturl[0] = "https://hk4e-api-os.mihoyo.com/event/gacha_info/api/getGachaLog"
    else:
        spliturl[0] = "https://hk4e-api.mihoyo.com/event/gacha_info/api/getGachaLog"
    url = "?".join(spliturl)
    return url


def getApi(url, gachaType, size, page, end_id=""):
    parsed = parse.urlparse(url)
    querys = parse.parse_qsl(str(parsed.query))
    param_dict = dict(querys)
    param_dict["size"] = size
    param_dict["gacha_type"] = gachaType
    param_dict["page"] = page
    param_dict["lang"] = "zh-cn"
    param_dict["end_id"] = end_id
    param = parse.urlencode(param_dict)
    path = str(url).split("?")[0]
    api = path + "?" + param
    return api


async def checkApi(url):
    try:
        async with ClientSession() as session:
            r = await session.get(url)
            j = await r.json()
    except Exception as e:
        return f'API请求解析出错：{e}'

    if not j["data"]:
        if j["message"] == "authkey error":
            return "authkey错误，请重新获取链接给派蒙！"
        elif j["message"] == "authkey timeout":
            return "authkey已过期，请重新获取链接给派蒙！"
        else:
            return f'数据为空，错误代码：{j["message"]}'
    return 'OK'


def getQueryVariable(url, variable):
    query = str(url).split("?")[1]
    vars = query.split("&")
    for v in vars:
        if v.split("=")[0] == variable:
            return v.split("=")[1]
    return ""


async def getGachaInfo(url):
    region = getQueryVariable(url, "region")
    lang = getQueryVariable(url, "lang")
    gachaInfoUrl = "https://webstatic.mihoyo.com/hk4e/gacha_info/{}/items/{}.json".format(region, lang)
    async with ClientSession() as session:
        r = await session.get(gachaInfoUrl)
        s = (await r.read()).decode("utf-8")
        gachaInfo = json.loads(s)
        return gachaInfo
