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

该分支正在积极**开发中**，核心功能基本完成，欢迎帮助测试！

## | 新特性
> 相较于主分支而言
- 1、全新风格UI，好看！
- 2、代码结构更优美，更高性能！
- 3、集成插件权限管理器、自动帮助图生成
- 4、可用Web UI添加私人Cookie
- 5、须弥支持！

## 丨安装方法

- 1、安装poetry`pip install poetry`
- 2、克隆本分支`git clone https://github.com/CMHopeSunshine/LittlePaimon -b Bot --depth=1`
- 3、进入目录并安装依赖`poetry install`
- 4、安装配置go-cqhttp`略`
- 5、启动`poetry run nb run`
- 6、添加公共ck`添加公共ck`

从旧版本迁移
方法一：
- 1、在新的文件夹，按上述前三步克隆并安装依赖，
- 2、然后将原来旧版本Nonebot中的除了`LittlePaimon`外的文件夹全部迁移到现在的新文件夹
- 3、如果你旧版本中使用`gocq插件`的话，要在新版本的文件夹运行`poetry run nb plugin nonebot-plugin-gocqhttp`
- 4、你还装了其他插件的话，也是用`poetry run nb plugin nonebot-plugin-xxxx`重新装回

方法二：
- 1、将旧版本Bot中的`LittlePaimon`文件夹删除
- 2、克隆或下载本分支的文件，将`LittlePaimon`、`matcher_patch.py`、`requirements.txt`放到Bot目录中
- 3、进入虚拟环境，cd到Bot目录，运行`pip install -r requirements.txt`
- 4、在`bot.py`的第6行位置加一句`import matcher_patch`
- 5、将`bot.py`的`load_plugins('LittlePaimon')`的s去掉