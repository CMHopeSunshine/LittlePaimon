import asyncio
from LittlePaimon.utils.image import PMImage, load_image
from LittlePaimon.utils.image import font_manager as fm
from LittlePaimon.utils.path import RESOURCE_BASE_PATH
from .models import Character, Relic, Element

PATH = RESOURCE_BASE_PATH / "star_rail"

LEVEL_COLOR = ["#404040", "#519d57", "#2f8dac", "#d16fe9", "#f5ad1e"]
ELEMENT_COLOR = {
    "雷": "#d16fe9",
    "冰": "#2f9de0",
    "风": "#42c28c",
    "火": "#e93d44",
    "物理": "#8c8b8f",
    "量子": "#723de8",
    "虚数": "#ebca47",
}


async def draw_relic(relic: Relic, element: Element) -> PMImage:
    # 背景
    bg = PMImage(await load_image(PATH / f"遗器-{element.name}.png"))
    # 名称
    await bg.text(relic.name, 19, 12, fm.get("汉仪雅酷黑", 30), "white")
    # 图标
    await bg.paste(
        await load_image(PATH / "relic" / relic.icon.split("/")[-1], size=(106, 106)),
        (4, 63),
    )
    # 稀有度
    await bg.draw_rectangle((6, 138, 47, 160), LEVEL_COLOR[relic.rarity - 1])
    # 等级
    await bg.text(
        f"+{relic.level}",
        (6, 47),
        (138, 160),
        fm.get("bahnschrift_regular", 24),
        "white",
        "center",
    )
    # 主属性名
    await bg.text(
        relic.main_affix.name.rstrip("提高"),
        328,
        67,
        fm.get("汉仪润圆", 36),
        "#333333",
        "right",
    )
    # 主属性值
    await bg.text(
        "+" + relic.main_affix.display,
        328,
        123,
        fm.get("汉仪润圆", 36),
        "#333333",
        "right",
    )
    # 副属性
    for i, affix in enumerate(relic.sub_affix):
        # 副属性名
        await bg.text(affix.name, 6, 178 + i * 56, fm.get("汉仪润圆", 36), "#333333")
        # 副属性值
        await bg.text(
            "+"
            + (affix.display if affix.name != "速度" else str(round(affix.value, 1))),
            328,
            178 + i * 56,
            fm.get("汉仪润圆", 36),
            "#333333",
            "right",
        )
    return bg


async def draw_character(chara: Character, uid: str):
    # 背景
    bg = PMImage(await load_image(PATH / f"背景-{chara.element.name}.png"))

    # 等级
    await bg.text(
        f"UID{uid} - Lv.{chara.level}",
        36,
        20,
        fm.get("bahnschrift_regular", 36),
        ELEMENT_COLOR[chara.element.name],
    )

    # 角色立绘
    pic = await load_image(
        PATH / "character_portrait" / chara.portrait.split("/")[-1],
        size=(1300, 1300),
        crop=(338, 146, 886, 1176),
    )
    await bg.paste(pic, (510, 28))
    await bg.paste(
        await load_image(PATH / f"立绘边框-{chara.element.name}.png"), (500, 13)
    )

    # 星魂图标
    circle = await load_image(PATH / "星魂圆.png")
    circle_lock = await load_image(PATH / "星魂圆暗.png")
    for i in range(6):
        await bg.paste(circle, (524, 443 + i * 104))
        icon = PMImage(
            await load_image(
                PATH / "skill" / chara.rank_icons[i].split("/")[-1], size=(76, 76)
            )
        )
        await bg.paste(icon, (536, 453 + i * 104))
        if i >= chara.rank:
            await bg.paste(circle_lock, (524, 443 + i * 104))

    # 星魂文字
    await bg.text(
        f"星魂{chara.rank}", (388, 488), 17, fm.get("汉仪雅酷黑", 30), "white", "center"
    )

    # 角色名称
    await bg.text(
        chara.name, 480, (59, 154), fm.get("汉仪雅酷黑", 72), "white", "right"
    )

    # 属性
    for i, attr in enumerate(
        ("生命值", "攻击力", "防御力", "速度", "暴击率", "暴击伤害")
    ):
        base = next((a for a in chara.attributes if a.name == attr), None)
        extra = next((a for a in chara.additions if a.name == attr), None)
        if attr in ("暴击率", "暴击伤害"):
            n = "0%"
            total = (
                str(
                    round(
                        ((base.value if base else 0) + (extra.value if extra else 0))
                        * 100,
                        1,
                    )
                )
                + "%"
            )
        else:
            n = "0"
            total = (
                str(int((base.value if base else 0) + (extra.value if extra else 0)))
                if attr != "速度"
                else str(
                    round(
                        (base.value if base else 0) + (extra.value if extra else 0), 1
                    )
                )
            )

        await bg.text(
            total,
            400,
            180 + i * 56,
            fm.get("bahnschrift_regular", 36),
            "#333333",
            "right",
        )
        await bg.text(
            base.display if base else n,
            483,
            175 + i * 56,
            fm.get("bahnschrift_regular", 24),
            "#333333",
            "right",
        )
        await bg.text(
            ("+" + (extra.display if extra else n))
            if attr != "速度"
            else ("+" + str(round(extra.value if extra else 0, 1))),
            483,
            196 + i * 56,
            fm.get("bahnschrift_regular", 24),
            "#5a9922",
            "right",
        )

    for i, attr in enumerate(
        (
            "效果抵抗",
            "效果命中",
            "击破特攻",
            "能量恢复效率",
            f"{chara.element.name}属性伤害提高",
        )
    ):
        affix = next((a for a in chara.properties if a.name == attr), None)

        if affix is None:
            value = "0%" if attr != "能量恢复效率" else "100%"
        else:
            value = (
                affix.display
                if attr != "能量恢复效率"
                else (str(round((1 + affix.value) * 100, 1)) + "%")
            )
        await bg.text(
            value,
            483,
            516 + i * 56,
            fm.get("bahnschrift_regular", 36),
            "#333333",
            "right",
        )

    # 光锥图标
    await bg.paste(
        await load_image(
            PATH / "light_cone" / chara.light_cone.icon.split("/")[-1], size=(96, 96)
        ),
        (24, 802),
    )

    # 光锥稀有度
    await bg.paste(
        await load_image(PATH / f"光锥{chara.light_cone.rarity}星.png"), (123, 813)
    )

    # 光锥名称
    await bg.text(chara.light_cone.name, 138, 847, fm.get("汉仪雅酷黑", 30), "#333333")

    # 光锥等级
    await bg.draw_rectangle((279, 813, 346, 841), ELEMENT_COLOR[chara.element.name])
    await bg.text(
        f"lv.{chara.light_cone.level}",
        (279, 346),
        (813, 841),
        fm.get("bahnschrift_regular", 30),
        "white",
        "center",
    )

    # 光锥叠影
    await bg.draw_rectangle(
        (353, 813, 427, 841), LEVEL_COLOR[chara.light_cone.rank - 1]
    )
    await bg.text(
        f"叠影{chara.light_cone.rank}",
        (353, 427),
        (813, 841),
        fm.get("汉仪雅酷黑", 24),
        "white",
        "center",
    )

    # 行迹
    for i, skill in enumerate(chara.skills[:4]):
        # 图标
        await bg.paste(
            await load_image(PATH / "skill" / skill.icon.split("/")[-1], size=(70, 70)),
            (50 + 113 * i, 962),
        )
        # 等级
        await bg.draw_rectangle(
            (65 + 113 * i, 1024, 104 + 113 * i, 1056),
            LEVEL_COLOR[(skill.level // 2 - 1) if skill.level < 10 else 4],
        )
        await bg.text(
            str(skill.level),
            (65 + 113 * i, 104 + 113 * i),
            1021,
            fm.get("汉仪雅酷黑", 30),
            "white",
            "center",
        )

    # 遗器
    await asyncio.gather(
        *[
            bg.paste(
                await draw_relic(relic, chara.element),
                ((19 + (i % 3) * 353, (1131 if i < 3 else 1537))),
            )
            for i, relic in enumerate(chara.relics)
        ]
    )

    # 其他文字
    await bg.text(
        "CREATED BY LITTLEPAIMON", 20, 1078, fm.get("汉仪雅酷黑", 30), "#252525"
    )
    await bg.text(
        "数据源 MiHoMo", 1060, 1078, fm.get("汉仪雅酷黑", 30), "#252525", "right"
    )

    return bg
