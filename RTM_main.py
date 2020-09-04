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
import hist_func_np
from en_client import en_client


client=en_client()
path='D:/03RTM/ALL_RTM_data/0811/'


tb1_name="en.rtm_6_2th"
tb2_name="en.vehicle_vin"
tb_join=' INNER JOIN en.vehicle_vin on en.rtm_6_2th.deviceid=en.vehicle_vin.deviceid'
con="en.vehicle_vin.project=='Lavida BEV 53Ah'  AND en.vehicle_vin.d_mileage > 100 AND en.vehicle_vin.region=='MidEast'  AND en.vehicle_vin.user_typ=='Private'"
con="en.vehicle_vin.project=='Lavida BEV 53Ah'  AND en.vehicle_vin.d_mileage > 100 "
sampling=1/6

def Start_charge_temp_soc1():
    '''
    考察di温环境下充电起始电池温度SOC分布
    '''    
    path='D:/03RTM/ALL_RTM_data/0723/'
    tb1_name="en.rtm_2th"
    tb2_name="en.vehicle_vin"
    l1=RtmAna(path,'Lavida',client,tb1_name,tb2_name)
    l1.datetime_select('2020-01-01','2020-01-31')
    l1.generate_log_file()
    __,__,__,__,charg_soc,charg_temp,__=l1.charge_ana()
    a=charg_soc[0]
    b=charg_temp[4]
    workbook = xlsxwriter.Workbook("开始充电SOC_temp分布_diwen.xlsx")
    hist_func_np.hist_cros_2con_show(workbook,['SOC_temp'],charg_soc[0],range(0,115,5),charg_temp[4],range(-20,62,2))
    workbook.close()


vin="LSVUY60T3L2028579"
def for_1_car(vin):
    sql="select deviceid, uploadtime,vehiclespeed, accmiles FROM ods.rtm_details WHERE deviceid=='"+vin+"' "
    aus=client.execute(sql)
    print_in_excel(aus,vin+'.xlsx')


def Start_charge_temp_soc():
    '''
    考察高温环境下充电起始电池温度SOC分布
    '''
    path='D:/03RTM/ALL_RTM_data/0723/'
    tb1_name="en.rtm_6_2th"
    tb2_name="en.vehicle_vin"
    l1=RtmAna(path,'Lavida',client,tb1_name,tb2_name)
    l1.d_mile_condition_select(100)
    l1.generate_log_file()
    __, __, __, __, charg_soc, charg_temp, __ = l1.charge_ana()
    workbook = xlsxwriter.Workbook("开始充电SOC_temp分布.xlsx")
    hist_func_np.hist_cros_2con_show(workbook,['SOC_temp'],charg_soc[0],range(0,115,5),charg_temp[4],range(-20,62,2))
    workbook.close()





#target1、统计不同驾驶风格（针对BEV），（前提，相同地理位置，相同用户类型，相同附件消耗）统计其全电续驶里程和能耗差别



def Start_soc_mode():
    '''
    考察DC充电下开始充电SOC分布
    '''
    path='D:/03RTM/ALL_RTM_data/0723/'
    tb1_name="en.rtm_6_2th"
    tb2_name="en.vehicle_vin"
    l1=RtmAna(path,'Lavida',client,tb1_name,tb2_name)
    l1.d_mile_condition_select(100)
    l1.generate_log_file()
    [__,__,__,mode,charg_soc,__,__]=l1.charge_ana()
    workbook = xlsxwriter.Workbook("不同充电模式下开始充电SOC分布.xlsx")
    mode_interval=['mode2','mode3_2','mode3_1','DC']
    hist_func_np.hist_cros_con_dis_show(workbook,['dad'],charg_soc[0],range(0,110,5),mode,mode_interval)
    workbook.close()

#Start_soc_mode()


def time_before_charge():
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







