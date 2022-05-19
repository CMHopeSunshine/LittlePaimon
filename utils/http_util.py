import base64
from typing import Dict, Optional, Any, Union, Tuple
from pathlib import Path
from io import BytesIO
from PIL import Image
from retrying import retry
import httpx


class aiorequests:

    @classmethod
    async def get(cls,
                  url: str,
                  *,
                  headers: Optional[Dict[str, str]] = None,
                  params: Optional[Dict[str, Any]] = None,
                  timeout: Optional[int] = 20,
                  **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            return await client.get(url,
                                    headers=headers,
                                    params=params,
                                    timeout=timeout,
                                    **kwargs)

    @classmethod
    async def post(cls,
                   url: str,
                   *,
                   headers: Optional[Dict[str, str]] = None,
                   params: Optional[Dict[str, Any]] = None,
                   data: Optional[Dict[str, Any]] = None,
                   json: Optional[Dict[str, Union[Any, str]]] = None,
                   timeout: Optional[int] = 20,
                   **kwargs) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            return await client.post(url,
                                     headers=headers,
                                     params=params,
                                     data=data,
                                     json=json,
                                     timeout=timeout,
                                     **kwargs)

    @classmethod
    @retry(stop_max_attempt_number=3, wait_fixed=300)
    async def get_img(cls,
                      url: str,
                      *,
                      headers: Optional[Dict[str, str]] = None,
                      params: Optional[Dict[str, Any]] = None,
                      timeout: Optional[int] = 20,
                      save_path: Optional[Union[str, Path]] = None,
                      size: Optional[Tuple[int, int]] = None,
                      mode: Optional[str] = None,
                      to_b64: bool = False,
                      **kwargs) -> Union[str, Image.Image]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url,

                                    headers=headers,
                                    params=params,
                                    timeout=timeout,
                                    **kwargs)
            if to_b64:
                return 'base64://' + base64.b64encode(resp.read()).decode()
            else:
                img = Image.open(BytesIO(resp.read()))
                if size:
                    img = img.resize(size, Image.ANTIALIAS)
                if mode:
                    img = img.convert(mode)
                if save_path:
                    if isinstance(save_path, str):
                        save_path = Path(save_path)
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    img.save(save_path)
                return img
