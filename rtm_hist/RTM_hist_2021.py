import sys
sys.path.append("..")#sys.path.append("..")的意思是增加搜索的路径，..代表上一个目录层级

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
VIN Usertype Project region province mileage---------------- en.vehicle_vin(to be updata)

用于统计车辆行驶特性，包括里程，速度，驾驶模式，能耗估算，充电行为，电机工作点，电池工作点等。

更新日志：

    V7.3   2021/1/27
        判断开始充电算法更新： charging_stoppped与no_charging之间反复跳变视为没有开始充电
        充电时间算法更新：    充电过程中数据丢失，帧信号时间间隔>1800s，不计算充电时间
        充电模式算法更新：    充电过程中，平均电流<19A && （电芯中最高温度）平均值<50℃ ->AC充电   else：DC充电
    v7.2

    V7.1    2021/1/20
        增加模块：根据VIN码和时间查询工况特性

    V6.2
        输出dataframe,用于前端显示
    V6.1 
        基于sc的原始表  ods.rtm_reissue_history

    v5.3
        client delete
    V5.2
        自定义处理数据时间选择;
        添加call函数;
        添加绝缘阻值统计
    V5.1
        自定义region province usertype mileage_range d_mileage
    V5.0
        基于预处理表en.rtm_6_2th更新程序

    V4.3
        数据库tablename自定义
    V4.2
        车型项目为5种：Lavida  Passat C5  Passat C6  Tiguan C5 Tiguan C6
    V4.1
        添加能耗计算模块 Change in 【percharge_mile(self,workbook)】
        添加每个小时的行驶时间和行驶距离统计create 【hourly_mileage(self,workbook)】
        BMS工作点，电机工作点，添加自定义采样频率 Change in 【E_motor_sample(self,workbook)，BMS_sample(self,workbook):】
    V4.0：
        统计函数采用numpy,统计函数速度提升99.9%
'''


class RtmHist():
    def __init__ (self,proj):
        '''
        project must be in {'Lavida','Passat','Tiguan','Passat C5','Passat C6','Tiguan C5','Tiguan C6'}
        '''
        tb1,tb2='ods.rtm_reissue_history','en.vehicle_vin'
        # 表1为rtm数据表，表2为销售提供的静态表
        self.tb1=tb1
        self.tb2=tb2
        self.con1=" vehiclestatus!='ERROR' AND chargingstatus!='INVALID' AND chargingstatus!='ERROR' AND cocesprotemp1!='NULL' "
        self.con2=''
        # con1 针对表1的筛选条件  con2针对表2的筛选条件
        self.con=''
        
        self.pro_typ='ALL'
        self.proj='ALL'
        self.region='ALL'
        self.user_type='ALL'
        self.province='ALL'
        self.mile_range=[]
        self.time_range=[]
        self.vin='ALL'

        #create log file
        dt=datetime.now()
        self.log_filename="D:/21python/rtm/rtm_hist/log_file/"+str(dt)+"_log.txt"

    def project_select(self,proj):
        '''
        project must be in {'Lavida','Passat','Tiguan','Passat C5','Passat C6','Tiguan C5','Tiguan C6'}
        '''
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

    def location_select(self,region='ALL',province='ALL'):
        '''
        region must be in {'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}
        province must in {"GuangDong","ShangHai","TianJin","ZheJiang","HeBei","SiChuan","Shan3Xi","HeNan","FuJian","ShanDong","GuangXi", \
            "Shan1Xi","LiaoNing","ChongQing","JiangSu","HuBei","YunNan","HuNan","GuiZhou","JiangXi","AnHui","HanNan","GanSu", \
            "NingXia","XinJinag","JiLin","QingHai","NeiMeng","HeiLongJiang","BeiJing","XiZang"}
        '''
        self.region=region
        self.province=province
        if region!='ALL':
            ss = {'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}
            if region in ss:
                self.con2 + = " AND region=='"+region+"' "
            else:
                print("input error:region must be in {'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}")
                sys.exit(-1)
        if province!='ALL':
            ss={"GuangDong","ShangHai","TianJin","ZheJiang","HeBei","SiChuan","Shan3Xi","HeNan","FuJian","ShanDong","GuangXi", \
                "Shan1Xi","LiaoNing","ChongQing","JiangSu","HuBei","YunNan","HuNan","GuiZhou","JiangXi","AnHui","HanNan","GanSu", \
                "NingXia","XinJinag","JiLin","QingHai","NeiMeng","HeiLongJiang","BeiJing","XiZang"}
            if province in ss:
                self.con2 + = " AND province=='"+province+"' "
            else:
                print("input error:province must be in province_list")
                print(ss)
                sys.exit(-1)
    
    def time_select(self,start,end):
        '''
        start,end:yyyy-mm-dd        eg: 2020-06-01,2020-06-13
        start date must < end date
        '''
        a = start + " 00:00:00"
        b = end + " 23:59:59"
        try:
            aa = datetime.strptime(a,"%Y-%m-%d %H:%M:%S")
            bb = datetime.strptime(a,"%Y-%m-%d %H:%M:%S")
        except:
            print("input error:data must be yyyy-mm-dd  eg: 2020-06-01,2020-06-13")
            sys.exit(-1)
        else:
            if aa<bb:
                self.time_range=[start,end]
                self.con1 + =" AND uploadtime BETWEEN '"+a+"' AND '"+b+"'"
            else:
                print("input error:start data must be small than end date  eg: 2020-06-01,2020-06-13")
                sys.exit(-1)
    
    def mileage_select(self,start_mileage,end_mileage):
        '''
        start_mileage must be smaller than end_mileage
        '''
        if start_mileage < end_mileage and start_mileage >= 0:
            self.mile_range=[start_mileage,end_mileage]
            self.con1 + = " AND cast(accmiles,'Float32') >= "+str(start_mileage)+" AND cast(accmiles,'Float32') <= "+str(end_mileage)
        else:
            print("input error:start_mileage must be smaller than end_mileage ")
            sys.exit(-1)

    def user_type_select(self,user_type):
        '''
        user_type must be in {'Private', 'Fleet', 'Taxi'}
        '''
        self.user_type = user_type
        if user_type in {'Private', 'Fleet', 'Taxi'} :
            self.con1 + = " AND user_typ =='"+user_type+"' "
        else:
            print("input error:user_type must be in {'Private', 'Fleet', 'Taxi'}")
            sys.exit(-1)

    def vin_select(self,vin):
        '''
        '''
        self.vin = vin
        sql = "SELECT uploadtime FROM "+ self.tb1 + " WHERE deviceid== '" + vin + "' "
        aus = client.execute(sql)
        if len(aus)>0:
            self.con1 + = " AND deviceid== '" + vin + "' "
        else:
            print("invalid VIN")
            sys.exit(-1)

    def reset_select_condution(self):
        self.pro_typ='ALL'
        self.proj='ALL'
        self.region='ALL'
        self.user_type='ALL'
        self.province='ALL'
        self.mile_range=[]
        self.time_range=[]
        self.vin='ALL'

        self.con1=" vehiclestatus!='ERROR' AND chargingstatus!='INVALID' AND chargingstatus!='ERROR' AND cocesprotemp1!='NULL' "
        self.con2=''
        self.con=''

    def condition_printer(self):
        print("--SELECT condition:")
        print(self.con1)
        print(self.con2)
        print(self.con)

    def count_nr(self):
        if self.con2=="":
            self.con = "WHERE " + self.con1 
        else:
            self.con = "WHERE deviceid in (SELECT deviceid FROM " +self.tb2 +" WHERE "+self.con2+" ) AND " + self.con1 
        
        self.condition_printer()

        sql = "select uniq(deviceid) FROM " + self.tb1 + self.con
        print(sql)
        aus=client.execute(sql)

        print("车辆数目：")
        print(aus[0][0])
        return aus[0][0]

    def generate_log_file(self):
        dt=datetime.now()
        n = self.count_nr()
        file=open(self.log_filename,'a')
        file.write("\r\n####################################\r\n")
        file.write("##Running Date & Time："+str(dt)+"\r\n")
        file.write("##Project："+self.proj+"\r\n")
        file.write("##Region："+self.region+"  Province:"+self.province+"\r\n")
        file.write("##User Type："+self.user_type+"\r\n")
        file.write("##mile range："+str(self.mile_range)+"\r\n")
        file.write("##Vehicle Count："+str(n)+"辆\r\n")
        file.write("##Raw data date："+str(self.time_range) +" \r\n")
        file.write("##VIN ："+self.vin +" \r\n")
        file.write("####################################\r\n")
        file.close()


    def daily_mileage(self,step=range(0,500,20)):
        sql="WITH cast(accmiles,'Float32') AS mile " \
            "SELECT max(mile)-min(mile) FROM " + self.tb1 + self.con+ \
            " GROUP BY deviceid, toDate(uploadtime) "
        aus=pd.DataFrame(client.execute(sql))
        mile=np.array(aus[0])

        freq = hist_func_np.hist_con(mile,step)
        re1=pd.DataFrame(freq[1])
        re1.index=freq[0]
        re1.columns=['频数']
        re2 =  hist_func_np.box_hist(mile,'每日行驶里程[km]')

        return re1,re2

    def v_mode(self,step=[0,10,20,30,40,50,60,70,80,90,100,110,120,200],sampling=1/6):
        sql="SELECT cast(vehiclespeed,'Float32'), operationmode FROM "+ self.tb1 + self.con+  \
            " AND cast(vehiclespeed,'Float32')>0 AND toSecond(uploadtime)<"+str(int(sampling*60))
        print(sql)
        aus=pd.DataFrame(client.execute(sql))
        v=np.array(aus[0])
        mode=np.array(aus[1])

        freq = hist_func_np.hist_con(v,step)
        re1 = pd.DataFrame(freq[1])
        re1.index=freq[0]
        re1.columns=['频数']
        re2 =  hist_func_np.box_hist(v,'车速[km/h]')
        
        if self.pro_typ=="PHEV":
            [a,b,c] = hist_func_np.hist_con_dis(v,step,mode,['EV','PHEV',"FV"],show_hist=1)
            re3=pd.DataFrame(np.array(b).T)
            re3.index=a
            re3.columns=['EV','PHEV',"FV"]
            print(re3)
            re4=pd.DataFrame(np.array(c).T)
            re4.index=['min','1%percentile','25%percentile','50%percentile','75%percentile','99%percentile','max','mean']
            re4.columns=['EV','PHEV',"FV"]
            print(re4)
            return re1,re2, re3, re4
        else:
            return re1,re2

    def percharge_mile(self, step=range(0,500,20)):
        pass

    def pedal(self):
        pass
    
    def E_motor_temp(self,step=range(-10,120,5),sampling=1/6):
        pass

    def E_motor_power(self,sampling=1/6):
        pass

    def BMS_power(self,workbook,sampling=1/6):
        pass
    
    def BMS_workingpoint(self,workbook,sampling=1/6):
        pass

    def BMS_voltage(self):
        pass

    def SOH(self):
        pass

    def get_charge(self):
        pass

    def charge_ana(self):
        pass

    def charge_soc(self,step=range(0,120,10)):
        pass

    def charge_start_time(self,step = range(25)):
        pass

    def charge_time(self, step = [0,30,60,120,180,240,300,360,420,480,540,600,660,720,780,840,900,1500]):
        pass

    def charge_power(self):
        pass

    def charge_temp(self):
        pass

    def warming_hist(self,workbook):
        pass

    def insulation_resistance(self,workbook):
        pass












