from clickhouse_driver import Client
import xlsxwriter
import time
import csv
import numpy as np
import RTM_ana
import gc
import hist_func

filepath("D:/03RTM/ALL_RTM_data/0509/")

client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')

#BMS working piont
sql35="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
    "SElECT soc,arrayReduce('sum',temp_list)/length(temp_list),totalcurrent*totalvolt/1000 " \
    "FROM en.rtm_vds " \
    "WHERE chargingstatus='NO_CHARGING' and totalcurrent>0 and cocesprotemp1!='NULL' " \
    "AND deviceid like 'LSVA%' AND CAST(accmiles,'float')>100"
aus=client.execute(sql35)

soc,temp_av,pow_bms=[],[],[]
for value in aus:
    soc.append(value[0])
    temp_av.append(value[1])
    pow_bms.append(value[2])


workbook = xlsxwriter.Workbook("BMS_working_point_lavida.xlsx")
RTM_ana.hist_2con_show(workbook,['discharging'],soc,range(0,115,5),temp_av,range(-10,55,5))

soc,temp_av,pow_bms=[],[],[]
sql35="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
    "SElECT soc,arrayReduce('sum',temp_list)/length(temp_list),totalcurrent*totalvolt/1000 " \
    "FROM en.rtm_vds " \
    "where chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') AND totalcurrent<0 AND cocesprotemp1!='NULL' " \
    "and deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 "
aus=client.execute(sql35)

for value in aus:
    soc.append(value[0])
    temp_av.append(value[1])
    pow_bms.append(value[2])

RTM_ana.hist_2con_show(workbook,['charging'],soc,range(0,115,5),temp_av,range(-10,55,5))
workbook.close()

#电机工作点分布
sql35="SELECT cast(emspeed,'float'),cast(emtq,'float') " \
    "from en.rtm_vds " \
    "where cast(emtq,'float')>0 and cast(emspeed,'float')>0 " \
    "and deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 "
aus=client.execute(sql35)
speed=[]
torq=[]
for value in aus:
    speed.append(value[0])
    torq.append(value[1])
del aus
gc.collect()
workbook = xlsxwriter.Workbook("LE_working_point_lavida.xlsx")
RTM_ana.hist_2con_show(workbook,['speed>0&t>0'],speed,range(0,13500,500),torq,range(0,400,50))

speed=[]
torq=[]
sql35="SELECT cast(emspeed,'float'),cast(emtq,'float') " \
    "from en.rtm_vds " \
    "where cast(emtq,'float')<0 and cast(emspeed,'float')>0 " \
    "and deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 "
aus=client.execute(sql35)
for value in aus:
    speed.append(value[0])
    torq.append(value[1])
del aus
gc.collect()
RTM_ana.hist_2con_show(workbook,['speed>0&t<0'],speed,range(0,13500,500),torq,range(-300,50,50))



workbook.close()


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