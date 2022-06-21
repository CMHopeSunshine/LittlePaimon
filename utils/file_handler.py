import json
from pathlib import Path
from typing import Union, Optional, Tuple
from ssl import SSLCertVerificationError
from PIL import Image
from utils import aiorequests


def load_image(
        path: Union[Path, str],
        *,
        size: Optional[Union[Tuple[int, int], float]] = None,
        crop: Optional[Tuple[int, int, int, int]] = None,
        mode: Optional[str] = None,
):
    """
    说明：
        读取图像，并预处理
    参数：
        :param path: 图片路径
        :param size: 预处理尺寸
        :param crop: 预处理裁剪大小
        :param mode: 预处理图像模式
        :return: 图像对象
    """
    img = Image.open(path)
    if size:
        if isinstance(size, float):
            img = img.resize((int(img.size[0] * size), int(img.size[1] * size)), Image.ANTIALIAS)
        elif isinstance(size, tuple):
            img = img.resize(size, Image.ANTIALIAS)
    if crop:
        img = img.crop(crop)
    if mode:
        img = img.convert(mode)
    return img


def load_json(file: str = None, path: Union[Path, str] = None, encoding: str = 'utf-8') -> dict:
    """
    说明：
        读取本地json文件，返回json字典。file和path参数2选1即可，file需为data/LittlePaimon中的文件，path哪的文件都行
    参数：
        :param file: 文件名
        :param path: 文件路径
        :param encoding: 编码，默认为utf-8
        :return: json字典
    """
    if file and not path:
        path = Path() / 'data' / 'LittlePaimon' / file
    elif path:
        if isinstance(path, str):
            path = Path(path)
    if not path.exists():
        save_json({}, file, path, encoding)
    return json.load(path.open('r', encoding=encoding))


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
    else:
        try:
            resp = await aiorequests.get(url)
        except SSLCertVerificationError:
            resp = await aiorequests.get(url.replace('https', 'http'))
        data = resp.json()
        if path and not Path(path).exists():
            save_json(data=data, path=path)
        return data


def save_json(data, file: str = None, path: Union[Path, str] = None, encoding: str = 'utf-8'):
    if file and not path:
        path = Path() / 'data' / 'LittlePaimon' / file
    elif path:
        if isinstance(path, str):
            path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, path.open('w', encoding=encoding), ensure_ascii=False, indent=4)
