

import requests
import urllib
import hashlib
#1 输入纬度、经度
lat,lon=input("输入地区所属的纬度、经度\n").split(" ")
#2 计算校验SN(百度API文档说明需要此步骤)
ak="DBpp4B41vR0CMbembeACol0mb7dMk1HT" # 参照自己的应用
sk="xxxxxx" # 参照自己的应用
url = "http://api.map.baidu.com"
query ="/geocoder/v2/?callback=renderReverse&location={0},{1}&output=json&pois=1&latest_admin=1&ak={2}".format(lat, lon, ak)
encodedStr = urllib.parse.quote(query, safe="/:=&?#+!$,;'@()*[]")
sn=hashlib.md5(urllib.parse.quote_plus(encodedStr + sk).encode()).hexdigest()
#3 使用requests获取返回的json
response=requests.get("{0}{1}&sn={2}".format(url,query,sn))
data=response.text
#4 处理json
city_name=eval(data[29:-1])['result']['addressComponent']['province']
print(data)
print(city_name)
