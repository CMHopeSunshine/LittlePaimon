import contextlib
from io import BytesIO
from pathlib import Path
from ssl import SSLCertVerificationError
from typing import Dict, Optional, Any, Union, Tuple

import httpx
from PIL import Image
import tqdm.asyncio

from LittlePaimon.utils import logger

class aiorequests:
    @staticmethod
    async def get(url: str,
                  *,
                  headers: Optional[Dict[str, str]] = None,
                  params: Optional[Dict[str, Any]] = None,
                  timeout: Optional[int] = 20,
                  **kwargs) -> httpx.Response:
        """
        说明：
            httpx的get请求封装
        参数：
            :param url: url
            :param headers: 请求头
            :param params: params
            :param timeout: 超时时间
        """
        async with httpx.AsyncClient() as client:
            return await client.get(url,
                                    headers=headers,
                                    params=params,
                                    timeout=timeout,
                                    **kwargs)

    @staticmethod
    async def post(url: str,
                   *,
                   headers: Optional[Dict[str, str]] = None,
                   params: Optional[Dict[str, Any]] = None,
                   data: Optional[Dict[str, Any]] = None,
                   json: Optional[Dict[str, Union[Any, str]]] = None,
                   timeout: Optional[int] = 20,
                   **kwargs) -> httpx.Response:
        """
        说明：
            httpx的post请求封装
        参数：
            :param url: url
            :param headers: 请求头
            :param params: params
            :param data: data
            :param json: json
            :param timeout: 超时时间
        """
        async with httpx.AsyncClient() as client:
            return await client.post(url,
                                     headers=headers,
                                     params=params,
                                     data=data,
                                     json=json,
                                     timeout=timeout,
                                     **kwargs)

    @staticmethod
    async def get_img(url: str,
                      *,
                      headers: Optional[Dict[str, str]] = None,
                      params: Optional[Dict[str, Any]] = None,
                      timeout: Optional[int] = 20,
                      save_path: Optional[Union[str, Path]] = None,
                      size: Optional[Union[Tuple[int, int], float]] = None,
                      mode: Optional[str] = None,
                      crop: Optional[Tuple[int, int, int, int]] = None,
                      **kwargs) -> Union[str, Image.Image]:
        """
        说明：
            httpx的get请求封装，获取图片
        参数：
            :param url: url
            :param headers: 请求头
            :param params: params
            :param timeout: 超时时间
            :param save_path: 保存路径，为空则不保存
            :param size: 图片尺寸，为空则不做修改
            :param mode: 图片模式，为空则不做修改
            :param crop: 图片裁剪，为空则不做修改
        """
        if save_path and Path(save_path).exists():
            img = Image.open(save_path)
        else:
            try:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url,
                                            headers=headers,
                                            params=params,
                                            timeout=timeout,
                                            **kwargs)
                    resp = resp.read()
                    if b'NoSuchKey' in resp or b'character not exists' in resp:
                        return 'No Such File'
                    img = Image.open(BytesIO(resp))
            except SSLCertVerificationError:
                async with httpx.AsyncClient() as client:
                    resp = await client.get(url.replace('https', 'http'),
                                            headers=headers,
                                            params=params,
                                            timeout=timeout,
                                            **kwargs)
                    resp = resp.read()
                    if b'error' in resp:
                        return 'No Such File'
                    img = Image.open(BytesIO(resp))
        if size:
            if isinstance(size, float):
                img = img.resize((int(img.size[0] * size), int(img.size[1] * size)), Image.ANTIALIAS)
            elif isinstance(size, tuple):
                img = img.resize(size, Image.ANTIALIAS)
        if mode:
            img = img.convert(mode)
        if crop:
            img = img.crop(crop)
        if save_path and not Path(save_path).exists():
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            img.save(save_path)
        return img

    @staticmethod
    async def download(url: str, save_path: Path, exclude_json: bool = False):
        """
        下载文件(带进度条)
        :param url: url
        :param save_path: 保存路径
        :param exclude_json: 是否排除json文件
        """
        save_path.parent.mkdir(parents=True, exist_ok=True)
        async with httpx.AsyncClient().stream(method='GET', url=url, follow_redirects=True) as datas:
            if exclude_json and 'application/json' in str(datas.headers['Content-Type']):
                raise Exception('file not match type')
            size = int(datas.headers['Content-Length'])
            f = save_path.open('wb')
            async for chunk in tqdm.asyncio.tqdm(iterable=datas.aiter_bytes(1),
                                                 desc=url.split('/')[-1],
                                                 unit='iB',
                                                 unit_scale=True,
                                                 unit_divisor=1024,
                                                 total=size,
                                                 colour='green'):
                f.write(chunk)
            f.close()

    @staticmethod
    async def download_icon(name: str,
                            headers: Optional[Dict[str, str]] = None,
                            save_path: Optional[Union[str, Path]] = None,
                            **kwargs):
        """
        下载icon
        :param name: url
        :param headers: 请求头
        :param save_path: 保存路径
        """
        urls = [
            f'https://file.microgg.cn/MiniGG/ui/{name}',
            f'https://api.ambr.top/assets/UI/{name}',
            f'https://enka.network/ui/{name}'
        ]
        for url in urls:
            with contextlib.suppress(Exception):
                return await aiorequests.get_img(url=url, headers=headers, save_path=save_path, **kwargs)
        logger.warning('资源检查', f'{name}下载失败，请检查网络')
        return None
