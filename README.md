<p align="center" >
  <a href="https://github.com/CMHopeSunshine/LittlePaimon/tree/nonebot2"><img src="http://static.cherishmoon.fun/LittlePaimon/readme/logo.png" width="256" height="256" alt="LittlePaimon"></a>
</p>
<h1 align="center">小派蒙|LittlePaimon</h1>
<h4 align="center">✨基于<a href="https://github.com/Ice-Cirno/HoshinoBot" target="_blank">HoshinoBot</a>|<a href="https://github.com/nonebot/nonebot2" target="_blank">NoneBot2</a>和<a href="https://github.com/Mrs4s/go-cqhttp" target="_blank">go-cqhttp</a>的原神Q群机器人✨</h4>

<p align="center">
    <a href="https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LICENSE"><img src="https://img.shields.io/github/license/CMHopeSunshine/LittlePaimon" alt="license"></a>
    <img src="https://img.shields.io/badge/Python-3.8+-yellow" alt="python">
    <a href="https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&inviteCode=MmWrI&from=246610&biz=ka"><img src="https://img.shields.io/badge/QQ频道交流-尘世闲游-green?style=flat-square" alt="QQ guild"></a>
</p>

## 丨简介

原神多功能机器人，通过米游社接口查询uid的游戏信息，并提供WIKI查询和各种各样的好玩的功能。

本README为NoneBot2版的介绍，Hoshino版详见：

+ [Github主页](https://github.com/CMHopeSunshine/LittlePaimon)
+ [README博客](https://blog.cherishmoon.fun/posts/littlepaimon-hoshino.html)

## 丨功能示例

<img src="http://static.cherishmoon.fun/LittlePaimon/readme/ys.jpg" alt="ys">

<details>
<summary>角色背包</summary>
<img src="http://static.cherishmoon.fun/LittlePaimon/readme/ysa.jpg" alt="ysa">
</details>

<details>
<summary>角色详情</summary>
<img src="http://static.cherishmoon.fun/LittlePaimon/readme/ysc.jpg" alt="ysc">
</details>

<details>
<summary>深渊信息</summary>
<img src="http://static.cherishmoon.fun/LittlePaimon/readme/sy12.jpg" alt="sy">
</details>

<details>
<summary>模拟抽卡</summary>
<img src="http://static.cherishmoon.fun/LittlePaimon/readme/十连.jpg" alt="十连">
</details>

<details>
<summary>实时便签</summary>
<img src="http://static.cherishmoon.fun/LittlePaimon/readme/ssbq.jpg" alt="ssbq">
</details>

<details>
<summary>每月札记</summary>
<img src="http://static.cherishmoon.fun/LittlePaimon/readme/myzj.jpg" alt="myzj">
</details>

<details>
<summary>角色材料</summary>
<img src="http://static.cherishmoon.fun/LittlePaimon/readme/material.png" alt="material">
</details>

<details>
<summary>抽卡记录</summary>
<img src="http://static.cherishmoon.fun/LittlePaimon/readme/gachalog.jpg" alt="gachalog">
</details>

## 丨更新日志
+ 5.19
  - 米游社签到新增`全部重签`，仅限超级管理员使用，需@机器人
  - `原神猜语音`不再需要`我猜`，直接回答角色别名即可参与猜猜看
  - 异步请求库从`aiohttp`改用`httpx`，需安装依赖库`pip install httpx`
  - 修复`60秒读世界`在频道无法关闭推送的BUG
+ 5.20
  - 修复`ysc`缺少资源问题
  - 封装部分常用方法，优化导包
  - `Paimon_Chat`新增`更新派蒙语音`，实时更新语音
+ 5.21
  - 修复可能因ssl证书导致的静态资源下载问题
+ 5.23
  - 新增`xx原魔图鉴`
+ 5.25
  - `ys、ysc、ysa、sy`等和`wiki`模块指令可以对话式查询
+ 5.27
  - 新增`原神日历`[@nicklly](https://github.com/nicklly)
+ 5.28
  - `Paimon_Chat`聊天新增`学习群友发言`（魔改自[Pallas-Bot](https://github.com/InvoluteHell/Pallas-Bot/tree/master/src/plugins/repeater)），需安装`jieba_fast、pymongo、pypinyin依赖库`、`mongodb数据库`且在`.env.*`配置文件中添加mongodb连接参数`paimon_mongodb_url`，例如`paimon_mongodb_url=mongodb://localhost:27017/
+ 6.3
  - 新增游戏内展柜角色面板卡片，使用`更新角色面板`来获取角色，`ysd角色名`来查看角色卡片
  - 修复部分不记录上次查询的uid的bug
  - 大幅缩短深渊指令`sy`的缓存时间
+ 6.6
  - 修复`模拟抽卡定轨`和`抽卡记录导出`bug
+ 6.7
  - 修复`原神猜语音`和`模拟抽卡`因`nonebot2.0.0b3`版本Union校验产生的bug，但`原神猜语音`将暂时无法私聊使用
+ 6.9
  - 新增`帮助菜单`指令~~(不太好看，继续美化)~~

## 丨功能列表

详见[功能列表](https://blog.cherishmoon.fun/posts/nonebot2funclist.html)

## 丨部署方法
### 我很熟悉NoneBot2

 + 部署NoneBot2和go-cqhttp

 + 在NoneBot2根目录，克隆本项目
   `git clone -b nonebot2 https://github.com/CMHopeSunshine/LittlePaimon `
   
 + 安装依赖
   ```shell
   # 定时任务插件
   nb plugin install nonebot-plugin-apscheduler
   # 需要的依赖库
   pip install aiohttp xlsxwriter sqlitedict matplotlib aiofiles
   ```
 + 启用插件
   ```python
   # 编辑bot.py，添加：
   nonebot.load_plugins("LittlePaimon")
   ```
   
### 我不熟悉NoneBot2
**详细部署教程：**

- [Linux](https://blog.cherishmoon.fun/posts/nonebot2deploy.html#linux)
- [安卓系统](https://blog.cherishmoon.fun/posts/nonebot2deploy.html#%E5%9C%A8%E5%AE%89%E5%8D%93%E6%89%8B%E6%9C%BA%E4%B8%8A%E9%83%A8%E7%BD%B2)
- [Windows](https://blog.cherishmoon.fun/posts/nonebot2deploy.html#windows)

### 添加公共cookie

部署完成后，你还需要至少添加一条**公共cookie**，小派蒙才能使用查询功能。

登录米游社网页版，在地址栏粘贴：

```
javascript:(function(){prompt(document.domain,document.cookie)})();
```

复制得到的cookie，向小派蒙发送**`添加公共ck`**和粘贴的内容，即可开始使用

## 丨感谢

代码水平很烂，站在巨人的肩膀上努力学习ing......

- [NoneBot2](https://github.com/nonebot/nonebot2) - 跨平台异步机器人框架
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) - Onebot标准的框架实现
- [西北一枝花](https://github.com/Nwflower) - 美工大大和武器攻略图提供
- [egenshin](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin) - 抽卡和猜语音代码、资源参考
- [bluemushoom](https://bbs.nga.cn/nuke.php?func=ucp&uid=62861898) - 全角色收益曲线和参考面板攻略图来源
- [genshin-gacha-export](https://github.com/sunfkny/genshin-gacha-export) - 抽卡记录导出代码参考
- [Pallas-Bot](https://github.com/InvoluteHell/Pallas-Bot/tree/master/src/plugins/repeater) - 群聊记录发言学习代码参考
- [西风驿站](https://bbs.mihoyo.com/ys/collection/307224) - 角色攻略一图流来源
- [游创工坊](https://space.bilibili.com/176858937) - 深渊排行榜数据来源

## 丨赞助
- 如果本项目对你有帮助，给个star~~求求啦
- 部分资源使用了云存储，如果想赞助流量费用，欢迎来[爱发电](https://afdian.net/@cherishmoon)，十分感谢！

| 赞助者          | 金额 |
| --------------- | ---- |
| 深海            | 10   |
| 夜空koi         | 30   |
| 情话            | 20   |
| 爱发电用户_Mfms | 15   |
| 米特建木        | 10   |
| 永远的皇珈骑士  | 30   |
| 小兔和鹿        | 30   |

## 丨其他

- 本项目仅供学习使用，禁止用于商业用途

- 如果您使用修改了本项目源码，请遵循[GPL-3.0](https://github.com/CMHopeSunshine/LittlePaimon/blob/master/LICENSE)开源
