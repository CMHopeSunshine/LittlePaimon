import math
from LittlePaimon.config import RESOURCE_BASE_PATH
from LittlePaimon.utils import logger, aiorequests
from LittlePaimon.utils.files import load_image
from LittlePaimon.utils.image import PMImage, font_manager as fm
from LittlePaimon.utils.message import MessageBuild

from .genshinmap import utils, models, request, img

from PIL import Image, ImageFile, ImageOps
ImageFile.LOAD_TRUNCATED_IMAGES = True
Image.MAX_IMAGE_PIXELS = None

map_name = {
    'teyvat': '提瓦特',
    'enkanomiya': '渊下宫',
    'chasm': '层岩巨渊'
}
map_name_reverse = {
    '提瓦特': 'teyvat',
    '渊下宫': 'enkanomiya',
    '层岩巨渊': 'chasm'
}


async def init_map(refresh: bool = False):
    """
    初始化地图
    :param refresh: 是否刷新
    """
    for map_id in models.MapID:
        save_path = RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_id.name}.png'
        save_path.parent.mkdir(parents=True, exist_ok=True)
        if map_id.name == 'golden_apple_archipelago' or (save_path.exists() and not refresh):
            continue
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
        logger.info('原神地图', f'<m>{map_name[map_id.name]}</m>地图初始化完成')


async def draw_map(name: str, map_: str):
    """
    获取地图
    :param name: 材料名
    :param map_: 地图名
    :return: 地图
    """
    map_id = models.MapID[map_name_reverse[map_]]
    maps = await request.get_maps(map_id)
    labels = await request.get_labels(map_id)
    if resources := list(filter(lambda x: x.name == name, [child for label in labels for child in label.children])):
        resource = resources[0]
    else:
        return MessageBuild.Text(f'未查找到材料{name}')
    points = await request.get_points(map_id)
    if not (points := utils.convert_pos(utils.get_points_by_id(resource.id, points), maps.detail.origin)):
        return MessageBuild.Text(f'在{map_}上未查找到材料{name}，请尝试其他地图')
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
    map_img = await load_image(RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_id.name}.png')
    lt_point = group_point[0][0]
    rb_point = group_point[0][1]
    map_img = map_img.crop((int(lt_point.x), int(lt_point.y), int(rb_point.x), int(rb_point.y)))
    for point in group_point[0][2]:
        point_trans = (int(point.x) - int(lt_point.x), int(point.y) - int(lt_point.y),)
        map_img.paste(point_icon, (point_trans[0] - 16, point_trans[1] - 16), point_icon)
    scale_f = map_img.width / map_img.height
    if scale_f > 980 / 850:
        map_img = map_img.resize((math.ceil(850 * scale_f), 850), Image.ANTIALIAS)
    else:
        map_img = map_img.resize((980, math.ceil(980 / scale_f)), Image.ANTIALIAS)
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
        await total_img.text_box(des.replace('\n', '^'), (482, 1010), (281, 520), fm.get('SourceHanSansCN-Bold.otf', 30), '#3c3c3c')
    await total_img.text('CREATED BY LITTLEPAIMON', (0, total_img.width), total_img.height - 45, fm.get('bahnschrift_bold', 36, 'Bold'), '#3c3c3c', align='center')
    total_img.save(RESOURCE_BASE_PATH / 'genshin_map' / 'results' / f'{map_}_{name}.png')
    return MessageBuild.Image(total_img, mode='RGB', quality=85)




