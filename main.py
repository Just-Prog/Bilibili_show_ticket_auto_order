import sys
import os
from api import Api
from geetest import dealCode

if not os.path.exists("config.txt"):
	print("config.txt文件缺失")
	input("按下Enter / Return键继续……")
	os._exit(0)

a = open("config.txt","r").readlines()
proxies = None if a[0].split("=")[1].strip() == "None" else a[0].split("=")[1].strip()
specificID = None if a[1].split("=")[1].strip() == "None" else a[1].split("=")[1].strip()
sleep = eval(a[2].split("=")[1].strip())
token = None if a[3].split("=")[1].strip() == "None" else a[3].split("=")[1].strip()
phone = None if a[4].split("=")[1].strip() == "None" else a[4].split("=")[1].strip()

if __name__ == '__main__':
	if not os.path.exists("url"):
		with open("url","w") as f:
			f.write("")
	print('!!! 请不要在社交平台/大型群组宣传本软件，感谢合作 !!!')
	print('!!! 请不要在社交平台/大型群组宣传本软件，感谢合作 !!!')
	print('!!! 请不要在社交平台/大型群组宣传本软件，感谢合作 !!!')
	print('!!! 本程序完全免费，如果你是买来的证明你被骗了 !!!')
	print('!!! 本程序完全免费，如果你是买来的证明你被骗了 !!!')
	print('!!! 本程序完全免费，如果你是买来的证明你被骗了 !!!')
	print('!!! 仅供学习使用，请在下载后24小时之内删除 !!!')
	print('!!! 仅供学习使用，请在下载后24小时之内删除 !!!')
	print('!!! 仅供学习使用，请在下载后24小时之内删除 !!!\n')
	Api(proxies=proxies,specificID=specificID,sleepTime=sleep,token=token,phone=phone).start()
