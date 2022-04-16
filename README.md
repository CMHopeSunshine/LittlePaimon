<p align="center">
  <a href="https://github.com/CMHopeSunshine/LittlePaimon"><img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/logo.png" width="256" height="256" alt="LittlePaimon"></a>
</p>
<h1 align="center">小派蒙|LittlePaimon</h1>
<h4 align="center">✨基于<a href="https://github.com/Ice-Cirno/HoshinoBot" target="_blank">HoshinoBot</a>和<a href="https://github.com/Mrs4s/go-cqhttp" target="_blank">go-cqhttp</a>的原神Q群机器人✨</h4>

<p align="center">
    <img src="https://img.shields.io/badge/version-v1.0.4-red" alt="version">
    <a href="https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LICENSE"><img src="https://img.shields.io/github/license/CMHopeSunshine/LittlePaimon" alt="license"></a>
    <img src="https://img.shields.io/badge/Python-3.8+-yellow" alt="python">
    <a href="https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&inviteCode=MmWrI&from=246610&biz=ka"><img src="https://img.shields.io/badge/QQ频道交流-尘世闲游-green?style=flat-square" alt="QQ guild"></a>
</p>




## 简介✨

原神多功能机器人，通过米游社接口查询uid的游戏信息，并提供WIKI查询和各种各样的好玩的功能。

## 功能示例💖

<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/ys.jpg" alt="ys">

<details>
<summary>角色背包</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/ysa.jpg" alt="ysa">
</details>

<details>
<summary>角色详情</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/ysc.jpg" alt="ysc">
</details>

<details>
<summary>深渊信息</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/sy12.jpg" alt="sy">
</details>

<details>
<summary>模拟抽卡</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/%E5%8D%81%E8%BF%9E.jpg" alt="十连">
</details>

<details>
<summary>实时便签</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/ssbq.jpg" alt="ssbq">
</details>

<details>
<summary>每月札记</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/myzj.jpg" alt="myzj">
</details>

<details>
<summary>角色材料</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/material.png" alt="material">
</details>

<details>
<summary>抽卡记录</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/gachalog.jpg" alt="gachalog">
</details>

## 功能列表🌅

详见[功能列表](https://github.com/CMHopeSunshine/LittlePaimon/wiki/%E5%8A%9F%E8%83%BD%E5%88%97%E8%A1%A8)，向派蒙发送`#帮助派蒙`可以查看指令列表。

## 部署方法🖥️

> 本项目基于HoshinoBot，可以使用HoshinoBot同样的部署方法。

### 手动部署

- [Linux](https://github.com/CMHopeSunshine/LittlePaimon/wiki/%E9%83%A8%E7%BD%B2%E6%96%B9%E6%B3%95#linux)
- [安卓系统](https://github.com/CMHopeSunshine/LittlePaimon/wiki/%E9%83%A8%E7%BD%B2%E6%96%B9%E6%B3%95#%E5%9C%A8%E5%AE%89%E5%8D%93%E6%89%8B%E6%9C%BA%E4%B8%8A%E9%83%A8%E7%BD%B2)
- [Windows](https://github.com/CMHopeSunshine/LittlePaimon/wiki/%E9%83%A8%E7%BD%B2%E6%96%B9%E6%B3%95#windows)

### Windows一键安装脚本

⚠️一键脚本会因计算机环境不同而可能产生各种各样的问题，出现问题请尝试手动部署

在你想安装的位置打开`powershell`，输入执行：

```powershell
iwr "https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LittlePaimon-install.ps1" -O .\pm.ps1 ; ./pm.ps1 ; Set-Location .. ; rm pm.ps1
```

安装成功后，用`powershell`运行文件夹内的`启动.ps1`来启动机器人  

### 添加公共cookie

需要至少添加一条公共cookie，小派蒙才能使用查询功能。

登录米游社网页版，在地址栏粘贴：

```
javascript:(function(){prompt(document.domain,document.cookie)})();
```

复制得到的cookie，向小派蒙发送`添加公共ck`和粘贴的内容即可开始使用


## 重要通知⚠️

4.11对代码进行了一次较大幅度的重构，cookie数据存储方式改用了`sqlite`数据库，原`json`数据会在首次启动时自动导入数据库；如果您对本项目代码有修改，请确保`git pull`时前解决冲突，目前测试未有BUG，如有请发起issue，且注意备份用户数据!

## 新功能更新😙

> 更新涉及的功能指令前往[功能列表](https://github.com/CMHopeSunshine/LittlePaimon/wiki/%E5%8A%9F%E8%83%BD%E5%88%97%E8%A1%A8)查看哦

- 3.20 新增Windows一键部署脚本
- 3.22 新增蓝佬授权提供的收益曲线和参考面板攻略图
- 3.24 新增抽卡记录导出和分析功能，原模拟抽卡的指令更改
- 3.30 个人信息卡片新增层岩巨渊和神里绫人信息
- 3.31 实时便签加入参量质变仪信息
- 4.11 改用数据库进行数据存储，优化代码
- 4.14 新增每日天赋突破材料表查询
- 4.15 新增实时便签树脂提醒功能
- 4.16 新增米游社原神自动签到功能

## ToDo🕛

- [x] 实时便签树脂提醒
- [x] 抽卡记录导出和分析
- [ ] ocr圣遗物评分和角色面板记录
- [ ] 角色、武器和圣遗物wiki
- [ ] 派蒙AI闲聊
- [x] 米游社自动签到
- [x] 今日可刷材料
- [ ] 角色练度统计
- [ ] 派蒙戳一戳集卡

持续画大饼ing......

## 额外说明🗝️

本项目也可作为HoshinoBot的插件来使用，移植`hoshino\modules`内模块即可，另外还需在`hoshino\util\__init__.py`中添加`PriFreqLimiter`方法用于模拟抽卡和派蒙聊天的冷却限制。

## 感谢❤️

代码水平很烂，站在巨人的肩膀上努力学习ing......

- [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) - 基于nonebot的QQ-bot框架
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) - Onebot标准的框架实现
- [egenshin](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin) - 参考了它的抽卡代码和资源
- [西风驿站](https://bbs.mihoyo.com/ys/collection/307224) - 角色攻略一图流来源
- [hoshino-installer](https://github.com/pcrbot/hoshino-installer) - 一键安装脚本参考
- [bluemushoom](https://bbs.nga.cn/nuke.php?func=ucp&uid=62861898) - 全角色收益曲线和参考面板攻略图来源
- [genshin-gacha-export](https://github.com/sunfkny/genshin-gacha-export) - 抽卡记录导出参考
- [Adachi-BOT](https://github.com/SilveryStar/Adachi-BOT) - 部分资源来源
