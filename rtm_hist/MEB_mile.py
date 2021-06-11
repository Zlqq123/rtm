import sys
sys.path.append(".")
sys.path.append("..")#sys.path.append("..")的意思是增加搜索的路径，..代表上一个目录层级

import xlsxwriter
import time
from datetime import datetime
import numpy as np
import pandas as pd

from rtm_hist import hist_func_np
from en_client import en_client
client=en_client()




def Meb_mileage(date_range):
    a=date_range[0]+" 00:00:00"
    b=date_range[1]+" 23:59:59"

    sql="SELECT deviceid, uploadtime, charg_s_c, socp, d_soc, acc  FROM( " \
        "SELECT deviceid, uploadtime, runningDifference(charg_s) as charg_s_c, socp, runningDifference(socp) as d_soc, cast(accmiles,'Float32') as acc " \
        "FROM ( "\
        "SELECT deviceid, uploadtime, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, " \
        "accmiles, if(soc<0,0,soc) AS socp " \
        "FROM ods.rtm_details_v2 " \
        "WHERE deviceid like 'LSVUB%' AND uploadtime BETWEEN '"+a+"' AND '"+b+"' " \
        "ORDER BY deviceid, uploadtime ) ORDER BY deviceid,uploadtime ) " \
        "where charg_s_c IN (1,-1)  ORDER BY deviceid,uploadtime "
    aus=client.execute(sql)
    #aus=[0 vin  1 时间  2充电变化标志位  3 soc   4 d_soc  5 mileage ]
    df=pd.DataFrame(aus)
    #df.to_csv('new.csv')
    all_drive=[]
    count_1=0#基数多少次行驶前数据丢失
    count_2=0#计数行驶后数据丢失
    count_12=0#行驶前，行驶后均数据丢失
    i=1
    while i<len(aus):
        if aus[i][0]==aus[i-1][0] and aus[i-1][2]==-1 and aus[i][2]==1:#i-1时刻是开始行驶，i是结束行驶时刻
            start_d_soc=abs(aus[i-1][4])
            end_d_soc=abs(aus[i][4])
            if start_d_soc>5 or end_d_soc>5:
                if start_d_soc>5:
                    count_1+=1
                if end_d_soc>5:
                    count_2+=1
                if start_d_soc>5 and end_d_soc>5:
                    count_12+=1
            elif aus[i-1][3]>aus[i][3] and aus[i-1][5]<aus[i][5]:# 行驶过程中SOC减少，里程增加
                all_drive.append([aus[i][0],aus[i-1][1],aus[i][1],aus[i-1][3],aus[i][3],aus[i-1][5],aus[i][5]])
                #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
            i+=2
        else:
            i+=1
    l1=len(all_drive)+count_1+count_2-count_12


    soc_r=[]
    mile_r=[]
    mile_r_c=[]
    Energy_consump=[]

    for i,a in enumerate(all_drive):
        soc_r.append(a[3]-a[4])
        mile_r.append(a[6]-a[5])

    l2=len(all_drive)
    print("------mile perCharging analysis---------\r\n")
    print("原始行驶次数："+str(l1)+"\r\n")
    print("充电前数据丢失次数："+str(count_1)+"占比："+str(round(count_1/l1*100,2))+"%\r\n")
    print("充电后数据丢失次数："+str(count_2)+"占比："+str(round(count_2/l1*100,2))+"%\r\n")
    print("充电前后数据均丢失次数："+str(count_12)+"占比："+str(round(count_12/l1*100,2))+"%\r\n")
    print("处理后行驶次数："+str(l2)+"\r\n")

    mile_r=np.array(mile_r)


    freq = hist_func_np.hist_con(mile_r,range(0,800,50))
    re1=pd.DataFrame(freq[1])
    re1.index=freq[0]
    re1.columns=['频数']
    re2 =  hist_func_np.box_hist(mile_r,'每次充电间隔里程[km]')

    charging_energy=82 #ID4x 82kWh 冲入电量88kWh,来源CLTC充电测试平均值
        
    for a in all_drive:
        #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
        if (a[6]-a[5])>10 and (a[3]-a[4])>5:
            Energy_consump.append(charging_energy*(a[3]-a[4])/(a[6]-a[5]))
            mile_r_c.append((a[6]-a[5])/(a[3]-a[4])*100)

    mile_r_c=np.array(mile_r_c)
    Energy_consump = np.array(Energy_consump)

    freq = hist_func_np.hist_con(mile_r_c,range(0,800,50))
    re3 = pd.DataFrame(freq[1])
    re3.index = freq[0]
    re3.columns = ['频数']
    re4 = hist_func_np.box_hist(mile_r_c,'折算纯电续驶里程[km]')


    freq = hist_func_np.hist_con(Energy_consump,[0,13,14,15,16,17,18,19,20,50])
    re5=pd.DataFrame(freq[1])
    re5.index=freq[0]
    re5.columns=['频数']
    re6 = hist_func_np.box_hist(Energy_consump,'折算电耗[kWh/100km]')

    return re1, re2, re3, re4, re5, re6

print('<<<<<<<<<<<<<<<二月>>>>>>>>>>>>>>>>>')
x1=Meb_mileage(['2021-02-01','2021-02-28'])
print(x1)
print('<<<<<<<<<<<<<<<三月>>>>>>>>>>>>>>>>>')
x2=Meb_mileage(['2021-03-01','2021-03-31'])
print(x2)
print('<<<<<<<<<<<<<<<四月>>>>>>>>>>>>>>>>>')
x3=Meb_mileage(['2021-04-01','2021-04-30'])
print(x3)