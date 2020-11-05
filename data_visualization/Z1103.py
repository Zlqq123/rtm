import sys
sys.path.append('./')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from en_client import en_client
from personal_info import vin
client=en_client()
'''
13辆质保提出的维修车辆检查
'''

vinlist=['LSVUZ60T8J2217528','LSVUZ60T6J2235946','LSVUZ60T8J2212247','LSVCZ6C48JN034824',
         'LSVUZ60T4J2224654','LSVCZ2C4XKN029912','LSVUZ60T5J2215199','LSVCZ6C41KN029367',
         'LSVUZ60T7J2225619','LSVCZ2C41KN081851','LSVUZ60T8J2198642',
         'LSVCZ6C41KN020796','LSVCZ6C46KN034371']

tb_name='ods.rtm_reissue_history'
sql="desc "+tb_name
title=pd.DataFrame(client.execute(sql))
print(title[0])


def date_export(vin):
    sql="SELECT * from " + tb_name + " WHERE deviceid=='"+vin+"' order by uploadtime "
    aus=client.execute(sql)
    if len(aus)>0:
        df = pd.DataFrame(aus)
        df.columns=title[0]
        df.drop(['devicetype','drivermotorsn','emnum','cocessys2','vocesd2','cocesd2','cel1num2','sbofsn2','cfnum2','celv2','cocessystemp2'],axis=1,inplace=True)
        df[['vehiclespeed','accmiles','ir','accpedtrav','brakepedstat','emctltemp','emspeed','emtq','emtemp','emvolt','emctlcut', \
            'cs','fc','lg','lat','mxvsysno','mxvcelno','mxcelvt','mivsysno','mivcelno','micelvt','mxtsysno','mxtpno','mxtemp','mitsysno','mitpno','mitemp', \
            'cocessys1','vocesd1','cocesd1','cel1num1','sbofsn1','cfnum1']] = df[['vehiclespeed','accmiles','ir','accpedtrav','brakepedstat', \
            'emctltemp','emspeed','emtq','emtemp','emvolt','emctlcut','cs','fc','lg','lat','mxvsysno','mxvcelno','mxcelvt','mivsysno','mivcelno','micelvt','mxtsysno', \
            'mxtpno','mxtemp','mitsysno','mitpno','mitemp','cocessys1','vocesd1','cocesd1','cel1num1','sbofsn1','cfnum1']].apply(pd.to_numeric)

        l=['tdfwn','celohwn','vedtovwn','vedtuvwn','lsocwn','celovwn','celuvwn','hsocwn','jpsocwn','cesysumwn',
           'celpoorwn','inswn','dctpwn','bksyswn','dcstwn','emctempwn','hvlockwn','emtempwn','vesoc']
        for ll in l:
            df[[ll]].replace([1,0],['TRUE','FALSE'])
        df.to_csv('D:/21python/RTM_数据相关/1103/'+vin+'_w.csv')
    else:
        print(vin)

for v in vinlist:
    date_export(v)