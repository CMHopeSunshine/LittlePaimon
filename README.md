# LittlePaimon

小派蒙，原神qq群机器人，基于[HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot)和[go-cqhttp](https://github.com/Mrs4s/go-cqhttp)开发。

## 指令列表

#### 查询功能

| 指令              | 介绍                                    | 备注                                                    | 例子              |
| ----------------- | --------------------------------------- | :------------------------------------------------------ | ----------------- |
| ys uid            | 查询uid的个人信息卡片                   |                                                         | ys100000001       |
| ysa uid           | 查询uid拥有的角色和武器                 | 没绑cookie则只显示8个                                   | ysa100000001      |
| ysc uid 角色名    | 查询uid指定角色的信息                   | 没绑cookie则只能查公开的8个，且不显示天赋；支持角色别名 | ysc100000001 钟离 |
| ysb cookie        | 绑定私人cookie到qq号                    |                                                         |                   |
| 添加公共ck cookie | 添加cookie到公共cookie池                | 至少需要添加一个公共cookie才能使用查询功能              |                   |
| sy uid (层数)     | 查询uid的深渊信息                       | 绑定私人cookie后才能查看具体层数信息                    | sy100000001 12    |
| ssbq uid          | 查询uid的实时便签，包括树脂、派遣情况等 | uid必须绑定了对应私人cookie才能使用                     | ssbq100000001     |
| myzj uid 月份     | 查询uid的该月札记                       | uid必须绑定了对应私人cookie才能使用                     | myzj100000001 3   |

#### 模拟抽卡功能

| 指令                   | 介绍                               | 备注                                                         | 例子              |
| ---------------------- | ---------------------------------- | ------------------------------------------------------------ | ----------------- |
| 抽n十连xx              | 模拟抽n个xx池子的十连              | n必须为阿拉伯数字，最多同时5次；xx池子有角色1\|角色2\|武器\|常驻\|彩蛋，可以DIY池子 | 抽5十连角色1      |
| 选择定轨 武器名称      | 武器定轨                           | 武器名必须是全称                                             | 选择定轨 护摩之杖 |
| 查看定轨               | 查看当前定轨的武器和能量值         |                                                              |                   |
| 删除定轨               | 删除定轨                           |                                                              |                   |
| 查看抽卡记录           | 查看模拟抽卡的出货率、保底数等信息 |                                                              |                   |
| 查看抽卡记录 角色/武器 | 查看模拟抽卡抽到的角色/武器列表    |                                                              |                   |
| 删除抽卡记录           | 清空自己的模拟抽卡记录             |                                                              |                   |

#### 原神WIKI

| 指令       | 介绍                               | 备注 | 例子         |
| ---------- | ---------------------------------- | ---- | ------------ |
| xx角色攻略 | 查看西风驿站出品的角色攻略一图流   |      | 钟离角色攻略 |
| xx角色材料 | 查看开发者本人出品的角色材料一图流 |      | 钟离角色材料 |



#### 米游币帮兑功能

私聊机器人回复```米游币兑换```，跟着机器人提示步骤来使用。

#### 派蒙语音功能

群聊关键词可能会触发派蒙语音哦（需要安装ffmepg）

#### 头像表情包制作

| 指令                                                         | 介绍                        | 备注      | 例子           |
| ------------------------------------------------------------ | --------------------------- | :-------- | -------------- |
| #亲亲/贴贴/拍拍/给爷爬/吃掉/扔掉/撕掉/精神支柱/要我一直 @人/qq号/图片 | 好玩的头像图片gif表情包生成 | 要以#开头 | #精神支柱@群主 |



## 指令示例

<details>
<summary>个人信息卡片ys</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/ys.jpg?token=GHSAT0AAAAAABSG2FHCDOJJR3Z6J6DZBQUYYR4KCBA" alt="ys">
</details>

<details>
<summary>角色背包ysa</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/ysa.jpg?token=GHSAT0AAAAAABSG2FHCQNM7JAMVI5MZFROYYR4KD5Q" alt="ysa">
</details>

<details>
<summary>角色详情ysc</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/ysc.jpg?token=GHSAT0AAAAAABSG2FHCOVL6FTKYVF5LZ27CYR4KETQ" alt="ysc">
</details>

<details>
<summary>深渊信息sy</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/sy12.jpg?token=GHSAT0AAAAAABSG2FHCCFQWAW3CYBFDD4EEYR4KF7Q" alt="sy">
</details>

<details>
<summary>模拟抽卡</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/%E5%8D%81%E8%BF%9E.jpg?token=GHSAT0AAAAAABSG2FHDJTKRZGUSNXIV6Y32YR4KHTA" alt="十连">
</details>

<details>
<summary>实时便签ssbq</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/ssbq.jpg?token=GHSAT0AAAAAABSG2FHDZM23HAQ4UCXGHUKOYR4KG5A" alt="ssbq">
</details>

<details>
<summary>每月札记myzj</summary>
<img src="https://raw.githubusercontent.com/CMHopeSunshine/LittlePaimon/master/readme/myzj.jpg?token=GHSAT0AAAAAABSG2FHDVIS6YRRTZ3C5KVGAYR4KIIQ" alt="myzj">
</details>

## 使用方法

> 本项目和HoshinoBot的部署方式一样，因此Linux可以参考：
>
> https://cn.pcrbot.com/deploy-hoshinobot-on-centos/
>
> Windows教程稍候补充...

## 未来计划

- 实时便签树脂提醒
- 抽卡记录导出和分析
- ocr圣遗物评分和角色面板记录
- 角色、武器和圣遗物wiki

## 感谢

- [HoshinoBot](https://github.com/Ice-Cirno/HoshinoBot) - 基于nonebot1的QQ-bot框架
- [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) - Onebot标准的框架实现
- [egenshin](https://github.com/pcrbot/erinilis-modules/tree/master/egenshin) - 参考了它的抽卡代码和资源
- 西风驿站 - 角色攻略一图流来源
