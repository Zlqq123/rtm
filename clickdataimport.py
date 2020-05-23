from clickhouse_driver import Client
import xlsxwriter
import time
import csv
import numpy as np
import hist_func
import RTM_ana

#import xlrd



client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')

sql0 = 'select * from en.rtm_vds limit 10' #选取前十条记录
sql1 ='desc en.rtm_vds' #查看表结构
aus=client.execute(sql0)



#"Sample 0.1 " \table doesn't support sampling

#for Lavida
# e_motor working piont电机工作点分布

sql35="SELECT cast(emspeed,'float'),cast(emtq,'float') " \
    "from en.rtm_vds " \
    "where cast(vehiclespeed,'float')>0 " \
    "and deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 "
aus=client.execute(sql35)
speed=[]
torq=[]
for value in aus:
    speed.append(value[0])
    torq.append(value[1])
del aus
gc.collect()
workbook = xlsxwriter.Workbook(filepath+"LE_working_point_lavida.xlsx")
RTM_ana.hist_2con_show(workbook,['sheet1'],speed,range(-5000,13500,500),torq,range(-300,400,50))
workbook.close()
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


workbook = xlsxwriter.Workbook(filepath+"BMS_working_point_lavida.xlsx")
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

sql36="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
    "SElECT soc,arrayReduce('sum',temp_list)/length(temp_list),totalcurrent*totalvolt/1000 " \
    "FROM en.rtm_vds " \
    "WHERE chargingstatus='NO_CHARGING' and totalcurrent>0 and cocesprotemp1!='NULL' " \
    "AND deviceid like 'LSVA%' AND CAST(accmiles,'float')>100"

sql35="SElECT soc,cocesprotemp1,totalcurrent,totalvolt " \
    "FROM en.rtm_vds " \
    "where chargingstatus='NO_CHARGING' and totalcurrent>0 " \
    "and deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 "
aus=client.execute(sql35)


#电池工作点


sql32="SELECT CAST(accmiles,'float') from rtm_vds Where deviceid='LSVAY60E3K2011395'"
aus=client.execute(sql32)
print(max(aus))
print(min(aus))

sql31="SELECT CAST(vehiclespeed,'float') from rtm_vds Where deviceid like 'LSVU%' AND CAST(accmiles,'float')>100 and CAST(vehiclespeed,'float')>=0.1 order by CAST(vehiclespeed,'float')"
aus=client.execute(sql31)
print(aus[-1])
print(aus[int(len(aus)/2)])


sql="SELECT uploadtime from en.rtm_vds limit 10"
aus=client.execute(sql)
a=aus[1]
b=a[0]
b1=aus[3][0]
c=b.hour
d=b1-b
e=d.seconds/60

#sql33="SELECT"
#绝缘阻值变化范围

#充电起始时间和SOC，每次充电间隔里程，
#充电模式，充电过程中电池温度范围,充电时长
sql33="SELECT deviceid,uploadtime,toHour(uploadtime),soc,accmiles,chargingstatus,totalcurrent,mxtemp,mitemp " \
    "from en.rtm_vds " \
    "where (chargingstatus='CHARGING_STOPPED' or chargingstatus='CHARGING_FINISH') " \
    "and deviceid like 'LSVC%' AND CAST(accmiles,'float')>100 " \
    "ORDER BY deviceid,uploadtime"
aus=client.execute(sql33)

[charge_start,charge_end,mile,current]=RTM_ana.per_charge(aus,'lavida')

a=charge_end[0][1]-charge_start[0][1]
print(a.seconds/3600)

[charge_start,charge_end,charge_cut]=RTM_ana.charge1(aus)





##速度分布统计##驾驶模式统计
sql31="SELECT vehiclespeed,operationmode,gp,soc from rtm_vds Where deviceid like 'LSVC%' AND CAST(accmiles,'float')>100 and CAST(vehiclespeed,'float')>=0.1"
aus=client.execute(sql31)

v,mode,SOC=[],[],[]
for i in range(len(aus)):
    a=float(aus[i][0])
    b=aus[i][1]
    c=aus[i][3]
    v.append(a)
    mode.append(b)
    SOC.append(c)

[result,res_mode_v]=hist_2(v,mode,[0,10,20,30,40,50,60,70,80,90,100,110,120,210])
[result,res_mode_SOC]=hist_2(SOC,mode,[0,2,10,20,101])

freq_mode={}
for x in mode:
    freq_mode[x]=freq_mode.get(x,0)+1


[v_cut,feq_v]=hist(v,[0,10,160])
print(max(v))
print(np.mean(np.array(v)))
print(np.median(np.array(v)))



sql31="SELECT vehiclespeed,operationmode,gp from rtm_vds Where deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 and CAST(vehiclespeed,'float')>=0.1"
aus=client.execute(sql31)

v_LSVA,mode_LSVA=[],[]
for i in range(len(aus)):
    a=float(aus[i][0])
    b=aus[i][1]
    v_LSVA.append(a)
    mode_LSVA.append(b)

print(max(v_LSVA))
[v_cut,feq_v_lavida]=hist(v_LSVA,[0,10,160])
print(np.mean(np.array(v_LSVA)))
print(np.median(np.array(v_LSVA)))

#每日行驶里程统计
sql32="SELECT deviceid,toDate(uploadtime), min(CAST(accmiles,'float')), max(CAST(accmiles,'float')) " \
    "from rtm_vds where deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 group by deviceid, toDate(uploadtime)"
aus=client.execute(sql32)
mileage_LSVA=[]
for i in range(len(aus)):
    a=float(aus[i][2])
    b=float(aus[i][3])
    mileage_LSVA.append(b-a)

sql32="SELECT deviceid,toDate(uploadtime), min(CAST(accmiles,'float')), max(CAST(accmiles,'float')) from rtm_vds where deviceid like 'LSVC%' AND CAST(accmiles,'float')>100 group by deviceid, toDate(uploadtime)"
aus=client.execute(sql32)
mileage_LSVC=[]
for i in range(len(aus)):
    a=float(aus[i][2])
    b=float(aus[i][3])
    mileage_LSVC.append(b-a)

sql32="SELECT deviceid,toDate(uploadtime), min(CAST(accmiles,'float')), max(CAST(accmiles,'float')) from rtm_vds where deviceid like 'LSVU%' AND CAST(accmiles,'float')>100 group by deviceid, toDate(uploadtime)"
aus=client.execute(sql32)
mileage_LSVU=[]
for i in range(len(aus)):
    a=float(aus[i][2])
    b=float(aus[i][3])
    mileage_LSVU.append(b-a)

[day_mile,feq_mile_lavida]=hist_Custom_interval(mileage_LSVA,[0,10,20,30,40,50,60,80,100,150,200,250,300,500,800])
[day_mile,feq_mile_passat]=hist_Custom_interval(mileage_LSVC,[0,10,20,30,40,50,60,80,100,150,200,250,300,500,800])
[day_mile,feq_mile_tiguan]=hist_Custom_interval(mileage_LSVU,[0,10,20,30,40,50,60,80,100,150,200,250,300,500,800])

print("lavida每天行驶里程")
print(np.mean(np.array(mileage_LSVA)))
print(np.median(np.array(mileage_LSVA)))
print("passat每天行驶里程")
print(np.mean(np.array(mileage_LSVC)))
print(np.median(np.array(mileage_LSVC)))
print("tiguan每天行驶里程")
print(np.mean(np.array(mileage_LSVU)))
print(np.median(np.array(mileage_LSVU)))


#新建表
sql29="CREATE TABLE Lavida AS SELECT * from rtm_vds where deviceid like 'LSVA%' AND CAST(accmiles,'float')>100"
sql30="SELECT uploaddate,uploadhour from en.lavida"
sql31="SELECT count(DISTINCT deviceid) from en.lavida"
client.execute(sql29)
aus=client.execute(sql31)
print(aus)


sql5 = "select distinct deviceid from en.rtm_vds where deviceid like 'LSVA%' AND CAST(accmiles,'float')>100"
lavida_vin=client.execute(sql5)
data_ss=[]
data_ee=[]
for i in range(200):
    a="".join(lavida_vin[i])
    sql20="SELECT min(uploadtime) FROM en.rtm_vds WHERE deviceid="+"'"+a+"'"
    sql21="SELECT max(uploadtime) FROM en.rtm_vds WHERE deviceid="+"'"+a+"'"
    date_s=client.execute(sql20)
    date_e=client.execute(sql21)
    data_ss.append(date_s[0])
    data_ee.append(date_e[0])



aus1=client.execute(sql21)
print(aus1)



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




#导出数据表结构，和两个例子
sql0 = 'select * from en.rtm_vds limit 10' 
sql1 ='desc en.rtm_vds' 
sam= client.execute(sql0)
index=client.execute(sql1)

workbook = xlsxwriter.Workbook('new_excel.xlsx')     
worksheet = workbook.add_worksheet('sheet1')
a=index[0][0]
for i in range(b1):
    a=index[i][0]
    worksheet.write(i+1,0,a)
    a=index[i][1]
    worksheet.write(i+1,1,a)
    a=index[i][4]
    worksheet.write(i+1,2,a)
    a=sam[0][i]
    worksheet.write(i+1,3,a)
    a=sam[5][i]
    worksheet.write(i+1,4,a)

workbook.close()


#导出lavida 所有车的里程，VIN码,用时971s
time_s=time.time()
workbook = xlsxwriter.Workbook("mile.xlsx")    
worksheet = workbook.add_worksheet('Lavida BEV')
sql5 = "select distinct deviceid from en.rtm_vds where deviceid like 'LSVA%'"
lavida_vin=client.execute(sql5)
mile_lavida=[]
for i in range(len(lavida_vin)):
    a="".join(lavida_vin[i])
    sql19="SELECT max(cast(accmiles as float)) FROM en.rtm_vds WHERE deviceid="+"'"+a+"'"
    mile1=client.execute(sql19)
    b=list(mile1[0])
    mile_lavida.append(b[0])
    worksheet.write(i+1,0,a)
    worksheet.write(i+1,1,b[0])

workbook.close()
time_1=time.time()
print("time",time_1-time_s)

#导出passat 所有车的里程，VIN码 用时4715s
time_s=time.time()
sql6 = "select distinct deviceid from en.rtm_vds where deviceid like 'LSVC%'" 
workbook = xlsxwriter.Workbook("mile_p.xlsx")    
worksheet = workbook.add_worksheet('Passat PHEV')
passat_vin=client.execute(sql6)
for i in range(len(passat_vin)):
    a="".join(passat_vin[i])
    sql19="SELECT max(cast(accmiles as float)) FROM en.rtm_vds WHERE deviceid="+"'"+a+"'"
    mile1=client.execute(sql19)
    b=list(mile1[0])
    worksheet.write(i+1,0,a)
    worksheet.write(i+1,1,b[0])
    if i%1000==0:
        print(i)

workbook.close()
time_1=time.time()
print("time",time_1-time_s)

#导出tiguan 所有车的里程，VIN码,用时2829s
time_s=time.time()
sql7 = "select distinct deviceid from en.rtm_vds where deviceid like 'LSVU%'"
workbook = xlsxwriter.Workbook("mile_t.xlsx")  
worksheet = workbook.add_worksheet('Tiguan L PHEV')
tiguan_vin=client.execute(sql7)
for i in range(len(tiguan_vin)):
    a="".join(tiguan_vin[i])
    sql19="SELECT max(cast(accmiles as float)) FROM en.rtm_vds WHERE deviceid="+"'"+a+"'"
    mile1=client.execute(sql19)
    b=list(mile1[0])
    worksheet.write(i+1,0,a)
    worksheet.write(i+1,1,b[0])
workbook.close()
time_1=time.time()
print("time",time_1-time_s)

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


a=1