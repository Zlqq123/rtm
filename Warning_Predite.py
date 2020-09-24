import sys
sys.path.append('./')
from clickhouse_driver import Client
import xlsxwriter
import time
import csv
import numpy as np
from rtm.RTM_ana import RtmAna
from rtm.RTM_ana import feature_extract
from genarl_func import print_in_excel
from genarl_func import time_cost
import hist_func_np
from en_client import en_client
import datetime

client=en_client()
tb1_name="en.rtm_6_2th"
filename1="D:/03RTM/报警预测/tiguan_no_warming.csv"
t_name1='no_warming_f.xlsx'
filename2="D:/03RTM/报警预测/tiguan_warming.csv"
t_name2='warming_f.xlsx'





def feature_ex(filename,t_name):
    workbook = xlsxwriter.Workbook(t_name)
    worksheet = workbook.add_worksheet("sheet1")
    rawdata_col_define={}
    r=0
    c=0
    worksheet.write(r,c,'VIN')
    worksheet.write(r,c+1,'Label')
    c+=2
    worksheet.write(r,c,'region')
    worksheet.write(r,c+1,'province')
    worksheet.write(r,c+2,'user_type')
    worksheet.write(r,c+3,'mileage')
    worksheet.write(r,c+4,'ir')
    c+=5
    worksheet.write(r,c,'mile')
    worksheet.write(r,c+1,'daily mile (mean)')
    worksheet.write(r,c+2,'driving time')
    c+=3
    worksheet.write(r,c,'v (mean)')
    worksheet.write(r,c+1,'v 99%')
    worksheet.write(r,c+2,'v 50%')
    worksheet.write(r,c+3,'EV %')
    worksheet.write(r,c+4,'FV %')
    worksheet.write(r,c+5,'acc pedal(mean)')
    worksheet.write(r,c+6,'acc pedal(99%)')
    worksheet.write(r,c+7,'acc pedal(50%)')
    worksheet.write(r,c+8,'dec pedal(mean)')
    worksheet.write(r,c+9,'dec pedal(99%)')
    worksheet.write(r,c+10,'dec pedal(50%)')
    c+=11
    worksheet.write(r,c,'BMS discharge temp max')
    worksheet.write(r,c+1,'BMS discharge temp mean')
    worksheet.write(r,c+2,'BMS discharge power max')
    worksheet.write(r,c+3,'BMS discharge power mean')
    worksheet.write(r,c+4,'cell discharge temp max')
    worksheet.write(r,c+5,'cell discharge temp min')
    worksheet.write(r,c+6,'cell discharge temp diff max')
    worksheet.write(r,c+7,'cell discharge temp diff mean')
    c+=8
    worksheet.write(r,c,'E-motor speed max')
    worksheet.write(r,c+1,'E-motor speed mean')
    worksheet.write(r,c+2,'E-motor torque+ max')
    worksheet.write(r,c+3,'E-motor torque+ mean')
    worksheet.write(r,c+4,'E-motor torque- max')
    worksheet.write(r,c+5,'E-motor torque- mean')
    worksheet.write(r,c+6,'E-motor torque- percentage')
    worksheet.write(r,c+7,'E-motor temp mean')
    worksheet.write(r,c+8,'E-motor temp 99%')
    worksheet.write(r,c+9,'E-motor temp 50%')
    worksheet.write(r,c+10,'E-motor temp 1%')
    worksheet.write(r,c+11,'LE temp mean')
    worksheet.write(r,c+12,'LE temp 99%')
    worksheet.write(r,c+13,'LE temp 50%')
    worksheet.write(r,c+14,'LE temp 1%')
    c+=15
    worksheet.write(r,c,'BMS charge temp max')
    worksheet.write(r,c+1,'BMS charge temp mean')
    worksheet.write(r,c+2,'BMS charge power max')
    worksheet.write(r,c+3,'BMS charge power mean')
    worksheet.write(r,c+4,'cell charge temp max')
    worksheet.write(r,c+5,'cell charge temp min')
    worksheet.write(r,c+6,'cell charge temp diff max')
    worksheet.write(r,c+7,'cell charge temp diff mean')
    c+=8
    worksheet.write(r,c,'charge times')
    worksheet.write(r,c+1,'charge start SOC mean')
    worksheet.write(r,c+2,'charge start SOC 50%')
    worksheet.write(r,c+3,'charge end SOC mean')
    worksheet.write(r,c+4,'charge end SOC 50%')
    worksheet.write(r,c+5,'sum(ΔSOC)')
    worksheet.write(r,c+6,'mean(ΔSOC)')
    worksheet.write(r,c+7,'mode2 percentage')
    worksheet.write(r,c+8,'mode3 percentage')

    with open(filename) as f:
        reader=csv.reader(f)
        header_row=next(reader)
        for index, column_header in enumerate(header_row):
            rawdata_col_define[column_header]=index   # find raw data columns title & index {columst title: colunms index}
        for row in reader:
            vin=row[rawdata_col_define['VIN']]
            start=row[rawdata_col_define['start']]
            end=row[rawdata_col_define['end']]
            target=row[rawdata_col_define['target date']]
            l1=feature_extract(vin,start,end,target,tb1_name)
            a=l1()
            r+=1
            print(r)
            c=0
            worksheet.write(r,c,vin)
            worksheet.write(r,c+1,a[0])
            c+=2
            for j in range(5):
                worksheet.write(r,c+j,a[1][j])
            c+=5
            for j in range(3):
                worksheet.write(r,c+j,a[2][j])
            c+=3
            for j in range(11):
                worksheet.write(r,c+j,a[3][j])
            c+=11
            for j in range(8):
                worksheet.write(r,c+j,a[4][j])
            c+=8
            for j in range(15):
                worksheet.write(r,c+j,a[5][j])
            c+=15
            for j in range(8):
                worksheet.write(r,c+j,a[6][j])
            c+=8
            for j in range(9):
                worksheet.write(r,c+j,a[7][j])
    
    workbook.close()


feature_ex(filename1,t_name1)
feature_ex(filename2,t_name2)



filename="D:/03RTM/报警预测/tiguan_warming.csv"
rawdata_col_define={}
all_feature=[]
with open(filename) as f:
    reader=csv.reader(f)
    header_row=next(reader)
    for index, column_header in enumerate(header_row):
        rawdata_col_define[column_header]=index   # find raw data columns title & index {columst title: colunms index}
    for row in reader:
        vin=row[rawdata_col_define['VIN']]
        start=row[rawdata_col_define['start']]
        end=row[rawdata_col_define['end']]
        target=row[rawdata_col_define['target date']]
        l1=feature_extract(vin,start,end,target,tb1_name)
        s=l1.get_static_feature()
        a=l1()
        all_feature.append(a)

r=1
workbook = xlsxwriter.Workbook('warming_f.xlsx')
worksheet = workbook.add_worksheet("sheet1")

for v in all_feature:
    if v!=[]:
        c=0
        worksheet.write(r,c,v[0])
        c+=1
        for j in range(5):
            worksheet.write(r,c+j,v[1][j])
        c+=5
        for j in range(3):
            worksheet.write(r,c+j,v[2][j])
        c+=3
        if v[3]!=[]:
            for j in range(11):
                worksheet.write(r,c+j,v[3][j])
        c+=11
        for j in range(8):
            worksheet.write(r,c+j,v[4][j])
        c+=8
        if v[5]!=[]:
            for j in range(15):
                worksheet.write(r,c+j,v[5][j])
        c+=15
        if v[6]!=[]:
            for j in range(8):
                worksheet.write(r,c+j,v[6][j])
        c+=8
        if v[7]!=[]:
            for j in range(9):
                worksheet.write(r,c+j,v[7][j])
    r+=1

workbook.close()
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







