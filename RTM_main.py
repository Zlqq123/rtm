import sys
sys.path.append('./')
from clickhouse_driver import Client
import xlsxwriter
import time
import csv
import numpy as np
#from range_test.range_test import Rangetest
from rtm.RTM_ana import RtmAna
from genarl_func import print_in_excel
from genarl_func import time_cost
from genarl_func import time_cost_all
import hist_func_np


client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')
path='D:/03RTM/ALL_RTM_data/0805/'
tb1_name="en.rtm_6_2th"
tb2_name="en.vehicle_vin"
tb_join=' INNER JOIN en.vehicle_vin on en.rtm_6_2th.deviceid=en.vehicle_vin.deviceid'
con="en.vehicle_vin.project=='Lavida BEV 53Ah'  AND en.vehicle_vin.d_mileage > 100 AND en.vehicle_vin.region=='MidEast'  AND en.vehicle_vin.user_typ=='Private'"
sampling=1/6


def RTM_june(proj):
    start=time.time()
    #client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')
    #path='D:/03RTM/ALL_RTM_data/0805/'
    #tb1_name="en.rtm_6_2th"
    #tb2_name="en.vehicle_vin"
    l1=RtmAna(path,proj,client,tb1_name,tb2_name)
    l1.d_mile_condition_select(100)
    l1.generate_log_file()
    l1.summary()
    dt=time.time()-start
    file=open(l1.log_filename,'a')
    file.write("------------------\r\n")
    file.write("running cost"+ str(round(dt,2))+"s \r\n")
    file.close()

RTM_june('Lavida')
#abd('Tiguan C5')

vin="LSVUY60T3L2028579"
def for_1_car(vin):
    client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')
    sql="select deviceid, uploadtime,vehiclespeed, accmiles FROM ods.rtm_details WHERE deviceid=='"+vin+"' "
    aus=client.execute(sql)
    print_in_excel(aus,vin+'.xlsx')

for_1_car(vin)

def Start_charge_temp_soc():
    '''
    考察高温环境下充电起始电池温度SOC分布
    '''
    client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')
    path='D:/03RTM/ALL_RTM_data/0723/'
    tb1_name="en.rtm_6_2th"
    tb2_name="en.vehicle_vin"
    l1=RtmAna(path,'Lavida',client,tb1_name,tb2_name)
    l1.d_mile_condition_select(100)
    l1.generate_log_file()
    __, __, __, __, charg_soc, charg_temp, __ = l1.charge_ana()
    a=charg_soc[0]
    b=charg_temp[4]
    workbook = xlsxwriter.Workbook("开始充电SOC_temp分布.xlsx")
    hist_func_np.hist_cros_2con_show(workbook,['SOC_temp'],charg_soc[0],range(0,115,5),charg_temp[4],range(-20,62,2))
    workbook.close()


sql="SELECT emspeed,emtq,em_eff,emctltemp,emtemp " \
    "FROM " +tb1_name+ tb_join+ " WHERE " + con + " AND "+ tb1_name +".emstat !='CLOSED'" \
    " AND toSecond(uploadtime)<"+str(int(sampling*60))
print(sql)
aus=client.execute(sql)

a=1
sql1="SELECT deviceid,uploadtime,charg_s_c,soc,soc_c,accmiles " \
    "FROM " +tb1_name+ tb_join+ " WHERE " + con + " AND "+ tb1_name +".charg_s_c IN (1,-1) ORDER BY deviceid,uploadtime "
print(sql1)
aus=client.execute(sql1)
#aus=[0 vin  1 时间  2充电变化标志位  3 soc   4 d_soc  5 mileage ]


sql="SELECT deviceid,uploadtime,-BMS_pow,cocesprotemp1_mean,soc,charg_mode " \
    "FROM " +tb1_name + tb_join+" WHERE "+ con+ " AND "+ tb1_name +".charg_s==1 " \
    "ORDER BY deviceid,uploadtime"
print(sql)
#aus=[i][0vin 1time 2power 3temp 4soc 5charg_mode]
aus=client.execute(sql)


sql1="SELECT deviceid,uploadtime,charg_s_c,soc,soc_c,accmiles,charg_mode FROM " + tb1_name + tb_join+ \
    " WHERE " + con + " AND "+ tb1_name +".charg_s_c IN (1,-1) ORDER BY deviceid,uploadtime "
print(sql1)


path='D:/03RTM/ALL_RTM_data/0717/'
l1=RtmAna(path,'Lavida',client,tb1_name,tb2_name,'MidEast','Private')
l1.condition_printer()

#target1、统计不同驾驶风格（针对BEV），（前提，相同地理位置，相同用户类型，相同附件消耗）统计其全电续驶里程和能耗差别



def Start_soc_mode():
    '''
    考察DC充电下开始充电SOC分布
    '''
    client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')
    path='D:/03RTM/ALL_RTM_data/0723/'
    tb1_name="en.rtm_6_2th"
    tb2_name="en.vehicle_vin"
    l1=RtmAna(path,'Lavida',client,tb1_name,tb2_name)
    l1.d_mile_condition_select(100)
    l1.generate_log_file()
    [time_h_s,time_d,time_d_c,mode,charg_soc,charg_pow,charg_temp]=l1.charge_ana()
    workbook = xlsxwriter.Workbook("不同充电模式下开始充电SOC分布.xlsx")
    mode_interval=['mode2','mode3_2','mode3_1','DC']
    hist_func_np.hist_cros_con_dis_show(workbook,['dad'],charg_soc[0],range(0,110,5),mode,mode_interval)
    workbook.close()

#Start_soc_mode()

@time_c
def time_before_charge():
    client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')
    sql1="SELECT deviceid,uploadtime,charg_s_c,vehicle_s_c,charg_mode FROM en.rtm_6_2th " \
            " WHERE (charg_s_c in (1,-1) or vehicle_s_c in (1,-1)) and deviceid like 'LSVA%' ORDER BY deviceid,uploadtime "
    aus=client.execute(sql1)
    d_time=[]
    mode=[]
    i=1
    while i<len(aus):
        if aus[i-1][0]==aus[i][0] and aus[i-1][3]==-1 and aus[i][2]==1:
            d=aus[i][1]-aus[i-1][1]
            d_time.append(d.seconds/60)
            mode.append(aus[i][4])
            i+=2
        else:
            i+=1
    workbook = xlsxwriter.Workbook("充电前时间间隔统计.xlsx")
    mode_interval=['mode2','mode3_2','mode3_1','DC']
    hist_func_np.hist_cros_con_dis_show(workbook,['充电前时间间隔'],np.array(d_time),[0,1,2,3,4,5,10,30,60,8000],np.array(mode),mode_interval)
    workbook.close()

#time_before_charge()


def BMS_temp_lavida():
    client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')

    sql="SELECT cast(mxtemp,'Int32'),cast(mitemp,'Int32') FROM en.rtm_data_june WHERE cast(mxtemp,'Int32')<200 and chargingstatus=='NO_CHARGING' and deviceid like 'LSVA%'"
    aus=client.execute(sql)
    max_temp_6_dr,min_temp_6_dr=[],[]
    for val in aus:
        max_temp_6_dr.append(val[0])
        min_temp_6_dr.append(val[1])
    
    sql="SELECT cast(mxtemp,'Int32'),cast(mitemp,'Int32') FROM en.rtm_data_june WHERE cast(mxtemp,'Int32')<200 and chargingstatus!='NO_CHARGING' and deviceid like 'LSVA%'"
    aus=client.execute(sql)
    max_temp_6_ch,min_temp_6_ch=[],[]
    for val in aus:
        max_temp_6_ch.append(val[0])
        min_temp_6_ch.append(val[1])
    
    sql="SELECT cast(mxtemp,'Int32'),cast(mitemp,'Int32') FROM en.rtm_vds WHERE cast(mxtemp,'Int32')<200 and chargingstatus=='NO_CHARGING' and deviceid like 'LSVA%'"
    aus=client.execute(sql)
    max_temp_3_dr,min_temp_3_dr=[],[]
    for val in aus:
        max_temp_3_dr.append(val[0])
        min_temp_3_dr.append(val[1])
    
    sql="SELECT cast(mxtemp,'Int32'),cast(mitemp,'Int32') FROM en.rtm_vds WHERE cast(mxtemp,'Int32')<200 and chargingstatus!='NO_CHARGING' and deviceid like 'LSVA%'"
    aus=client.execute(sql)
    max_temp_3_ch,min_temp_3_ch=[],[]
    for val in aus:
        max_temp_3_ch.append(val[0])
        min_temp_3_ch.append(val[1])
    
    workbook = xlsxwriter.Workbook("BMS温度分布.xlsx")
    name_list=['discharge_max','March','June']
    hist_func_np.hist_con_show(workbook,name_list,[np.array(max_temp_3_dr),np.array(max_temp_6_dr)],range(-10,70,5),2)
    name_list=['charge_max','March','June']
    hist_func_np.hist_con_show(workbook,name_list,[np.array(max_temp_3_ch),np.array(max_temp_6_ch)],range(-10,70,5),2)
    name_list=['discharge_min','March','June']
    hist_func_np.hist_con_show(workbook,name_list,[np.array(min_temp_3_dr),np.array(min_temp_6_dr)],range(-10,60,5),2)
    name_list=['charge_min','March','June']
    hist_func_np.hist_con_show(workbook,name_list,[np.array(min_temp_3_ch),np.array(min_temp_6_ch)],range(-10,60,5),2)
    workbook.close()







NEDC_path='D:/11test/01BEV-NEDC/1-lavida 53Ah/14 LBE734/vp426/D/'
NEDC_D=Rangetest('LBE734_NEDC_D',NEDC_path,'NEDC')
#NEDC_D.cut_range()
#range_dyno=295.9
#E_AC=38.055
#NEDC_D.sum_to_excel_NEDC(range_dyno,E_AC)
#NEDC_D.plot_v()



