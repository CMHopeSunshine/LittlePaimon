import math
from typing import List

from PIL import Image, ImageFile, ImageOps

from LittlePaimon.utils import logger
from LittlePaimon.utils.image import PMImage, font_manager as fm, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH
from LittlePaimon.utils.requests import aiorequests
from .genshinmap import utils, models, request, img, XYPoint

ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

map_name = {
    'teyvat':     '提瓦特',
    'enkanomiya': '渊下宫',
    'chasm':      '层岩巨渊'
}
map_name_reverse = {
    '提瓦特':   'teyvat',
    '渊下宫':   'enkanomiya',
    '层岩巨渊': 'chasm'
}


async def init_map():
    """
    初始化地图
    """
    for map_id in models.MapID:
        save_path = RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_id.name}.png'
        save_path.parent.mkdir(parents=True, exist_ok=True)
        if map_id.name == 'golden_apple_archipelago':
            continue
        if save_path.exists():
            save_path.unlink()
        status_icon = await load_image(RESOURCE_BASE_PATH / 'genshin_map' / 'status_icon.png')
        anchor_icon = await load_image(RESOURCE_BASE_PATH / 'genshin_map' / 'anchor_icon.png')
        maps = await request.get_maps(map_id)
        points = await request.get_points(map_id)
        status_points = utils.convert_pos(utils.get_points_by_id(2, points), maps.detail.origin)  # 七天神像
        anchor_points = utils.convert_pos(utils.get_points_by_id(3, points), maps.detail.origin)  # 传送锚点
        map_img = await utils.make_map(maps.detail)
        for point in status_points:
            map_img.paste(status_icon, (int(point.x) - 32, int(point.y) - 64), status_icon)
        for point in anchor_points:
            map_img.paste(anchor_icon, (int(point.x) - 32, int(point.y) - 64), anchor_icon)
        map_img.save(save_path)
        logger.info('原神地图', f'<m>{map_name[map_id.name]}</m>地图生成完成')
    return f'地图资源生成完成，目前有{"、".join(list(map_name_reverse.keys()))}地图。'


async def draw_map(name: str, map_: str):
    """
    获取地图
    :param name: 材料名
    :param map_: 地图名
    :return: 地图
    """
    map_id = models.MapID[map_name_reverse[map_]]
    if not (RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_id.name}.png').exists():
        return f'缺少{map_id.name}地图资源，请联系超级用户进行[生成地图]'
    maps = await request.get_maps(map_id)
    labels = await request.get_labels(map_id)
    if resources := list(filter(lambda x: x.name == name, [child for label in labels for child in label.children])):
        resource = resources[0]
    else:
        return MessageBuild.Text(f'未查找到材料{name}')
    points = await request.get_points(map_id)
    if not (points := utils.convert_pos(utils.get_points_by_id(resource.id, points), maps.detail.origin)):
        return MessageBuild.Text(f'{map_}未查找到材料{name}，请尝试其他地图')
    point_icon = await load_image(RESOURCE_BASE_PATH / 'genshin_map' / 'point_icon.png')
    if len(points) >= 3:
        group_point = img.k_means_points(points, 700)
    else:
        x1_temp = int(points[0].x) - 670
        x2_temp = int(points[0].x) + 670
        y1_temp = int(points[0].y) - 700
        y2_temp = int(points[0].y) + 700
        group_point = [(
            models.XYPoint(x1_temp, y1_temp),
            models.XYPoint(x2_temp, y2_temp),
            points)]
    map_img = (await load_image(RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_id.name}.png')).copy()
    lt_point = group_point[0][0]
    rb_point = group_point[0][1]
    map_img = map_img.crop((int(lt_point.x), int(lt_point.y), int(rb_point.x), int(rb_point.y)))
    for point in group_point[0][2]:
        point_trans = (int(point.x) - int(lt_point.x), int(point.y) - int(lt_point.y),)
        map_img.paste(point_icon, (point_trans[0] - 16, point_trans[1] - 16), point_icon)
    scale_f = map_img.width / map_img.height
    if scale_f > 980 / 850:
        map_img = map_img.resize((math.ceil(850 * scale_f), 850), Image.LANCZOS)
    else:
        map_img = map_img.resize((980, math.ceil(980 / scale_f)), Image.LANCZOS)
    map_img = map_img.crop((0, 0, 980, 850))
    map_img = ImageOps.expand(map_img, border=4, fill='#633da3')
    total_img = PMImage(await load_image(RESOURCE_BASE_PATH / 'genshin_map' / 'bg.png'))
    await total_img.paste(map_img, (48, total_img.height - 60 - map_img.height))
    icon = await aiorequests.get_img(resource.icon, size=(300, 300))
    await total_img.paste(icon, (100, 100))
    await total_img.text(f'「{name}」', 454, 145, fm.get('SourceHanSerifCN-Bold.otf', 72), 'white')
    info = await aiorequests.get(f'https://info.minigg.cn/materials?query={name}')
    info = info.json()
    des = ''
    if 'description' in info:
        des += info['description'].strip('\n')
    if 'source' in info:
        des += '\n推荐采集地点：' + '，'.join(info['source']).replace('推荐：', '')
    if des:
        await total_img.text_box(des.replace('\n', '^'), (482, 1010), (281, 520),
                                 fm.get('SourceHanSansCN-Bold.otf', 30), '#3c3c3c')
    await total_img.text('CREATED BY LITTLEPAIMON', (0, total_img.width), total_img.height - 45,
                         fm.get('bahnschrift_bold', 36, 'Bold'), '#3c3c3c', align='center')
    total_img.save(RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_}_{name}.png')
    return MessageBuild.Image(total_img, mode='RGB', quality=85)


async def get_full_map(names: List[str], map_: str):
    map_id = models.MapID[map_name_reverse[map_]]
    if not (RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_id.name}.png').exists():
        return f'缺少{map_id.name}地图资源，请联系超级用户进行[生成地图]'
    maps = await request.get_maps(map_id)
    labels = await request.get_labels(map_id)
    resources = []
    resources_not = []
    resources_points = []
    childs = [child for label in labels for child in label.children]
    for name in names:
        if res_filter := list(filter(lambda x: x.name == name, childs)):
            resources.append(res_filter[0])
        else:
            resources_not.append(name)
    if not resources:
        return MessageBuild.Text(f'未查找到材料{"、".join(names)}')
    points = await request.get_points(map_id)
    for resource in resources:
        if points_ := utils.convert_pos(utils.get_points_by_id(resource.id, points), maps.detail.origin):
            resources_points.append(points_)
        else:
            resources_not.append(resource.name)
    if not resources_points:
        return MessageBuild.Text(f'{map_}未查找到材料{"、".join(names)}，请尝试其他地图')
    map_img = (await load_image(RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_id.name}.png')).copy()
    box_icon = await load_image(RESOURCE_BASE_PATH / 'genshin_map' / 'point_box.png')
    max_point = XYPoint(x=0, y=0)
    min_point = XYPoint(x=map_img.width, y=map_img.height)
    for i, points in enumerate(resources_points):
        resource_icon = box_icon.copy()
        resource_icon.alpha_composite(await aiorequests.get_img(resources[i].icon, size=(90, 90)), (28, 15))
        resource_icon = resource_icon.resize((48, 48), Image.LANCZOS)
        if len(points) >= 3:
            group_point = img.k_means_points(points, 2000)
        else:
            x1_temp = int(points[0].x) - 2000
            x2_temp = int(points[0].x) + 2000
            y1_temp = int(points[0].y) - 2000
            y2_temp = int(points[0].y) + 2000
            group_point = [(
                models.XYPoint(x1_temp, y1_temp),
                models.XYPoint(x2_temp, y2_temp),
                points)]
        if len(group_point[0][2]) > 400:
            group_point = img.k_means_points(points, 600)
        lt_point = group_point[0][0]
        rb_point = group_point[0][1]
        min_point = XYPoint(x=min(min_point.x, lt_point.x), y=min(min_point.y, lt_point.y))
        max_point = XYPoint(x=max(max_point.x, rb_point.x), y=max(max_point.y, rb_point.y))
        for point in group_point[0][2]:
            point_trans = (int(point.x), int(point.y))
            map_img.paste(resource_icon, (point_trans[0] - 24, point_trans[1] - 48), resource_icon)
    map_img = map_img.crop((int(min_point.x) - 50, int(min_point.y) - 50, int(max_point.x) + 50, int(max_point.y) + 50))
    if resources_not:
        return MessageBuild.Text(f'{map_}未找到材料{"、".join(resources_not)}，请尝试其他地图\n') + MessageBuild.Image(
            map_img)
    else:
        return MessageBuild.Image(map_img)
