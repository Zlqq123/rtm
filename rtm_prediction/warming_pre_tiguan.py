import sys
sys.path.append('./')
import numpy as np
import pandas as pd
import datetime

#from genarl_func import print_in_excel,time_cost
from en_client import en_client


client=en_client()


'''
original table
最近三个月数据-----------------------------------ods.rtm_details_v2
All data(without warmingsignal)----------------------------- ods.rtm_details  
All data with warmingsignal------------------------ods.rtm_reissue_history

2020/03 Data(without warmingsignal)------------------------- en.rtm_vds
2020/06 Data(with warmingsignal)---------------------------- en.rtm_data_june

attachment table:
VIN Usertype Project region province mileage---------------- en.vehicle_vin

pre analyzed tabel:
2020/06 Data(with warmingsignal) after pre analyzing----- en.rtm_data_june-->-->--- en.rtm_6_2th
All data(without warmingsignal) after pre analyzing -------- en.rtm_2th
All data with warmingsignal Tiguan -------------en.rtm_tiguan  {'2018-01-01 00:00:00' ~~ '2020-12-31 23:59:59'}
'''

#基于原数据的报警数目探索
def tiguan_warming_detective():
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
        " FROM ods.rtm_reissue_history WHERE deviceid IN (SELECT deviceid FROM en.vehicle_vin WHERE project like 'Tiguan%') " \
        " AND uploadtime BETWEEN '2019-06-01 00:00:00' AND '2020-05-31 23:59:59' group by deviceid "

    #" FROM ods.rtm_reissue_history INNER JOIN en.vehicle_vin ON ods.rtm_reissue_history.deviceid=en.vehicle_vin.deviceid WHERE en.vehicle_vin.project like 'Tiguan%' group by deviceid "
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    df.to_csv('tiguan_warning.csv')



# clickhouse中数据表预处理，预处理规则见excel
def tb_pre_ana(original_tb_name,new_tb_name,start_time,end_time):
    '''
    start_time str   '2018-01-01 00:00:00'
    '''
    sql="CREATE TABLE IF NOT EXISTS " + new_tb_name + \
            " (deviceid String, uploadtime DateTime, d_time Int, vehicle_s UInt8, vehicle_s_c Int8, charg_s UInt8, charg_s_c Int8, " \
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
    sql="desc "+ new_tb_name
    aus=client.execute(sql)
    print(aus)
    print(len(aus))

    sql="INSERT INTO "+ new_tb_name + \
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
        "FROM " + original_tb_name + \
        "WHERE vehiclestatus!='ERROR' and chargingstatus!='INVALID' and chargingstatus!='ERROR' and cocesprotemp1!='NULL' " \
        "AND uploadtime BETWEEN '" + start_time + "' AND '" + end_time + "' " \
        "AND deviceid IN (SELECT deviceid FROM en.vehicle_vin WHERE project like 'Tiguan%') " \
        "ORDER BY deviceid,uploadtime ) "
    print(sql)
    aus=client.execute(sql)
    sql="SELECT COUNT(deviceid) from "+ new_tb_name
    aus=client.execute(sql)
    print(aus)
    sql="SELECT COUNT(DISTINCT deviceid) from "+ new_tb_name
    aus=client.execute(sql)
    print(aus)
    sql="SELECT * from " + new_tb_name + " limit 10"
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    sql="desc "+ new_tb_name
    title=pd.DataFrame(client.execute(sql))
    df.columns=title[0]
    df.to_csv(new_tb_name+'.csv')

def sample_extraction(tb_name,start_time,end_time,sample_file_name):
    
    
    #提取训练集
    #提取所有的非报警样本， 
    sql="SELECT c0, c1, c2, c3 FROM " \
    "(SELECT deviceid as c0, toDate(uploadtime) as c1, sum(bksyswn) as c2, max(accmiles) as c3 " \
    "FROM en.rtm_tiguan WHERE uploadtime BETWEEN '"+ start_time +"' AND '"+ end_time +"' " \
    "GROUP BY deviceid,toDate(uploadtime) ORDER BY deviceid, toDate(uploadtime)) " \
    " WHERE c3>200 AND c2==0 "# 删除里程小于200km
    aus=client.execute(sql)
    print(len(aus))
    df = pd.DataFrame(aus)
    df = df.sample(n=60000)  #随机采样
    print(df.shape)
    df.columns=['VIN','target date','bksyswn','mileage']
    df['start']=df['target date']-datetime.timedelta(days=31)
    df['end']=df['target date']-datetime.timedelta(days=1)
    df.to_csv(sample_file_name + 'no_warning.csv')

    #提取所有的报警样本
    sql="SELECT c0, c1,c2,c3 FROM " \
    "(SELECT deviceid as c0, toDate(uploadtime) as c1, sum(bksyswn) as c2, max(accmiles) as c3 " \
    "FROM en.rtm_tiguan WHERE bksyswn>0 AND uploadtime BETWEEN '"+ start_time +"' AND '"+ end_time +"' " \
    "GROUP BY deviceid,toDate(uploadtime) ORDER BY deviceid, toDate(uploadtime)) " \
    " WHERE c3>200 "# 删除里程小于200km
    aus=client.execute(sql)
    df = pd.DataFrame(aus)
    df.columns=['VIN','target date','bksyswn','mileage']
    df['start']=df['target date']-datetime.timedelta(days=31)
    df['end']=df['target date']-datetime.timedelta(days=1)
    df.to_csv(sample_file_name + 'warning.csv')

def feature_extraction(tb_name,sample_file_name,feature_file_name):
    from rtm_hist.RTM_ana import feature_extract
    feature_all=pd.DataFrame()
    sample_in=pd.read_csv(sample_file_name,encoding="gbk")
    print(sample_in.dtypes)
    for __,row in sample_in.iterrows():
        vin=row['VIN']
        target=row['target date']
        start=row['start']
        end=row['end']
        l1=feature_extract(vin,start,end,target,tb_name)
        feature_list1=l1()
        feature_list=[vin]
        for x in feature_list1:
            feature_list.extend(x)
        if 'null' in feature_list:# 判断是否有缺省特征
            feature_list.append(1)
        else:
            feature_list.append(0)
        #print(v)
        feature_all=feature_all.append([feature_list],ignore_index=True)
    print(feature_all.shape)
    feature_all.columns=['VIN','Label','week_num', 'region','province','user_type','acc_mileage','ir','mile','daily mile (mean)','driving time', \
        'v (mean)','v 99%','v 50%','EV %','FV %','acc pedal(mean)','acc pedal(99%)','acc pedal(50%)','dec pedal(mean)','dec pedal(99%)','dec pedal(50%)', \
        'BMS discharge temp max','BMS discharge temp min','BMS discharge temp mean','BMS discharge power max','BMS discharge power mean','cell discharge temp max','cell discharge temp min','cell discharge temp diff max','cell discharge temp diff mean',\
        'E-motor speed max','E-motor speed mean','E-motor torque+ max','E-motor torque+ mean','E-motor torque- max','E-motor torque- mean',\
        'E-motor torque- percentage','E-motor temp mean','E-motor temp 99%','E-motor temp 50%','E-motor temp 1%','LE temp mean','LE temp 99%','LE temp 50%','LE temp 1%',\
        'BMS charge temp max','BMS discharge temp min','BMS charge temp mean','BMS charge power max','BMS charge power mean','cell charge temp max','cell charge temp min','cell charge temp diff max','cell charge temp diff mean',\
        'charge times','mode2 percentage','mode3 percentage','charge start SOC mean','charge start SOC 50%','charge end SOC mean','charge end SOC 50%','mean(ΔSOC)','sum(ΔSOC)','Integrity']

    print("样本个数: {}".format(feature_all.shape[0]))
    print("特征个数: {}".format(feature_all.shape[1]))
    print("Label == 1: {}".format(feature_all[feature_all.Label == 1].shape[0]))
    print("Label == 0: {}".format(feature_all[feature_all.Label == 0].shape[0]))
    print("特征不完整的样本数: {}".format(feature_all[feature_all.Integrity == 1].shape[0]))

    feature_all.to_csv(feature_file_name,encoding="gbk",index=False)


tb_pre_ana('ods.rtm_details_v2','en.tiguan2021','2021-02-01 00:00:00','2021-06-01 00:00:00')

a=1
