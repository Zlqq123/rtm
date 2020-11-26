import sys
import xlsxwriter
import time
from datetime import datetime
import numpy as np
import pandas as pd

import hist_func_np
from genarl_func import time_cost,time_cost_all
from en_client import en_client
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
All data with warmingsignal Tiguan -------------en.rtm_tiguan  {'2018-01-01 00:00:00' ~~ '2020-12-31 23:59:59'}
'''

class RtmHist():
    '''
    用于统计车辆行驶特性，包括里程，速度，驾驶模式，能耗估算，充电行为，电机工作点，电池工作点等。
    基于sc的原始表  ods.rtm_reissue_history

    '''

    def __init__ (self,path,proj,region=0,province=0,user_type=0,date_range=[],mile_range=[]):
        '''
        project must be in {'Lavida','Passat','Tiguan','Passat C5','Passat C6','Tiguan C5','Tiguan C6','ALL BEV','ALL PHEV'}
        region must be in {'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}
        province must be in {"GuangDong","ShangHai","TianJin","ZheJiang","HeBei","SiChuan","Shan3Xi","HeNan","FuJian","ShanDong","GuangXi","NingXia","XinJinag","JiLin", \
            "Shan1Xi","LiaoNing","ChongQing","JiangSu","HuBei","YunNan","HuNan","GuiZhou","JiangXi","AnHui","HanNan","GanSu","QingHai","NeiMeng","HeiLongJiang","BeiJing","XiZang"}
        user_type must be in {'Private', 'Fleet', 'Taxi'}
        date_range=[start_date,end_date]:yyyy-mm-dd        eg: ['2020-06-01','2020-06-13']
        mile_range=[start_mileage,end_mileage]
        '''
        self.path=path
        tb1='ods.rtm_reissue_history'
        tb2='en.vehicle_vin'
        self.tb1=tb1
        self.tb2=tb2
        con1=""

        proj=proj.upper()
        self.proj=proj

        if proj=="LAVIDA" or proj=='All BEV':
            con2 = "project=='Lavida BEV 53Ah' "
            typ_v='BEV'
        else:
            typ_v='PHEV'
            if proj=="TIGUAN":
                con2 =  "project in ('Tiguan L PHEV C6', 'Tiguan L PHEV C5') "
            elif proj=="TIGUAN C5":
                con2 =  "project=='Tiguan L PHEV C5' "
            elif proj=="TIGUAN C6":
                con2 =  "project=='Tiguan L PHEV C6' "
            elif proj=="PASSAT":
                con2 =  "project in ('Passat PHEV C6', 'Passat PHEV C5') "
            elif proj=="PASSAT C5":
                con2 =  "project=='Passat PHEV C5' "
            elif proj=="PASSAT C6":
                con2 =  "project=='Passat PHEV C6' "
            elif proj=='ALL PHEV':
                con2 = "project in ('Tiguan L PHEV C6', 'Tiguan L PHEV C5', 'Passat PHEV C6', 'Passat PHEV C5') "
            else:
                print("input error:project must be in {'Lavida','Passat','Tiguan','Passat C5', 'Passat C6','Tiguan C5','Tiguan C6','ALL BEV','ALL PHEV'}")
                sys.exit(-1)
        
        
        if region!=0:
            ss={'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}
            if region in ss :
                con2 += " AND region=='"+region+"' "
            else:
                print("input error:region must be in {'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}")
                sys.exit(-1)
        
        if user_type!=0:
            if user_type in {'Private', 'Fleet', 'Taxi'} :
                con2 +=" AND user_typ=='"+user_type+"' "
            else:
                print("input error:user_type must be in {'Private', 'Fleet', 'Taxi'}")
                sys.exit(-1)

        if province!=0:
            ss={"GuangDong","ShangHai","TianJin","ZheJiang","HeBei","SiChuan","Shan3Xi","HeNan","FuJian","ShanDong","GuangXi", \
                "Shan1Xi","LiaoNing","ChongQing","JiangSu","HuBei","YunNan","HuNan","GuiZhou","JiangXi","AnHui","HanNan","GanSu", \
                "NingXia","XinJinag","JiLin","QingHai","NeiMeng","HeiLongJiang","BeiJing","XiZang"}
            if province in ss:
                con2 +=" AND province=='"+province+"' "
            else:
                print("input error:province must be in")
                print(ss)
                sys.exit(-1)

        if date_range!=[]:
            a=date_range[0]+" 00:00:00"
            b=date_range[1]+" 23:59:59"
            con1 +=" AND uploadtime BETWEEN '"+a+"' AND '"+b+"'"

        if mile_range!=[]:
            con1 +=" AND cast(accmiles,'Float32') >= "+str(mile_range[0])+" AND cast(accmiles,'Float32') <= "+str(mile_range[1])
        
        self.pro_typ=typ_v
        self.con=" WHERE deviceid in (SELECT deviceid FROM "+ tb2 +" WHERE "+con2+" ) "+ con1

        #print(self.con)
        
        
    def count_nr(self):
        sql = "select uniq(deviceid) FROM "+self.tb1 + self.con
        aus=client.execute(sql)
        
        return aus[0][0]
        
    def daily_mileage(self,step=range(0,500,20)):
        sql="WITH cast(accmiles,'Float32') AS mile " \
            "SELECT max(mile)-min(mile) FROM " + self.tb1 + self.con+ \
            " GROUP BY deviceid,toDate(uploadtime) "
        aus=pd.DataFrame(client.execute(sql))
        mile=np.array(aus[0])

        freq = hist_func_np.hist_con(mile,step)
        re=pd.DataFrame(freq[1])
        re.index=freq[0]
        re.columns=['daily mileage']
        re.loc['min']=np.min(mile)
        re.loc['1%percentile']=np.percentile(mile,1)
        re.loc['25%percentile']=np.percentile(mile,25)
        re.loc['50%percentile']=np.percentile(mile,50)
        re.loc['75%percentile']=np.percentile(mile,75)
        re.loc['99%percentile']=np.percentile(mile,99)
        re.loc['max']=np.max(mile)
        re.loc['mean']=np.mean(mile)

        print(re)
        return re

    def v_mode(self,workbook,step=[0,10,20,30,40,50,60,70,80,90,100,110,120,200],sampling=1/6):
        sql="SELECT cast(vehiclespeed,'Float32'),operationmode FROM "+ self.tb1 + self.con+  \
            "AND　cast(vehiclespeed,'Float32')>0 and toSecond(uploadtime)<"+str(int(sampling*60))
        aus=pd.DataFrame(client.execute(sql))
        v=np.array(aus[0])
        mode=np.array(aus[1])

        freq = hist_func_np.hist_con(v,step)
        re1 = pd.DataFrame(freq[1])
        re1.index=freq[0]
        re1.columns=['velocity']
        re1.loc['min']=np.min(v)
        re1.loc['1%percentile']=np.percentile(v,1)
        re1.loc['25%percentile']=np.percentile(v,25)
        re1.loc['50%percentile']=np.percentile(v,50)
        re1.loc['75%percentile']=np.percentile(v,75)
        re1.loc['99%percentile']=np.percentile(v,99)
        re1.loc['max']=np.max(v)
        re1.loc['mean']=np.mean(v)
        freq=[]

        if self.pro_typ=="PHEV":
            [block,re,re2] = hist_func_np.hist_con_dis(v,step,mode,['EV','PHEV',"FV"])
            print(freq)
    





