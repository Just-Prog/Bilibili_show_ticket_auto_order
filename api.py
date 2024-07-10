# -*- coding: UTF-8 -*-
"""
API
"""
import json
import os
import time
import re
import json
import sys
import http.cookies
import qrcode
import bili_ticket_gt_python
from time import sleep
from urllib import request
from urllib.request import Request as Reqtype
from urllib.parse import urlencode
from geetest import dealCode
from plyer import notification as trayNotify
import ntplib



class Api:
    """
    API操作
    """
    def __init__(self,proxies=None,specificID=None,sleepTime=0.15,token=None,phone=None):
        self.proxies=proxies
        self.specificID=specificID
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.1.4.514 Safari/537.36",
            "Referer":"https://mall.bilibili.com/",
            "Origin":"https://mall.bilibili.com/",
            "Pregma":"no-cache",
            "Cache-Control":"max-age=0",
            "Upgrade-Insecure-Requests":"1",
            "Sec-Fetch-Site":"none",
            "Sec-Fetch-Mode":"navigate",
            "Sec-Fetch-User":"?1",
            "Sec-Fetch-Dest":"document",
            "Cookie":"a=b;",
            "Accept": "*/*",
            "Accept-Language": "zh-CN;q=0.9",
            "Accept-Encoding": "",
            "Connection": "keep-alive"
        }
        self.sleepTime = sleepTime
        self.token = token
        self.start_time = time.time()
        self.user_data = {}
        self.user_data["specificID"] = specificID
        self.user_data["username"] = ""
        self.user_data["project_id"] = ""
        # self.user_data["deliver_info"] = ""
        self.user_data["token"] = ""
        self.appName = "BilibiliShow_AutoOrder"
        self.selectedTicketInfo = "未选择"
        self.userCountLimit = ""
        self.selectedScreen = 0
        self.selectedTicket = 0
        self.ntp_client = ntplib.NTPClient()
        self.validatePhoneNum = str(phone) if phone else str()
        self.date = "2000-01-01"
        # ALL_USER_DATA_LIST = [""]

    def load_cookie(self):
        if not os.path.exists("user_data.json"):
            t =  open("user_data.json","w")
            t.write("{}")
            t.close
        with open("user_data.json","r") as r:
            try:
                j = json.load(r)
            except:
                r.close()
                print("请重新使用login登录一次bilibili")
                t =  open("user_data.json","w")
                t.write("{}")
                t.close()
                self.error_handle("")
            if not len(j):
                print("请先使用login登录一次bilibili")
                t =  open("user_data.json","w")
                t.write("{}")
                t.close()
                self.error_handle("")
            if self.user_data["specificID"]:
                self.user_data["username"],self.headers["Cookie"] = j[self.user_data["specificID"]][0],j[self.user_data["specificID"]][1]
            else:
                j = j[list(j.keys())[0]]
                self.user_data["username"],self.headers["Cookie"] = j[0],j[1]

            
    def _http(self,url,j=False,data=None,raw=False):
        data = data.encode() if type(data) == type("") else data
        try:
            if self.proxies and data:
                opener = request.build_opener(request.ProxyHandler({'http':self.proxies,'https':self.proxies}))
                res = opener.open(Reqtype(url,headers=self.headers,method="POST",data=data),timeout=120)
            elif self.proxies and not data:
                opener = request.build_opener(request.ProxyHandler({'http':self.proxies,'https':self.proxies}))
                res = opener.open(Reqtype(url,headers=self.headers,method="GET"),timeout=120)
            elif data and not self.proxies:
                res = request.urlopen(Reqtype(url,headers=self.headers,method="POST",data=data),timeout=120)
            else:
                res = request.urlopen(Reqtype(url,headers=self.headers,method="GET"),timeout=120)
        except Exception as e:
            print("请求超时 请检查网络")
            print(e)
            # self.error_handle("ip可能被风控。请求地址: " + url)
        else:
            if res.code != 200:
                self.error_handle("ip可能被风控，请求地址: " + url)
            if j:
                return json.loads(res.read().decode("utf-8","ignore"))
            elif raw:
                return res
            else:
                return res.read().decode("utf-8","ignore")

    def getCSRF(self):
        cookie = http.cookies.BaseCookie()
        cookie.load(self.headers["Cookie"])
        return cookie["bili_jct"].value
    
    def orderInfo(self):
        # 获取目标
        self.user_data["project_id"] = re.search(r"id=\d+",self.menu("GET_SHOW")).group().split("=")[1]
        # print(self.user_data["project_id"])
        # exit(0)
        # 获取订单信息
        url = "https://show.bilibili.com/api/ticket/project/getV2?version=134&id=" + self.user_data["project_id"] + "&project_id="+ self.user_data["project_id"] + "&requestSource=pc-new"
        data = self._http(url,True)
        if not data["data"]:
            print(data)
            return 1
        # print(self.menu("GET_ORDER_IF",data["data"]))
        self.setAuthType(data)

        if data["data"]["sales_dates"]:
            self.menu("GET_DATE",data["data"])
            url = "https://show.bilibili.com/api/ticket/project/infoByDate?id="+self.user_data["project_id"] +"&date=" +self.date
            data = self._http(url,True)
            self.user_data["screen_id"],self.user_data["sku_id"],self.user_data["pay_money"],self.userCountLimit = self.menu("GET_ORDER_IF_DATE",data["data"])
        # print(self.user_data["auth_type"])
        else:
            self.user_data["screen_id"],self.user_data["sku_id"],self.user_data["pay_money"],self.userCountLimit = self.menu("GET_ORDER_IF",data["data"])

        url = "https://show.bilibili.com/api/ticket/project/getV2?version=134&id=" + self.user_data["project_id"] + "&project_id="+ self.user_data["project_id"] + "&requestSource=pc-new"
        data = self._http(url,True)
        if(data["data"]["has_paper_ticket"]):
            a = self.addressInfo()
            fa = a["prov"]+a["city"]+a["area"]+a["addr"]
            self.user_data["deliver_info"] = {}
            self.user_data["deliver_info"]["name"],self.user_data["deliver_info"]["tel"],self.user_data["deliver_info"]["addr_id"],self.user_data["deliver_info"]["addr"] = a["name"],a["phone"],a["id"],fa

        # print("订单信息获取成功")
    
    def getExpressFee(self):
        url = "https://show.bilibili.com/api/ticket/project/get?version=134&id=" + self.user_data["project_id"] + "&project_id="+ self.user_data["project_id"]
        data = self._http(url,True)
        if not data["data"]:
            print(data)
            return 1
        e = data["data"]["express_fee"]
        if(e == -1 or e == -2):
            return 0
        return e

    def setAuthType(self,data):
        if not data:
            self.error_handle("项目不存在")
        self.user_data["auth_type"] = ""
        if data['data']['id_bind']:
            # 哔哩哔哩会员购移动端的脚本代码明确表述了id_bind=1为一单一证，id_bind=2为一票一证，与脚本内部现行判断一致
            # 关键字检测太考验维护频率了
            self.user_data["auth_type"] = data['data']['id_bind'] 
        else:
            self.user_data["auth_type"] = 0

    def buyerinfo(self):
        if self.user_data["auth_type"] == 0:
            self.user_data["buyer_name"], self.user_data["buyer_phone"] = self.menu("GET_NORMAL_INFO")
            self.user_data["user_count"] = self.menu("GET_T_COUNT")
            return
        # 获取购票人
        url = "https://show.bilibili.com/api/ticket/buyer/list?is_default&projectId=" + self.user_data["project_id"]
        data = self._http(url,True)

        self.user_data["buyer"] = self.menu("GET_ID_INFO", data["data"])
        # print(self.user_data["buyer"])
        # exit(0)
        if self.user_data["auth_type"] == 2:
            self.user_data["user_count"] = len(self.user_data["buyer"])
        else:
            self.user_data["user_count"] = self.menu("GET_T_COUNT")

        for i in range(0, len(self.user_data["buyer"])):
            self.user_data["buyer"][i]["isBuyerInfoVerified"] = "true"
            self.user_data["buyer"][i]["isBuyerValid"] = "true"
       
        # self.user_data["buyer"] = data["data"]["list"]
        # print(self.user_data["buyer"])
        # exit()
        # print("购票人信息获取成功")

    def addressInfo(self):
        url = "https://show.bilibili.com/api/ticket/addr/list"
        data = self._http(url,True)
        if(len(data["data"]["addr_list"])<=0):
            self.error_handle("请先前往会员购地址管理添加收货地址")
        if data["errno"] != 0:
            print("[会员购地址管理] 失败信息: " + data["msg"])
            return 1
        n = int(self.menu("GET_ADDRESS_LIST",data["data"]))-1
        return data["data"]["addr_list"][n]
        
    def geetestPass(self, gt, challenge):
        try:
        # using sample code & binary NodeJS components from https://github.com/Amorter/biliTicker_gt

            click = bili_ticket_gt_python.ClickPy()
            slide = bili_ticket_gt_python.SlidePy()

            (c, s) = slide.get_c_s(gt, challenge)
            _type = slide.get_type(gt, challenge)
            print(_type)
            if _type == "click":
                (c, s, args) = click.get_new_c_s_args(gt, challenge)
                before_calculate_key = time.time()
                key = click.calculate_key(args)
                w = click.generate_w(key, gt, challenge, str(c), s, "abcdefghijklmnop")
                w_use_time = time.time() - before_calculate_key
                if w_use_time < 2:
                    time.sleep(2 - w_use_time)
                (msg, validate) = click.verify(gt, challenge, w)
            else:
                (c, s, args) = slide.get_new_c_s_args(gt, challenge)
                challenge = args[0]
                key = slide.calculate_key(args)
                w = slide.generate_w(key, gt, challenge, str(c), s, "abcdefghijklmnop")
                (msg, validate) = slide.verify(gt, challenge, w)
            print(_type, validate)
        except Exception as e:
            print(f"Geetest自动化检测出错。错误代码：{e}")
            sleep(2)
            return self.geetestPass(gt, challenge)
        return validate
    
    def phoneCheckPass(self, tel, telLen):
        print(f'正在从配置文件补全手机号码：{tel}, {telLen}')
        if(self.validatePhoneNum!='0'):
            return self.validatePhoneNum
        else:
            self.error_handle('请在配置文件中预留哔哩哔哩账号绑定的手机号。')

    def tokenGet(self):
        # 获取token
        url = "https://show.bilibili.com/api/ticket/order/prepare?project_id=" + self.user_data["project_id"]
        payload = {
            'count': str(self.user_data["user_count"]),
            'project_id': self.user_data["project_id"],
            'screen_id': self.user_data["screen_id"],
            'order_type': '1',
            'sku_id': str(self.user_data["sku_id"]),
            'buyer_info': '',
            'token': '',
            "ignoreRequestLimit": 'true',
            'ticket_agent': '',
            'newRisk': 'true',
            'requestSource': 'neul-next'
        }
        payload = urlencode(payload)
        data = self._http(url,True,payload)
        
        # R.I.P. 旧滑块验证

        # if not data["data"]:
        #     # self.error_handle("获取token失败")
        #     timestr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + ": "
        #     print(timestr+"失败信息: " + data["msg"])
        #     return 1
        # if data["data"]["shield"]["verifyMethod"]:
        #     with open("url","w") as f:
        #         print("需要验证，正在拉取验证码")
        #         f.write(data["data"]["shield"]["naUrl"])
        #     if self.token:
        #         self.end_time = time.time()
        #         if self.end_time - self.start_time > 60:
        #             print(self.end_time - self.start_time)
        #             self.sendNotification("该拉滑块验证码啦！")
        #             self.start_time = self.end_time            
        # self.user_data["token"] = data["data"]["token"]
        # # print(data)
        # # print(self.user_data["user_count"])
        # print("\n购买Token获取成功")

        if data:
            if data["errno"] == -401:
                print("=== 发现验证 ===")
                __url = "https://api.bilibili.com/x/gaia-vgate/v1/register"
                __payload = urlencode(data["data"]["ga_data"]["riskParams"])
                __data = self._http(__url,True,__payload)
                if __data.get('data').get('type')=='geetest':
                    gt = __data["data"]["geetest"]["gt"]
                    challenge = __data["data"]["geetest"]["challenge"]
                    token = __data["data"]["token"]
                    validate = self.geetestPass(gt, challenge)
                    _payload = {
                        "challenge": challenge,
                        "token": token,
                        "seccode": validate+'|jordan',
                        "csrf": self.getCSRF(),
                        "validate": validate
                    }
                elif __data.get('data').get('type')=='phone':
                    token = __data["data"]["token"]
                    _payload = {
                        "code": self.phoneCheckPass(__data['data']['phone']['tel'], __data['data']['phone']['telLen']),
                        "csrf": self.getCSRF(),
                        "token": token,
                    }
                else:
                    self.error_handle("验证码类别无法辨别，请重启程序后重试")
                _url = "https://api.bilibili.com/x/gaia-vgate/v1/validate"
                _data = self._http(_url,True,urlencode(_payload))
                if(_data["code"]==-111):
                    self.error_handle("csrf校验失败")
                if _data["data"]["is_valid"] == 1:
                    print("认证成功。")
                    return 0
                elif _data["code"]==100001:
                    self.error_handle("验证码校验失败。")
                elif _data["code"]==100003:
                    self.error_handle("验证码过期")
                else:
                    self.error_handle("验证失败。")
            elif data["errno"] == 100041:
                # print("指定展览/演出未开票或账号异常")
                url_ = "https://show.bilibili.com/api/ticket/project/getV2?version=134&id=" + self.user_data["project_id"] + "&project_id="+ self.user_data["project_id"] + "&requestSource=pc-new"
                data_ = self._http(url_,True)
                time_s = data_["data"]["screen_list"][self.selectedScreen]["ticket_list"][self.selectedTicket]['saleStart']
                if int(time.time())<time_s:
                    time_x = self.ntp_client.request('ntp.aliyun.com').tx_time
                    print("未开票，正在等待 开票时间:", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_s)), "请求发起时间(阿里云授时):", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time_x)))
                    for i in range(time_s - int(time_x), 0, -1):
                        print("\r剩余时间：{}s".format(i), end="", flush=True)
                        time.sleep(1)
                else:
                    self.error_handle("账号状态异常，请检查您的哔哩哔哩账号")
            elif data['errno'] == 100098:
                self.error_handle('当前票种/展览/演出设定状态为为哔哩哔哩大会员限定购买，如已是大会员请确认大会员权能是否冻结')
            elif data['errno'] == 100039:
                self.error_handle('活动收摊了，下次要快点哦')
            else:
                if not data["data"]:
                    timestr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.ntp_client.request('ntp.aliyun.com').tx_time)) + ":"
                    print(timestr,"失败信息: ",data["code"],data["msg"])
                    return 1
                if data["data"]["token"]:
                    self.user_data["token"] = data["data"]["token"]
        return 0
        
    def orderCreate(self):
        # noTicket = False
        # while True:
        #     if self.checkAvaliable() == 2:
        #         print("!!!检测到预售状态，开始购买!!!")
        #         break
        #     else:
        #         if noTicket == False:
        #             print("---暂无库存---")
        #             noTicket = True

        # 创建订单
        # url = "https://show.bilibili.com/api/ticket/order/createV2?project_id=" + config["projectId"]
        url = "https://show.bilibili.com/api/ticket/order/createV2?project_id=" + self.user_data["project_id"]

        try:
            self.user_data["deliver_info"]
        except KeyError:
            if self.user_data["auth_type"] == 0:
                payload = {
                    "buyer": self.user_data["buyer_name"],
                    "tel": self.user_data["buyer_phone"],
                    "count": self.user_data["user_count"],
                    "deviceId": "",
                    "order_type": 1,
                    "pay_money": int(self.user_data["pay_money"]) * int(self.user_data["user_count"]),
                    "project_id": self.user_data["project_id"],
                    "screen_id": self.user_data["screen_id"],
                    "sku_id": self.user_data["sku_id"],
                    "timestamp": int(round(time.time() * 1000)),
                    "token": self.user_data["token"],
                    "again": 1,
                }
            else:
                payload = {
                    "buyer_info": self.user_data["buyer"],
                    "count": self.user_data["user_count"],
                    "deviceId": "",
                    "order_type": 1,
                    "pay_money": int(self.user_data["pay_money"]) * int(self.user_data["user_count"]),
                    "project_id": self.user_data["project_id"],
                    "screen_id": self.user_data["screen_id"],
                    "sku_id": self.user_data["sku_id"],
                    "timestamp": int(round(time.time() * 1000)),
                    "token": self.user_data["token"],
                    "again": 1
                }
        else:
            if self.user_data["auth_type"] == 0:
                payload = {
                    "buyer": self.user_data["buyer_name"],
                    "tel": self.user_data["buyer_phone"],
                    "count": self.user_data["user_count"],
                    "deviceId": "",
                    "order_type": 1,
                    "pay_money": int(self.user_data["pay_money"]) * int(self.user_data["user_count"]) + self.getExpressFee(),
                    "project_id": self.user_data["project_id"],
                    "screen_id": self.user_data["screen_id"],
                    "sku_id": self.user_data["sku_id"],
                    "timestamp": int(round(time.time() * 1000)),
                    "token": self.user_data["token"],
                    "deliver_info": json.dumps(self.user_data["deliver_info"],ensure_ascii=0),
                    "again": 1
                }
            else:
                payload = {
                    "buyer_info": self.user_data["buyer"],
                    "count": self.user_data["user_count"],
                    "deviceId": "",
                    "order_type": 1,
                    "pay_money": int(self.user_data["pay_money"]) * int(self.user_data["user_count"]) + self.getExpressFee(),
                    "project_id": self.user_data["project_id"],
                    "screen_id": self.user_data["screen_id"],
                    "sku_id": self.user_data["sku_id"],
                    "timestamp": int(round(time.time() * 1000)),
                    "token": self.user_data["token"],
                    "deliver_info": json.dumps(self.user_data["deliver_info"],ensure_ascii=0),
                    "again": 1
                }
        timestr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time())) + ' (LT)'
        data = self._http(url,True,urlencode(payload).replace("%27true%27","true").replace("%27","%22"))
        if data:
            if data["errno"] == 0:
                if self.checkOrder(data["data"]["token"],data["data"]["orderId"]):
                    _ts = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.ntp_client.request('ntp.aliyun.com').tx_time))
                    print("已成功抢到票, 请在10分钟内完成支付。通知发送时间 (NTP):",_ts)
                    trayNotifyMessage = _ts+" (NTP) 已成功抢到票, 请在10分钟内完成支付" + "\n" + "购票人："
                    # + thisBuyerInfo + self.selectedTicketInfo + "\n"
                    # Add buyer info
                    if "buyer_info" in payload:
                        for i in range(0, len(payload["buyer_info"])):
                            if self.user_data["auth_type"] == 0:
                                trayNotifyMessage += ['buyer_info'][i][0] + " "
                            else:
                                trayNotifyMessage += payload['buyer_info'][i]["name"] + " "
                    elif "buyer" in payload:
                        trayNotifyMessage += payload["buyer"]
                    trayNotifyMessage += "\n" + self.selectedTicketInfo
                    # check if trayNotifyMessage is too long
                    if len(trayNotifyMessage) > 500:
                        trayNotifyMessage = trayNotifyMessage[:500] + "..."
                    self.tray_notify("抢票成功", trayNotifyMessage, "./ico/success.ico", timeout=20)
                    if self.token:
                        self.sendNotification(trayNotifyMessage)
                    return 1
                else:
                    print("糟糕，是张假票(同时锁定一张票，但是被其他人抢走了)\n马上重新开始抢票")
                    self.tray_notify("抢票失败", "糟糕，是张假票(同时锁定一张票，但是被其他人抢走了)\n马上重新开始抢票", "./ico/failed.ico", timeout=8)
            elif data["errno"] == 209002:
                print(timestr,"未获取到购买人信息")
            elif "10005" in str(data["errno"]):    # Token过期
                print(timestr,"Token已过期! 正在重新获取")
                self.tokenGet()
            elif "100009" in str(data["errno"]):
                print(timestr,"错误信息：当前暂无余票，请耐心等候。")
            elif "100001" in str(data["errno"]):
                print(timestr,"错误信息：获取频率过快或无票。")
            # elif "100079" in str(data["errno"]):
            #     trayNotifyMessage = ""
            #     if "buyer_info" in payload:
            #         for i in range(0, len(payload["buyer_info"])):
            #             if self.user_data["auth_type"] == 0:
            #                 trayNotifyMessage += ['buyer_info'][i][0] + " "
            #             else:
            #                 trayNotifyMessage += payload['buyer_info'][i]["name"] + " "
            #     elif "buyer" in payload:
            #         trayNotifyMessage += payload["buyer"]
            #     trayNotifyMessage += "\n" + self.selectedTicketInfo
            #     self.tray_notify("存在未付款订单", trayNotifyMessage, "./ico/success.ico", timeout=20)
            #     self.error_handle(timestr+"指定的购买人存在已付款订单")
            else:
                print(timestr,"错误信息: ["+str(data["errno"])+"]", data["msg"])
                # print(data)
        return 0

    def checkOrder(self,_token,_orderId):
        timestr = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.ntp_client.request('ntp.aliyun.com').tx_time))+":"
        print(timestr, "下单成功！正在检查票务状态...请稍等")
        self.tray_notify("下单成功", "正在检查票务状态...请稍等", "./ico/info.ico", timeout=5)
        # sleep(5)
        # url = "https://show.bilibili.com/api/ticket/order/list?page=0&page_size=10"
        # data = self._http(url,True)
        # # print(data)
        # if data["errno"] != 0:
        #     print("检测到网络波动，正在重新检查...")
        #     return self.checkOrder()
        # elif not data["data"]["list"]:
        #     return 0
        # elif data['data']['list'][0]['status'] == 1:
        #     return 1
        # else:
        #     return 0
        url = "https://show.bilibili.com/api/ticket/order/createstatus?token="+_token+"&timestamp="+str(int(round(time.time() * 1000)))+"&project_id="+self.user_data["project_id"]+"&orderId="+str(_orderId)
        data = self._http(url,True)
        if(data["errno"] == 0):
            _qrcode = data["data"]["payParam"]["code_url"]
            print("请使用微信/QQ/支付宝扫描二维码完成支付")
            print("请使用微信/QQ/支付宝扫描二维码完成支付")
            print("请使用微信/QQ/支付宝扫描二维码完成支付\n")
            print(f"若二维码显示异常请扫描程序目录下 ticket_{str(_orderId)}.png 图片文件的二维码")
            print(f"若二维码显示异常请扫描程序目录下 ticket_{str(_orderId)}.png 图片文件的二维码")
            print(f"若二维码显示异常请扫描程序目录下 ticket_{str(_orderId)}.png 图片文件的二维码")
            _ts = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(self.ntp_client.request('ntp.aliyun.com').tx_time))
            qr_gen = qrcode.QRCode()
            qr_gen.add_data(_qrcode)
            qr_gen.print_ascii()
            qr_gen.make_image().save(f'ticket_{str(_orderId)}.png')
            # print(qrcode)
            print(f'\n二维码生成时间 (NTP)：{_ts}')
            return 1
        else:
            return 0

    def error_handle(self,msg):
        print(msg)
        os.system("pause")
        sys.exit(0)

    def menu(self,mtype,data=None):
        if mtype == "GET_SHOW":
            i = input("请输入购票链接并按回车继续 格式例如 https://show.bilibili.com/platform/detail.html?id=73711\n>>> ").strip()
            if "bilibili" not in i or "id" not in i:
                self.error_handle("网址格式错误")
            return i
        elif mtype == "GET_DATE":
            print("\n请选择日期序号并按回车继续，格式例如 1")
            for i in range(len(data["sales_dates"])):
                print(str(i+1)+":"+data["sales_dates"][i]["date"])
            date = input("日期序号 >>> ").strip()
            try:
                date = int(date) - 1
                if date not in [i for i in range(len(data["sales_dates"][i]["date"]))]:
                    self.error_handle("请输入正确序号")
            except:
                self.error_handle("请输入正确数字")
            self.date=data["sales_dates"][date]["date"]
        elif mtype =="GET_ORDER_IF_DATE":
            print("\n请选择场次序号并按回车继续，格式例如 1")
            for i in range(len(data["screen_list"])):
                print(str(i+1) + ":",data["screen_list"][i]["name"])
            date = input("场次序号 >>> ").strip()
            try:
                date = int(date) - 1
                if date not in [i for i in range(len(data["screen_list"]))]:
                    self.error_handle("请输入正确序号")
            except:
                self.error_handle("请输入正确数字")
            print("已选择：", data["screen_list"][date]["name"])
            print("\n请输入票种并按回车继续，格式例如 1")
            for i in range(len(data["screen_list"][date]["ticket_list"])):
                print(str(i+1) + ":",data["screen_list"][date]["ticket_list"][i]["desc"],"-",data["screen_list"][date]["ticket_list"][i]["price"]//100,"RMB")
            choice = input("票种序号 >>> ").strip()
            try:
                choice = int(choice) - 1
                if choice not in [i for i in range(len(data["screen_list"][date]["ticket_list"]))]:
                    self.error_handle("请输入正确序号")
            except:
                self.error_handle("请输入正确数字")
            self.selectedTicketInfo = self.date+" "+data["screen_list"][date]["name"] + " " + data["screen_list"][date]["ticket_list"][choice]["desc"]+ " " + str(data["screen_list"][date]["ticket_list"][choice]["price"]//100)+ " " +"CNY"
            print("\n已选择：", self.selectedTicketInfo)
            self.selectedScreen = date
            self.selectedTicket = choice
            return data["screen_list"][date]["id"],data["screen_list"][date]["ticket_list"][choice]["id"],data["screen_list"][date]["ticket_list"][choice]["price"],data["screen_list"][date]["ticket_list"][choice]["static_limit"]["num"]
        elif mtype == "GET_ORDER_IF":
            print("\n演出名称: " + data["name"])
            print("票务状态: " + data["sale_flag"])
            if data["has_eticket"] == 1:
                print("本演出/展览票面为电子票/兑换票。")
            if data["has_paper_ticket"] == 1:
                print("本演出/展览包含纸质票。")
            print("\n请选择场次序号并按回车继续，格式例如 1")
            for i in range(len(data["screen_list"])):
                print(str(i+1) + ":",data["screen_list"][i]["name"],data["screen_list"][i]["saleFlag"]["display_name"])
            date = input("场次序号 >>> ").strip()
            try:
                date = int(date) - 1
                if date not in [i for i in range(len(data["screen_list"]))]:
                    self.error_handle("请输入正确序号")
            except:
                self.error_handle("请输入正确数字")
            print("已选择：", data["screen_list"][date]["name"])
            print("\n请输入票种并按回车继续，格式例如 1")
            for i in range(len(data["screen_list"][date]["ticket_list"])):
                print(str(i+1) + ":",data["screen_list"][date]["ticket_list"][i]["desc"],"-",data["screen_list"][date]["ticket_list"][i]["price"]//100,"RMB",data["screen_list"][date]["ticket_list"][i]["sale_flag"]["display_name"])
            choice = input("票种序号 >>> ").strip()
            try:
                choice = int(choice) - 1
                if choice not in [i for i in range(len(data["screen_list"][date]["ticket_list"]))]:
                    self.error_handle("请输入正确序号")
            except:
                self.error_handle("请输入正确数字")
            self.selectedTicketInfo = data["name"] + " " + data["screen_list"][date]["name"] + " " + data["screen_list"][date]["ticket_list"][choice]["desc"]+ " " + str(data["screen_list"][date]["ticket_list"][choice]["price"]//100)+ " " +"CNY"
            print("\n已选择：", self.selectedTicketInfo)
            self.selectedScreen = date
            self.selectedTicket = choice
            return data["screen_list"][date]["id"],data["screen_list"][date]["ticket_list"][choice]["id"],data["screen_list"][date]["ticket_list"][choice]["price"],data["screen_list"][date]["ticket_list"][choice]["static_limit"]["num"]
        elif mtype == "GET_ID_INFO":
            if not data:
                self.error_handle("用户信息为空，请登录或先上传身份信息并认证后重试")
            if self.user_data["auth_type"] == 1:
                print("\n按照监管部门要求，此项目需要实名购票，一个订单需要填写一个证件，支持身份证(包括临时身份证)、护照、港澳居民来往内地通行证、台湾居民来往大陆通行证等证件类型，入场时需要本人携带填写证件；\n本展览只可选择1个实名信息，请输入对应数字，如 '1'")
                if len(data["list"]) <= 0:
                    self.error_handle("你的账号里一个购票人信息都没填写哦，请前往哔哩哔哩客户端-会员购-个人中心-购票人信息提前填写购票人信息")
                for i in range(len(data["list"])):
                    print(str(i+1) + ":" , "姓名: " + data["list"][i]["name"], "手机号:" , data["list"][i]["tel"], "身份证:", data["list"][i]["personal_id"])
                p = input("购票人序号 >>> ").strip()
                try:
                    t = []
                    print("\n已选择: ",data["list"][int(p)-1]["name"])
                    t.append(data["list"][int(p)-1])
                    return t
                except:
                    self.error_handle("请输入正确序号")
            if self.user_data["auth_type"] == 2:
                if len(data["list"]) <= 0:
                    self.error_handle("你的账号里一个购票人信息都没填写哦，请前往哔哩哔哩客户端-会员购-个人中心-购票人信息提前填写购票人信息")
                print("\n按照监管部门要求，此项目需要实名购票，一张票需要填写一个证件，支持身份证(包括临时身份证)、护照、港澳居民来往内地通行证、台湾居民来往大陆通行证等证件类型，入场时需要本人携带填写证件；\n全部购票请输入0，其他请输入购票人序号，多个购票请用空格分隔，如 1 2")
                for i in range(len(data["list"])):
                    print(str(i+1) + ":" , "姓名: " + data["list"][i]["name"], "手机号:" , data["list"][i]["tel"], "身份证:", data["list"][i]["personal_id"])
                p = input("购票人序号 >>> ").strip()

                t = []
                if p == "0":
                    print("\n已选择列表中全部购票人")
                    return data["list"]
                elif " " in p:
                    try:
                        print("\n已选择: ",end="")
                        for i in p.split(" "):
                            if i:
                                print(data["list"][int(i)-1]["name"],end=" ")
                                t.append(data["list"][int(i)-1])
                        print("")
                        return t
                    except:
                        self.error_handle("请输入正确序号")
                else:
                    try:
                        print("\n已选择: ",data["list"][int(p)-1]["name"])
                        t.append(data["list"][int(p)-1])
                        return t
                    except:
                        self.error_handle("请输入正确序号")
        elif mtype == "GET_NORMAL_INFO":
            print("\n此演出无需身份电话信息，请填写姓名和联系方式后按回车")
            name = input("姓名 >>> ").strip()
            tel = input("电话 >>> ").strip()
            if not re.match(r"^\d{9,14}$",tel):
                self.error_handle("请输入正确格式的电话号码")
            return name, tel

        elif mtype == "GET_T_COUNT":
            print("\n请输入购买数量 (最多",self.userCountLimit,"张票)")
            n = input(">>> ").strip()
            if not re.match(r"^\d{1,2}$",n):
                self.error_handle("请输入正确的数量")
            return n
        elif mtype == "GET_ADDRESS_LIST":
            print("\n请选择实体票发货地址(仅单地址)")
            for i in range(len(data["addr_list"])):
                print(str(i+1) + ":" , data["addr_list"][i]["prov"]+data["addr_list"][i]["city"]+data["addr_list"][i]["area"]+data["addr_list"][i]["addr"] + " 收件人:" + data["addr_list"][i]["name"] + " " + data["addr_list"][i]["phone"])
            p = input("收货地址序号 >>> ").strip()
            return p


    def sendNotification(self,msg):
        data = {
            "token": self.token,
            "title": "抢票通知",
            "content": msg,
        }
        url = "http://www.pushplus.plus/send"
        self._http(url,data=urlencode(data),j=True)

    def tray_notify(self, title, msg, iconPath, timeout=10):  # windows系统托盘通知（部分功能可能只在Win10及之后版本有效）
        if not iconPath.endswith(".ico"):
            raise ValueError(f"iconPath must be a .ico file or icon doesn't exist. Your icon path: {iconPath}")
        trayNotify.notify(
            title = title,
            message = msg,
            app_name= self.appName,
            app_icon = iconPath,
            timeout = timeout,
        )

    def start(self):
        # 加载登录信息
        self.load_cookie()
        # 加载演出信息
        self.orderInfo()
        # while True:
            # try:
                # sleep(1.7)
                # if not self.orderInfo():
                    # break
            # except Exception as e:
            #     pass
        # 加载购买人信息
        self.buyerinfo()
        # 获取购票token
        while True:
            sleep(self.sleepTime)
            if self.tokenGet() == 0:
                break
        # 购票
        i = 0
        while True:
            i = 1+i
            sleep(self.sleepTime)
            print("正在尝试第: %d次抢票"%i)
            # if self.tokenGet():
                # continue
            if self.orderCreate():
                # open("url","w").write("https://show.bilibili.com/orderlist")
                os.system("pause")
                break

    def test(self):
        self.load_cookie()
        self.checkOrder()


if __name__ == '__main__':
    Api("127.0.0.1:8080").start()