import sys
sys.path.append('./')
import xlsxwriter
import time
import csv
import numpy as np
import hist_func_np
from en_client import en_client
from default_hist import RtmHist
import os
client=en_client()

def f1(pro, date_range, region, userType, mile_range,fuc_name):
    print(pro,date_range, region, userType, mile_range,fuc_name)
    if userType=='all':
        userType=0

    if region=='all':
        region=0

    if mile_range == ['','']:
        l2=RtmHist(pro, date_range=date_range, region=region, user_type=userType )
    else:
        m=[int(mile_range[0]),int(mile_range[0])]
        l2=RtmHist(pro, date_range=date_range, region=region, user_type=userType, mile_range=m)
    n = l2.count_nr()
    if n>0 :
        if fuc_name=='fc11':
            [re1, _]= l2.daily_mileage()
            #col_name = re1.columns.tolist()
            #col_name.insert(0,'每日行驶里程范围[km]')
            re1['每日行驶里程范围[km]']=re1.index.tolist()
            #re1.reindex(columns=col_name)            
            return re1
        if fuc_name=='fc12':
            x = l2.percharge_mile()
            re1 = x[0]
            #col_name = re1.columns.tolist()
            #col_name.insert(0,'每次充电之间行驶里程范围[km]')
            re1['每次充电之间行驶里程范围[km]'] = re1.index.tolist()
            #re1.reindex(columns=col_name)
            return re1


'''
l2=RtmHist(path,"lavida",date_range=['2020-06-01','2020-06-03'])
l2.count_nr()
l2.charge_soc()
'''