<h1 align="center">nonebot-plugin-couplets</h1>
<h4 align="center">Nonebot2对对联插件</h4>
<p align="center" >
<a href="https://pypi.python.org/pypi/nonebot-plugin-couplets">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-couplets" alt="pypi">
</a>
<img src="https://img.shields.io/badge/Python-3.8+-yellow" alt="python">
<img src="https://img.shields.io/badge/Nonebot-2.0.0b5-green" alt="python">
</p>

## 安装
> 需要配合nonebot2使用，安装方法详见[nb文档](https://v2.nonebot.dev/)
- 通过nb脚手架安装（推荐）
```
nb plugin install nonebot-plugin-couplets
```
- 通过pip安装
```
pip install nonebot-plugin-couplets

# 还需要在bot.py加载插件，在bot.py中添加
nonebot.load_plugin("nonebot-plugin-couplets")
```
- 通过poetry安装
```
poetry add nonebot-plugin-couplets

# 还需要在bot.py加载插件，同上
```


## 指令
```
对联 <上联内容> (数量)
· 数量可选，默认为1
```
例如，`对联 苟利国家生死以 3`

