import sys
sys.path.append('./')
from clickhouse_driver import Client
from rtm.RTM_ana import print_in_excel
import csv

client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')

sql="desc en.vehicle_vin"
'''
SQL notes
三月数据：en.rtm_vds
六月数据：en.rtm_data_june
六月数据预处理表：en.rtm_6_2th
车辆vin码对应客户信息+里程：en.vehicle_vin 
车辆vin码对应客户信息：en.vehicle_vin1 临时表（已删除）
车辆vin码对应的里程信息：en.vehicle_mile临时表（已删除）
'''
def db_pre_ana(client):
    sql="CREATE TABLE IF NOT EXISTS en.vehicle_mile " \
        "(deviceid String, mile_min Float32,mile_max Float32, d_mileage Float32 ) " \
        "ENGINE = MergeTree() ORDER BY deviceid"
    sql="INSERT INTO en.vehicle_mile " \
        "SELECT deviceid,min(CAST(accmiles,'float')) as m1, max(CAST(accmiles,'float')) as m2, m2-m1 " \
        "FROM en.rtm_data_june GROUP BY deviceid"

    #创建临时表
    sql="CREATE TABLE IF NOT EXISTS en.vehicle_vin1 " \
        "(deviceid String, project String,City String, province String, region String, user_typ String ) " \
        "ENGINE = MergeTree() ORDER BY deviceid"
    aus=client.execute(sql)
    sql ='desc en.vehicle_vin1'
    aus=client.execute(sql)
    print(aus)
    #将地理位置信息写入clickhouse
    filename="C:/Users/zhanglanqing/Desktop/vin_list.csv"
    all_vin=[]
    rawdata_col_define={}
    with open(filename) as f:
        reader=csv.reader(f)
        header_row=next(reader)
        for index, column_header in enumerate(header_row):
            rawdata_col_define[column_header]=index   # find raw data columns title & index {columst title: colunms index}
        for row in reader:
            a=row[rawdata_col_define['VIN']]
            b=row[rawdata_col_define['project']]
            c=row[rawdata_col_define['city']]
            d=row[rawdata_col_define['province']]
            e=row[rawdata_col_define['region']]
            f=row[rawdata_col_define['user_type']]
            all_vin.append("('"+a+"','"+b+"','"+c+"','"+d+"','"+e+"','"+f+"')")
    for i in range(len(all_vin)):
        sql="INSERT INTO en.vehicle_vin1 FORMAT Values "+all_vin[i]
        aus=client.execute(sql)

    sql ='SELECT * FROM en.vehicle_vin1'
    aus=client.execute(sql)
    print(aus)
    #创建表
    sql="CREATE TABLE IF NOT EXISTS en.vehicle_vin " \
        "(deviceid String, project String,City String, province String, region String, user_typ String, mile_min Float32,mile_max Float32, d_mileage Float32 ) " \
        "ENGINE = MergeTree() ORDER BY deviceid"
    aus=client.execute(sql)
    sql ='desc en.vehicle_vin'
    aus=client.execute(sql)
    print(aus)

    sql="INSERT INTO vehicle_vin " \
        "SELECT vehicle_mile.deviceid, vehicle_vin1.project, vehicle_vin1.City, vehicle_vin1.province, vehicle_vin1.region, vehicle_vin1.user_typ, " \
        "vehicle_mile.mile_min, vehicle_mile.mile_max, vehicle_mile.d_mileage " \
        "FROM en.vehicle_mile INNER JOIN en.vehicle_vin1 on vehicle_vin1.deviceid = vehicle_mile.deviceid"
    aus=client.execute(sql)
    sql ='SELECT * FROM en.vehicle_vin'
    aus=client.execute(sql)
    print(aus)
    #删除临时表
    sql="DROP TABLE en.vehicle_vin1"
    aus=client.execute(sql)
    sql="DROP TABLE en.vehicle_mile"
    aus=client.execute(sql)


def create_tb(client):
    sql="CREATE TABLE IF NOT EXISTS en.rtm_6_2th " \
            "(deviceid String, uploadtime DateTime, vehicle_s UInt8, vehicle_s_c Int8, charg_s UInt8, charg_s_c Int8, " \
            " vehiclespeed Float32, accmiles Float32, soc UInt8, soc_c Int8, operationmode String, " \
            " totalvolt Float64, totalcurrent Float64, BMS_pow Float32, charg_mode String, " \
            " ir UInt32, accpedtrav UInt8, brakepedstat UInt8," \
            " emstat String, emctltemp Int32, emtemp Int32, emspeed Float32, emtq Float32, em_me_pow Float32, " \
            " emvolt Float32, emctlcut Float32, em_el_pow Float32, em_eff Float32, other_pow Float32, " \
            " tdfwn UInt8, celohwn UInt8, vedtovwn UInt8, vedtuvwn UInt8, lsocwn UInt8, celovwn UInt8, celuvwn UInt8, " \
            " hsocwn UInt8, jpsocwn UInt8, cesysumwn UInt8, celpoorwn UInt8, inswn UInt8, dctpwn UInt8, bksyswn UInt8, " \
            " dcstwn UInt8, emctempwn UInt8, hvlockwn UInt8, emtempwn UInt8, vesoc UInt8, " \
            " mxal UInt8, count_wn UInt8, cocesprotemp1 Array(Int8), cocesprotemp1_mean Float32 " \
            ") ENGINE = MergeTree() ORDER BY (deviceid, uploadtime )"
    aus=client.execute(sql)
    sql="ALTER TABLE en.rtm_6_2th ADD COLUMN d_time Int AFTER uploadtime"
    aus=client.execute(sql)
    sql="desc en.rtm_6_2th"
    aus=client.execute(sql)
    print_in_excel(aus,'june_2rd.xlsx')


def insert_tb(client):
    sql="INSERT INTO en.rtm_6_2th " \
        "SELECT deviceid, uploadtime,cast(runningDifference(uploadtime),'Int'), vehicle_s, runningDifference(vehicle_s), charg_s, runningDifference(charg_s), " \
        "cast(vehiclespeed,'Float32'), cast(accmiles,'Float32')," \
        "socp, runningDifference(socp), operationmode, totalvolt, totalcurrent, totalcurrent*totalvolt/1000 AS P, " \
        "multiIf(P<-7.5,'DC',P>=-7.5 and P<-4,'mode3_1',P>=-4 and P<-2,'mode3_2',P>=-2 and P<0,'mode2','discharging'),  " \
        "cast(ir,'UInt32'), if(accped<0,0,accped), if(brakeped<0,0,brakeped), " \
        "emstat, cast(emctltemp,'Int32'),cast(emtemp,'Int32'), sp, tq, sp*tq/9550 as me_pow, em_v, em_i, em_v*em_i/1000 as el_pow, " \
        "multiIf(emstat=='CLOSED' or el_pow*me_pow==0,0,emstat=='CONSUMING_POWER',me_pow/el_pow,emstat=='GENERATING_POWER',el_pow/me_pow,100), (P-el_pow), " \
        "wn01, wn02, wn03, wn04, wn05, wn06, wn07, wn08, wn09, wn10, wn11, wn12, wn13, wn14, wn15, wn16, wn17, wn18, wn19, if(wn_r<0,0,wn_r), " \
        "(wn01 + wn02 + wn03 + wn04 + wn05 + wn06 + wn07 + wn08 + wn09 + wn10 + wn11 + wn12 + wn13 + wn14 + wn15 + wn16 + wn17 + wn18 + wn19), " \
        "temp_list, arrayReduce('sum',temp_list)/length(temp_list) " \
        "FROM (SELECT deviceid, uploadtime, if(vehiclestatus=='STARTED',1,0) AS vehicle_s, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, " \
        "vehiclespeed, accmiles, if(soc<0,0,soc) as socp, operationmode, totalvolt, totalcurrent, " \
        "ir, cast(accpedtrav,'Int32') as accped, cast(brakepedstat,'Int32') as brakeped, " \
        "emstat, emctltemp, emtemp, cast(emspeed,'Float32') as sp, cast(emtq,'Float32') as tq, " \
        "cast(emvolt,'Float32') as em_v, cast(emctlcut,'Float32') as em_i, " \
        "if(tdfwn=='true',1,0) as wn01, if(celohwn=='true',1,0) as wn02, if(vedtovwn=='true',1,0) as wn03, if(vedtuvwn=='true',1,0) as wn04, if(lsocwn=='true',1,0) as wn05, " \
        "if(celovwn=='true',1,0) as wn06, if(celuvwn=='true',1,0) as wn07, if(hsocwn=='true',1,0) as wn08, if(jpsocwn=='true',1,0) as wn09, if(cesysumwn=='true',1,0) as wn10, " \
        "if(celpoorwn=='true',1,0) as wn11, if(inswn=='true',1,0) as wn12, if(dctpwn=='true',1,0) as wn13, if(bksyswn=='true',1,0) as wn14, if(dcstwn=='true',1,0) as wn15, " \
        "if(emctempwn=='true',1,0) as wn16, if(hvlockwn=='true',1,0) as wn17, if(emtempwn=='true',1,0) as wn18, if(vesoc=='true',1,0)as wn19, cast(mxal,'Int8') as wn_r,  " \
        "cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
        "FROM en.rtm_data_june WHERE vehiclestatus!='ERROR' and chargingstatus!='INVALID' and chargingstatus!='ERROR' and cocesprotemp1!='NULL' " \
        "ORDER BY deviceid,uploadtime ) "
    aus=client.execute(sql)
    sql="SELECT COUNT(deviceid) from en.rtm_6_2th"
    aus=client.execute(sql)
    print(aus)
    sql="SELECT COUNT(DISTINCT deviceid) from en.rtm_6_2th"
    aus=client.execute(sql)
    print(aus)
    sql="SELECT * from en.rtm_6_2th limit 10"
    aus=client.execute(sql)
    print(aus)



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

