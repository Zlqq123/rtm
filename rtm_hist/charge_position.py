import sys
sys.path.append("..")#sys.path.append("..")的意思是增加搜索的路径，..代表上一个目录层级

import time
from datetime import datetime
import numpy as np
import pandas as pd
import hist_func_np
from genarl_func import time_cost,time_cost_all
from en_client import en_client
client=en_client()

# All data with warmingsignal------------------------ods.rtm_reissue_history
def f1():
    '''
    sql="SELECT deviceid, uploadtime, charg_s_c, socp, d_soc, acc, v, longitude, latitude " \
        "FROM  " \
        "(SELECT deviceid, uploadtime, runningDifference(charg_s) AS charg_s_c, " \
            "socp, runningDifference(socp) AS d_soc, cast(accmiles,'Float32') AS acc, " \
            "cast(vehiclespeed, 'Float32') AS v, cast(lg, 'Float32') AS longitude, cast(lat, 'Float32') AS latitude " \
            "FROM  " \
                "(SELECT deviceid, uploadtime, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, "\
                    "accmiles, vehiclespeed, if(soc<0,0,soc) AS socp, lg, lat " \
                    "FROM ods.rtm_reissue_history " \
                    "WHERE deviceid like 'LSVA%' " \
                    "ORDER BY deviceid, uploadtime ) " \
            "ORDER BY deviceid,uploadtime ) " \
        "WHERE charg_s_c IN (1,-1) ORDER BY deviceid,uploadtime "
    '''
    sql="SELECT deviceid, uploadtime, charg_s_c, socp, d_soc " \
        "FROM  " \
        "(SELECT deviceid, uploadtime, runningDifference(charg_s) AS charg_s_c, " \
            "socp, runningDifference(socp) AS d_soc " \
            "FROM  " \
                "(SELECT deviceid, uploadtime, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, "\
                    "if(soc<0,0,soc) AS socp  " \
                    "FROM ods.rtm_reissue_history " \
                    "WHERE deviceid like 'LSVAX60%' and vehiclestatus!='ERROR' and chargingstatus!='INVALID' and chargingstatus!='ERROR' and cocesprotemp1!='NULL' " \
                    "ORDER BY deviceid, uploadtime ) " \
            "ORDER BY deviceid,uploadtime ) " \
        "WHERE charg_s_c IN (1,-1) ORDER BY deviceid,uploadtime "
    # print(sql)
    aus=client.execute(sql) 
    #aus=[0 vin  1 time  2充电变化标志位  3 soc   4 d_soc ]
    #df=pd.DataFrame(aus)
    #df.to_csv('new.csv')
    all_charge = []    #all_charge=[0vin,1time_start,2time_end]
    #temp=[]          #temp=[0soc_start,1soc_end,2mile_start,3end_mile ]
    i=1
    while i < len(aus):
        s = aus[i-1] #i-1时刻是开始充电，i是结束充电时刻
        e = aus[i]
        d = e[1]-s[1] #充电时长
        if s[0] == e[0] and s[2] == 1 and e[2] == -1 and abs(s[4]) < 6 and abs(e[4]) < 6 and d.seconds/60 > 5 :
            #是同一辆车  #开始和结束SOC跳变需小于5% #充电时间大于5分钟
            all_charge.append([s[0],s[1],e[1]])
            #all_charge=[0vin,1time_start,2time_end]
        i+=1
    print(len(all_charge))
    df=pd.DataFrame(all_charge)
    df.to_csv('LSVAX60.csv')




sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list, " \
        "if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, "\
        "totalcurrent*totalvolt/1000 AS P " \
    "SELECT deviceid, uploadtime, -P, if(soc<0,0,soc), " \
        "multiIf(P<-7.5,'DC',P>=-7.5 and P<-4,'mode3_1',P>=-4 and P<-2,'mode3_2',P>=-2 and P<0,'mode2','discharging') as charg_mode, " \
        "arrayReduce('max',temp_list), -totalcurrent, " \
        "cast(vehiclespeed, 'Float32') AS v, cast(lg, 'Float32') AS longitude, cast(lat, 'Float32') AS latitude " \
    "FROM ods.rtm_reissue_history " \
    "WHERE deviceid like 'LSVAX60%' and charg_s==1 and vehiclestatus!='ERROR' and chargingstatus!='INVALID' and chargingstatus!='ERROR' and cocesprotemp1!='NULL'" \
    "ORDER BY deviceid, uploadtime " 
aus=client.execute(sql) 
#aus=[i][0vin, 1time, 2 BMS_power 3soc 4charg_mode 5max_temp  8current, 9 v , 10longitude, 11 latitude]



all_charge = pd.read_csv('LSVAX60.csv',index_col=0,header=0)
print(all_charge)
#print(all_charge.shape[0])
#print(all_charge.shape)
#print(all_charge.iloc[1,1])


ss, ee = [], []#用于存放aus中每段充电开始的index 和每次充电结束的index
i, j = 0, 0 #j为all_charge的index      i 为aus的index
mode1 = []#根据功率判断的充电模式
mode2 =[] #根据电流级温度判断充电模式

for j in range(all_charge.shape[0]):#根据all_charge中每次充电开始时间，找到aus中每次充电开始-结束时间
    vin = all_charge.iloc[j,0]
    start_time = all_charge.iloc[j,1]
    end_time = all_charge.iloc[j,2]
    if ee == []: 
        i = 0
    else:
        i = ee[-1]#每次i从上次充电结束的时候开始搜索

    ff = 0

    while aus[i][0] <= vin and i < len(aus)-1: #如果vin码已经搜索到下一辆车，循环停止#如果找到了，ff=1循环停止
        if aus[i][0] == vin and aus[i][1] == start_time:
            #找到aus中vin码和时间与all_charge中开始时间完全相同的数据条，index保存在ss中
            ss.append(i)
            ff = 1
            while aus[i][0] == vin and aus[i][1] < end_time and i < len(aus)-1:
                if (aus[i+1][1] > end_time and aus[i+1][0] == vin) or aus[i+1][0] > vin:
                    ee.append(i)
                    ff = 2
                    break
                else:
                    i+=1
            if ff==1:
                ss.pop()
            else:
                break
        else:
            i+=1
    if ff==2:
        print(j,i)

print(len(ss))
print(len(ee))

z=1