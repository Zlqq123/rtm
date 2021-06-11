'''
# -*- encoding: utf-8 -*-
@File    : geocode.py
@Time    : 2021/04/26 09:36:27
@Author  : Pan Yang 
@Version : 1.0
'''

import json
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

f = open('D://1_Work//0_RTM//clickhouse//0_RTM_script//中华人民共和国.json', encoding='utf-8')
x = json.loads(f.readline())['features']
geocode = dict()
for i in range(len(x)-1): # 最后一个地区为空白，删除
    print(x[i]['properties']['name'])
    bd = x[i]['geometry']['coordinates'][0][0] #电子围栏列表
    y = [114,30]
    point = Point(y)
    print(Polygon(bd).contains(point))#判断是否在围栏内
f.close()