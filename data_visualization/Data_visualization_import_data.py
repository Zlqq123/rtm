import sys
sys.path.append('./')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from en_client import en_client
from vin import myself
client=en_client()
vin=myself()


sql="desc ods.rtm_details"
title=pd.DataFrame(client.execute(sql))
sql="SELECT * from ods.rtm_details WHERE deviceid=='"+vin+"' AND uploadtime between '2020/09/01 00:00:00' AND '2020/12/31 23:59:59' order by uploadtime "
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
df.to_csv('test.csv')
