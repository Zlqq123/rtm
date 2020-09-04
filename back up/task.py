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


def for_1_car(vin):
    sql="select deviceid, uploadtime,vehiclespeed, accmiles FROM ods.rtm_details WHERE deviceid=='"+vin+"' "
    aus=client.execute(sql)
    print_in_excel(aus,vin+'.xlsx')

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