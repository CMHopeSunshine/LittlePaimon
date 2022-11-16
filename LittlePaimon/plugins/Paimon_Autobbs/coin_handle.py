import asyncio
import datetime
import random
import time
from collections import defaultdict
from typing import Tuple

from nonebot import get_bot

from LittlePaimon.config import config
from LittlePaimon.database import PrivateCookie, MihoyoBBSSub, LastQuery
from LittlePaimon.utils import logger, scheduler
from LittlePaimon.utils.requests import aiorequests
from LittlePaimon.utils.api import random_text, random_hex, get_old_version_ds, get_ds

# 米游社的API列表
bbs_Cookieurl = 'https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}'
bbs_Cookieurl2 = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}'
bbs_Taskslist = 'https://bbs-api.mihoyo.com/apihub/sapi/getUserMissionsState'
bbs_Signurl = 'https://bbs-api.mihoyo.com/apihub/app/api/signIn'
bbs_Listurl = 'https://bbs-api.mihoyo.com/post/api/getForumPostList?forum_id={}&is_good=false&is_hot=false&page_size=20&sort_type=1'
bbs_Detailurl = 'https://bbs-api.mihoyo.com/post/api/getPostFull?post_id={}'
bbs_Shareurl = 'https://bbs-api.mihoyo.com/apihub/api/getShareConf?entity_id={}&entity_type=1'
bbs_Likeurl = 'https://bbs-api.mihoyo.com/apihub/sapi/upvotePost'

mihoyo_bbs_List = [
    {
        'id':      '1',
        'forumId': '1',
        'name':    '崩坏3',
        'url':     'https://bbs.mihoyo.com/bh3/',
    },
    {
        'id':      '2',
        'forumId': '26',
        'name':    '原神',
        'url':     'https://bbs.mihoyo.com/ys/',
    },
    {
        'id':      '3',
        'forumId': '30',
        'name':    '崩坏2',
        'url':     'https://bbs.mihoyo.com/bh2/',
    },
    {
        'id':      '4',
        'forumId': '37',
        'name':    '未定事件簿',
        'url':     'https://bbs.mihoyo.com/wd/',
    },
    {
        'id':      '5',
        'forumId': '34',
        'name':    '大别野',
        'url':     'https://bbs.mihoyo.com/dby/',
    },
    {
        'id':      '6',
        'forumId': '52',
        'name':    '崩坏：星穹铁道',
        'url':     'https://bbs.mihoyo.com/sr/',
    },
    {
        'id': '8',
        'forumId': '57',
        'name': '绝区零',
        'url': 'https://bbs.mihoyo.com/zzz/'
    }
]


class MihoyoBBSCoin:
    """
    米游币获取
    """

    def __init__(self, cookies):
        self.headers: dict = {
            'DS':                 get_old_version_ds(),
            'cookie':             cookies,
            'x-rpc-client_type':  '2',
            'x-rpc-app_version':  '2.34.1',
            'x-rpc-sys_version':  '6.0.1',
            'x-rpc-channel':      'miyousheluodi',
            'x-rpc-device_id':    random_hex(32),
            'x-rpc-device_name':  random_text(random.randint(1, 10)),
            'x-rpc-device_model': 'Mi 10',
            'Referer':            'https://app.mihoyo.com',
            'Host':               'bbs-api.mihoyo.com',
            'User-Agent':         'okhttp/4.8.0'
        }
        self.postsList: list = []
        self.Task_do: dict = {
            'bbs_Sign':           False,
            'bbs_Read_posts':     False,
            'bbs_Read_posts_num': 3,
            'bbs_Like_posts':     False,
            'bbs_Like_posts_num': 5,
            'bbs_Share':          False
        }
        self.mihoyo_bbs_List: list = mihoyo_bbs_List
        self.available_coins: int = 0
        self.received_coins: int = 0
        self.total_coins: int = 0
        self.is_valid: bool = True
        self.state: str = ''

    async def run(self) -> Tuple[bool, str]:
        """
        执行米游币获取任务
        :return: 获取消息
        """
        await self.get_tasks_list()
        await self.get_list()
        tasks_list = [
            self.signing,
            self.read_posts,
            self.like_posts,
            self.share_post
        ]
        result = '米游币获取结果：\n'
        for task in tasks_list:
            if not self.is_valid:
                return False, self.state
            msg = await task()
            result += msg + '\n'
        return True, result

    async def get_tasks_list(self):
        """
        获取任务列表，用来判断做了哪些任务
        """
        data = await aiorequests.get(url=bbs_Taskslist, headers=self.headers)
        data = data.json()
        if data['retcode'] != 0:
            self.is_valid = False
            self.state = 'Cookie已失效' if data['retcode'] in [-100, 10001] else f"出错了:{data['message']} {data['message']}"
            logger.info('米游币自动获取', f'➤➤<r>{self.state}</r>')
            return self.state
        self.available_coins = data['data']['can_get_points']
        self.received_coins = data['data']['already_received_points']
        self.total_coins = data['data']['total_points']
        # 如果当日可获取米游币数量为0直接判断全部任务都完成了
        if self.available_coins == 0:
            self.Task_do['bbs_Sign'] = True
            self.Task_do['bbs_Read_posts'] = True
            self.Task_do['bbs_Like_posts'] = True
            self.Task_do['bbs_Share'] = True
        else:
            # 如果第0个大于或等于62则直接判定任务没做
            if data['data']['states'][0]['mission_id'] < 62:
                for i in data['data']['states']:
                    # 58是讨论区签到
                    if i['mission_id'] == 58:
                        if i['is_get_award']:
                            self.Task_do['bbs_Sign'] = True
                    # 59是看帖子
                    elif i['mission_id'] == 59:
                        if i['is_get_award']:
                            self.Task_do['bbs_Read_posts'] = True
                        else:
                            self.Task_do['bbs_Read_posts_num'] -= i[
                                'happened_times'
                            ]
                    # 60是给帖子点赞
                    elif i['mission_id'] == 60:
                        if i['is_get_award']:
                            self.Task_do['bbs_Like_posts'] = True
                        else:
                            self.Task_do['bbs_Like_posts_num'] -= i[
                                'happened_times'
                            ]
                    # 61是分享帖子
                    elif i['mission_id'] == 61:
                        if i['is_get_award']:
                            self.Task_do['bbs_Share'] = True
                            # 分享帖子，是最后一个任务，到这里了下面都是一次性任务，直接跳出循环
                            break
            logger.info('米游币自动获取', f'➤➤该用户今天还可获取<m>{self.available_coins}</m>个米游币')

    async def get_list(self):
        """
        获取进行操作的帖子列表
        :return: 帖子id列表
        """
        req = await aiorequests.get(
            url=bbs_Listurl.format(random.choice([bbs['forumId'] for bbs in self.mihoyo_bbs_List])),
            headers=self.headers)
        data = req.json()
        self.postsList = [[d['post']['post_id'], d['post']['subject']] for d in data['data']['list'][:5]]
        logger.info('米游币自动获取', '➤➤获取帖子列表成功')

    # 进行签到操作
    async def signing(self):
        """
        讨论区签到
        """
        if self.Task_do['bbs_Sign']:
            return '讨论区签到：已经完成过了~'
        header = self.headers.copy()
        for i in self.mihoyo_bbs_List:
            header['DS'] = get_ds('', {'gids': i['id']}, True)
            req = await aiorequests.post(url=bbs_Signurl, json={'gids': i['id']}, headers=header)
            data = req.json()
            if data['retcode'] != 0:
                if data['retcode'] != 1034:
                    self.is_valid = False
                self.state = 'Cookie已失效' if data['retcode'] in [-100,
                                                                10001] else f"出错了:{data['retcode']} {data['message']}" if data['retcode'] != 1034 else '遇验证码阻拦'
                logger.info('米游币自动获取', f'➤➤<r>{self.state}</r>')
                return f'讨论区签到：{self.state}'
            await asyncio.sleep(random.randint(15, 30))
        logger.info('米游币自动获取', '➤➤讨论区签到<g>完成</g>')
        return '讨论区签到：完成！'

    async def read_posts(self):
        """
        浏览帖子
        """
        if self.Task_do['bbs_Read_posts']:
            return '浏览帖子：已经完成过了~'
        num_ok = 0
        for i in range(self.Task_do['bbs_Read_posts_num']):
            req = await aiorequests.get(url=bbs_Detailurl.format(self.postsList[i][0]), headers=self.headers)
            data = req.json()
            if data['message'] == 'OK':
                num_ok += 1
            await asyncio.sleep(random.randint(5, 10))
        logger.info('米游币自动获取', '➤➤看帖任务<g>完成</g>')
        return f'浏览帖子：完成{str(num_ok)}个！'

    async def like_posts(self):
        """
        点赞帖子
        """
        if self.Task_do['bbs_Like_posts']:
            return '点赞帖子：已经完成过了~'
        num_ok = 0
        num_cancel = 0
        for i in range(self.Task_do['bbs_Like_posts_num']):
            req = await aiorequests.post(url=bbs_Likeurl,
                                         headers=self.headers,
                                         json={
                                             'post_id':   self.postsList[i][0],
                                             'is_cancel': False,
                                         })
            data = req.json()
            if data['message'] == 'OK':
                num_ok += 1
            # 取消点赞
            await asyncio.sleep(random.randint(3, 6))
            req = await aiorequests.post(url=bbs_Likeurl,
                                         headers=self.headers,
                                         json={
                                             'post_id':   self.postsList[i][0],
                                             'is_cancel': True,
                                         })
            data = req.json()
            if data['message'] == 'OK':
                num_cancel += 1
        logger.info('米游币自动获取', '➤➤点赞任务<g>完成</g>')
        await asyncio.sleep(random.randint(5, 10))
        return f'点赞帖子：完成{str(num_ok)}个{"，遇验证码" if num_ok == 0 else ""}！'

    async def share_post(self):
        """
        分享帖子
        """
        if self.Task_do['bbs_Share']:
            return '分享帖子：已经完成过了~'
        for _ in range(3):
            req = await aiorequests.get(
                url=bbs_Shareurl.format(self.postsList[0][0]),
                headers=self.headers)
            data = req.json()
            if data['message'] == 'OK':
                return '分享帖子：完成！'
            else:
                await asyncio.sleep(random.randint(5, 10))
        logger.info('米游币自动获取', '➤➤分享任务<g>完成</g>')
        await asyncio.sleep(random.randint(5, 10))
        return '分享帖子：完成！'


async def mhy_bbs_coin(user_id: str, uid: str) -> str:
    """
    执行米游币获取任务
    :param user_id: 用户id
    :param uid: 原神uid
    :return: 结果
    """
    cookie = await PrivateCookie.get_or_none(user_id=user_id, uid=uid)
    if not cookie:
        return '你尚未绑定Cookie和Stoken，请先用ysb指令绑定！'
    elif cookie.stoken is None:
        return '你绑定Cookie中没有login_ticket，请重新用ysb指令绑定！'
    await LastQuery.update_or_create(user_id=user_id,
                                     defaults={'uid': uid, 'last_time': datetime.datetime.now()})
    logger.info('米游币自动获取', '➤执行', {'用户': user_id, 'UID': uid, '的米游币获取': '......'})
    get_coin_task = MihoyoBBSCoin(cookie.stoken)
    result, msg = await get_coin_task.run()
    return msg if result else f'UID{uid}{msg}'


@scheduler.scheduled_job('cron', hour=config.auto_myb_hour, minute=config.auto_myb_minute, misfire_grace_time=10)
async def _():
    await bbs_auto_coin()


async def bbs_auto_coin():
    """
    指定时间，执行所有米游币获取订阅任务， 并将结果分群绘图发送
    """
    if not config.auto_myb_enable:
        return
    t = time.time()
    subs = await MihoyoBBSSub.filter(sub_event='米游币自动获取').all()
    if not subs:
        return
    logger.info('米游币自动获取', f'开始执行米游币自动获取，共<m>{len(subs)}</m>个任务，预计花费<m>{round(100 * len(subs) / 60, 2)}</m>分钟')
    coin_result_group = defaultdict(list)
    coin_result_private = defaultdict(list)
    for sub in subs:
        result = await mhy_bbs_coin(str(sub.user_id), sub.uid)
        if sub.user_id != sub.group_id:
            coin_result_group[sub.group_id].append({
                'user_id': sub.user_id,
                'uid': sub.uid,
                'result': '出错' not in result and 'Cookie' not in result
            })
        else:
            coin_result_private[sub.user_id].append({
                'uid': sub.uid,
                'result': '出错' not in result and 'Cookie' not in result,
                'msg': result
            })
        await asyncio.sleep(random.randint(15, 25))

    for group_id, result_list in coin_result_group.items():
        result_num = len(result_list)
        if result_fail := len([result for result in result_list if not result['result']]):
            fails = '\n'.join(result['uid'] for result in result_list if not result['result'])
            msg = f'本群米游币自动获取共{result_num}个任务，其中成功{result_num - result_fail}个，失败{result_fail}个，失败的UID列表：\n{fails}'
        else:
            msg = f'本群米游币自动获取共{result_num}个任务，已全部完成'
        try:
            await get_bot().send_group_msg(group_id=int(group_id), message=msg)
        except Exception as e:
            logger.info('米游币自动获取', '➤➤', {'群': group_id}, f'发送米游币自动结果失败: {e}', False)
        await asyncio.sleep(random.randint(3, 6))

    for user_id, result_list in coin_result_private.items():
        for result in result_list:
            try:
                await get_bot().send_private_msg(user_id=int(user_id), message=result['msg'])
            except Exception as e:
                logger.info('米游币自动获取', '➤➤', {'用户': user_id}, f'发送米游币自动结果失败: {e}', False)
            await asyncio.sleep(random.randint(3, 6))

    logger.info('米游币自动获取', f'获取完成，共花费<m>{round((time.time() - t) / 60, 2)}</m>分钟')
