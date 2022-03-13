<div align="center">
    <h1>HoshinoBot在线运行代码插件</h1>
</div>

移植自nonebot2插件 [https://github.com/yzyyz1387/nonebot_plugin_code/](https://github.com/yzyyz1387/nonebot_plugin_code/)

## 安装
到`/hoshino/modules`目录下`git clone https://github.com/CMHopeSunshine/codeonline`
并在`/hoshino/config/__bot__.py`的`MODULES_ON`处添加`codeonline`开启模块

## 指令
```
#code [语言] (-i) (输入) [代码]
[]为必须，()为可选
-i：可选 输入 后跟输入内容
[语言]/(输入)之后必须要有一个空格

运行代码示例(c)(无输入)：
    #code c (注意此处必须要有空格)
    printf("hello world")
    
运行代码示例(python)(有输入)：
    #code py -i 你好 
    print(input())
        
运行代码示例(python)(生成随机数)：
    #code py -i 50,100,3 import random
    list=str(input()).split(',')
    p='roll%s个%s到%s以内的数：' % (list[2],list[0],list[1])
    for i in range(0,int(list[2])):
        n=random.randint(int(list[0]),int(list[1]))
        p+=str(n)+' '
    print(p)
```
支持语言:`py|php|java|cpp|js|c#|c|go|asm`
## 示例截图
![imgae](https://github.com/CMHopeSunshine/codeonline/blob/main/example.png)
