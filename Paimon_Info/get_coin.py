import asyncio
import random
from nonebot import logger

from littlepaimon_utils import aiorequests
from ..utils.auth_util import random_text, random_hex, get_old_version_ds, get_ds

# 米游社的API列表
bbs_Cookieurl = 'https://webapi.account.mihoyo.com/Api/cookie_accountinfo_by_loginticket?login_ticket={}'
bbs_Cookieurl2 = 'https://api-takumi.mihoyo.com/auth/api/getMultiTokenByLoginTicket?login_ticket={}&token_types=3&uid={}'
bbs_Taskslist = 'https://bbs-api.mihoyo.com/apihub/sapi/getUserMissionsState'  # 获取任务列表
bbs_Signurl = 'https://bbs-api.mihoyo.com/apihub/app/api/signIn'  # post
bbs_Listurl = 'https://bbs-api.mihoyo.com/post/api/getForumPostList?forum_id={}&is_good=false&is_hot=false&page_size=20&sort_type=1'
bbs_Detailurl = 'https://bbs-api.mihoyo.com/post/api/getPostFull?post_id={}'
bbs_Shareurl = 'https://bbs-api.mihoyo.com/apihub/api/getShareConf?entity_id={}&entity_type=1'
bbs_Likeurl = 'https://bbs-api.mihoyo.com/apihub/sapi/upvotePost'  # post json

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
]


class MihoyoBBSCoin:
    """
    米游币获取
    """

    def __init__(self, cookies: str, user_id: str, uid: str):
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
        self.received_coins: int = 0  # 这个变量以后可能会用上，先留着了
        self.total_coins: int = 0
        self.state: bool = True
        self.user_id = user_id
        self.uid = uid

    async def run(self):
        """
        执行米游币获取任务
        :return: 获取消息
        """
        logger.info(f'开始执行{self.user_id}的UID{self.uid}的米游币获取任务')
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
            if self.state:
                msg = await task()
                result += msg + '\n'
            else:
                return 'Cookie已失效'
        return result

    async def get_tasks_list(self):
        """
        获取任务列表，用来判断做了哪些任务
        """
        data = await aiorequests.get(url=bbs_Taskslist, headers=self.headers)
        data = data.json()
        if 'err' in data['message'] or data['retcode'] == -100:
            self.state = False
            return
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

    # 进行签到操作
    async def signing(self):
        """
        讨论区签到
        """
        if self.Task_do['bbs_Sign']:
            return '讨论区签到任务已经完成过了~'
        header = self.headers.copy()
        for i in self.mihoyo_bbs_List:
            header['DS'] = get_ds('', {'gids': i['id']}, True)
            req = await aiorequests.post(url=bbs_Signurl, json={'gids': i['id']}, headers=header)
            data = req.json()
            if 'err' in data['message']:
                self.state = False
                return
            await asyncio.sleep(random.randint(3, 6))
        return '讨论区签到：完成！'

    async def read_posts(self):
        """
        浏览帖子
        """
        if self.Task_do['bbs_Read_posts']:
            return '看帖任务已经完成过了~'
        num_ok = 0
        for i in range(self.Task_do['bbs_Read_posts_num']):
            req = await aiorequests.get(url=bbs_Detailurl.format(self.postsList[i][0]), headers=self.headers)
            data = req.json()
            if data['message'] == 'OK':
                num_ok += 1
            await asyncio.sleep(random.randint(2, 5))
        return f'浏览帖子：完成{str(num_ok)}个！'

    async def like_posts(self):
        """
        点赞帖子
        """
        if self.Task_do['bbs_Like_posts']:
            return '点赞任务已经完成过了~'
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
            await asyncio.sleep(random.randint(1, 3))
            req = await aiorequests.post(url=bbs_Likeurl,
                                         headers=self.headers,
                                         json={
                                             'post_id':   self.postsList[i][0],
                                             'is_cancel': True,
                                         })
            data = req.json()
            if data['message'] == 'OK':
                num_cancel += 1
        await asyncio.sleep(random.randint(2, 5))
        return f'点赞帖子：完成{str(num_ok)}个并{str(num_cancel)}个！'

    async def share_post(self):
        """
        分享帖子
        """
        if self.Task_do['bbs_Share']:
            return '分享任务已经完成过了~'
        for _ in range(3):
            req = await aiorequests.get(
                url=bbs_Shareurl.format(self.postsList[0][0]),
                headers=self.headers)
            data = req.json()
            if data['message'] == 'OK':
                return '分享帖子：完成！'
            else:
                await asyncio.sleep(random.randint(3, 6))
        await asyncio.sleep(random.randint(2, 5))
