import math
from pathlib import Path
from LittlePaimon.config import RESOURCE_BASE_PATH
from LittlePaimon.utils import aiorequests, scheduler
from LittlePaimon.utils.files import save_json, load_json, load_image
from LittlePaimon.utils.image import PMImage, font_manager as fm
from LittlePaimon.utils.message import MessageBuild

week_cn = {
    'monday':    '周一',
    'tuesday':   '周二',
    'wednesday': '周三',
    'thursday':  '周四',
    'friday':    '周五',
    'saturday':  '周六',
}

MATERIAL_URL = 'https://api.ambr.top/v2/chs/material'
CHARACTER_URL = 'https://api.ambr.top/v2/chs/avatar'
WEAPON_URL = 'https://api.ambr.top/v2/chs/weapon'
DAILY_URL = 'https://api.ambr.top/v2/chs/dailyDungeon'
UPGRADE_URL = 'https://api.ambr.top/v2/static/upgrade'


async def get_daily_material():
    daily_info = {
        '天赋': {},
        '武器': {}
    }
    daily_data = (await aiorequests.get(DAILY_URL)).json()['data']
    material_data = (await aiorequests.get(MATERIAL_URL)).json()['data']
    upgrade_data = (await aiorequests.get(UPGRADE_URL)).json()['data']
    for week in daily_data:
        if week == 'sunday':
            continue
        daily_info['天赋'][week_cn[week]], daily_info['武器'][week_cn[week]] = {}, {}
        domain_data = daily_data[week]
        domain_data_sort = sorted(domain_data, key=lambda x: domain_data[x]['city'])
        for domain_key in domain_data_sort:
            item_type = 'avatar' if domain_data[domain_key]['name'].startswith('精通秘境') else 'weapon'
            material = material_data['items'][str(domain_data[domain_key]['reward'][-1])]
            used = [upgrade_data[item_type][id] for id in upgrade_data[item_type] if
                    str(material['id']) in upgrade_data[item_type][id]['items'] and 'Player' not in
                    upgrade_data[item_type][id]['icon']]
            daily_info['天赋' if item_type == 'avatar' else '武器'][week_cn[week]][
                f'{material["name"]}-{material["icon"]}'] = [f'{u["rank"]}{u["icon"]}' for u in used]
    save_json(daily_info, Path() / 'data' / 'LittlePaimon' / 'daily_material.json')


async def draw_material(week: str = '周一'):
    if not (Path() / 'data' / 'LittlePaimon' / 'daily_material.json').exists():
        await get_daily_material()
    if week in {'周一', '周四'}:
        week_str = '周一/周四'
    elif week in {'周二', '周五'}:
        week_str = '周二/周五'
    else:
        week_str = '周三/周六'
    daily_info = load_json(Path() / 'data' / 'LittlePaimon' / 'daily_material.json')
    avatar = daily_info['天赋'][week]
    weapon = daily_info['武器'][week]
    total_height = max(70 * len(avatar) + sum(math.ceil(len(items) / 5) * 140 for items in avatar.values()),
                       70 * len(weapon) + sum(math.ceil(len(items) / 5) * 140 for items in weapon.values())) + 165
    img = PMImage(RESOURCE_BASE_PATH / 'general' / 'bg.png')
    await img.stretch((50, img.width - 50), 1520, 'width')
    await img.stretch((50, img.height - 50), total_height - 100, 'height')
    frame = await load_image(RESOURCE_BASE_PATH / 'general' / 'frame.png')
    await img.paste(frame, (190, 62))
    await img.paste(frame, (1000, 62))
    await img.text(f'{week_str}角色天赋材料', 223, 69, fm.get('SourceHanSerifCN-Bold.otf', 35), 'black')
    await img.text(f'{week_str}武器突破材料', 1033, 69, fm.get('SourceHanSerifCN-Bold.otf', 35), 'black')
    star_bg = {
        '3': await load_image(RESOURCE_BASE_PATH / 'icon' / 'star3.png', size=(110, 110)),
        '4': await load_image(RESOURCE_BASE_PATH / 'icon' / 'star4.png', size=(110, 110)),
        '5': await load_image(RESOURCE_BASE_PATH / 'icon' / 'star5.png', size=(110, 110))
    }
    now_height = 165
    for name, items in avatar.items():
        name, icon = name.split('-')
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / 'star5.png', size=(60, 60)), (90, now_height))
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'material' / f'{icon}.png', size=(60, 60)),
                        (90, now_height))
        await img.text(name, 165, now_height + 5, fm.get('SourceHanSerifCN-Bold.otf', 30), 'black')
        now_height += 70
        items.sort(key=lambda x: int(x[0]), reverse=True)
        for i in range(len(items)):
            star = items[i][0]
            icon = items[i][1:]
            await img.paste(star_bg[star], (90 + 128 * (i % 5), now_height + 125 * int(i / 5)))
            await img.paste(await load_image(RESOURCE_BASE_PATH / 'avatar' / f'{icon}.png', size=(110, 110)),
                            (90 + 128 * (i % 5), now_height + 125 * int(i / 5)))
        now_height += math.ceil(len(items) / 5) * 125 + 15
    now_height = 165
    for name, items in weapon.items():
        name, icon = name.split('-')
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'icon' / 'star5.png', size=(60, 60)), (908, now_height))
        await img.paste(await load_image(RESOURCE_BASE_PATH / 'material' / f'{icon}.png', size=(60, 60)),
                        (908, now_height))
        await img.text(name, 983, now_height + 5, fm.get('SourceHanSerifCN-Bold.otf', 30), 'black')
        now_height += 70
        items.sort(key=lambda x: int(x[0]), reverse=True)
        for i in range(len(items)):
            star = items[i][0]
            icon = items[i][1:]
            await img.paste(star_bg[star], (908 + 128 * (i % 5), now_height + 125 * int(i / 5)))
            await img.paste(await load_image(RESOURCE_BASE_PATH / 'weapon' / f'{icon}.png', size=(110, 110)),
                            (908 + 128 * (i % 5), now_height + 125 * int(i / 5)))
        now_height += math.ceil(len(items) / 5) * 125 + 15
    await img.text('CREATED BY LITTLEPAIMON', (0, img.width), img.height - 83,
                   fm.get('bahnschrift_bold', 44, 'Bold'), '#3c3c3c', align='center')

    return MessageBuild.Image(img, mode='RGB', quality=80)

@scheduler.scheduled_job('cron', hour=7, misfire_grace_time=10)
async def update_daily_material():
    await get_daily_material()