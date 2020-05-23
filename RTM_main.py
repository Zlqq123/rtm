import sys
sys.path.append('./')
from clickhouse_driver import Client
import xlsxwriter
import time
import csv
import numpy as np
import gc
import hist_func
from range_test.range_test import Rangetest
from rtm.Charge_ana import RtmCharging

client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')

#mile
l1=RtmCharging("lavida","D:/03RTM/ALL_RTM_data/0509/","lavida",client)#charging_lavida
[soc_s,soc_e,soc_d]=l1.get_soc()
[time_h_s,time_d]=l1.get_time()

count=0
a,b=[],[]
for i,s in enumerate(soc_d):
    if s<0:
        count+=1
        print(i)
        a.append(time_d[i])
        b.append(s)
print(count,len(soc_d),count/len(soc_d))
l1.Charge_summary()

l1.cut_data()
[mile,soc_r,mile1]=l1.get_mile_soc()
[block,mile_freq]=hist_func.hist_con(mile,[0,10,20,30,40,50,60,80,100,150,200,250,300,350,400,1000])
[block,mile_freq1]=hist_func.hist_con(mile1,[0,150,200,210,220,230,240,250,260,270,280,290,300,310,320,330,340,350,400,1000])
print(np.mean(np.array(mile1)))
print(np.median(np.array(mile1)))




[block,mile_freq]=hist_func.hist_con(mile,[0,10,20,30,40,50,60,80,100,150,200,250,300,400,1000])





l1=RtmCharging("lavida","D:/03RTM/ALL_RTM_data/0509/","lavida",client)#charging_lavida
l1.cut_data()
[soc_s,soc_e,soc_d]=l1.get_soc()
[time_h_s,time_d]=l1.get_time()
[temp_s,temp_e,temp_min,temp_max,temp_mean]=l1.get_temp()
charge_mode=l1.get_mode()
[power_max,power_mean]=l1.get_pow()
[mile,soc_r]=l1.get_mile_soc()


NEDC_path='D:/11test/01BEV-NEDC/1-lavida 53Ah/14 LBE734/vp426/D/'
NEDC_D=Rangetest('LBE734_NEDC_D',NEDC_path,'NEDC')
#NEDC_D.cut_range()
#range_dyno=295.9
#E_AC=38.055
#NEDC_D.sum_to_excel_NEDC(range_dyno,E_AC)
#NEDC_D.plot_v()




#计算电机工作效率
sql35="SELECT cast(emspeed,'float')*cast(emtq,'float')/9550, cast(emvolt,'float')*cast(emctlcut,'float')/1000 " \
    "from en.rtm_vds " \
    "where cast(emtq,'float')>0 and cast(emctlcut,'float')>0 " \
    "and deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 "
aus=client.execute(sql35)




sql33="SELECT deviceid,uploadtime,soc,CAST(accmiles,'float'),totalcurrent,CAST(mxtemp,'int'),CAST(mitemp,'int') " \
    "from en.rtm_vds " \
    "where chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') " \
    "and deviceid like 'LSVU%' AND CAST(accmiles,'float')>100 " \
    "ORDER BY deviceid,uploadtime"
aus=client.execute(sql33)


[ss,ee,res]=RTM_ana.charge3(aus,"tiguan")

#Charging start SOC, charging end SOC
#charge start time,charging time
#mileage per charge
#charge mode
# battery temp while charging
sql33="SELECT deviceid,uploadtime,toHour(uploadtime),soc,accmiles,chargingstatus,totalcurrent,mxtemp,mitemp " \
    "from en.rtm_vds " \
    "where (chargingstatus='CHARGING_STOPPED' or chargingstatus='CHARGING_FINISH') " \
    "and deviceid like 'LSVC%' AND CAST(accmiles,'float')>100 " \
    "ORDER BY deviceid,uploadtime"
aus=client.execute(sql33)

freq_mode=RTM_ana.charge2(aus,"passat")


a=1