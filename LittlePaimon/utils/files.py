try:
    import ujson as json
except ImportError:
    import json
from pathlib import Path
from ssl import SSLCertVerificationError
from typing import Union

from ruamel.yaml import YAML

from .requests import aiorequests


def load_json(path: Union[Path, str], encoding: str = 'utf-8'):
    """
    读取本地json文件，返回文件数据。

    :param path: 文件路径
    :param encoding: 编码，默认为utf-8
    :return: 数据
    """
    if isinstance(path, str):
        path = Path(path)
    if not path.name.endswith('.json'):
        path = path.with_suffix('.json')
    return json.loads(path.read_text(encoding=encoding)) if path.exists() else {}


async def load_json_from_url(url: str, path: Union[Path, str] = None, force_refresh: bool = False) -> dict:
    """
    从网络url中读取json，当有path参数时，如果path文件不存在，就会从url下载保存到path，如果path文件存在，则直接读取path

    :param url: url
    :param path: 本地json文件路径
    :param force_refresh: 是否强制重新下载
    :return: json字典
    """
    if path and Path(path).exists() and not force_refresh:
        return load_json(path=path)
    try:
        resp = await aiorequests.get(url)
    except SSLCertVerificationError:
        resp = await aiorequests.get(url.replace('https', 'http'))
    data = resp.json()
    if path and not Path(path).exists():
        save_json(data=data, path=path)
    return data


def save_json(data: dict, path: Union[Path, str] = None, encoding: str = 'utf-8'):
    """
    保存json文件

    :param data: json数据
    :param path: 保存路径
    :param encoding: 编码
    """
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding=encoding)


def load_yaml(path: Union[Path, str], encoding: str = 'utf-8'):
    """
    读取本地yaml文件，返回字典。

    :param path: 文件路径
    :param encoding: 编码，默认为utf-8
    :return: 字典
    """
    if isinstance(path, str):
        path = Path(path)
    yaml=YAML(typ='safe')
    return yaml.load(path.read_text(encoding=encoding)) if path.exists() else {}


def save_yaml(data: dict, path: Union[Path, str] = None, encoding: str = 'utf-8'):
    """
    保存yaml文件

    :param data: 数据
    :param path: 保存路径
    :param encoding: 编码
    """
    if isinstance(path, str):
        path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', encoding=encoding) as f:
        yaml=YAML(typ='safe')
        yaml.dump(
            data,
            f)
