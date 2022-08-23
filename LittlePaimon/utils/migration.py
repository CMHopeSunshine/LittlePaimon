import sqlite3
from pathlib import Path
import datetime
from LittlePaimon.utils import logger
from LittlePaimon.database.models import PublicCookie, PrivateCookie, LastQuery, DailyNoteSub, MihoyoBBSSub


async def migrate_database():
    old_db_path = Path() / 'data' / 'LittlePaimon' / 'user_data' / 'user_data.db'
    if not old_db_path.exists():
        return
    logger.info('派蒙数据库迁移', '开始迁移数据库')
    conn = sqlite3.connect(old_db_path)
    cursor = conn.cursor()
    # 迁移公共cookie
    try:
        cursor.execute('SELECT cookie FROM public_cookies;')
        cookie = cursor.fetchall()
        for c in cookie:
            await PublicCookie.create(cookie=c[0])
            logger.info('派蒙数据库迁移', f'成功迁移公共cookie<m>{c[0][:20]}...</m>')
    except Exception:
        logger.info('派蒙数据库迁移', '公共cookie没有可迁移的数据')
    # 迁移私人cookie
    try:
        cursor.execute('SELECT user_id, uid, mys_id, cookie, stoken FROM private_cookies;')
        cookie = cursor.fetchall()
        for c in cookie:
            await PrivateCookie.update_or_create(user_id=c[0], uid=c[1], mys_id=c[2], cookie=c[3], stoken=c[4])
            logger.info('派蒙数据库迁移', f'成功迁移用户<m>{c[0]}</m>的UID<m>{c[1]}</m>的<m>私人cookie</m>')
    except Exception:
        logger.info('派蒙数据库迁移', '私人cookie没有可迁移的数据')
    # 最后查询记录迁移
    try:
        cursor.execute('SELECT user_id, uid FROM last_query;')
        query = cursor.fetchall()
        for q in query:
            await LastQuery.update_or_create(user_id=q[0], uid=q[1], last_time=datetime.datetime.now())
        logger.info('派蒙数据库迁移', f'成功迁移UID查询记录<m>{len(query)}</m>条')
    except Exception:
        logger.info('派蒙数据库迁移', 'UID查询记录没有可迁移的数据')
    # 实时便签提醒迁移
    try:
        cursor.execute('SELECT user_id, uid, count, remind_group FROM note_remind;')
        note = cursor.fetchall()
        for n in note:
            await DailyNoteSub.update_or_create(user_id=n[0], uid=n[1], remind_type='private' if n[3] == n[1] else 'group', group_id=n[3], resin_num=n[2])
            logger.info('派蒙数据库迁移', f'成功迁移用户<m>{n[0]}</m>的UID<m>{n[1]}</m>的米游社自动签到')
    except Exception:
        logger.info('派蒙数据库迁移', '米游社自动签到没有可迁移的数据')
    # 米游社签到迁移
    try:
        cursor.execute('SELECT user_id, uid, group_id FROM bbs_sign;')
        sign = cursor.fetchall()
        for s in sign:
            await MihoyoBBSSub.update_or_create(user_id=s[0], uid=s[1], group_id=s[2], sub_event='米游社原神签到')
            logger.info('派蒙数据库迁移', f'成功迁移用户<m>{s[0]}</m>的UID<m>{s[1]}</m>的米游社原神签到')
    except Exception:
        logger.info('派蒙数据库迁移', '米游社原神签到没有可迁移的数据')
    # 米游币获取迁移
    try:
        cursor.execute('SELECT user_id, uid, group_id FROM coin_bbs_sign;')
        sign = cursor.fetchall()
        for s in sign:
            await MihoyoBBSSub.update_or_create(user_id=s[0], uid=s[1], group_id=s[2], sub_event='米游币自动获取')
            logger.info('派蒙数据库迁移', f'成功迁移用户<m>{s[0]}</m>的UID<m>{s[1]}</m>的米游币自动获取')
    except Exception:
        logger.info('派蒙数据库迁移', '米游币自动获取没有可迁移的数据')

    conn.close()

    # 将old_db_path文件改名为old_db_path.bak
    old_db_path.rename(old_db_path.parent / f'{old_db_path.name}.bak')
