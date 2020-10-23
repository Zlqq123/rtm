import sys
sys.path.append('./')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from en_client import en_client
from personal_info import vin
client=en_client()
vin0=vin()

'''
original table
All data(without warmingsignal)----------------------------- ods.rtm_details  
All data with warmingsignal------------------------ods.rtm_reissue_history

2020/03 Data(without warmingsignal)------------------------- en.rtm_vds
2020/06 Data(with warmingsignal)---------------------------- en.rtm_data_june

attachment table:
VIN Usertype Project region province mileage---------------- en.vehicle_vin

pre analyzed tabel:
2020/06 Data(with warmingsignal) after pre analyzing----- en.rtm_data_june-->-->--- en.rtm_6_2th
All data(without warmingsignal) after pre analyzing -------- en.rtm_2th
All data with warmingsignal Tiguan -------------en.rtm_tiguan
'''

sql="desc ods.rtm_details"
title=pd.DataFrame(client.execute(sql))
sql="SELECT * from ods.rtm_details WHERE deviceid=='"+vin0+"' AND uploadtime between '2020/09/01 00:00:00' AND '2020/12/31 23:59:59' order by uploadtime "
aus=client.execute(sql)
df = pd.DataFrame(aus)
# 重命名列命
df.columns=title[0]
print(df.columns)
# 删除指定列
df.drop(['deviceid','devicetype','drivermotorsn','emnum','cocessys2','vocesd2','cocesd2','cel1num2','sbofsn2','cfnum2','celv2','cocessystemp2'],axis=1,inplace=True)
#print(df.dtypes)
# 类型转化
df[['vehiclespeed','accmiles','ir','accpedtrav','brakepedstat','emctltemp','emspeed','emtq','emtemp','emvolt','emctlcut', \
    'cs','fc','lg','lat','mxvsysno','mxvcelno','mxcelvt','mivsysno','mivcelno','micelvt','mxtsysno','mxtpno','mxtemp','mitsysno','mitpno','mitemp', \
    'cocessys1','vocesd1','cocesd1','cel1num1','sbofsn1','cfnum1']] = df[['vehiclespeed','accmiles','ir','accpedtrav','brakepedstat', \
    'emctltemp','emspeed','emtq','emtemp','emvolt','emctlcut','cs','fc','lg','lat','mxvsysno','mxvcelno','mxcelvt','mivsysno','mivcelno','micelvt','mxtsysno', \
    'mxtpno','mxtemp','mitsysno','mitpno','mitemp','cocessys1','vocesd1','cocesd1','cel1num1','sbofsn1','cfnum1']].apply(pd.to_numeric)

#print(df.dtypes)
df.to_csv('D:/21python/rtm/data_visualization/test.csv')
