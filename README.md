<p align="center">
  <a href="https://github.com/CMHopeSunshine/LittlePaimon"><img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/logo.png" width="256" height="256" alt="LittlePaimon"></a>
</p>
<h1 align="center">小派蒙|LittlePaimon</h1>
<h4 align="center">✨基于<a href="https://github.com/Ice-Cirno/HoshinoBot" target="_blank">HoshinoBot</a>和<a href="https://github.com/Mrs4s/go-cqhttp" target="_blank">go-cqhttp</a>的原神Q群机器人✨</h4>

<p align="center">
    <img src="https://img.shields.io/badge/version-v1.0.2-red" alt="version">
    <a href="https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LICENSE"><img src="https://img.shields.io/github/license/CMHopeSunshine/LittlePaimon" alt="license"></a>
    <img src="https://img.shields.io/badge/Python-3.8+-yellow" alt="python">
    <a href="https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&inviteCode=MmWrI&from=246610&biz=ka"><img src="https://img.shields.io/badge/QQ频道-尘世闲游-green?style=flat-square" alt="QQ guild"></a>
</p>




## 简介

通过米游社接口，查询uid的游戏信息，并附带各种娱乐功能。

## 功能示例

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

## 指令列表

### 查询功能

以下指令会记录上一次查询的uid，因此只需第一次查询时写上uid即可。

| 指令              | 介绍                                    | 备注                                                         |
| ----------------- | --------------------------------------- | :----------------------------------------------------------- |
| ys uid            | 查询uid的个人信息卡片                   |                                                              |
| ysa uid           | 查询uid拥有的角色和武器                 | 没绑cookie则只显示8个                                        |
| ysc uid 角色名    | 查询uid指定角色的信息                   | 没绑cookie则只能查公开的8个，且不显示天赋；支持角色别名      |
| ysb cookie        | 绑定私人cookie到qq号                    | 建议使用私聊绑定                                             |
| 添加公共ck cookie | 添加cookie到公共cookie池                | 需要添加至少一个公共cookie才能使用查询功能，每个cookie每日查询上限30次 |
| sy uid (层数)     | 查询uid的深渊信息                       | 绑定私人cookie后才能查看具体层数信息                         |
| ssbq uid          | 查询uid的实时便签，包括树脂、派遣情况等 | uid必须绑定了对应私人cookie才能使用                          |
| myzj uid (月份)   | 查询uid的该月札记                       | uid必须绑定了对应私人cookie才能使用，不写月份时默认为本月，只能看最近3个月 |

### 抽卡记录导出和分析

| 指令                  | 介绍                             | 备注                                   |
| --------------------- | -------------------------------- | -------------------------------------- |
| 查看抽卡记录 uid 池子 | 查看uid已有的抽卡记录的分析图片  | 池子有all\|角色\|武器\|常驻，默认为all |
| 获取抽卡记录 uid 链接 | 从api获取抽卡记录，时间较长      |                                        |
| 导出抽卡记录 uid 格式 | 导出抽卡记录的文件，上传到群文件 | 格式有xlsx和json;只能在群里导出        |

抽卡记录链接的获取方式和其他工具是一样的，这里不多介绍了；

本派蒙导出的xlsx和json符合UIGF标准，可用于其他UIGF标准的抽卡记录分析工具。

### 模拟抽卡功能

| 指令                       | 介绍                               | 备注                                                         |
| -------------------------- | ---------------------------------- | ------------------------------------------------------------ |
| 抽n十连xx                  | 模拟抽n个xx池子的十连              | n必须为阿拉伯数字，最多同时5次；xx池子有角色1\|角色2\|武器\|常驻\|彩蛋，可以DIY池子 |
| 选择定轨 武器名称          | 武器定轨                           | 武器名必须是全称                                             |
| 查看定轨                   | 查看当前定轨的武器和能量值         |                                                              |
| 删除定轨                   | 删除定轨                           |                                                              |
| 查看模拟抽卡记录           | 查看模拟抽卡的出货率、保底数等信息 |                                                              |
| 查看模拟抽卡记录 角色/武器 | 查看模拟抽卡抽到的角色/武器列表    |                                                              |
| 删除模拟抽卡记录           | 清空自己的模拟抽卡记录             |                                                              |

### 原神WIKI

| 指令       | 介绍                                | 备注     |
| ---------- | ----------------------------------- | -------- |
| xx角色攻略 | 查看西风驿站出品的角色攻略一图流    | 支持别名 |
| xx角色材料 | 查看我出品的角色材料一图流          | 支持别名 |
| xx参考面板 | 查看bluemushoom出品的角色参考面板图 | 支持别名 |
| xx收益曲线 | 查看bluemushoom出品的角色收益曲线图 | 支持别名 |

### 米游币帮兑功能

私聊机器人回复```米游币兑换```，跟着派蒙的提示步骤来使用。

### 派蒙语音功能

> 发送语音功能需要额外安装FFmpeg，请自行安装

群聊关键词可能会触发派蒙语音哦，尝试发送`诶嘿、大佬、羡慕`等词吧！

### 头像表情包制作

| 指令                                                         | 介绍                        | 备注      | 例子           |
| ------------------------------------------------------------ | --------------------------- | :-------- | -------------- |
| #亲亲/贴贴/拍拍/给爷爬/吃掉/扔掉/撕掉/精神支柱/要我一直 @人/qq号/图片 | 好玩的头像图片gif表情包生成 | 要以#开头 | #精神支柱@群主 |

## 更新日志

- 3.20 新增Windows一键部署脚本
- 3.22 新增蓝佬授权提供的收益曲线和参考面板攻略图
- 3.24 新增抽卡记录导出和分析功能，原模拟抽卡的指令更改

## 未来计划

- [ ] 实时便签树脂提醒
- [x] 抽卡记录导出和分析
- [ ] ocr圣遗物评分和角色面板记录
- [ ] 角色、武器和圣遗物wiki
- [ ] 派蒙AI闲聊
- [ ] 米游社自动签到

## 部署方法

> 本项目和HoshinoBot的部署方式一样，因此Linux可以参考：
>
> https://cn.pcrbot.com/deploy-hoshinobot-on-centos/

### 一键安装脚本

#### Windows

在你想安装的位置打开`powershell`，输入执行：

```powershell
iwr "https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LittlePaimon-install.ps1" -O .\pm.ps1 ; ./pm.ps1 ; Set-Location .. ; rm pm.ps1
```

安装成功后，`powershell`运行文件夹内的`启动.ps1`来启动机器人  
完成go-cqhttp的登录后，登录米游社网页版，在地址栏粘贴：

```
javascript:(function(){prompt(document.domain,document.cookie)})();
```

复制得到的cookie，向机器人私聊发送`添加公共ck`和粘贴的内容即可开始使用

#### Linux

代补充...

## 额外说明

本项目也可作为HoshinoBot的插件来使用，移植`hoshino/modules`内模块即可，不过对HoshinoBot有所魔改，报错时查看修改一下代码即可。

## 感谢

代码水平很烂，站在巨人的肩膀上努力学习ing......

- [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) - 基于nonebot1的QQ-bot框架
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) - Onebot标准的框架实现
- [egenshin](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin) - 参考了它的抽卡代码和资源
- [西风驿站](https://bbs.mihoyo.com/ys/collection/307224) - 角色攻略一图流来源
- [hoshino-installer](https://github.com/pcrbot/hoshino-installer) - 一键安装脚本参考
- [bluemushoom](https://bbs.nga.cn/nuke.php?func=ucp&uid=62861898) - 全角色收益曲线和参考面板攻略图来源
- [genshin-gacha-export](https://github.com/sunfkny/genshin-gacha-export) - 抽卡记录导出参考
