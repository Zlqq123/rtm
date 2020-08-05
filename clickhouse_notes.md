##############
sql="SELECT uploadtime FROM en.rtm_6_2th WHERE deviceid='LSVAX60E0K2016511' AND uploadtime between toDateTime('2020-06-01 19:12:04') AND toDateTime('2020-06-02 14:12:95') ORDER BY uploadtime "

sql="SELECT cast(runningDifference(uploadtime),'Int') FROM (SELECT deviceid, uploadtime FROM en.rtm_data_june order by deviceid, uploadtime) limit 10000"

sql="desc en.rtm_6_2th"

sql="SELECT max(CAST(accmiles,'float')),min(CAST(accmiles,'float')),cast(max(CAST(accmiles,'float'))-min(CAST(accmiles,'float')),'UInt32') "\
    "FROM en.rtm_data_june INNER JOIN en.vehicle_vin on rtm_data_june.deviceid=vehicle_vin.deviceid"
sql="DROP TABLE en.vehicle_vin"
#删除表
sql="INSERT INTO en.vehicle_vin (deviceid,project,city,province,region,user_typ) FORMAT Values ('LSVUZ60T1J2179379','Tiguan L PHEV C5','广州市','GuangDong','MidSouth','Private')"
#click house 没有update语句 没有delete
sql = 'select count(distinct deviceid) from en.rtm_vds' 
sql = 'select uniq(deviceid) from en.rtm_vds' 
#输出车辆个数，上面两个表述等价
sql="CREATE TABLE IF NOT EXISTS en.vehicle_vin ( deviceid String, project String, city String, province String, region String, mileage UInt32, user_type String ) ENGINE = MergeTree() ORDER BY deviceid"
#新建表，默认deviceid为主键
'''
CREATE TABLE [IF NOT EXISTS] [db.]table_name [ON CLUSTER cluster]
(
    name1 [type1] [DEFAULT|MATERIALIZED|ALIAS expr1] [TTL expr1],
    name2 [type2] [DEFAULT|MATERIALIZED|ALIAS expr2] [TTL expr2],
    ...
    INDEX index_name1 expr1 TYPE type1(...) GRANULARITY value1,
    INDEX index_name2 expr2 TYPE type2(...) GRANULARITY value2
) ENGINE = MergeTree()
ORDER BY expr
[PARTITION BY expr]
[PRIMARY KEY expr]
[SAMPLE BY expr]
[TTL expr [DELETE|TO DISK 'xxx'|TO VOLUME 'xxx'], ...]
[SETTINGS name=value, ...]
'''
sql="ALTER TABLE en.vehicle_vin ADD COLUMN user_typ String"
sql="ALTER TABLE en.vehicle_vin ADD COLUMN d_mile UInt32 AFTER mileage"
#更新表
'''
ALTER TABLE [db].name [ON CLUSTER cluster] ADD|DROP|CLEAR|COMMENT|MODIFY COLUMN ...
ADD COLUMN — Adds a new column to the table.
DROP COLUMN — Deletes the column.
CLEAR COLUMN — Resets column values.
COMMENT COLUMN — Adds a text comment to the column.
MODIFY COLUMN — Changes column’s type, default expression and TTL.
'''
sql0 = 'select * from en.rtm_vds limit 10' 
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


sql26="SELECT vehiclespeed from rtm_vds where cast(accmiles as float)>100 and cast(vehiclespeed as float)>0.09 and deviceid like 'LSVC%'"
sql26="SELECT vehiclespeed from rtm_vds where cast(accmiles as float)>100 and cast(vehiclespeed as float)>0.09 and deviceid like 'LSVC%'"


sql1="SELECT deviceid,uploadtime,delta,soc,d_soc,acc,d_mile,ch_mode " \
    "FROM (SELECT deviceid,uploadtime,chargingstatus,runningDifference(char_s) AS delta,soc, runningDifference(soc) AS d_soc,acc, runningDifference(acc) as d_mile,ch_mode " \
    "from (SELECT deviceid,uploadtime,soc,chargingstatus,CAST(accmiles,'float') as acc,if(chargingstatus=='NO_CHARGING',7,8) as char_s, " \
    "multiIf(totalcurrent<=-20,'DC',totalcurrent<=-10 and totalcurrent>-20,'mode3_1',totalcurrent<=-5 and totalcurrent>-10,'mode3_2',totalcurrent<0 and totalcurrent>-5,'mode2','discharging') as ch_mode " \
    "from en.rtm_vds " \
    "where deviceid='LSVAX60E0K2016749' AND acc>100 ORDER BY uploadtime)) " \
    "WHERE delta in (1,-1)"

