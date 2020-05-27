from clickhouse_driver import Client
#import xlsxwriter
import time
#import csv
#import numpy as np

client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')

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



a=1