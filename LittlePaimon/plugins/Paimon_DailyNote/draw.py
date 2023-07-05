import datetime
import random

from LittlePaimon.utils.image import PMImage
from LittlePaimon.utils.image import font_manager as fm
from LittlePaimon.utils.image import load_image
from LittlePaimon.utils.message import MessageBuild
from LittlePaimon.utils.path import RESOURCE_BASE_PATH
from LittlePaimon.utils.requests import aiorequests


async def draw_daily_note_card(data, uid):
    circle_img = await load_image(RESOURCE_BASE_PATH / "daily_note" / "透明圆.png")
    finished_icon = await load_image(RESOURCE_BASE_PATH / "daily_note" / "finished.png")
    bg_img = PMImage(
        image=await load_image(
            RESOURCE_BASE_PATH / "daily_note" / "ssbq.png", mode="RGBA"
        )
    )
    # uid文字
    await bg_img.text(f"uid{uid}", 152, 251, fm.get("number.ttf", 60), "#5680d2")
    # 树脂文字
    await bg_img.text(
        f"{data['current_resin']}/160", 337, 480, fm.get("number.ttf", 48), "white"
    )
    await bg_img.draw_ring(
        (266, 266),
        (98, 369),
        percent=data["current_resin"] / 160,
        width=0.18,
        colors=["#507bd0", "#FFFFFF"],
    )
    if data["current_resin"] == 160:
        await bg_img.text("树脂满了哦~", 892, 480, fm.get("优设标题黑.ttf", 40), "white")
    else:
        recover_time = datetime.datetime.now() + datetime.timedelta(
            seconds=int(data["resin_recovery_time"])
        )
        recover_time_day = (
            "今天" if recover_time.day == datetime.datetime.now().day else "明天"
        )
        recover_time_str = f'将于{recover_time_day}{recover_time.strftime("%H:%M")}回满'
        await bg_img.text(recover_time_str, 780, 480, fm.get("优设标题黑.ttf", 40), "white")
    # 宝钱文字
    await bg_img.text(
        f"{data['current_home_coin']}/{data['max_home_coin']}",
        337,
        701,
        fm.get("number.ttf", 48),
        "white",
    )
    await bg_img.draw_ring(
        (266, 266),
        (98, 593),
        percent=data["current_home_coin"]
        / (data["max_home_coin"] if data["max_home_coin"] != 0 else 1),
        width=0.18,
        colors=["#507bd0", "#FFFFFF"],
    )
    if data["current_home_coin"] == data["max_home_coin"]:
        await bg_img.text("洞天宝钱满了哦~", 820, 701, fm.get("优设标题黑.ttf", 40), "white")
    else:
        recover_time = datetime.datetime.now() + datetime.timedelta(
            seconds=int(data["home_coin_recovery_time"])
        )
        recover_time_day = recover_time.day - datetime.datetime.now().day
        if recover_time_day == 1:
            recover_time_day_str = "明天"
        elif recover_time_day == 0:
            recover_time_day_str = "今天"
        else:
            recover_time_day_str = str(recover_time.day) + "日"
        recover_time_str = f'将于{recover_time_day_str}{recover_time.strftime("%H:%M")}攒满'
        await bg_img.text(recover_time_str, 762, 701, fm.get("优设标题黑.ttf", 40), "white")
    # 委托文字
    await bg_img.text(
        f"{data['finished_task_num']}/4", 337, 924, fm.get("number.ttf", 48), "white"
    )
    await bg_img.draw_ring(
        (266, 266),
        (98, 816),
        percent=data["finished_task_num"] / 4,
        width=0.18,
        colors=["#507bd0", "#FFFFFF"],
    )
    if data["finished_task_num"] == 4:
        await bg_img.text("今日委托已全部完成~", 750, 924, fm.get("优设标题黑.ttf", 40), "white")
    else:
        await bg_img.text("今日委托完成情况", 790, 924, fm.get("优设标题黑.ttf", 40), "white")
    # 质变文字
    if data["transformer"]["obtained"]:
        await bg_img.text(
            f"{7 - data['transformer']['recovery_time']['Day']}/7",
            337,
            1147,
            fm.get("number.ttf", 48),
            "white",
        )
        await bg_img.draw_ring(
            (266, 266),
            (98, 1039),
            percent=(7 - data["transformer"]["recovery_time"]["Day"]) / 7,
            width=0.18,
            colors=["#507bd0", "#FFFFFF"],
        )
        rt = data["transformer"]["recovery_time"]
        if rt["Day"] == 0 and rt["reached"]:
            await bg_img.text("可使用", 465, 1147, fm.get("优设标题黑.ttf", 40), "white")
        elif rt["Day"] == 0 and not rt["reached"]:
            await bg_img.text(
                f"{rt['Hour']}时后", 463, 1127, fm.get("优设标题黑.ttf", 40), "white"
            )
            await bg_img.text("可使用", 465, 1167, fm.get("优设标题黑.ttf", 40), "white")
        else:
            await bg_img.text(
                f"{rt['Day']}天后", 471, 1127, fm.get("优设标题黑.ttf", 40), "white"
            )
            await bg_img.text("可使用", 465, 1167, fm.get("优设标题黑.ttf", 40), "white")
    else:
        await bg_img.text("未获得", 337, 1143, fm.get("优设标题黑.ttf", 48), "white")
    # 周本文字
    await bg_img.text(
        f"{3 - data['remain_resin_discount_num']}/3",
        843,
        1147,
        fm.get("number.ttf", 48),
        "white",
    )
    await bg_img.draw_ring(
        (266, 266),
        (604, 1039),
        percent=(3 - data["remain_resin_discount_num"]) / 3,
        width=0.18,
        colors=["#507bd0", "#FFFFFF"],
    )
    if data["remain_resin_discount_num"] == 0:
        await bg_img.text("已完成", 1005, 1147, fm.get("优设标题黑.ttf", 40), "white")
    else:
        await bg_img.text(
            f"剩余{data['remain_resin_discount_num']}次",
            977,
            1127,
            fm.get("优设标题黑.ttf", 40),
            "white",
        )
        await bg_img.text("周本减半", 965, 1167, fm.get("优设标题黑.ttf", 40), "white")
    # 深渊文字
    now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    abyss_new = (
        now.replace(day=16)
        if now.day < 16
        else now.replace(
            year=now.year + 1 if (next_month := now.month % 12 + 1) == 1 else now.year,
            month=next_month,
            day=1,
        )
    )
    abyss_now = now.replace(day=1) if now.day < 16 else now.replace(day=16)
    left_day = (abyss_new - now).days
    total_day = (abyss_new - abyss_now).days
    await bg_img.text(
        f"{left_day}/{total_day}", 337, 1358, fm.get("number.ttf", 48), "white"
    )
    await bg_img.text(
        f"本期深渊还有{left_day}天结束", 745, 1358, fm.get("优设标题黑.ttf", 40), "white"
    )
    await bg_img.draw_ring(
        percent=left_day / total_day,
        pos=(100, 1249),
        size=(266, 266),
        width=0.18,
        colors=["#507bd0", "#FFFFFF"],
    )

    # 派遣情况
    exp = data["expeditions"]
    if exp:
        i = 0
        # await asyncio.gather(*[draw_exp(bg_img, exp[i], circle_img, finished_icon, i) for i in range(len(exp))])
        for role in exp:
            # role_avatar = await load_image(RESOURCE_BASE_PATH / 'avatar_side' / role['avatar_side_icon'].split('/')[-1],
            #                                size=(135, 135), mode='RGBA')
            role_avatar = await aiorequests.get_img(
                role["avatar_side_icon"],
                save_path=RESOURCE_BASE_PATH
                / "avatar_side"
                / role["avatar_side_icon"].split("/")[-1],
                size=(135, 135),
                mode="RGBA",
            )
            await bg_img.paste(role_avatar, (i * 200 + 168, 1537))
            await bg_img.draw_ring(
                percent=1 - int(role["remained_time"]) / 72000,
                pos=(i * 201 + 101, 1490),
                size=(266, 266),
                width=0.18,
                colors=["#507bd0", "#FFFFFF"],
            )
            if role["status"] == "Ongoing":
                await bg_img.paste(circle_img, (i * 201 + 172, 1559))
                hour = int(role["remained_time"]) // 3600
                await bg_img.text(
                    f"{hour}h", i * 200 + 212, 1580, fm.get("number.ttf", 40), "white"
                )
                minute = int(role["remained_time"]) % 3600 // 60
                await bg_img.text(
                    f"{minute}m", i * 200 + 197, 1620, fm.get("number.ttf", 40), "white"
                )
            else:
                await bg_img.paste(finished_icon, (i * 200 + 191, 1576))
            i += 1

        await bg_img.text("派遣全部", 1220, 1580, fm.get("优设标题黑.ttf", 40), "#5680d2")
        await bg_img.text("完成时间", 1220, 1620, fm.get("优设标题黑.ttf", 40), "#5680d2")
        max_time = int(max([s["remained_time"] for s in exp]))
        if max_time == 0:
            await bg_img.text("已全部完成~", 1410, 1583, fm.get("优设标题黑.ttf", 60), "#5680d2")
        else:
            last_finish_time = datetime.datetime.now() + datetime.timedelta(
                seconds=max_time
            )
            last_finish_day = (
                last_finish_time.day > datetime.datetime.now().day and "明天" or "今天"
            )
            last_finish_str = f'{last_finish_day}{last_finish_time.strftime("%H:%M")}'
            await bg_img.text(
                last_finish_str, 1408, 1588, fm.get("优设标题黑.ttf", 60), "#5680d2"
            )
    else:
        await bg_img.text("未安排派遣", 1408, 1588, fm.get("优设标题黑.ttf", 60), "#5680d2")
    role_img = await load_image(
        random.choice(list((RESOURCE_BASE_PATH / "emoticons").iterdir())),
        size=3.5,
        mode="RGBA",
    )
    await bg_img.paste(role_img, (1220, 200))
    now = datetime.datetime.now().strftime("%m月%d日%H:%M")
    await bg_img.text(
        "Created by LittlePaimon·" + now, 554, 1794, fm.get("优设标题黑.ttf", 40), "#5680d2"
    )
    return MessageBuild.Image(bg_img.image, size=0.35, quality=70, mode="RGB")
