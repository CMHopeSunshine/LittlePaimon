# this file should be saved as "UTF-8 with BOM"
$ErrorActionPreference = "Stop"

function Expand-ZIPFile($file, $destination) {
    $file = (Resolve-Path -Path $file).Path
    $destination = (Resolve-Path -Path $destination).Path
    $shell = new-object -com shell.application
    $zip = $shell.NameSpace($file)
    foreach ($item in $zip.items()) {
        $shell.Namespace($destination).copyhere($item)
    }
}

# 检查运行环境
if ($Host.Version.Major -lt 3) {
    Write-Output 'powershell 版本过低，无法一键安装'
    exit
}
if ((Get-ChildItem -Path Env:OS).Value -ine 'Windows_NT') {
    Write-Output '当前操作系统不支持一键安装'
    exit
}
if (![Environment]::Is64BitProcess) {
    Write-Output '暂时不支持32位系统'
    exit
}

if (Test-Path ./LittlePaimon-Bot) {
    Write-Output '发现重复，是否删除旧文件并重新安装？'
    $reinstall = Read-Host '请输入 y 或 n (y/n)'
    Switch ($reinstall) { 
        Y { Remove-Item .\LittlePaimon-Bot -Recurse -Force } 
        N { exit } 
        Default { exit } 
    } 
}

try {
    py -3.8 --version
    if ($LASTEXITCODE = '0') {
        Write-Output 'python 3.8 已发现，跳过安装'
        $install_git = $false
    }
    else {
        $install_python = $true
        Write-Output 'python 3.8 未发现，将自动安装'
    }
}
catch [System.Management.Automation.CommandNotFoundException] {
    $install_python = $true
    Write-Output 'python 3.8 未发现，将自动安装'
}

try {
    git --version
    $install_git = $false
    Write-Output 'git 已发现，跳过安装'
}
catch [System.Management.Automation.CommandNotFoundException] {
    $install_git = $true
    Write-Output 'git 未发现，将自动安装'
}

$qqid = Read-Host '请输入作为机器人的QQ号：'
$qqpassword = Read-Host -AsSecureString '请输入作为机器人的QQ密码：'
$qqsuperuser = Read-Host '请输入机器人管理员的QQ号：'

$loop = $true
while ($loop) {
    $loop = $false
    Write-Output '请选择下载源'
    Write-Output '1、中国大陆'
    Write-Output '2、港澳台或国外'
    $user_in = Read-Host '请输入 1 或 2'
    Switch ($user_in) {
        1 { $source_cn = $true }
        2 { $source_cn = $false }
        Default { $loop = $true }
    }
}

if ($source_cn) {
    # 中国大陆下载源
    $python38 = 'https://mirrors.huaweicloud.com/python/3.8.6/python-3.8.6-amd64.exe'
    $git = 'https://mirrors.huaweicloud.com/git-for-windows/v2.35.1.windows.1/Git-2.35.1-64-bit.exe'
    $gocqhttp = 'https://download.fastgit.org/Mrs4s/go-cqhttp/releases/download/v1.0.0-rc1/go-cqhttp_windows_amd64.zip'
    $LittlePaimongit = 'https://hub.fastgit.xyz/CMHopeSunshine/LittlePaimon.git'
    $pypi = 'http://mirrors.aliyun.com/pypi/simple/'
}
else {
    # 国际下载源
    $python38 = 'https://www.python.org/ftp/python/3.8.6/python-3.8.6-amd64.exe'
    $git = 'https://github.com/git-for-windows/git/releases/download/v2.35.1.windows.1/Git-2.35.1-64-bit.exe'
    $gocqhttp = 'https://github.com/Mrs4s/go-cqhttp/releases/download/v1.0.0-rc1/go-cqhttp_windows_amd64.zip'
    $LittlePaimongit = 'https://github.com/CMHopeSunshine/LittlePaimon.git'
    $pypi = 'https://pypi.org/simple/'
}

# 创建运行目录
New-Item -Path .\LittlePaimon-Bot -ItemType Directory
Set-Location LittlePaimon-Bot
New-Item -ItemType Directory -Path .\go-cqhttp

# 下载安装程序
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

if ($install_python) {
    Write-Output "正在安装 python"
    Invoke-WebRequest $python38 -OutFile .\python-3.8.6.exe
    Start-Process -Wait -FilePath .\python-3.8.6.exe -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1 Include_test=0"
    Write-Output "python 安装成功"
    Remove-Item python-3.8.6.exe
}
if ($install_git) {
    Write-Output "正在安装 git"
    Invoke-WebRequest $git -OutFile .\git-2.35.1.exe
    Start-Process -Wait -FilePath .\git-2.35.1.exe -ArgumentList "/SILENT /SP-"
    $env:Path += ";C:\Program Files\Git\bin"  # 添加 git 环境变量
    Write-Output "git 安装成功"
    Remove-Item git-2.35.1.exe
}
Invoke-WebRequest $gocqhttp -O .\go-cqhttp.zip
Expand-ZIPFile go-cqhttp.zip -Destination .\go-cqhttp\
Remove-Item go-cqhttp.zip

# 下载源码
git clone $LittlePaimongit --depth=1
Set-Location LittlePaimon
pip install -r requirements.txt -i $pypi
Copy-Item -Recurse hoshino\config_example hoshino\config
Set-Location ..

# 写入 gocqhttp 配置文件
$realpassword = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($qqpassword))
New-Item -Path .\go-cqhttp\config.yml -ItemType File -Value @"
# go-cqhttp 默认配置文件

account: # 账号相关
  uin: ${qqid} # QQ账号
  password: '${realpassword}' # 密码为空时使用扫码登录
  encrypt: false  # 是否开启密码加密
  status: 0      # 在线状态 请参考 https://docs.go-cqhttp.org/guide/config.html#在线状态
  relogin: # 重连设置
    delay: 3   # 首次重连延迟, 单位秒
    interval: 3   # 重连间隔
    max-times: 0  # 最大重连次数, 0为无限制

  # 是否使用服务器下发的新地址进行重连
  # 注意, 此设置可能导致在海外服务器上连接情况更差
  use-sso-address: true

heartbeat:
  # 心跳频率, 单位秒
  # -1 为关闭心跳
  interval: 5

message:
  # 上报数据类型
  # 可选: string,array
  post-format: string
  # 是否忽略无效的CQ码, 如果为假将原样发送
  ignore-invalid-cqcode: false
  # 是否强制分片发送消息
  # 分片发送将会带来更快的速度
  # 但是兼容性会有些问题
  force-fragment: true
  # 是否将url分片发送
  fix-url: false
  # 下载图片等请求网络代理
  proxy-rewrite: ''
  # 是否上报自身消息
  report-self-message: false
  # 移除服务端的Reply附带的At
  remove-reply-at: false
  # 为Reply附加更多信息
  extra-reply-data: false
  # 跳过 Mime 扫描, 忽略错误数据
  skip-mime-scan: false

output:
  # 日志等级 trace,debug,info,warn,error
  log-level: warn
  # 日志时效 单位天. 超过这个时间之前的日志将会被自动删除. 设置为 0 表示永久保留.
  log-aging: 15
  # 是否在每次启动时强制创建全新的文件储存日志. 为 false 的情况下将会在上次启动时创建的日志文件续写
  log-force-new: true
  # 是否启用日志颜色
  log-colorful: true
  # 是否启用 DEBUG
  debug: false # 开启调试模式

# 默认中间件锚点
default-middlewares: &default
  # 访问密钥, 强烈推荐在公网的服务器设置
  access-token: ''
  # 事件过滤器文件目录
  filter: ''
  # API限速设置
  # 该设置为全局生效
  # 原 cqhttp 虽然启用了 rate_limit 后缀, 但是基本没插件适配
  # 目前该限速设置为令牌桶算法, 请参考:
  # https://baike.baidu.com/item/%E4%BB%A4%E7%89%8C%E6%A1%B6%E7%AE%97%E6%B3%95/6597000?fr=aladdin
  rate-limit:
    enabled: false # 是否启用限速
    frequency: 1  # 令牌回复频率, 单位秒
    bucket: 1     # 令牌桶大小

database: # 数据库相关设置
  leveldb:
    # 是否启用内置leveldb数据库
    # 启用将会增加10-20MB的内存占用和一定的磁盘空间
    # 关闭将无法使用 撤回 回复 get_msg 等上下文相关功能
    enable: true

  # 媒体文件缓存， 删除此项则使用缓存文件(旧版行为)
  cache:
    image: data/image.db
    video: data/video.db

# 连接服务列表
servers:
  # 添加方式，同一连接方式可添加多个，具体配置说明请查看文档
  #- http: # http 通信
  #- ws:   # 正向 Websocket
  #- ws-reverse: # 反向 Websocket
  #- pprof: #性能分析服务器
  # 反向WS设置
  - ws-reverse:
      # 反向WS Universal 地址
      # 注意 设置了此项地址后下面两项将会被忽略
      universal: ws://127.0.0.1:6660/ws/
      # 反向WS API 地址
      api: ws://127.0.0.1:6660/api/
      # 反向WS Event 地址
      event: ws://127.0.0.1:6660/event/
      # 重连间隔 单位毫秒
      reconnect-interval: 3000
      middlewares:
        <<: *default # 引用默认中间件

"@

# 写入 LittlePaimon 配置文件
Set-Content .\LittlePaimon\hoshino\config\__bot__.py -Value @"
# coding=gbk
# hoshino监听的端口与ip
PORT = 6660
HOST = '127.0.0.1'      # 本地部署使用此条配置（QQ客户端和bot端运行在同一台计算机）
# HOST = '0.0.0.0'      # 开放公网访问使用此条配置（不安全）

DEBUG = False           # 调试模式

WHITE_LIST = []
SUPERUSERS = [${qqsuperuser}]    # 填写超级用户的QQ号，可填多个用半角逗号","隔开
GUILDADMIN = []
NICKNAME = ('派蒙','bot')          # 机器人的昵称。呼叫昵称等同于@bot，可用元组配置多个昵称

COMMAND_START = {''}    # 命令前缀（空字符串匹配任何消息）
COMMAND_SEP = set()     # 命令分隔符（hoshino不需要该特性，保持为set()即可）

# 发送图片的协议
# 可选 http, file, base64
# 当QQ客户端与bot端不在同一台计算机时，可用http协议
RES_PROTOCOL = 'file'
# 资源库文件夹，需可读可写，windows下注意反斜杠转义
RES_DIR = r'./res/'
# 使用http协议时需填写，原则上该url应指向RES_DIR目录
RES_URL = 'http://127.0.0.1:5000/static/'


# 启用的模块
# 初次尝试部署时请先保持默认
# 如欲启用新模块，请认真阅读部署说明，逐个启用逐个配置
# 切忌一次性开启多个
MODULES_ON = {
    'botmanage',
    'dice',
    'avatar_gif',
    'codeonline',
    'Paimonchat',
    'Genshin_Paimon',
    'myb_exchange'
}
"@

# 写启动程序
New-Item -Path .\启动.ps1 -ItemType File -Value @"
Start-Process powershell.exe -ArgumentList "Set-Location .\LittlePaimon ; python run.py"
Set-Location .\go-cqhttp
./go-cqhttp.exe
"@

Write-Output '安装完成！用powershell运行"启动.ps1"来启动机器人吧！'