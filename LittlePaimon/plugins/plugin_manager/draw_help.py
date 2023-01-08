import math
from typing import List

from LittlePaimon import __version__
from LittlePaimon.config import PluginInfo
from LittlePaimon.utils.image import PMImage, font_manager as fm, load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH


async def draw_plugin_card(plugin: PluginInfo):
    matchers = plugin.matchers
    matcher_groups = [matchers[i:i + 3] for i in range(0, len(matchers), 3)]
    # 确定长度
    total_height = 66
    for matcher_group in matcher_groups:
        max_length = max(len(matcher.pm_description) for matcher in matcher_group)
        max_height = max_length // 13 * 22 + 59 + 15
        total_height += max_height + 6
    total_height -= 6
    img = PMImage(size=(1080, total_height), color=(255, 255, 255, 0), mode='RGBA')
    await img.paste


async def draw_help(plugin_list: List[PluginInfo]):
    bg = PMImage(await load_image(RESOURCE_BASE_PATH / 'general' / 'bg.png'))
    img = PMImage(size=(1080, 1000 + 600 * len(plugin_list)), color=(255, 255, 255, 0), mode='RGBA')
    orange_line = await load_image(RESOURCE_BASE_PATH / 'general' / 'orange.png')
    orange_name_bg = await load_image(RESOURCE_BASE_PATH / 'general' / 'orange_card.png')
    black_line = await load_image(RESOURCE_BASE_PATH / 'general' / 'black2.png')
    black_name_bg = await load_image(RESOURCE_BASE_PATH / 'general' / 'black_card2.png')
    orange_bord = await load_image(RESOURCE_BASE_PATH / 'general' / 'orange_bord.png')
    black_bord = await load_image(RESOURCE_BASE_PATH / 'general' / 'black_bord.png')
    await img.text('小派蒙帮助', 38, 40, fm.get('SourceHanSerifCN-Bold.otf', 72), 'black')
    await img.text(f'V{__version__}', 1040, 75, fm.get('bahnschrift_regular', 36), 'black', 'right')
    await img.text('<>内为必须，[]内为可选', 1040, 105, fm.get('SourceHanSerifCN-Bold.otf', 22), 'black', 'right')
    await img.text('描述前带*号的需要绑定私人cookie', 1040, 130, fm.get('SourceHanSerifCN-Bold.otf', 22), 'black', 'right')

    height_now = 172
    for plugin in plugin_list:
        if not plugin.status:
            plugin_line = PMImage(black_line)
            plugin_name_bg = PMImage(black_name_bg)
            matcher_card = PMImage(black_bord)
        else:
            plugin_line = PMImage(orange_line)
            plugin_name_bg = PMImage(orange_name_bg)
            matcher_card = PMImage(orange_bord)
        plugin_name = plugin.name.replace('\n', '')
        name_length = img.text_length(plugin_name, fm.get('SourceHanSerifCN-Bold.otf', 30))
        await img.paste(plugin_line, (40, height_now))
        await plugin_name_bg.stretch((23, plugin_name_bg.width - 36), int(name_length), 'width')
        await img.paste(plugin_name_bg, (40, height_now))
        await img.text(plugin_name, 63, height_now + 5, fm.get('SourceHanSerifCN-Bold.otf', 30), 'white')
        height_now += plugin_line.height + 11
        if plugin.matchers and (matchers := [matcher for matcher in plugin.matchers if matcher.pm_show and (matcher.pm_usage or matcher.pm_name)]):
            matcher_groups = [matchers[i:i + 3] for i in range(0, len(matchers), 3)]
            for matcher_group in matcher_groups:
                max_length = max(len(matcher.pm_description.replace('\n', '')) if matcher.pm_description else 0 for matcher in matcher_group)
                max_height = math.ceil(max_length / 16) * 22 + 40
                await matcher_card.stretch((5, matcher_card.height - 5), max_height, 'height')
                for matcher in matcher_group:
                    await img.paste(matcher_card, (40 + 336 * matcher_group.index(matcher), height_now))
                    await img.text(matcher.pm_usage or matcher.pm_name, 40 + 336 * matcher_group.index(matcher) + 15, height_now + 10, fm.get('SourceHanSansCN-Bold.otf', 24), 'black')
                    if matcher.pm_description:
                        await img.text_box(matcher.pm_description.replace('\n', '^'), (40 + 336 * matcher_group.index(matcher) + 10, 40 + 336 * matcher_group.index(matcher) + matcher_card.width - 22),
                                           (height_now + 44, height_now + max_height - 10), fm.get('SourceHanSansCN-Bold.otf', 18), '#40342d')
                height_now += max_height + 10 + 6
        elif plugin.usage:
            text_height = len(plugin.usage) // 43 * 22 + 45
            await matcher_card.stretch((5, matcher_card.width - 5), 990, 'width')
            await matcher_card.stretch((5, matcher_card.height - 5), text_height, 'height')
            await img.paste(matcher_card, (40, height_now))
            await img.text_box(plugin.usage.replace('\n', '^'), (50, 1030), (height_now + 10, height_now + text_height - 10), fm.get('SourceHanSansCN-Bold.otf', 18), '#40342d')
            height_now += matcher_card.height + 6
        height_now += 19
    await img.text('CREATED BY LITTLEPAIMON', (0, 1080), height_now + 8, fm.get('SourceHanSerifCN-Bold.otf', 24), 'black', 'center')
    height_now += 70
    await bg.stretch((50, bg.height - 50), height_now - 100, 'height')
    await bg.paste(img, (0, 0))

    return MessageBuild.Image(bg, quality=80, mode='RGB')
