import sys
sys.path.append('./')
import xlsxwriter
import time
import csv
import numpy as np
import pandas as pd
#from range_test.range_test import Rangetest
#from RTM_ana import RtmAna
#from genarl_func import time_cost
#import hist_func_np
from en_client import en_client
#from default_hist import RtmHist
import os
#from RTM_ana import RtmAna
client=en_client()
from rtm_hist.default_hist import f1


sql="SELECT distinct deviceid from ods.rtm_details_v2 where deviceid like 'LSVAX40E__2______'"
df = pd.DataFrame(client.execute(sql))
print(df)

'''
deviceid like 'LSVUB%'  ID4x 82kWh
deviceid like 'LSVUA%'  ID4x 55kWh

Lavida BEV 53Ah	LSVAX40E××2××××××
	            LSVAX60E××2××××××
Tharu BEV 61Ah	LSVUZ6B2××N××××××
Lavida BEV 61Ah	LSVAV40E××2××××××
	            LSVAV60E××2××××××
Tiguan L PHEV C5	LSVUZ60T××2××××××
Tiguan L PHEV C6	LSVUY60T××2××××××
Passat PHEV C5	LSVCZ2C4××N××××××
	            LSVCZ6C4××N××××××
Passat PHEV C6	LSVCY2C4××N××××××
	            LSVCY6C4××N××××××

'''

sql="SELECT * from ods.rtm_details_v2 " \
    " where deviceid=='LSVUB6E43L2011932' order by uploadtime"
aus=client.execute(sql)
df = pd.DataFrame(aus)
df.to_csv('temp/LSVUB6E43L2011932.csv')

a=1
sql="WITH cast(emnum,'Float32') as m_num, cast(cel1num1,'Float32') as cell_num" \
    " SELECT deviceid, max(m_num), topK(2)(cell_num) FROM ods.rtm_details_v2 " \
    " WHERE (deviceid like 'LSVUB%' or deviceid like 'LSVUA%') AND emnum!='NULL' and cel1num1!= 'NULL' " \
    " GROUP BY deviceid"
aus=client.execute(sql)
df = pd.DataFrame(aus)
df.to_csv('MEB_VIN_0428-1.csv')


sql=" SELECT topK(10)(cel1num1) from ods.rtm_details_v2 " \
    " WHERE deviceid like 'LSVUB%' "
aus=client.execute(sql)
print(aus)






'''
sql="desc ods.rtm_details_v2"
aus=client.execute(sql)
df = pd.DataFrame(aus)
df.to_csv('rtm_details_v2.csv')
'''







sql="SELECT deviceid,uploadtime, cast(vehiclespeed,'Float32'), cast(accmiles,'Float32'),chargingstatus, vehiclestatus FROM ods.rtm_reissue_history WHERE deviceid == 'LSVUB6E45L2011107' "
aus=client.execute(sql)
df = pd.DataFrame(aus)

df.to_csv('LSVUB6E45L2011107.csv')


pro="Tiguan C6"
date_range=["2020-01-01","2020-11-20"]
region='all'
userType="Private"
fuc_name="fc11"
mile_range=['','']
df = f1(pro, date_range, region, userType, mile_range,fuc_name)
print(df)


sql="SELECT uniq(deviceid) FROM ods.rtm_reissue_history WHERE deviceid like 'LSVC%'"
aus=client.execute(sql)
print(aus[0][0])
path=os.getcwd()
print(path)



#l1=RtmHist(path,"ALL PHEV",'MidEast','ShangHai','Fleet',['2020-06-01','2020-06-03'],[100,3000])
#l1.daily_mileage()
l2=RtmHist(path,"lavida",date_range=['2020-06-01','2020-06-03'])
l2.count_nr()
l2.charge_soc()



tb1_name = "en.rtm_6_2th"
tb2_name = "en.vehicle_vin"
l1=RtmAna(path,"lavida",tb1_name,tb2_name)
l1.condition_printer()
l1(start_date='2020-06-01',end_date='2020-06-03')

l2.E_motor_workingPoint()
l2.E_motor_temp()
l2.percharge_mile()
a=1
def f1(proj,u):
    #path='D:/01zlq/temp/_'+u+'/'
    start=time.time()
    print("----------"+proj+'---'+u+'-----------')
    l1=RtmAna(path,proj,tb1_name,tb2_name)
    l1(user_type=u)
    dt=time.time()-start
    file=open(l1.log_filename,'a')
    file.write("------------------\r\n")
    file.write("running cost"+ str(round(dt,2))+"s \r\n")
    file.close()
    print("all_cost"+str(round(dt/60,2))+"min" )

f1("Lavida",'Taxi')
f1("Lavida",'Fleet')
f1("Lavida",'Private')


f1("Tiguan C5",'Taxi')
f1("Tiguan C6",'Taxi')
f1("Passat C5",'Taxi')
f1("Passat C6",'Taxi')

f1("Lavida",'Fleet')
f1("Tiguan C5",'Fleet')
f1("Tiguan C6",'Fleet')
f1("Passat C5",'Fleet')
f1("Passat C6",'Fleet')


f1("Tiguan C5",'Private')
f1("Tiguan C6",'Private')
f1("Passat C5",'Private')
f1("Passat C6",'Private')

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

def Start_soc_mode():
    '''
    考察DC充电下开始充电SOC分布
    '''
    path='D:/03RTM/ALL_RTM_data/0723/'
    tb1_name="en.rtm_6_2th"
    tb2_name="en.vehicle_vin"
    l1=RtmAna(path,'Lavida',tb1_name,tb2_name)
    l1.d_mile_condition_select(100)
    l1.generate_log_file()
    [__,__,__,mode,charg_soc,__,__]=l1.charge_ana()
    workbook = xlsxwriter.Workbook("不同充电模式下开始充电SOC分布.xlsx")
    mode_interval=['mode2','mode3_2','mode3_1','DC']
    hist_func_np.hist_cros_con_dis_show(workbook,['dad'],charg_soc[0],range(0,110,5),mode,mode_interval)
    workbook.close()





