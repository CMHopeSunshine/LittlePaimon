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


def load_json(file: str = None, path: Union[Path, str] = None, encoding: str = 'utf-8'):
    if file and not path:
        path = Path() / 'data' / 'LittlePaimon' / file
    elif path:
        if isinstance(path, str):
            path = Path(path)
    if not path.exists():
        save_json({}, file, path, encoding)
    return json.load(path.open('r', encoding=encoding))


async def load_json_from_url(url: str, encoding: str = 'utf-8', refresh: bool = False):
    if 'static.cherishmoon.fun' in url:
        url_path = Path() / 'data' / url.split('static.cherishmoon.fun/')[1]
        if refresh or not url_path.exists():
            try:
                resp = await aiorequests.get(url)
            except SSLCertVerificationError:
                resp = await aiorequests.get(url.replace('https', 'http'))
            save_json(resp.json(), path=url_path, encoding=encoding)
            return resp.json()
        else:
            return load_json(path=url_path, encoding=encoding)


def save_json(data, file: str = None, path: Union[Path, str] = None, encoding: str = 'utf-8'):
    if file and not path:
        path = Path() / 'data' / 'LittlePaimon' / file
    elif path:
        if isinstance(path, str):
            path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, path.open('w', encoding=encoding), ensure_ascii=False, indent=4)
