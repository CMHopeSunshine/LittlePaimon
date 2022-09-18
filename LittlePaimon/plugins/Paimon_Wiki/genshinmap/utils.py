from __future__ import annotations

from io import BytesIO
from typing import List, Union
from asyncio import gather, create_task

from PIL import Image
from httpx import AsyncClient

from .models import Maps, Point, XYPoint

CLIENT = AsyncClient()


async def get_img(url: str) -> Image.Image:
    resp = await CLIENT.get(url)
    resp.raise_for_status()
    return Image.open(BytesIO(resp.read()))


async def make_map(map: Maps) -> Image.Image:
    """
    获取所有地图并拼接

    警告：可能导致内存溢出

    在测试中，获取并合成「提瓦特」地图时占用了约 1.4 GiB

    建议使用 `genshinmap.utils.get_map_by_pos` 获取地图单片

    参数：
        map: `Maps`
            地图数据，可通过 `get_maps` 获取

    返回：
        `PIL.Image.Image` 对象

    另见：
        `get_map_by_pos`
    """
    img = Image.new("RGBA", tuple(map.total_size))
    x = 0
    y = 0
    maps: List[Image.Image] = await gather(
        *[create_task(get_img(url)) for url in map.slices]
    )
    for m in maps:
        img.paste(m, (x, y))
        x += 4096
        if x >= map.total_size[0]:
            x = 0
            y += 4096
    return img


async def get_map_by_pos(
    map: Maps, x: Union[int, float], y: Union[int, float] = 0
) -> Image.Image:
    """
    根据横坐标获取地图单片

    参数：
        map: `Maps`
            地图数据，可通过 `get_maps` 获取

        x: `int | float`
            横坐标

        y: `int | float` (default: 0)
            纵坐标

    返回：
        `PIL.Image.Image` 对象
    """
    # 4 * (y // 4096) {0,4,8}
    # x // 4096 {0,1,2,3}
    return await get_img(map.slices[4 * (int(y // 4096)) + int(x // 4096)])


def get_points_by_id(id_: int, points: List[Point]) -> List[XYPoint]:
    """
    根据 Label ID 获取坐标点

    参数：
        id_: `int`
            Label ID

        points: `list[Point]`
            米游社坐标点列表，可通过 `get_points` 获取

    返回：
        `list[XYPoint]`
    """
    return [
        XYPoint(point.x_pos, point.y_pos)
        for point in points
        if point.label_id == id_
    ]


def convert_pos(points: List[XYPoint], origin: List[int]) -> List[XYPoint]:
    """
    将米游社资源坐标转换为以左上角为原点的坐标系的坐标

    参数：
        points: `list[XYPoint]`
            米游社资源坐标

        origin: `list[Point]`
            米游社地图 Origin，可通过 `get_maps` 获取

    返回：
        `list[XYPoint]`

    示例：
        >>> from genshinmap.models import XYPoint
        >>> points = [XYPoint(1200, 5000), XYPoint(-4200, 1800)]
        >>> origin = [4844,4335]
        >>> convert_pos(points, origin)
        [XYPoint(x=6044, y=9335), XYPoint(x=644, y=6135)]
    """
    return [XYPoint(x + origin[0], y + origin[1]) for x, y in points]
