import sys
sys.path.append('./')
from clickhouse_driver import Client
import xlsxwriter
import time
import csv
import numpy as np
import hist_func
import hist_func_np
from rtm.charge_ana1 import RtmAna


client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')




#sql ="SELECT * from en.rtm_data_june where deviceid=='LSVCY6C4XLN045071'"
sql="select deviceid,min(uploadtime),max(uploadtime),min(CAST(accmiles,'float')), max(CAST(accmiles,'float')) from rtm_data_june group by deviceid"  
#选出每辆车记录结束时间
aus=client.execute(sql)
#print(aus)

def print_in_excel(aus,s1):
    workbook = xlsxwriter.Workbook(s1)
    worksheet = workbook.add_worksheet("sheet1")
    for i in range(len(aus)):
        for j in range(len(aus[0])):
            worksheet.write(i+1,j,aus[i][j])
    workbook.close()

print_in_excel(aus,'mile_june.xlsx')

client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')



aus=client.execute(sql)
print(aus)
#新建表# 权限不支持新建表

sql="SELECT deviceid,uploadtime,soc, runningDifference(soc) AS d_soc,v,vehiclestatus,c2,chargingstatus,c1,acc,P, " \
    "multiIf(P>7.5,'DC',P<=7.5 and P>4,'mode3_1',P<=4 and P>2,'mode3_2',P<=2 and P>0,'mode2','discharging') AS ch_mode " \
    "FROM (SELECT deviceid,uploadtime,soc,CAST(accmiles,'float') AS acc,cast(vehiclespeed,'float') AS v,chargingstatus,if(chargingstatus=='NO_CHARGING',0,1) AS c1," \
    "-totalcurrent*totalvolt/1000 AS P, vehiclestatus, if(vehiclestatus=='STARTED',1,0) as c2 FROM en.rtm_vds " \
    "WHERE deviceid=='LSVCY6C41KN185637' order by uploadtime) " \

#sql="SELECT deviceid,uploadtime,CAST(accmiles,'float'),soc,cast(vehiclespeed,'float'),totalvolt*totalcurrent/1000," \
#    "chargingstatus,if(chargingstatus=='NO_CHARGING',0,1),vehiclestatus,if(vehiclestatus=='STARTED',1,0)" \
#    "from rtm_vds where deviceid=='LSVCY6C42KN185422' order by uploadtime "
aus=client.execute(sql)

print_in_excel(aus,'passat_C6_LSVCY6C41KN185637.xlsx')

path='D:/03RTM/ALL_RTM_data/0629/'
l1=RtmAna("D:/03RTM/ALL_RTM_data/0629/","lavida",client)#charging_lavida
workbook = xlsxwriter.Workbook(path+"lavida"+"_append"+".xlsx")
l1.E_motor_sample(workbook,1/6)
workbook.close()





