import sys
sys.path.append('./')
from clickhouse_driver import Client
import csv
from genarl_func import print_in_excel
from genarl_func import time_cost
from genarl_func import time_cost_all

client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')


def View_table(tb_name):
    sql="DESC " + tb_name
    aus=client.execute(sql)
    print("------"+tb_name+"------")
    print(len(aus))
    print(aus)
    sql="select count(distinct deviceid) from "+ tb_name
    aus=client.execute(sql)
    print("------Vehicle number------")
    print(aus)
    sql="SELECT topK(1)(toDate(t1)),topK(1)(toDate(t2)) " \
        "FROM (select deviceid,min(uploadtime) as t1,max(uploadtime) as t2 " \
        " From " +tb_name+" group by deviceid) "
    aus=client.execute(sql)
    print("------date------")
    print(aus)
    sql="SELECT topK(10)(toDate(t1)) FROM " \
        "(Select deviceid,min(uploadtime) as t1,max(uploadtime) as t2 " \
        " From " +tb_name+" group by deviceid) "
    aus=client.execute(sql)
    print("------date------")
    print(aus)
    sql="select deviceid,min(toDate(uploadtime)), max(toDate(uploadtime)) " \
        " From " +tb_name+ " group by deviceid"
    aus=client.execute(sql)
    print_in_excel(aus,'rtm_details.xlsx')


View_table("ods.rtm_details")

sql="desc en.vehicle_vin"
'''
host='10.122.17.69',port='9005',database='en',user='en' ,password='en1Q'
1. ods.rtm_details ，为t-1的实时RTM数据，即今天可以查到昨天的数据
2. ods.vehicles_info ，为2019.1-2020.6的RTM历史数据
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



