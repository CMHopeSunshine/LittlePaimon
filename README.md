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
> README只展示最近3条更新，全部更新日志详见[这里](https://github.com/CMHopeSunshine/LittlePaimon/blob/nonebot2/UPDATE_LOG.md)
+ 6.21
  - 适配`nonebot2 beta4`插件元数据，**请更新nb版本`pip install nonebot2 --upgrade`**
  - `Paimon_Chat`现在可以发图片、视频等，可自行添加
  - 修复`Paimon_Wiki`搜索对象名结果只有一个时仍需要选择的bug
  - 对对联功能api更换
  - 增加部分注释文档
  - 更换原神日历样式[@nicklly](https://github.com/nicklly) ，需用到htmlrender插件`pip install nonebot-plugin-htmlrender`
  - 添加`pyproject.toml`和`poetry.lock`
+ 6.22
  - 增加文本敏感词过滤
  - fix `原神日历`和发送图片bug
+ 6.23
  - 新增查看所有已获取面板信息的角色的列表`ysda`
  - 暂时取消凌晨3点的自动更新角色面板操作
  
## 丨功能列表

详见我的博客[功能列表](https://blog.cherishmoon.fun/posts/nonebot2funclist.html) <br>
博客内容可能滞后于实际版本 ~~太懒了~~

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

复制得到的cookie，向小派蒙发送`添加公共ck`和粘贴的内容，即可开始使用

## 丨感谢

代码水平很烂，站在巨人的肩膀上努力学习ing......

- [NoneBot2](https://github.com/nonebot/nonebot2) - 跨平台异步机器人框架
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) - Onebot标准的框架实现
- [西北一枝花](https://github.com/Nwflower) - 美工大大和武器攻略图提供
- [nicklly](https://github.com/nicklly) 、[SCU_OP](https://github.com/SCUOP) - PR贡献者们
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
| 夜空koi          | 30  |
| 情话             | 20  |
| 爱发电用户_Mfms     | 15  |
| 米特建木           | 10  |
| 永远的皇珈骑士        | 30  |
| 小兔和鹿           | 30  |
| el psy congroo | 20  |
| SCU_OP         | 30  |
| 南絮ヽ            | 20  |
| 夜空koi我老婆       | 30  |
## 丨其他

- 本项目仅供学习使用，禁止用于商业用途

- 如果您使用修改了本项目源码，请遵循[GPL-3.0](https://github.com/CMHopeSunshine/LittlePaimon/blob/master/LICENSE)开源
