import re
import aiohttp
from ._language_dict import search_dict, suffix_list

GLOT_TOKEN = "2b42fd59-563f-4855-870d-f564c4e407b5"


async def run(command: str) -> str:
    # "py -i 50,100,3 import random" -> {'language_type': 'py', 'stdin': '50,100,3', 'code': 'import random'}
    match_obj = re.match(r"^(?P<language_type>[^ \n]+) ?(-i *(?P<stdin>[^ \n]+))?[\n ]+(?P<code>[\w\W]+)", command)
    code_type = match_obj.group("language_type").strip()
    if code_type not in search_dict:  # 如果发送的语言类型不在查询字典里面
        return f"输入有误, www找不到{code_type}, 请检查您的输入"
    code = match_obj.group("code").strip()  # 获取code的字段
    if len(code) == 0:  # 如果code为空
        return "运行代码不能为空~"
    stdin = match_obj.group("stdin")  # 获取stdin的输入
    type_name = search_dict[code_type]  # 从查询字典中拿到运行代码的完整语言名

    # 请求部分
    header = {
        "Authorization": f"Token {GLOT_TOKEN}",
        "Content-type": "application/json"
    }
    data = {
        "files": [
            {
                'name': f'main.{suffix_list[type_name]}',  # 固定文件名的话用户在处理java类文件的时候类名可能会不方便, 需要改进
                'content': code
            }
        ],
        "stdin": stdin if stdin is not None else "",
        "command": ""
    }
    try:
        async with aiohttp.TCPConnector(ssl=False) as connector:
            async with aiohttp.request("POST", headers=header,
                                       json=data,
                                       url=f"https://glot.io/api/run/{type_name}/latest",
                                       connector=connector
                                       ) as resp:
                rep_json = await resp.json()  # 获取响应
                if 'message' in rep_json:  # 如果message在里面的话基本上都是请求失败了, 运行时间过长或者api出错
                    return rep_json['message']

                result = "\n"
                stdout = rep_json['stdout'].rstrip()
                error = rep_json["error"].rstrip()
                stderr = rep_json["stderr"].rstrip()
                if stdout:
                    result += f"{stdout}\n"
                if stderr:
                    result += f"{stderr}\n"
                if error:
                    result += f"{error}\n"
                if len(result) > 500 or result.count("\n") > 15:
                    return f"输出结果过长，仅显示前500：\n{result[0:500]}"
                return result
    except Exception as e:  # 网络请求失败时走该分支
        from . import sv
        sv.logger.error(f"{e} occurred when request l: {code_type} c:{code}")
        return f"请求失败...请联系维护者"
