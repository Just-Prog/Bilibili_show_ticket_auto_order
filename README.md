# Bilibili_show_ticket_auto_order

## 本项目仅供Python网络编程学习、urllib/requests库网络请求操作学习、Selenium操作学习使用，请勿用于商业以及危害网站正常运行及数据安全用途，请勿利用进行盈利活动！
## 本项目仅供Python网络编程学习、urllib/requests库网络请求操作学习、Selenium操作学习使用，请勿用于商业以及危害网站正常运行及数据安全用途，请勿利用进行盈利活动！
## 本项目仅供Python网络编程学习、urllib/requests库网络请求操作学习、Selenium操作学习使用，请勿用于商业以及危害网站正常运行及数据安全用途，请勿利用进行盈利活动！

## 本项目无破坏干扰哔哩哔哩票务支付系统正常运行等恶意倾向，仅用作学习用途
## 本项目无破坏干扰哔哩哔哩票务支付系统正常运行等恶意倾向，仅用作学习用途
## 本项目无破坏干扰哔哩哔哩票务支付系统正常运行等恶意倾向，仅用作学习用途

## 温馨提示：请不要将本程序使用于 `Bilibili World 2025` 与 `Bilibili Macro Link 2025`，由尝试行为产生的对出票失败/自动退票、账号/IP/设备封禁等处罚措施的触发以及数字资产/经济损失等与本程序无关，已尽告知义务。

## 截止到 2024/11/15 仍然可用

![image](https://github.com/user-attachments/assets/2cd00f81-6194-4083-8060-eb933b6c3eba)

<img width="273" alt="屏幕截图 2023-08-09 182035" src="https://github.com/fengx1a0/Bilibili_show_ticket_auto_order/assets/74698099/f0b2d1ad-928b-498d-9a79-f735e3f01c00">

<img width="277" alt="屏幕截图 2023-08-09 182012" src="https://github.com/fengx1a0/Bilibili_show_ticket_auto_order/assets/74698099/4363ff9a-23a7-4f31-b0ea-0919ed1279d1">

> 本软件无法保证 100% 命中率和 100% 不受哔哩哔哩安全团队行为风险控制限制，一切交给天意
>
> 本软件可能无法及时跟进哔哩哔哩/极验Geetest验证码机制更新，望知悉
>
> 本项目遵循GPL（GNU General Public License）协议进行开源，仅供学习使用，请在24小时之后删除

# 原介绍

本项目核心借鉴自https://github.com/Hobr 佬

感谢原开发者 [fengx1ao](https://github.com/fengx1a0/Bilibili_show_ticket_auto_order)

极验验证码自动化解决方案提供：[BiliTicker-gt-python](https://github.com/Amorter/biliTicker_gt)

本脚本仅供学习交流使用, 不得用于商业用途, 如有侵权请联系删除

<img src="images\image-20230708221711220.png" alt="image-20230708221711220" style="zoom:50%;" />

<img src="images/a.png" alt="image-20230708221143842" style="zoom:50%;" />

## 致谢 from fengx1ao

以下排名不分先后，我也不想搞的攀比起来，因为很多都是学生，原则上我是不收赞助的，大家太热情了：

------------------------------------------------++++

```
晚安乃琳Queen
kankele
倔强
宵宫
yxw
星海云梦
穆桉
mizore
傩祓
CChhdCC
w2768
iiiiimilet
利维坦战斧
路人
Impact
骤雨初歇
明月夜
晓读
Simpson
Goognaloli
闹钟
LhiaS
洛天华
猪猪侠
awasl
房Z
浙江大学第一深情
superset245
ChinoHao
神秘的miku
Red_uncle
czpwpq
```

------------------------------------------------++++


## 功能截图

纯api请求

目前已经支持漫展演出等的 无证 / 单证 / 一人一证 的购买

<img src="images/image-20230708014050624.png" alt="image-20230708014050624" style="zoom:50%;" />

<img src="images\image-20230708014124395.png" alt="image-20230708014124395" style="zoom:50%;" />

## 使用

相关内容感谢@123485k的提交

### 执行exe

登录和抢票分开的，先运行登录.exe，登陆后再运行抢票.exe，运行了之后不要急着选，先把验证.exe启动起来

不需要依赖

如果运行失败的请安装依赖[Edgewebdriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/)

### 执行脚本

请确保引用的库安装正常。

```shell
pip install -r requirements.txt
```

```shell
python login.py     //登录.exe
python main.py      //抢票
python geetest.py   //极验滑块验证（暂时废弃）
```

### 自行打包

```shell
pyinstaller -F main.py --hidden-import plyer.platforms.win.notification -i ico/pyinstaller_logo.png
```

### 新功能：微信公众号推送结果

需要关注pushplus微信公众号，关注后激活，然后点击个人中心-获取token，在config.txt中填入token即可在需要验证或者抢票成功后收到微信公众号通知

## 配置说明

config.txt为配置文件，不指定值为None

- proxies 指定代理 如：127.0.0.1:8080 (IP:PORT 请不要加前缀)
- specificID 多个用户登陆后指定某一个人uid(bilibili) (多用户还没做等后面有必要再写)
- sleep设置每次抢票请求间隔时间
- token设置pushplus的个人token

## 问题报告

提issue即可

## 更新

脱离浏览器的新登录模块

库存检测

极验验证码自动化解决方案集成
