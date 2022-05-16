<div style="text-align: center" >
  <a href="https://github.com/CMHopeSunshine/LittlePaimon"><img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/logo.png" width="256" height="256" alt="LittlePaimon"></a>
</div>
<br>
<br>
<div style="font-size: 32px; text-align:center"><b>小派蒙|LittlePaimon</b></div>
<br>

<div style="font-size: 16px; text-align: center">✨基于<a href="https://github.com/Ice-Cirno/HoshinoBot" target="_blank">HoshinoBot</a>|<a href="https://github.com/nonebot/nonebot2" target="_blank">NoneBot2</a>和<a href="https://github.com/Mrs4s/go-cqhttp" target="_blank">go-cqhttp</a>的原神Q群机器人✨</div>
<br>
<div style="text-align: center" >
    <a href="https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LICENSE"><img src="https://img.shields.io/github/license/CMHopeSunshine/LittlePaimon" alt="license"></a>
    <img src="https://img.shields.io/badge/Python-3.8+-yellow" alt="python">
    <a href="https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&inviteCode=MmWrI&from=246610&biz=ka"><img src="https://img.shields.io/badge/QQ频道交流-尘世闲游-green?style=flat-square" alt="QQ guild"></a>
</div>


## 简介

原神多功能机器人，通过米游社接口查询uid的游戏信息，并提供WIKI查询和各种各样的好玩的功能。

本README为Hoshino版的介绍，NoneBot2版详见：

+ [Github主页](https://github.com/CMHopeSunshine/LittlePaimon/tree/nonebot2)
+ [README博客](https://blog.cherishmoon.fun/bot/LittlePaimon-nonebot2.html)

本人已经转用NoneBot2，Hoshino版停止新功能的更新（有BUG请提[issue](https://github.com/CMHopeSunshine/LittlePaimon/issues)），**强烈建议您使用NoneBot2版体验最新功能！**

## 功能示例

<img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/ys.jpg" alt="ys">

<details>
<summary>角色背包</summary>
<img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/ysa.jpg" alt="ysa">
</details>

<details>
<summary>角色详情</summary>
<img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/ysc.jpg" alt="ysc">
</details>

<details>
<summary>深渊信息</summary>
<img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/sy12.jpg" alt="sy">
</details>

<details>
<summary>模拟抽卡</summary>
<img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/十连.jpg" alt="十连">
</details>

<details>
<summary>实时便签</summary>
<img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/ssbq.jpg" alt="ssbq">
</details>

<details>
<summary>每月札记</summary>
<img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/myzj.jpg" alt="myzj">
</details>

<details>
<summary>角色材料</summary>
<img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/material.png" alt="material">
</details>

<details>
<summary>抽卡记录</summary>
<img src="https://cherishmoon.oss-cn-shenzhen.aliyuncs.com/LittlePaimon/readme/gachalog.jpg" alt="gachalog">
</details>


## 功能列表

详见[功能列表](https://blog.cherishmoon.fun/bot/hoshinoFuncList.html)

## 部署方法

> 本项目基于HoshinoBot，可以使用HoshinoBot同样的部署方法。

### 手动部署

- [Linux](https://blog.cherishmoon.fun/bot/HoshinoDeploy.html#linux)
- [安卓系统](https://blog.cherishmoon.fun/bot/HoshinoDeploy.html#%E5%9C%A8%E5%AE%89%E5%8D%93%E6%89%8B%E6%9C%BA%E4%B8%8A%E9%83%A8%E7%BD%B2)
- [Windows]https://blog.cherishmoon.fun/bot/HoshinoDeploy.html#windows)

### Windows一键安装脚本

⚠️一键脚本会因计算机环境不同而可能产生各种各样的问题，出现问题请尝试手动部署

在你想安装的位置打开`powershell`，输入执行：

```powershell
iwr "https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LittlePaimon-install.ps1" -O .\pm.ps1 ; ./pm.ps1 ; Set-Location .. ; rm pm.ps1
```

安装成功后，用`powershell`运行文件夹内的`启动.ps1`来启动机器人  

### 添加公共cookie

部署完成后，你还需要至少添加一条**公共cookie**，小派蒙才能使用查询功能。

登录米游社网页版，在地址栏粘贴：

```
javascript:(function(){prompt(document.domain,document.cookie)})();
```

复制得到的cookie，向小派蒙发送**`添加公共ck`**和粘贴的内容，即可开始使用


## 额外说明

本项目也可作为HoshinoBot的插件来使用，移植`hoshino\modules`内模块即可，另外还需在`hoshino\util\__init__.py`中添加`PriFreqLimiter`方法用于模拟抽卡和派蒙聊天的冷却限制。

## 感谢

代码水平很烂，站在巨人的肩膀上努力学习ing......

- [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) - 基于nonebot的QQ-bot框架
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) - Onebot标准的框架实现
- [egenshin](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin) - 参考了它的抽卡代码和资源
- [西风驿站](https://bbs.mihoyo.com/ys/collection/307224) - 角色攻略一图流来源
- [hoshino-installer](https://github.com/pcrbot/hoshino-installer) - 一键安装脚本参考
- [bluemushoom](https://bbs.nga.cn/nuke.php?func=ucp&uid=62861898) - 全角色收益曲线和参考面板攻略图来源
- [genshin-gacha-export](https://github.com/sunfkny/genshin-gacha-export) - 抽卡记录导出参考
- [Adachi-BOT](https://github.com/SilveryStar/Adachi-BOT) - 部分资源来源
