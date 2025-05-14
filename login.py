import requests
import qrcode
import os
import sys
import time
import json

qr_baseurl = 'https://passport.bilibili.com/x/passport-login/web/qrcode/generate'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.1.4.514 Safari/537.36 360se/19.19.81.0",
    "Referer": "https://passport.bilibili.com/",
    "Origin": "https://passport.bilibili.com/",
    "Pregma": "no-cache",
    "Cache-Control": "max-age=0",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-User": "?1",
    "Sec-Fetch-Dest": "document",
    "Accept": "*/*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Accept-Encoding": "",
    "Connection": "keep-alive"
}

qr_data = requests.get(qr_baseurl,headers=headers).json()

qr_url = qr_data["data"]["url"]
qrcode_key = qr_data["data"]["qrcode_key"]

qr = qrcode.QRCode()
qr.add_data(qr_url)
qr.make()
qr.print_ascii()
qr.make_image().save('bili_login.png')

print("请在180秒内使用哔哩哔哩移动端扫描终端内二维码\n或程序目录内图片 bili_login.png 进行登录")

poll_url = "https://passport.bilibili.com/x/passport-login/web/qrcode/poll"
poll_params = {
    "qrcode_key": qrcode_key
}

if not os.path.exists('user_data.json'):
    with open('user_data.json','w') as f:
        f.write("{}")
        f.close()
cookies = {}
with open('user_data.json','r') as f:
    cookies = json.load(f)

for i in range(1,180):
    qr_check = requests.get(poll_url,headers=headers,params=poll_params)
    qr_ckjson = qr_check.json()
    if(qr_ckjson["data"]["code"]!=0):
        if(qr_ckjson["data"]["code"]==86038):
            print("二维码已失效。")
            input("按下Enter / Return键继续……")
            os.remove('bili_login.png')
            os._exit(0)
    else:
        uid = qr_check.cookies["DedeUserID"]
        userName = qr_check.cookies["DedeUserID"]
        cookies[uid]=[userName]
        cookie_raw = ""
        for key in qr_check.cookies.iterkeys():
            cookie_raw+=key+"="+qr_check.cookies[key]+"; "
            # cookies[uid][key] = qr_check.cookies[key]
        cookies[uid].append(cookie_raw)
        break
    time.sleep(1)

with open('user_data.json','w') as f:
    json.dump(cookies,f)

print("获取完毕.")
os.remove('bili_login.png')
input("按下Enter / Return键继续……")

