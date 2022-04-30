# LittlePaimon_nb2
nonebot2版本的小派蒙

## 已完成迁移
- Paimon_Info 派蒙uid查询插件
- Paimon_Wiki 派蒙wiki查询插件
- Paimon_Gacha 派蒙模拟抽卡插件
- Paimon_Gacha_Log 派蒙抽卡记录获取插件

具体插件命令与hoshino版一致<br>
nonebot2刚上手，测试时间较短，如有bug，请及时反馈。


## 安装
> 已装nonebot2的，只需看`安装插件`
### 1. 安装Git和Python3
不多说了，看wiki的部署教程

### 2. 安装nonebot2
先安装脚手架以及依赖
```
pip install nb-cli
pip install matplotlib
pip install aiohttp
```
创建nonebot2项目
`nb create`
```
[?] Project Name: LittlePaimon
注：名字，随便填即可，这里以LittlePaimon为例
[?] Where to store the plugin?
> In a "genshinimpact_bot" folder
> In a src folder
注：选择插件放置目录，键盘↑↓选择，回车确认，随便选
[?] Which builtin plugin(s) would you like to user?
注：直接回车即可
[?] which adapter(s) would you like to use?
>  ● OneBot V11
   o 钉钉
   o 飞书
   o Telegram
   o QQ 频道
   o 开黑啦
   o mirai2
注：在第一个OneBot那里按空格，然后回车
```
`cd LittlePaimon`进入刚刚创建的nb2项目<br>
编辑`.env`，把`dev`改成`prod`<br>
编辑`.env.prod`，修改以下内容
```
HOST=127.0.0.1 # Nonebot监听的IP
PORT=6789 # Nonebot监听的端口，和go-cqhttp的端口一致
LOG_LEVEL=INFO # 日志等级
SUPERUSERS=["123456"] # 超级用户
NICKNAME=["派蒙", "bot"] # 机器人的昵称
COMMAND_START=["", "/", "#"] # 命令前缀
COMMAND_SEP=[""] # 命令分隔符
```

### 3. 安装go-cqhttp
也不多说了，看wiki的部署教程的go-cqhttp部分

### 4. 安装插件
```

nb plugin install nonebot-plugin-apscheduler
# 安装定时任务插件

git clone -b nonebot2 https://github.com/CMHopeSunshine/LittlePaimon
# 克隆小派蒙nonebot2分支
```
编辑`bot.py`
```
nonebot.load_plugins("LittlePaimon")
# 添加这句，加载插件
```

### 5. 启动机器人
`nb run`