<p align="center" >
  <a href="https://github.com/CMHopeSunshine/LittlePaimon/tree/nonebot2"><img src="http://static.cherishmoon.fun/LittlePaimon/readme/logo.png" width="256" height="256" alt="LittlePaimon"></a>
</p>
<h1 align="center">nonebot-plugin-myb-exchange</h1>
<h4 align="center">Nonebot2米游币商品自动兑换插件</h4>
<p align="center" >
<a href="https://pypi.python.org/pypi/nonebot-plugin-myb-exchange">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-myb-exchange" alt="pypi">
</a>
<img src="https://img.shields.io/badge/Python-3.8+-yellow" alt="python">
<img src="https://img.shields.io/badge/Nonebot-2.0.0b5-green" alt="python">
</p>

## 安装
> 需要配合nonebot2使用，安装方法详见[nb文档](https://v2.nonebot.dev/)
- 通过nb脚手架安装（推荐）
```
nb plugin install nonebot-plugin-myb-exchange
```
- 通过pip安装
```
pip install nonebot-plugin-myb-exchange

# 还需要在bot.py加载插件，在bot.py中添加
nonebot.load_plugin("nonebot-plugin-myb-exchange")
```
- 通过poetry安装
```
poetry add nonebot-plugin-myb-exchange

# 还需要在bot.py加载插件，同上
```


## 使用方法
> 由于涉及到cookie、地址等敏感信息，所以仅限**私聊**Bot使用

- 发送`myb`，跟随Bot的指引一步一步录入信息，需要用户提供`米游社cookie、收货地址、商品名称`等信息
- 发送`myb_info`可查看已录入的兑换计划
- 发送`myb_delete`可一键删除所有你的兑换计划

## 成功兑换示范

<img src="https://static.cherishmoon.fun/LittlePaimon/readme/QQ%E5%9B%BE%E7%89%8720220630233519.png" alt="myb">