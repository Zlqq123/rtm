import sys
sys.path.append('./')
from clickhouse_driver import Client
import xlsxwriter
import time
import csv
import numpy as np
from rtm.RTM_ana import RtmAna
from genarl_func import print_in_excel
from genarl_func import time_cost
import hist_func_np
from en_client import en_client
import datetime

client=en_client()
sql="desc ods.rtm_reissue_history"
aus=client.execute(sql)
print(aus)



def pre1():
    '''
    非报警样本筛选
    '''
    filename="D:/03RTM/报警预测/tiguan.csv"
    vin=[]
    s=[]
    e=[]
    rawdata_col_define={}
    with open(filename) as f:
        reader=csv.reader(f)
        header_row=next(reader)
        for index, column_header in enumerate(header_row):
            rawdata_col_define[column_header]=index   # find raw data columns title & index {columst title: colunms index}
        for row in reader:
            vin.append(row[rawdata_col_define['vin']])
            s.append(row[rawdata_col_define['start time']])
            e.append(row[rawdata_col_define['end time']])
    all_sample=[]
    i=0
    delta1=datetime.timedelta(days=5)
    delta2=datetime.timedelta(days=6)
    vl=0


    while i<len(vin):
        start_time=datetime.datetime.strptime(s[i],'%Y/%m/%d').date()
        end_time=datetime.datetime.strptime(e[i],'%Y/%m/%d').date()
        vv=vin[i]
        if vv!=vl:
            os=start_time
        else:
            os=ot+datetime.timedelta(days=1)
        oe=os+delta1
        ot=os+delta2
        vl=vin[i]
        if oe<end_time:
            all_sample.append([vv,os,oe,ot,start_time,end_time])
        else:
            i=i+1

    workbook = xlsxwriter.Workbook('tiguan_sample.xlsx')
    worksheet = workbook.add_worksheet("sheet1")
    for i in range(len(all_sample)):
        for j in range(len(all_sample[0])):
            worksheet.write(i+1,j,all_sample[i][j])
    workbook.close()





'''
All data(without warmingsignal)----------------------------- ods.rtm_details  
warmingsignal------------------------ods.rtm_reissue_history
2020/03 Data(without warmingsignal)------------------------- en.rtm_vds
2020/06 Data(with warmingsignal)---------------------------- en.rtm_data_june
2020/06 Data(with warmingsignal) after pre analyzing-------- en.rtm_6_2th
VIN Usertype Project region province mileage---------------- en.vehicle_vin 
'''

client=en_client()

def wm_detect(proj):
    if proj=="lavida":
        con=" deviceid like 'LSVA%' "
    elif proj=="tiguan":
        con=" deviceid like 'LSVU%' "
    elif proj=="passat":
        con=" deviceid like 'LSVC%' "
    
    sql="SELECT deviceid,uploadtime,inswn,ir/1000,charg_s,vehicle_s,vehiclespeed,soc,accmiles,BMS_pow,charg_mode,mxal " \
        "FROM en.rtm_6_2th where inswn>0 and "+con+" order by deviceid, uploadtime "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_inswn.xlsx')
    sql="SELECT deviceid,uploadtime,jpsocwn,charg_s,vehicle_s,vehiclespeed,soc,soc_c,accmiles,mxal " \
        "FROM en.rtm_6_2th where jpsocwn>0 and "+con+" order by deviceid, uploadtime "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_jpsocwn.xlsx')
    sql="SELECT deviceid,uploadtime,bksyswn,mxal,charg_s,vehicle_s,vehiclespeed,soc,soc_c,accmiles " \
    "FROM en.rtm_6_2th where bksyswn>0 and"+con+" order by deviceid, uploadtime "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_bksyswn.xlsx')
    
    sql="SELECT deviceid,uploadtime,hvlockwn,mxal,charg_s,vehicle_s,vehiclespeed,soc,soc_c,accmiles " \
        "FROM en.rtm_6_2th where hvlockwn>0 and "+con+" order by deviceid, uploadtime "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_hvlockwn.xlsx')


def acc_wn(proj):
    if proj=="lavida":
        con=" deviceid like 'LSVA%' "
    elif proj=="tiguan":
        con=" deviceid like 'LSVU%' "
    elif proj=="passat":
        con=" deviceid like 'LSVC%' "
    #查询每辆车max(uploadtime)对应accmiles
    sql="SELECT  deviceid,uploadtime,accmiles from en.rtm_6_2th " \
        "INNER JOIN (SELECT deviceid,min(uploadtime) as x1 from en.rtm_6_2th group by deviceid) as tbx " \
        "ON (tbx.deviceid=en.rtm_6_2th.deviceid and tbx.x1=en.rtm_6_2th.uploadtime ) " \
        "WHERE"+con+" order by deviceid, uploadtime"
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_start_milage.xlsx')
    #查询每辆车min(uploadtime)对应accmiles
    sql="SELECT  deviceid,uploadtime,accmiles from en.rtm_6_2th " \
        "INNER JOIN (SELECT deviceid,max(uploadtime) as x1 from en.rtm_6_2th group by deviceid) as tbx " \
        "ON (tbx.deviceid=en.rtm_6_2th.deviceid and tbx.x1=en.rtm_6_2th.uploadtime ) " \
        "WHERE "+con+" order by deviceid, uploadtime"
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_end_milage.xlsx')
    #查询所有故障
    sql="SELECT deviceid,toDate(uploadtime),sum(celohwn), sum(jpsocwn),sum(inswn),sum(bksyswn),sum(dcstwn),sum(emctempwn),sum(hvlockwn), avg(accmiles) " \
        "FROM en.rtm_6_2th WHERE "+con+" and count_wn>0 group by deviceid,toDate(uploadtime) order by deviceid, toDate(uploadtime) "
    aus=client.execute(sql)
    print_in_excel(aus,proj+'_warming.xlsx')







