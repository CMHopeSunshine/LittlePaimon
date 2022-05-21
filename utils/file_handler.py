import json
import requests
from pathlib import Path
from typing import Union, Optional, Tuple
from ssl import SSLCertVerificationError
from PIL import Image

from .decorator import cache


@cache()
def load_image(
        path: Union[Path, str],
        *,
        size: Optional[Union[Tuple[int, int], float]] = None,
        crop: Optional[Tuple[int, int, int, int]] = None,
        mode: Optional[str] = None,
        use_cache: bool = True
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


def load_json_from_url(url: str):
    try:
        resp = requests.get(url)
    except SSLCertVerificationError:
        resp = requests.get(url.replace('https', 'http'))
    return resp.json()


def save_json(data, file: str = None, path: Union[Path, str] = None, encoding: str = 'utf-8'):
    if file and not path:
        path = Path() / 'data' / 'LittlePaimon' / file
    elif path:
        if isinstance(path, str):
            path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    json.dump(data, path.open('w', encoding=encoding), ensure_ascii=False, indent=4)
