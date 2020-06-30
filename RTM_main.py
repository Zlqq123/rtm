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
from rtm.charge_ana1 import RtmAna

def print_in_excel(aus,s1):
    workbook = xlsxwriter.Workbook(s1)
    worksheet = workbook.add_worksheet("sheet1")
    for i in range(len(aus)):
        for j in range(len(aus[0])):
            worksheet.write(i+1,j,aus[i][j])
    workbook.close()


client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')
path='D:/03RTM/ALL_RTM_data/0629/'

start=time.time()
l1=RtmAna(path,"lavida",client)
l1.Charge_summary()
l1.drive_summary()
dt=time.time()-start
file=open(path+"lavida"+"_log.txt",'a')
file.write("------------------\r\n")
file.write("running cost"+ str(round(dt,2))+"s \r\n")
file.close()
print("lavida end-----------------")

start=time.time()
l1=RtmAna(path,"tiguan",client)
l1.Charge_summary()
l1.drive_summary()
dt=time.time()-start
file=open(path+"tiguan"+"_log.txt",'a')
file.write("------------------\r\n")
file.write("running cost"+ str(round(dt,2))+"s \r\n")
file.close()
print("-----------------")

start=time.time()
l1=RtmAna(path,"passat",client)
l1.Charge_summary()
l1.drive_summary()
dt=time.time()-start
file=open(path+"passat"+"_log.txt",'a')
file.write("------------------\r\n")
file.write("running cost"+ str(round(dt,2))+"s \r\n")
file.close()


l1=RtmAna(path,"lavida",client)#charging_lavida
workbook = xlsxwriter.Workbook(path+"lavida"+"_append"+".xlsx")
l1.hourly_mileage(workbook)
l1.percharge_mile(workbook)
l1.BMS(workbook)
workbook.close()

l1=RtmAna(path,"tiguan",client)#charging_lavida
workbook = xlsxwriter.Workbook(path+"Tiguan"+"_append"+".xlsx")
l1.hourly_mileage(workbook)
l1.BMS(workbook)
workbook.close()

l1=RtmAna(path,"passat",client)#charging_lavida
workbook = xlsxwriter.Workbook(path+"Passat"+"_append"+".xlsx")
l1.hourly_mileage(workbook)
l1.BMS(workbook)
workbook.close()



NEDC_path='D:/11test/01BEV-NEDC/1-lavida 53Ah/14 LBE734/vp426/D/'
NEDC_D=Rangetest('LBE734_NEDC_D',NEDC_path,'NEDC')
#NEDC_D.cut_range()
#range_dyno=295.9
#E_AC=38.055
#NEDC_D.sum_to_excel_NEDC(range_dyno,E_AC)
#NEDC_D.plot_v()




'''
client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')


sql = 'select count(distinct deviceid) from en.rtm_vds' 
sql = 'select uniq(deviceid) from en.rtm_vds' 
aus=client.execute(sql)
#输出车辆个数，上面两个表述等价

sql0 = 'select * from en.rtm_vds limit 10' 
aus=client.execute(sql0)
#选取前十条记录
sql1 ='desc en.rtm_vds'
#查看表结构
sql3 = 'select distinct deviceid from en.rtm_vds' 
#distinct 从 "deviceid" 列中仅选取唯一不同的值
sql24="select deviceid,min(uploadtime),max(uploadtime) from rtm_vds group by deviceid"  
#选出每辆车记录结束时间
sql32="SELECT deviceid,toDate(uploadtime), min(CAST(accmiles,'float')), max(CAST(accmiles,'float')) " \
    "from rtm_vds where deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 group by deviceid, toDate(uploadtime)"
#每日行驶里程统计
#toDate(datetime)

#Checks whether a string matches a simple regular expression.
#The regular expression can contain the metasymbols % and _.
#% indicates any quantity of any bytes (including zero characters).
#_ indicates any one byte.
#Use the backslash (\) for escaping metasymbols. See the note on escaping in the description of the ‘match’ function.

sql="SELECT deviceid,uploadtime,soc,runningDifference(soc) from (SELECT deviceid,uploadtime,soc from en.rtm_vds where cocesprotemp1!='NULL' " \
    "and deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 ORDER BY deviceid,uploadtime)"
input_data1=client.execute(sql)
#第n行runningDifference(变量)=第n行变量值-第n-1行变量值
#runningDifference(变量) 需要在子查询中查询
#SLELCT 变量1，变量2.。。runningDifference(变量) from（SELECT 变量1，变量2.。。 FROM table ORDER BY 变量1，变量2）

sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list SELECT arrayReduce('sum',temp_list)/length(temp_list) " \
    "from en.rtm_vds where chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') AND cocesprotemp1!='NULL' " \
    "and deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 ORDER BY deviceid,uploadtime"

#splitByChar(',',字符串)将字符串用','分割，得到一个字符串数组
#cast(字符串数组,'Array(Int8)')将字符串数组转化成整形数组
# with 变量1 as 别名 将变量1命名为别名
# arrayReduce('sum',整形/浮点类型数组)数组求和
#arrayReduce('max',整形/浮点类型数组)求数组中的最大值
#length(数组)求数组长度

sql="SELECT deviceid,uploadtime,soc,acc,chargingstatus,char_s,runningDifference(char_s) AS delta " \
    "from (SELECT deviceid,uploadtime,soc,chargingstatus,CAST(accmiles,'float') as acc,if(chargingstatus=='NO_CHARGING',7,8) as char_s from en.rtm_vds " \
    "where cocesprotemp1!='NULL' and deviceid like 'LSVU%' AND acc>100 ORDER BY deviceid,uploadtime) " \
    "where delta==1 or delta==-1"
#if(chargingstatus=='NO_CHARGING',7,8)
#if(condition, then, else)


sql29="CREATE TABLE Lavida AS SELECT * from rtm_vds where deviceid like 'LSVA%' AND CAST(accmiles,'float')>100"
#新建表# 权限不支持新建表
#"Sample 0.1 " \table doesn't support sampling
sql0 = 'select * from en.rtm_vds limit 10' #选取前十条记录
sql1 ='desc en.rtm_vds' #查看表结构
sql2 = 'select uploadtime,deviceid,operationmode,vehiclespeed,accmiles,soc from en.rtm_vds limit 10' #查看前十条指定列的记录
sql3 = 'select distinct deviceid from en.rtm_vds' #distinct 从 "deviceid" 列中仅选取唯一不同的值
sql24="select deviceid,min(uploadtime),max(uploadtime) from rtm_vds group by deviceid"  #选出每辆车记录结束时间


#查看所有车辆VIN码,结果一共有38299辆车
sql4 = "select uploadtime,deviceid,operationmode,vehiclespeed,accmiles,soc from en.rtm_vds where deviceid='LSVCY6C44KN188693'"
#导出指定车辆VIN码的所有数据
sql5 = "select distinct deviceid from en.rtm_vds where deviceid like 'LSVA%'" #从 "deviceid" 列中仅选取唯一不同的值,条件是"deviceid"以LSVA开头
sql6 = "select distinct deviceid from en.rtm_vds where deviceid like 'LSVC%'" 
sql7 = "select distinct deviceid from en.rtm_vds where deviceid like 'LSVU%'" 
#查看所有车辆VIN码以LSVA开头,结果一共有4317辆车lavida；  LSVC开头passat 21069辆  LSVU开头 Tiguan 12911辆
sql8 = "select distinct deviceid from en.rtm_vds where deviceid not like 'LSVU%' and deviceid not like 'LSVC%' and deviceid not like 'LSVA%'" 
#从 "deviceid" 列中仅选取唯一不同的值,条件是"deviceid"均不以LSVA/LSVU/LSVC开头
#结果两辆车，VIN码为：[('LFVNB9AU1J5800003',), ('TESTK2BM90312N002',)]分别有84条记录，有2条记录
sql9 = "select * from en.rtm_vds where deviceid='LFVNB9AU1J5800003'"
sql10 = 'SELECT count(DISTINCT deviceid) FROM en.rtm_vds where cast(accmiles as float)>100'#筛选所有累计行驶里程大于100的车,结果有32766辆
sql11 = "SELECT distinct deviceid FROM en.rtm_vds where cast(accmiles as float)>100 and deviceid like 'LSVUZ60%'"
#tiguan L PHEV SVW6471APV  LSVUZ60T..2.....     12314辆
sql12 = "SELECT distinct deviceid FROM en.rtm_vds where cast(accmiles as float)>100 and deviceid like 'LSVUY60%'"
#tiguan L PHEV SVW6472APV  LSVUY60T..2.....     0辆
sql13 = "SELECT distinct deviceid FROM en.rtm_vds where cast(accmiles as float)>100 and deviceid like 'LSVUZ6B%'"
#Tharu BEV SVW6451AEV  LSVUZ6BZ..N.....     0辆 
sql14 = "SELECT distinct deviceid FROM en.rtm_vds WHERE deviceid LIKE 'LSVC%' AND CAST(accmiles,'float')>100" 
#Passat PHEV 18604 辆
sql15 = "SELECT distinct deviceid FROM en.rtm_vds where cast(accmiles as float)>100 and deviceid like 'LSVA%'"
#Lavida BEV 1846 辆


sql26="SELECT vehiclespeed from rtm_vds where cast(accmiles as float)>100 and cast(vehiclespeed as float)>0.09 and deviceid like 'LSVC%'"
sql26="SELECT vehiclespeed from rtm_vds where cast(accmiles as float)>100 and cast(vehiclespeed as float)>0.09 and deviceid like 'LSVC%'"
aus=client.execute(sql26)
#print(aus)

v=[]
for i in range(len(aus)):
    a=list(aus[i])
    v.append(float(a[0]))
a=np.array(v)
v1=a.reshape(a.shape[0],1)
with open ("velocity_P.csv", "w", newline='') as f : 
    f_csv = csv.writer(f)
    f_csv.writerow(['velocity']) 
    f_csv.writerows([v1]) 

sql1="SELECT deviceid,uploadtime,delta,soc,d_soc,acc,d_mile,ch_mode " \
    "FROM (SELECT deviceid,uploadtime,chargingstatus,runningDifference(char_s) AS delta,soc, runningDifference(soc) AS d_soc,acc, runningDifference(acc) as d_mile,ch_mode " \
    "from (SELECT deviceid,uploadtime,soc,chargingstatus,CAST(accmiles,'float') as acc,if(chargingstatus=='NO_CHARGING',7,8) as char_s, " \
    "multiIf(totalcurrent<=-20,'DC',totalcurrent<=-10 and totalcurrent>-20,'mode3_1',totalcurrent<=-5 and totalcurrent>-10,'mode3_2',totalcurrent<0 and totalcurrent>-5,'mode2','discharging') as ch_mode " \
    "from en.rtm_vds " \
    "where deviceid='LSVAX60E0K2016749' AND acc>100 ORDER BY uploadtime)) " \
    "WHERE delta in (1,-1)"
#and d_soc<5
aus=client.execute(sql1)
workbook = xlsxwriter.Workbook("test1.xlsx")
worksheet = workbook.add_worksheet("sheet1_lavida")
for i in range(len(aus)):
    for j in range(len(aus[0])):
        worksheet.write(i+1,j,aus[i][j])
workbook.close()


'''
a=1