
from en_client import en_client
import pandas as pd
client=en_client()
'''
original table
All data(without warmingsignal)----------------------------- ods.rtm_details  
All data with warmingsignal------------------------ods.rtm_reissue_history

2020/03 Data(without warmingsignal)------------------------- en.rtm_vds
2020/06 Data(with warmingsignal)---------------------------- en.rtm_data_june

attachment table:
VIN Usertype Project region province mileage---------------- en.vehicle_vin

pre analyzed tabel:
2020/06 Data(with warmingsignal) after pre analyzing----- en.rtm_data_june-->-->--- en.rtm_6_2th
All data(without warmingsignal) after pre analyzing -------- en.rtm_2th
All data with warmingsignal Tiguan -------------en.rtm_tiguan

'''
def f1():
    #tiguan 总报警数
    sql=" with if(tdfwn=='true',1,0) as wn01, if(celohwn=='true',1,0) as wn02, if(vedtovwn=='true',1,0) as wn03, " \
        " if(vedtuvwn=='true',1,0) as wn04, if(lsocwn=='true',1,0) as wn05, if(celovwn=='true',1,0) as wn06, " \
        " if(celuvwn=='true',1,0) as wn07, if(hsocwn=='true',1,0) as wn08, if(jpsocwn=='true',1,0) as wn09, " \
        " if(cesysumwn=='true',1,0) as wn10, if(celpoorwn=='true',1,0) as wn11, if(inswn=='true',1,0) as wn12, " \
        " if(dctpwn=='true',1,0) as wn13, if(bksyswn=='true',1,0) as wn14, if(dcstwn=='true',1,0) as wn15, " \
        " if(emctempwn=='true',1,0) as wn16, if(hvlockwn=='true',1,0) as wn17, if(emtempwn=='true',1,0) as wn18, " \
        " if(vesoc=='true',1,0)as wn19 SELECT deviceid, sum(wn01),sum(wn02), " \
        " sum(wn03),sum(wn04), sum(wn05),sum(wn06),sum(wn07),sum(wn08),sum(wn09),sum(wn10), " \
        " sum(wn11),sum(wn12),sum(wn13),sum(wn14),sum(wn15),sum(wn16),sum(wn17),sum(wn18),sum(wn19) " \
        " FROM ods.rtm_reissue_history WHERE deviceid like 'LSVU%' group by deviceid "
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    df.to_csv('tiguan_warning.csv')


def C_tiguan():
    sql="CREATE TABLE IF NOT EXISTS en.rtm_tiguan " \
            "(deviceid String, uploadtime DateTime,d_time Int, vehicle_s UInt8, vehicle_s_c Int8, charg_s UInt8, charg_s_c Int8, " \
            " vehiclespeed Float32, accmiles Float32, soc UInt8, soc_c Int8, operationmode String, " \
            " totalvolt Float64, totalcurrent Float64, BMS_pow Float32, charg_mode String, " \
            " ir UInt32, accpedtrav UInt8, brakepedstat UInt8," \
            " emstat String, emctltemp Int32, emtemp Int32, emspeed Float32, emtq Float32, em_me_pow Float32, " \
            " emvolt Float32, emctlcut Float32, em_el_pow Float32, em_eff Float32, cocesprotemp1 Array(Int8), " \
            " tdfwn UInt8, celohwn UInt8, vedtovwn UInt8, vedtuvwn UInt8, lsocwn UInt8, celovwn UInt8, celuvwn UInt8, " \
            " hsocwn UInt8, jpsocwn UInt8, cesysumwn UInt8, celpoorwn UInt8, inswn UInt8, dctpwn UInt8, bksyswn UInt8, " \
            " dcstwn UInt8, emctempwn UInt8, hvlockwn UInt8, emtempwn UInt8, vesoc UInt8, mxal UInt8, count_wn UInt8 " \
            ") ENGINE = MergeTree() ORDER BY (deviceid, uploadtime )"
    aus=client.execute(sql)
    sql="desc en.rtm_tiguan"
    aus=client.execute(sql)
    print(aus)
    print(len(aus))

    sql="INSERT INTO en.rtm_tiguan " \
        "SELECT deviceid, uploadtime,cast(runningDifference(uploadtime),'Int'), vehicle_s, runningDifference(vehicle_s), charg_s, runningDifference(charg_s), " \
        "cast(vehiclespeed,'Float32'), cast(accmiles,'Float32'), socp, runningDifference(socp), operationmode, " \
        "totalvolt, totalcurrent, totalcurrent*totalvolt/1000 AS P, multiIf(P<-2,'mode3_2',P>=-2 and P<0,'mode2','discharging'), " \
        "cast(ir,'UInt32'), if(accped<0,0,accped), if(brakeped<0,0,brakeped), " \
        "emstat, cast(emctltemp,'Int32'),cast(emtemp,'Int32'), sp, tq, sp*tq/9550 as me_pow, em_v, em_i, em_v*em_i/1000 as el_pow, " \
        "multiIf(emstat=='CLOSED' or el_pow*me_pow==0,0,emstat=='CONSUMING_POWER',me_pow/el_pow,emstat=='GENERATING_POWER',el_pow/me_pow,100), temp_list, " \
        "wn01, wn02, wn03, wn04, wn05, wn06, wn07, wn08, wn09, wn10, wn11, wn12, wn13, wn14, wn15, wn16, wn17, wn18, wn19, if(wn_r<0,0,wn_r), " \
        "(wn01 + wn02 + wn03 + wn04 + wn05 + wn06 + wn07 + wn08 + wn09 + wn10 + wn11 + wn12 + wn13 + wn14 + wn15 + wn16 + wn17 + wn18 + wn19) " \
        "FROM ( SELECT deviceid, uploadtime, if(vehiclestatus=='STARTED',1,0) AS vehicle_s, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, " \
        "vehiclespeed, accmiles, if(soc<0,0,soc) AS socp, operationmode, totalvolt, totalcurrent, " \
        "ir, cast(accpedtrav,'Int32') AS accped, CAST(brakepedstat,'Int32') AS brakeped, " \
        "emstat, emctltemp, emtemp, cast(emspeed,'Float32') AS sp, cast(emtq,'Float32') AS tq, " \
        "cast(emvolt,'Float32') AS em_v, cast(emctlcut,'Float32') AS em_i, " \
        "cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list, " \
        "if(tdfwn=='true',1,0) as wn01, if(celohwn=='true',1,0) as wn02, if(vedtovwn=='true',1,0) as wn03, if(vedtuvwn=='true',1,0) as wn04, if(lsocwn=='true',1,0) as wn05, " \
        "if(celovwn=='true',1,0) as wn06, if(celuvwn=='true',1,0) as wn07, if(hsocwn=='true',1,0) as wn08, if(jpsocwn=='true',1,0) as wn09, if(cesysumwn=='true',1,0) as wn10, " \
        "if(celpoorwn=='true',1,0) as wn11, if(inswn=='true',1,0) as wn12, if(dctpwn=='true',1,0) as wn13, if(bksyswn=='true',1,0) as wn14, if(dcstwn=='true',1,0) as wn15, " \
        "if(emctempwn=='true',1,0) as wn16, if(hvlockwn=='true',1,0) as wn17, if(emtempwn=='true',1,0) as wn18, if(vesoc=='true',1,0)as wn19, cast(mxal,'Int8') as wn_r  " \
        "FROM ods.rtm_reissue_history " \
        "WHERE vehiclestatus!='ERROR' and chargingstatus!='INVALID' and chargingstatus!='ERROR' and cocesprotemp1!='NULL' " \
        "AND uploadtime BETWEEN '2018-01-01 00:00:00' AND '2020-12-31 23:59:59' AND deviceid IN (SELECT deviceid FROM en.vehicle_vin WHERE project like 'Tiguan%') " \
        "ORDER BY deviceid,uploadtime ) "
    print(sql)
    aus=client.execute(sql)
    sql="SELECT COUNT(deviceid) from en.rtm_tiguan"
    aus=client.execute(sql)
    print(aus)
    sql="SELECT COUNT(DISTINCT deviceid) from en.rtm_tiguan"
    aus=client.execute(sql)
    print(aus)
    sql="SELECT * from en.rtm_tiguan limit 10"
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    sql="desc en.rtm_tiguan"
    title=pd.DataFrame(client.execute(sql))
    df.columns=title[0]
    df.to_csv('rtm_tiguan.csv')


C_tiguan()