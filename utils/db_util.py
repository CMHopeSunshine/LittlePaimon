import sqlite3
import os
from datetime import datetime

db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'user_data', 'user_data.db')


# 初始化数据库，将原json数据导入数据库
def init_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute('SELECT NAME FROM sqlite_master WHERE TYPE="table" and NAME="private_cookies"')
    if not cursor.fetchone():
        cursor.execute('''CREATE TABLE private_cookies
            (
                user_id TEXT NOT NULL,
                uid TEXT NOT NULL,
                mys_id TEXT,
                cookie TEXT,
                stoken TEXT,
                PRIMARY KEY (user_id, uid)
            );''')
        cursor.execute('DROP TABLE IF EXISTS last_query;')
        cursor.execute('''CREATE TABLE last_query
        (
            user_id TEXT PRIMARY KEY NOT NULL,
            uid TEXT,
            mys_id TEXT,
            last_time datetime
        );''')
        # try:
        #     with open(os.path.join(os.path.dirname(__file__), 'user_data', 'user_cookies.json'), 'r',
        #               encoding='utf-8') as f:
        #         data = json.load(f)
        #     for d in data['私人'].items():
        #         for c in d[1]['cookies']:
        #             match = re.search(r'account_id=(\d{6,12})', c['cookie'])
        #             mys_id = match.group(1) if match else ''
        #             cursor.execute('INSERT INTO private_cookies (user_id, uid, mys_id, cookie) VALUES (?, ?, ?, ?);',
        #                            (d[0], c['uid'], mys_id, c['cookie']))
        #         cursor.execute('INSERT INTO last_query (user_id, uid, last_time) VALUES (?, ?, ?);',
        #                        (d[0], d[1]['last_query'], datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        #     cursor.execute('''CREATE TABLE IF NOT EXISTS public_cookies (
        #         no int IDENTITY(1,1) PRIMARY KEY,
        #         cookie TEXT,
        #         status TEXT);''')
        #     for d in data['通用']:
        #         if d['cookie']:
        #             try:
        #                 cursor.execute('INSERT INTO public_cookies VALUES (?, ?, "OK");', (d['no'], d['cookie']))
        #             except:
        #                 pass
        #     logger.info('---派蒙初始化数据库成功，已导入原json数据---')
        # except:
        #     logger.error('---派蒙初始化数据库失败，请检查user_cookies.json文件是否存在---')
    conn.commit()
    conn.close()


# 获取公共cookie
async def get_public_cookie():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS public_cookies(
        no int IDENTITY(1,1) PRIMARY KEY,
        cookie TEXT,
        status TEXT);''')
    cursor.execute('SELECT no, cookie FROM public_cookies WHERE status="OK";')
    cookie = cursor.fetchone()
    conn.commit()
    conn.close()
    return cookie


# 插入公共cookie
async def insert_public_cookie(cookie):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS public_cookies 
    (
        no int IDENTITY(1,1) PRIMARY KEY,
        cookie TEXT,
        status TEXT
    );''')
    cursor.execute('INSERT OR IGNORE INTO public_cookies (cookie, status) VALUES (?,"OK");', (cookie,))
    conn.commit()
    conn.close()


# 设置公共cookie到上限
async def limit_public_cookie(cookie):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS public_cookies(
        no int IDENTITY(1,1) PRIMARY KEY,
        cookie TEXT,
        status TEXT);''')
    cursor.execute('UPDATE public_cookies SET status="limited30" WHERE cookie=?;', (cookie,))
    conn.commit()
    conn.close()


# 清除公共cookie上限
async def reset_public_cookie():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS public_cookies(
        no int IDENTITY(1,1) PRIMARY KEY,
        cookie TEXT,
        status TEXT);''')
    cursor.execute('UPDATE public_cookies SET status="OK" WHERE status="limited30";')
    conn.commit()
    conn.close()


# 通过key(如user_id, uid)获取私人cookie
async def get_private_cookie(value, key='user_id'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f'SELECT user_id, cookie, uid, mys_id FROM private_cookies WHERE {key}="{value}";')
    cookie = cursor.fetchall()
    conn.close()
    return cookie


# 更新cookie
async def update_private_cookie(user_id, uid='', mys_id='', cookie='', stoken=''):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO private_cookies VALUES (?, ?, ?, ?, ?);', (user_id, uid, mys_id, cookie, stoken))
    conn.commit()
    conn.close()


# 删除私人cookie
async def delete_private_cookie(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM private_cookies WHERE user_id=?', (user_id,))
    conn.commit()
    conn.close()


# 删除cookie
async def delete_cookie(cookie, type='public'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM cookie_cache WHERE cookie=?;', (cookie,))
    cursor.execute(f'DELETE FROM {type}_cookies WHERE cookie="{cookie}";')
    conn.commit()
    conn.close()


# 获取cookie缓存
async def get_cookie_cache(value, key='uid'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cookie_cache(
        uid TEXT PRIMARY KEY NOT NULL,
        mys_id TEXT,
        cookie TEXT);''')
    cursor.execute(f'SELECT cookie FROM cookie_cache WHERE {key}="{value}"')
    res = cursor.fetchone()
    if res:
        try:
            cursor.execute('SELECT user_id, uid, mys_id FROM private_cookies WHERE cookie=?;', (res[0],))
            is_in_private = cursor.fetchone()
            if is_in_private:
                return {'type': 'private', 'user_id': is_in_private[0], 'cookie': res[0], 'uid': is_in_private[1],
                        'mys_id': is_in_private[2]}
        except:
            pass
        try:
            cursor.execute('SELECT no FROM public_cookies WHERE cookie=?;', (res[0],))
            is_in_public = cursor.fetchone()
            if is_in_public:
                return {'type': 'public', 'cookie': res[0], 'no': is_in_public[0]}
        except:
            pass
    conn.close()
    return None


# 更新cookie缓存
async def update_cookie_cache(cookie, value, key='uid'):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS cookie_cache(
        uid TEXT PRIMARY KEY NOT NULL,
        mys_id TEXT,
        cookie TEXT);''')
    cursor.execute(f'REPLACE INTO cookie_cache ({key}, cookie) VALUES ("{value}", "{cookie}");')
    conn.commit()
    conn.close()


# 删除cookie缓存
async def delete_cookie_cache(value='', key='cookie', all=False):
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        if all:
            cursor.execute('DROP TABLE cookie_cache;')
        else:
            cursor.execute(f'DELETE FROM cookie_cache WHERE {key}="{value}";')
        conn.commit()
        conn.close()
    except:
        pass


# 获取user_id最后查询的uid
async def get_last_query(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS last_query(
        user_id TEXT PRIMARY KEY NOT NULL,
        uid TEXT,
        last_time datetime);''')
    cursor.execute('SELECT uid FROM last_query WHERE user_id=?;', (user_id,))
    uid = cursor.fetchone()
    conn.close()
    return uid[0] if uid else None


# 更新user_id最后查询的uid
async def update_last_query(user_id, value, key='uid'):
    t = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS last_query(
        user_id TEXT PRIMARY KEY NOT NULL,
        uid TEXT,
        mys_id TEXT,
        last_time datetime);''')
    cursor.execute(f'REPLACE INTO last_query (user_id, {key}, last_time) VALUES ("{user_id}", "{value}", "{t}");')
    conn.commit()
    conn.close()


async def get_all_query():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS last_query(
            user_id TEXT PRIMARY KEY NOT NULL,
            uid TEXT,
            mys_id TEXT,
            last_time datetime);''')
    cursor.execute('SELECT uid, last_time FROM last_query')
    uid_list = cursor.fetchall()
    uids = []
    for uid, last_time in uid_list:
        if (datetime.now() - datetime.strptime(last_time, '%Y-%m-%d %H:%M:%S')).days <= 3:
            uids.append(uid)
    conn.close()
    return uids


# 获取树脂提醒信息
async def get_note_remind():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS note_remind
    (
        user_id TEXT NOT NULL,
        uid TEXT NOT NULL,
        count INTEGER,
        remind_group TEXT,
        enable boolean,
        last_remind_time datetime,
        today_remind_count INTEGER,
        PRIMARY KEY (user_id, uid)
    );''')
    cursor.execute('SELECT * FROM note_remind;')
    res = cursor.fetchall()
    conn.close()
    return res


# 更新树脂提醒信息
async def update_note_remind(user_id, uid, count, remind_group, enable, last_remind_time, today_remind_count):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS note_remind
    (
        user_id TEXT NOT NULL,
        uid TEXT NOT NULL,
        count INTEGER,
        remind_group TEXT,
        enable boolean,
        last_remind_time datetime,
        today_remind_count INTEGER,
        PRIMARY KEY (user_id, uid)
    );''')
    cursor.execute('REPLACE INTO note_remind VALUES (?, ?, ?, ?, ?, ?, ?);',
                   (user_id, uid, count, remind_group, enable, last_remind_time, today_remind_count))
    conn.commit()
    conn.close()


async def update_note_remind2(user_id, uid, remind_group, enable=True, count=''):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS note_remind
    (
        user_id TEXT NOT NULL,
        uid TEXT NOT NULL,
        count INTEGER,
        remind_group TEXT,
        enable boolean,
        last_remind_time datetime,
        today_remind_count INTEGER,
        PRIMARY KEY (user_id, uid)
    );''')
    if count:
        cursor.execute(
            f'REPLACE INTO note_remind (user_id, uid, remind_group, count, enable) VALUES ("{user_id}", "{uid}", "{remind_group}", {count}, {enable});')
    else:
        cursor.execute(
            f'UPDATE note_remind SET enable={enable}, remind_group={remind_group} WHERE user_id="{user_id}" AND uid="{uid}"')
    conn.commit()
    conn.close()


async def update_day_remind_count():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS note_remind
    (
        user_id TEXT NOT NULL,
        uid TEXT NOT NULL,
        count INTEGER,
        remind_group TEXT,
        enable boolean,
        last_remind_time datetime,
        today_remind_count INTEGER,
        PRIMARY KEY (user_id, uid)
    );''')
    cursor.execute('UPDATE note_remind SET today_remind_count=0 WHERE today_remind_count!=0')
    conn.commit()
    conn.close()


# 删除树脂提醒信息
async def delete_note_remind(user_id, uid):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS note_remind
    (
        user_id TEXT NOT NULL,
        uid TEXT NOT NULL,
        count INTEGER,
        remind_group TEXT,
        enable boolean,
        last_remind_time datetime,
        today_remind_count INTEGER,
        PRIMARY KEY (user_id, uid)
    );''')
    cursor.execute('DELETE FROM note_remind WHERE user_id=? AND uid=?;', (user_id, uid))
    conn.commit()
    conn.close()


async def get_auto_sign():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS bbs_sign
    (
        user_id TEXT NOT NULL,
        uid TEXT NOT NULL,
        group_id TEXT,
        PRIMARY KEY (user_id, uid)
    );''')
    cursor.execute('SELECT * FROM bbs_sign;')
    res = cursor.fetchall()
    conn.close()
    return res


async def add_auto_sign(user_id, uid, group_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS bbs_sign
    (
        user_id TEXT NOT NULL,
        uid TEXT NOT NULL,
        group_id TEXT,
        PRIMARY KEY (user_id, uid)
    );''')
    cursor.execute('REPLACE INTO bbs_sign VALUES (?, ?, ?);', (user_id, uid, group_id))
    conn.commit()
    conn.close()


async def delete_auto_sign(user_id, uid):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS bbs_sign
    (
        user_id TEXT NOT NULL,
        uid TEXT NOT NULL,
        group_id TEXT,
        PRIMARY KEY (user_id, uid)
    );''')
    cursor.execute('DELETE FROM bbs_sign WHERE user_id=? AND uid=?;', (user_id, uid))
    conn.commit()
    conn.close()


async def get_all_myb_exchange():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS myb_exchange
    (
        user_id TEXT NOT NULL PRIMARY KEY,
        uid TEXT,
        cookie TEXT,
        address_id INTEGER,
        goods_id TEXT,
        exchange_time datetime
    );''')
    cursor.execute('SELECT * FROM myb_exchange;')
    res = cursor.fetchall()
    conn.close()
    return res


async def get_myb_exchange(user_id, key):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS myb_exchange
    (
        user_id TEXT NOT NULL PRIMARY KEY,
        uid TEXT,
        cookie TEXT,
        address_id INTEGER,
        goods_id TEXT,
        exchange_time datetime
    );''')
    cursor.execute(f'SELECT {key} FROM myb_exchange WHERE user_id = "{user_id}";')
    res = cursor.fetchone()
    conn.close()
    return res[0] or None


async def add_myb_exchange(user_id, value, key):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS myb_exchange
    (
        user_id TEXT NOT NULL PRIMARY KEY,
        uid TEXT,
        cookie TEXT,
        address_id INTEGER,
        goods_id TEXT,
        exchange_time datetime
    );''')
    cursor.execute('SELECT * FROM myb_exchange WHERE user_id=?;', (user_id,))
    res = cursor.fetchone()
    if res:
        cursor.execute(f'UPDATE myb_exchange SET {key}="{value}" WHERE user_id="{user_id}";')
    else:
        cursor.execute(f'INSERT INTO myb_exchange (user_id, {key}) VALUES ("{user_id}", "{value}");')
    conn.commit()
    conn.close()


async def delete_myb_exchange(user_id):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS myb_exchange
    (
        user_id TEXT NOT NULL PRIMARY KEY,
        uid TEXT,
        cookie TEXT,
        address_id INTEGER,
        goods_id TEXT,
        exchange_time datetime
    );''')
    cursor.execute('DELETE FROM myb_exchange WHERE user_id=?;', (user_id,))
    conn.commit()
    conn.close()


init_db()
