<p align="center" >
  <a href="https://github.com/CMHopeSunshine/LittlePaimon/tree/nonebot2"><img src="http://static.cherishmoon.fun/LittlePaimon/readme/logo.png" width="256" height="256" alt="LittlePaimon"></a>
</p>
<h1 align="center">小派蒙|LittlePaimon</h1>
<h4 align="center">✨基于<a href="https://github.com/nonebot/nonebot2" target="_blank">NoneBot2</a>和<a href="https://github.com/Mrs4s/go-cqhttp" target="_blank">go-cqhttp</a>的原神Q群机器人✨</h4>

<p align="center">
    <a href="https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LICENSE"><img src="https://img.shields.io/github/license/CMHopeSunshine/LittlePaimon" alt="license"></a>
    <img src="https://img.shields.io/badge/Python-3.8+-yellow" alt="python">
    <img src="https://img.shields.io/badge/Nonebot-2.0.0b4-green" alt="python">
    <a href="https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&inviteCode=MmWrI&from=246610&biz=ka"><img src="https://img.shields.io/badge/QQ频道交流-尘世闲游-blue?style=flat-square" alt="QQ guild"></a>
</p>


## 丨简介

原神多功能机器人，通过米游社接口查询uid的游戏信息，并提供WIKI查询和各种各样的好玩的功能。

## 丨功能示例

<img src="https://static.cherishmoon.fun/LittlePaimon/readme/ys.jpg" alt="ys">
<details>
<summary>角色面板</summary>
<img src="https://static.cherishmoon.fun/LittlePaimon/readme/ysd.jpg" alt="ysd">
</details>

<details>
<summary>角色背包</summary>
<img src="https://static.cherishmoon.fun/LittlePaimon/readme/ysa.jpg" alt="ysa">
</details>

<details>
<summary>深渊信息</summary>
<img src="https://static.cherishmoon.fun/LittlePaimon/readme/sy12.jpg" alt="sy">
</details>

<details>
<summary>模拟抽卡</summary>
<img src="https://static.cherishmoon.fun/LittlePaimon/readme/十连.jpg" alt="十连">
</details>

<details>
<summary>实时便签</summary>
<img src="https://static.cherishmoon.fun/LittlePaimon/readme/ssbq.jpg" alt="ssbq">
</details>

<details>
<summary>每月札记</summary>
<img src="https://static.cherishmoon.fun/LittlePaimon/readme/myzj.jpg" alt="myzj">
</details>

<details>
<summary>角色材料</summary>
<img src="https://static.cherishmoon.fun/LittlePaimon/readme/material.png" alt="material">
</details>

## 丨更新日志
> README只展示最近更新，全部更新日志详见[这里](https://github.com/CMHopeSunshine/LittlePaimon/blob/nonebot2/UPDATE_LOG.md)
 
### 近期进行全新版本重构，具体详见`Bot`分支，本分支暂缓更新，预计一到两周内重构完成。

+ 7.14
  - ysd支持`鹿野院平藏`，增加`枫原万叶、鹿野院平藏`伤害计算
+ 7.15
  - 增加新武器的攻略，修复`ysd`命座天赋加成以及岩元素护盾数值
+ 7.17
  - `ysd`新增`班尼特、莫娜、七七、琴、温迪`伤害计算
  - `mys自动签到`支持私聊
  - `sy`修正深渊信息时间介绍
  - `sy`没有绑定cookie时将不再错误的展示空阵容信息
  - `ssbq`修复没有派遣时会报错的bug
+ 7.19
  - 新增`米游币自动获取`#124，不确保一定可用，如产生其他bug请反馈
+ 7.23
  - 深渊登场率数据改为2.8

## 丨功能列表

详见我的博客[功能列表](https://blog.cherishmoon.fun/posts/nonebot2funclist.html) <br>
博客内容可能滞后于实际版本 ~~太懒了~~

## 丨重要提示
如果你是**7月3日**之前克隆的用户，且之后没有更新过，请按照下面的方法迁移数据：
- 1、将派蒙的`res`文件夹改名`LittlePaimon`，移到nonebot根目录的`resources`中（没有`resources`就新建一个）
- 2、将派蒙的`user_data`文件夹移到nonebot根目录的`data/LittlePaimon`目录中（同理，没有就新建）

## 丨部署方法
### 我很熟悉NoneBot2

 + 部署NoneBot2和go-cqhttp

 + 安装和启用派蒙
   
   - git clone方式
   ```bash
   # 在nonebot根目录运行:
   # 1、克隆派蒙源码
   git clone https://github.com/CMHopeSunshine/LittlePaimon
   
   
   # 2、编辑bot.py，在load_from_toml下方添加一句
   nonebot.load_plugins("LittlePaimon")
   
   # 3、进入LittlePaimon目录，安装依赖
   cd LittlePaimon
   pip install -r requirements.txt
   ```
### 我不熟悉NoneBot2

- [详细部署教程](https://blog.cherishmoon.fun/posts/nonebot2deploy.html)

### 添加公共cookie

部署完成后，你还需要至少添加一条**公共cookie**，小派蒙才能使用查询功能。

登录米游社网页版，在地址栏粘贴：

```
javascript:(function(){prompt(document.domain,document.cookie)})();
```

复制得到的cookie，向小派蒙发送`添加公共ck`和粘贴的内容，即可开始使用<br>
获取之后不能退出账号登录状态！推荐在无痕模式下取

## 丨相关配置项

> 以下配置为派蒙的默认配置，你可以在`.env.prod`文件中，添加以下配置来进行修改
>
> 例如你想将对联冷却改为2秒，就在`.env.prod`中加一句paimon_couplets_cd=2

```python
# 群组模拟抽卡冷却（秒）
paimon_gacha_cd_group = 30
# 个人模拟抽卡冷却（秒）
paimon_gacha_cd_user = 60
# 树脂提醒停止检查时间（小时）
paimon_remind_start = 0
paimon_remind_end = 8
# 树脂提醒检查间隔（分钟）
paimon_check_interval = 16
# 树脂提醒每日提醒次数上限
paimon_remind_limit = 3
# 自动签到开始时间（小时）
paimon_sign_hour = 0
# 自动签到开始时间（分钟）
paimon_sign_minute = 0
# 自动米游币获取开始时间（小时）
paimon_coin_hour = 0
# 自动米游币获取开始时间（分钟）
paimon_coin_minute = 5
    
# 对联冷却（秒）
paimon_couplets_cd = 6
# 猫图冷却（秒）
paimon_cat_cd = 12
# 二次元图冷却（秒）
paimon_ecy_cd = 6
# 原神壁纸图冷却（秒）
paimon_ysp_cd = 10
# 派蒙猜语音持续时间
paimon_guess_voice = 30

# 派蒙收到好友申请或群邀请时是否向超级管理员发通知
paimon_request_remind = true
# 是否自动通过好友请求
paimon_add_friend = false
# 是否自动通过群组请求
paimon_add_group = false
# 禁用群新成员欢迎语和龙王提醒的群号列表
paimon_greet_ban = []

# 以下为机器学习聊天模块配置
# mongodb数据库连接url
paimon_mongodb_url = None
# 派蒙聊天&机器学习开启群组
paimon_chat_group = []
# 派蒙机器学习屏蔽用户
paimon_chat_ban = []
# 派蒙聊天学习阈值，越小学习越快
paimon_answer_threshold = 3
# 派蒙聊天上限阈值
paimon_answer_limit_threshold = 25
# N个群有相同的回复，就跨群作为全局回复
paimon_cross_group_threshold = 2
# 复读的阈值
paimon_repeat_threshold = 3
# 主动发言阈值，越小话越多
paimon_speak_threshold = 3
# 喝醉的概率
paimon_drunk_probability = 0.07
# 用文字转语音来回复的概率
paimon_voice_probability = 0.03
# 连续主动说话的概率
paimon_speak_continuously_probability = 0.5
# 主动说话加上随机戳一戳群友的概率
paimon_speak_poke_probability = 0.5
# 连续主动说话最多几句话
paimon_speak_continuously_max_len = 3
```

## 丨感谢

代码水平很烂，站在巨人的肩膀上努力学习ing......

- [NoneBot2](https://github.com/nonebot/nonebot2) - 跨平台异步机器人框架
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) - Onebot标准的框架实现
- [西北一枝花](https://github.com/Nwflower) - 美工大大和武器攻略图提供
- [nicklly](https://github.com/nicklly) 、[SCU_OP](https://github.com/SCUOP) 、[meatjam](https://github.com/meatjam) - PR贡献者们
- [egenshin](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin) - 抽卡和猜语音代码、资源参考
- [bluemushoom](https://bbs.nga.cn/nuke.php?func=ucp&uid=62861898) - 全角色收益曲线和参考面板攻略图来源
- [genshin-gacha-export](https://github.com/sunfkny/genshin-gacha-export) - 抽卡记录导出代码参考
- [GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID) - 部分map资源来源
- [Pallas-Bot](https://github.com/InvoluteHell/Pallas-Bot/tree/master/src/plugins/repeater) - 群聊记录发言学习代码参考
- [西风驿站](https://bbs.mihoyo.com/ys/collection/307224) - 角色攻略一图流来源
- [游创工坊](https://space.bilibili.com/176858937) - 深渊排行榜数据来源
- [Enka Network](https://enka.shinshin.moe/) - 角色面板查询数据来源

## 丨赞助
- 如果本项目对你有帮助，给个star~~求求啦
- 部分资源使用了云存储，如果想赞助流量费用，欢迎来[爱发电](https://afdian.net/@cherishmoon)，十分感谢！

| 赞助者(排名不分先后)    | 金额  |
|----------------|-----|
| 深海             | 10  |
| 夜空koi          | 60  |
| 情话             | 20  |
| 爱发电用户_Mfms     | 15  |
| 米特建木           | 10  |
| 永远的皇珈骑士        | 30  |
| 小兔和鹿           | 50  |
| el psy congroo | 20  |
| SCU_OP         | 30  |
| 南絮ヽ            | 30  |
| 夜空koi我老婆       | 30  |
| 昔。             | 5   |
| dix            | 20  |
| 凤御白            | 30  |
| RivenNero      | 5   |

## 丨其他

- 本项目仅供学习使用，禁止用于商业用途

- 如果您使用修改了本项目源码，请遵循[GPL-3.0](https://github.com/CMHopeSunshine/LittlePaimon/blob/master/LICENSE)开源
