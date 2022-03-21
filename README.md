<p align="center">
  <a href="https://github.com/CMHopeSunshine/LittlePaimon"><img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/logo.png" width="200" height="200" alt="LittlePaimon"></a>
</p>
<h1 align="center">小派蒙|LittlePaimon</h1>
<h4 align="center">✨基于<a href="https://github.com/Ice-Cirno/HoshinoBot" target="_blank">HoshinoBot</a>和<a href="https://github.com/Mrs4s/go-cqhttp" target="_blank">go-cqhttp</a>的原神Q群机器人✨</h4>

<p align="center">
    <img src="https://img.shields.io/badge/version-v1.0.0-red" alt="version">
    <a href="https://cdn.jsdelivr.net/gh/CMHopeSunshine/LittlePaimon@master/LICENSE"><img src="https://img.shields.io/github/license/CMHopeSunshine/LittlePaimon" alt="license"></a>
    <img src="https://img.shields.io/badge/python-3.8+-yellow" alt="python">
    <a href="https://github.com/Mrs4s/go-cqhttp"><img src="https://img.shields.io/badge/go--cqhttp-v1.0.0--rc1-green?style=flat-square" alt="go-cqhttp"></a>
    <a href="https://docs.nonebot.dev/"><img src="https://img.shields.io/badge/NoneBot-1.6.0+,2.0.0---cyan?style=flat-square" alt="go-cqhttp"></a>
    <a href="https://qm.qq.com/cgi-bin/qm/qr?k=C7QsbLOA4SNWWy8_lofoR1CPipG-aTi3&jump_from=webapi"><img src="https://img.shields.io/badge/QQ群-906635633-blue?style=flat-square" alt="QQ Chat"></a>
    <a href="https://qun.qq.com/qqweb/qunpro/share?_wv=3&_wwv=128&inviteCode=MmWrI&from=246610&biz=ka"><img src="https://img.shields.io/badge/QQ频道-尘世闲游-purple?style=flat-square" alt="QQ guild"></a>
</p>


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

## 指令列表

### 查询功能

以下指令会记录上一次查询的uid，因此只需第一次查询时写上uid即可。

| 指令              | 介绍                                    | 备注                                                    |
| ----------------- | --------------------------------------- | :------------------------------------------------------ |
| ys uid            | 查询uid的个人信息卡片                   |                                                         |
| ysa uid           | 查询uid拥有的角色和武器                 | 没绑cookie则只显示8个                                   |
| ysc uid 角色名    | 查询uid指定角色的信息                   | 没绑cookie则只能查公开的8个，且不显示天赋；支持角色别名 |
| ysb cookie        | 绑定私人cookie到qq号                    |                                                         |
| 添加公共ck cookie | 添加cookie到公共cookie池                | 至少需要添加一个公共cookie才能使用查询功能              |
| sy uid (层数)     | 查询uid的深渊信息                       | 绑定私人cookie后才能查看具体层数信息                    |
| ssbq uid          | 查询uid的实时便签，包括树脂、派遣情况等 | uid必须绑定了对应私人cookie才能使用                     |
| myzj uid 月份     | 查询uid的该月札记                       | uid必须绑定了对应私人cookie才能使用                     |

### 模拟抽卡功能

| 指令                   | 介绍                               | 备注                                                         |
| ---------------------- | ---------------------------------- | ------------------------------------------------------------ |
| 抽n十连xx              | 模拟抽n个xx池子的十连              | n必须为阿拉伯数字，最多同时5次；xx池子有角色1\|角色2\|武器\|常驻\|彩蛋，可以DIY池子 |
| 选择定轨 武器名称      | 武器定轨                           | 武器名必须是全称                                             |
| 查看定轨               | 查看当前定轨的武器和能量值         |                                                              |
| 删除定轨               | 删除定轨                           |                                                              |
| 查看抽卡记录           | 查看模拟抽卡的出货率、保底数等信息 |                                                              |
| 查看抽卡记录 角色/武器 | 查看模拟抽卡抽到的角色/武器列表    |                                                              |
| 删除抽卡记录           | 清空自己的模拟抽卡记录             |                                                              |

### 原神WIKI

| 指令       | 介绍                               | 备注 |
| ---------- | ---------------------------------- | ---- |
| xx角色攻略 | 查看西风驿站出品的角色攻略一图流   |      |
| xx角色材料 | 查看开发者本人出品的角色材料一图流 |      |



### 米游币帮兑功能

私聊机器人回复```米游币兑换```，跟着机器人提示步骤来使用。

### 派蒙语音功能

群聊关键词可能会触发派蒙语音哦（需要额外安装ffmepg）

### 头像表情包制作

| 指令                                                         | 介绍                        | 备注      | 例子           |
| ------------------------------------------------------------ | --------------------------- | :-------- | -------------- |
| #亲亲/贴贴/拍拍/给爷爬/吃掉/扔掉/撕掉/精神支柱/要我一直 @人/qq号/图片 | 好玩的头像图片gif表情包生成 | 要以#开头 | #精神支柱@群主 |

## 部署方法

> 本项目和HoshinoBot的部署方式一样，因此Linux可以参考：
>
> https://cn.pcrbot.com/deploy-hoshinobot-on-centos/
>

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

## 未来计划

- [ ] 实时便签树脂提醒

- [ ] 抽卡记录导出和分析
- [ ] ocr圣遗物评分和角色面板记录
- [ ] 角色、武器和圣遗物wiki
- [ ] 派蒙AI闲聊

## 感谢

- [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) - 基于nonebot1的QQ-bot框架
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) - Onebot标准的框架实现
- [egenshin](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin) - 参考了它的抽卡代码和资源
- 西风驿站 - 角色攻略一图流来源
- [hoshino-installer](https://github.com/pcrbot/hoshino-installer) - 一键安装脚本参考
