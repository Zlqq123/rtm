import xlsxwriter
import time
import numpy as np
import hist_func_np
import sys
from datetime import datetime

'''
V4.0
统计函数采用numpy,统计函数速度提升99.9%
hist function 138.67->0.88
综合速度提升？
passat 5421-> 1146 提升79%
tiguan 2408->391 提升83%

V4.1
添加能耗计算模块 Change in 【percharge_mile(self,workbook)】
添加每个小时的行驶时间和行驶距离统计create 【hourly_mileage(self,workbook)】
BMS工作点，电机工作点，添加自定义采样频率 Change in 【E_motor_sample(self,workbook)，BMS_sample(self,workbook):】

V4.2
车型项目为5种：Lavida  Passat C5  Passat C6  Tiguan C5 Tiguan C6

V4.3
数据库tablename自定义

V5.0
基于预处理表en.rtm_6_2th更新程序
六月数据预处理表：en.rtm_6_2th
车辆vin码对应客户信息+里程：en.vehicle_vin 
V5.1
自定义region province usertype mileage_range d_mileage


'''

class RtmAna():
    def __init__ (self,path,proj,client,tb1_name,tb2_name):
        '''
        project must be in {'Lavida','Passat','Tiguan','Passat C5','Passat C6','Tiguan C5','Tiguan C6'}
        '''
        self.path=path
        self.client=client
        self.tb1_name=tb1_name
        self.tb2_name=tb2_name

        if proj=="Lavida":
            con_pro= tb2_name + ".project=='Lavida BEV 53Ah' "
            typ_v='BEV'
        else:
            typ_v='PHEV'
            if proj=="Tiguan":
                con_pro= tb2_name + ".project in {'Tiguan L PHEV C6', 'Tiguan L PHEV C5'} "
            elif proj=="Tiguan C5":
                con_pro= tb2_name + ".project=='Tiguan L PHEV C5' "
            elif proj=="Tiguan C6":
                con_pro= tb2_name + ".project=='Tiguan L PHEV C6' "
            elif proj=="Passat":
                con_pro= tb2_name + ".project in {'Passat PHEV C6', 'Passat PHEV C5'} "
            elif proj=="Passat C5":
                con_pro= tb2_name + ".project=='Passat PHEV C5' "
            elif proj=="Passat C6":
                con_pro= tb2_name + ".project=='Passat PHEV C6' "
            else:
                print("input error:project must be in {'Lavida','Passat','Tiguan','Passat C5','Passat C6','Tiguan C5','Tiguan C6'}")
                sys.exit(-1)
        
        self.con=con_pro
        self.tb_join=" INNER JOIN "+tb2_name+" on "+ tb1_name +".deviceid="+tb2_name+".deviceid " 

        self.proj=proj
        self.pro_typ=typ_v
        self.con_pro=con_pro
        self.region='ALL'
        self.user_type='ALL'
        self.d_mile_condition=0
        self.province='ALL'
        self.mile_range=[]

        #create log file
        dt=datetime.now()
        self.log_filename=path+str(dt.date())+"_log.txt"

    def region_select(self,region):
        '''
        region must be in {'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}
        '''
        self.region=region
        ss={'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}
        if region in ss :
            self.con+=" AND "+self.tb2_name+".region=='"+region+"' "
        else:
            print("input error:region must be in {'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}")
            sys.exit(-1)

    def user_type_select(self,user_type):
        '''
        user_type must be in {'Private', 'Fleet', 'Taxi'}
        '''
        self.user_type=user_type
        if user_type in {'Private', 'Fleet', 'Taxi'} :
            self.con+=" AND "+self.tb2_name+".user_typ=='"+user_type+"' "
        else:
            print("input error:user_type must be in {'Private', 'Fleet', 'Taxi'}")
            sys.exit(-1)
    
    def mileage_select(self,start_mileage,end_mileage):
        self.mile_range=[start_mileage,end_mileage]
        self.con+=" AND "+self.tb2_name+ ".mile_min>="+str(start_mileage)+" AND "+self.tb2_name+ ".mile_min<="+str(end_mileage)

    def province_select(self,province):
        self.province=province
        ss={"GuangDong","ShangHai","TianJin","ZheJiang","HeBei","SiChuan","Shan3Xi","HeNan","FuJian","ShanDong","GuangXi", \
            "Shan1Xi","LiaoNing","ChongQing","JiangSu","HuBei","YunNan","HuNan","GuiZhou","JiangXi","AnHui","HanNan","GanSu", \
            "NingXia","XinJinag","JiLin","QingHai","NeiMeng","HeiLongJiang","BeiJing","XiZang"}
        if province in ss:
            self.con+=" AND "+self.tb2_name+".province=='"+province+"' "
        else:
            print("input error:province must be in")
            print(ss)
            sys.exit(-1)

    def d_mile_condition_select(self,d_mile_condition):
        self.d_mile_condition=d_mile_condition
        self.con+=" AND "+self.tb2_name+ ".d_mileage>"+str(d_mile_condition)

    def reset_select_condution(self):
        self.con=self.con_pro
        self.province="All"
        self.region="All"
        self.user_type="All"
        self.d_mile_condition=0
        self.mile_range=[]

    def generate_log_file(self):
        sql = "select uniq(deviceid) from "+self.tb2_name+" Where "+self.con
        aus=self.client.execute(sql)
        dt=datetime.now()
        file=open(self.log_filename,'a')
        file.write("\r\n####################################\r\n")
        file.write("##Running Date & Time："+str(dt)+"\r\n")
        file.write("##Project："+self.proj+"\r\n")
        file.write("##Region："+self.region+"  Province:"+self.province+"\r\n")
        file.write("##User Type："+self.user_type+"\r\n")
        file.write("##mile range："+str(self.mile_range)+"  d_mile_condition:>"+str(self.d_mile_condition)+"\r\n")
        file.write("##Vehicle Count："+str(aus[0][0])+"辆\r\n")
        file.write("##Raw data date：2020/06/01~2020/06/30 \r\n")
        file.write("####################################\r\n")
        file.close()

    def condition_printer(self):
        print("------------tb_jion:")
        print(self.tb_join)
        print("------------SELECT condition:")
        print(self.con)

    '''
    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_value,exc_trackback):
        pass

    def __call__(self):
        pass
    '''

    def daily_mileage(self,workbook):
        sql="SELECT max(accmiles)-min(accmiles) FROM " +self.tb1_name+ self.tb_join+ \
            " where "+ self.con+" group by deviceid,toDate(uploadtime) "
        aus=self.client.execute(sql)
        mileage=[]
        for value in aus:
            mileage.append(value[0])
        
        hist_func_np.hist_con_show(workbook,["daily_mile",'mileage per day'],[np.array(mileage)],range(0,500,20),2)

    def percharge_mile(self,workbook):
        sql="SELECT deviceid,uploadtime,charg_s_c,soc,soc_c,accmiles " \
            "FROM " +self.tb1_name+ self.tb_join+ " WHERE " + self.con + " AND "+ self.tb1_name +".charg_s_c IN (1,-1) ORDER BY deviceid,uploadtime "
        aus=self.client.execute(sql)
        #aus=[0 vin  1 时间  2充电变化标志位  3 soc   4 d_soc  5 mileage ]
        all_drive=[]
        count_1=0#基数多少次行驶前数据丢失
        count_2=0#计数行驶后数据丢失
        count_12=0#行驶前，行驶后均数据丢失
        i=1
        while i<len(aus):
            if aus[i][0]==aus[i-1][0] and aus[i-1][2]==-1 and aus[i][2]==1:#i-1时刻是开始行驶，i是结束行驶时刻
                i+=2
                start_d_soc=aus[i-1][4]
                end_d_soc=aus[i][4]
                if abs(start_d_soc)>5 or abs(end_d_soc)>5:
                    if abs(start_d_soc)>5:
                        count_1+=1
                    if abs(end_d_soc)>5:
                        count_2+=1
                    if abs(start_d_soc)>5 and abs(end_d_soc)>5:
                        count_12+=1
                elif aus[i-1][3]>aus[i][3] and aus[i-1][5]<aus[i][5]:# 行驶过程中SOC减少，里程增加
                    all_drive.append([aus[i][0],aus[i-1][1],aus[i][1],aus[i-1][3],aus[i][3],aus[i-1][5],aus[i][5]])
                    #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
            else:
                i+=1
        l1=len(all_drive)+count_1+count_2-count_12
        
        soc_r=[]
        mile_r=[]
        mile_r_c=[]
        Energy_consump=[]

        for i,a in enumerate(all_drive):
            soc_r.append(a[3]-a[4])
            mile_r.append(a[6]-a[5])
            mile_r_c.append((a[6]-a[5])/(a[3]-a[4])*100)
        
        l2=len(mile_r_c)
        file=open(self.log_filename,'a')
        file.write("------mile perCharging analysis---------\r\n")
        file.write("原始行驶次数："+str(l1)+"\r\n")
        file.write("充电前数据丢失次数："+str(count_1)+"占比："+str(round(count_1/l1*100,2))+"%\r\n")
        file.write("充电后数据丢失次数："+str(count_2)+"占比："+str(round(count_2/l1*100,2))+"%\r\n")
        file.write("充电前后数据均丢失次数："+str(count_12)+"占比："+str(round(count_12/l1*100,2))+"%\r\n")
        file.write("处理后行驶次数："+str(l2)+"\r\n")
        file.close()

        name_list=['mile_perCharging','mile_perCharging','mile_convert']
        in_list=[np.array(mile_r),np.array(mile_r_c)]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(0,500,20),2)

        if self.pro_typ=='BEV':
            charging_energy=37 #lavida BEV 实际SOC96~8% 冲入电量37kWh,来源NEDC充电测试平均值
            for a in all_drive:
                Energy_consump.append(charging_energy*(a[3]-a[4])/(a[6]-a[5]))
            hist_func_np.hist_con_show(workbook,['Energy consumption','Energy consumption'],[np.array(Energy_consump)],np.arange(6,30,0.5),2)

    '''
    def hourly_mileage(self,workbook):
        sql="SELECT deviceid,toDate(uploadtime),toHour(uploadtime),max(CAST(accmiles,'float')),min(CAST(accmiles,'float')),COUNT(deviceid) " \
            "from " +self.tb_name+" where vehiclestatus=='STARTED' AND "+ self.con+" group by deviceid,toDate(uploadtime),toHour(uploadtime) "
        aus=self.client.execute(sql)
        mileage_h=[]
        hour=[]
        durate=[]
        for value in aus:
            if value[3]>value[4]:
                hour.append(value[2])
                mileage_h.append(value[3]-value[4])
                if value[5]<120:
                    durate.append(value[5]*0.5)
                else:
                    durate.append(60)
        
        hist_func_np.hist_cros_con_dis_show(workbook,["hourly_mileage"],np.array(mileage_h),[0,5,10,15,20,30,40,60,100,200],np.array(hour),range(24))
        hist_func_np.hist_cros_con_dis_show(workbook,["hourly_driving_time"],np.array(durate),range(0,65,5),np.array(hour),range(24))
    '''
    def v_mode(self,workbook,sampling=1/6):
        sql="SELECT vehiclespeed,operationmode FROM " + self.tb1_name + self.tb_join+  \
            " Where "+ self.con+ " AND "+ self.tb1_name +".vehiclespeed>0 and toSecond(uploadtime)<"+str(int(sampling*60))
        aus=self.client.execute(sql)
        v,mode=[],[]
        for value in aus:
            v.append(value[0])
            mode.append(value[1])
        hist_func_np.hist_con_show(workbook,['v','vehicle speed km/h'],[np.array(v)],[0,10,20,30,40,50,60,70,80,90,100,110,120,200],2)
        if self.pro_typ=="PHEV":
            hist_func_np.hist_cros_con_dis_show(workbook,["driving mode"],np.array(v),[0,10,20,30,40,50,60,70,80,90,100,110,120,200],np.array(mode),['EV','PHEV',"FV"])

    def get_drive(self,workbook):
        sql="SELECT deviceid,uploadtime,vehicle_s_c,accmiles,soc,soc_c FROM " +self.tb1_name+ self.tb_join+ \
            " WHERE " + self.con + " AND "+self.tb1_name+".vehicle_s_c in (1,-1) ORDER BY deviceid,uploadtime"
        aus=self.client.execute(sql)
        #aus=[0 vin  1 time  2车辆状态变化标志位（-1start->stop 1stop->start）  3 mileage   4 soc   5 d_soc]
        all_drive=[]        
        #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]

        count_1=0#行驶前数据丢失计数
        count_2=0#行驶后的数据丢失计数
        count_12=0#行驶前，行驶后均数据丢失

        i=1
        while i<len(aus):
            if aus[i][0]==aus[i-1][0] and aus[i-1][2]==1 and aus[i][2]==-1:
                #aus[i-1]: Start drving(stop->start)，aus[i]: Stop drving(start->stop)
                start_d_soc=aus[i-1][5]
                end_d_soc=aus[i][5]
                if abs(start_d_soc)>5 or abs(end_d_soc)>5:
                    if abs(start_d_soc)>5:
                        count_1+=1
                    if abs(end_d_soc)>5:
                        count_2+=1
                    if abs(start_d_soc)>5 and abs(end_d_soc)>5:
                        count_12+=1
                elif aus[i-1][3]<aus[i][3]: # mileage increase
                    all_drive.append([aus[i][0],aus[i-1][1],aus[i][1],aus[i-1][4],aus[i][4],aus[i-1][3],aus[i][3]])
                    #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
                i+=2
            else:
                i+=1
        l1=len(all_drive)+count_1+count_2-count_12

        i=1
        count_3=0#计数合并行驶情况
        while i<len(all_drive):
            d=all_drive[i][1]-all_drive[i-1][2]
            if all_drive[i-1][0]==all_drive[i][0] and (d.seconds<300 or all_drive[i][6]-all_drive[i][5]<1):
                #如果两次行驶间隔小于3分钟或者行驶距离小于1km,合并为同一次行驶。前提是同一辆车。
                count_3+=1
                all_drive[i-1][2]=all_drive[i][2]
                all_drive[i-1][4]=all_drive[i][4]
                all_drive[i-1][6]=all_drive[i][6]
                all_drive.pop(i)
            else:
                i+=1
        
        l2=len(all_drive)

        file=open(self.log_filename,'a')
        file.write("---------driving analysis--------------\r\n")
        file.write("原始行驶次数："+str(l1)+"\r\n")
        file.write("行驶前数据丢失次数："+str(count_1)+"占比："+str(round(count_1/l1*100,2))+"%\r\n")
        file.write("行驶后数据丢失次数："+str(count_2)+"占比："+str(round(count_2/l1*100,2))+"%\r\n")
        file.write("行驶前后数据均丢失次数："+str(count_12)+"占比："+str(round(count_12/l1*100,2))+"%\r\n")
        file.write("行驶合并次数："+str(count_3)+"占比："+str(round(count_3/l1*100,2))+"%\r\n")
        file.write("处理后行驶次数："+str(l2)+"\r\n")
        file.close()

        time_h_s,time_d=[],[]
        soc_s,soc_e,soc_d=[],[],[]
        mile_d,mile_d_c=[],[]
        v_mean=[]

        for a in all_drive:
            time_h_s.append(a[1].hour)
            d=a[2]-a[1]
            time_d.append(d.seconds/60)
            soc_s.append(a[3])
            soc_e.append(a[4])
            soc_d.append(a[3]-a[4])
            mile_d.append(a[6]-a[5])
            if a[4]-a[3]>1:
                mile_d_c.append((a[6]-a[5])/(a[3]-a[4])*100)
            if d.seconds>60:
                v_mean.append((a[6]-a[5])/d.seconds*3.6)

        hist_func_np.hist_cros_con_dis_show(workbook,['24h_drvingtime'],np.array(time_d),[0,10,20,30,60,90,120,1500],np.array(time_h_s),range(24))
        hist_func_np.hist_cros_con_dis_show(workbook,['24h_mile'],np.array(mile_d),[0,10,20,30,40,50,60,80,100,1500],np.array(time_h_s),range(24))

        '''
        name_list=['driving_Start_Hour','start time']
        hist_func_np.hist_con_show(workbook,name_list,[time_h_s],range(25))

        name_list=['driving_time','driving_time']
        hist_func_np.hist_con_show(workbook,name_list,[time_d],[0,10,20,30,60,90,120,1500],2)
        
        name_list=['SOC','start_SOC','end_SOC']
        in_list=[soc_s,soc_e]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(0,120,10),2)

        name_list=['mile_perCharging(to delete)','mile_perCharging','mile_convert']
        in_list=[mile_d,mile_d_c]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(0,500,20),2)

        name_list=['mean_V','mean_V(Including idle speed)']
        hist_func_np.hist_con_show(workbook,name_list,[v_mean],[0,10,20,30,40,50,60,100,210],2)
        '''

    def E_motor(self,workbook,sampling=1/6):
        '''
        sampling自定义采样频率 取值范围[1/60,1]
        '''
        sql="SELECT emspeed,emtq,em_eff,emctltemp,emtemp " \
            " FROM " +self.tb1_name+ self.tb_join+ " WHERE " + self.con + " AND "+ self.tb1_name +".emstat !='CLOSED'" \
            " AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=self.client.execute(sql)
        #aus=[0 em_speed  1 em_torq  2en_efficincy  3 LE_temperature   4 motor_temperature ]
        speed,torq,eff=[],[],[]
        temp_motor,temp_LE=[],[]
        for value in aus:
            temp_motor.append(value[4])
            temp_LE.append(value[3])
            if value[0]!=0 and value[1]!=0:
                speed.append(value[0])
                torq.append(value[1])
                if value[2]>0 and value[2]<1:
                    eff.append(value[2]*100)
        l1=len(temp_LE)
        l2=len(speed)
        l3=len(eff)
        file=open(self.log_filename,'a')
        file.write("-------E-Motor Working Point Analysis---------\r\n")
        file.write("原始抓取点数："+str(l1)+"\r\n")
        file.write("去除转矩为零或转速为零之后工作点数："+str(l2)+"   占比："+str(round(l2/l1*100,2))+"%\r\n")
        file.write("效率值在合理范围数："+str(l3)+"   占比："+str(round(l3/l2*100,2))+"%\r\n")
        file.close()
        
        hist_func_np.hist_con_show(workbook,["LE-eff",'LE_efficiency'],[np.array(eff)],[0,20,40,50,60,62,64,66,68,70,72,74,76,78,80,82,84,86,88,90,92,94,96,98,100],2)
        hist_func_np.hist_con_show(workbook,["LE-temp",'E_motor temperature','LE temperature'],[np.array(temp_motor),np.array(temp_LE)],range(-10,120,5),2)
        hist_func_np.hist_cros_2con_show(workbook,['LE_working_point'],np.array(speed),range(-4000,13000,500),np.array(torq),range(-300,400,50))
    
    def power_distribution(self,workbook,sampling=1/6):
        '''
        sampling自定义采样频率 取值范围[1/60,1]
        '''
        sql="SELECT accpedtrav,brakepedstat,BMS_pow,em_me_pow,em_el_pow,other_pow " \
            " FROM " +self.tb1_name+ self.tb_join+ " WHERE " + self.con + " AND "+ self.tb1_name +".vehicle_s ==1" \
            " AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=self.client.execute(sql)
        #aus=[0加速踏板  1制动踏板  2电池放电功率  3 电机机械输出功率 4 电机电功率 5附件消耗功率 ]
        BMS_pow,em_me_pow,em_el_pow,other_pow=[],[],[],[]
        for value in aus:
            BMS_pow.append(value[2])
            em_me_pow.append(value[3])
            em_el_pow.append(value[4])
            other_pow.append(value[5])
        name_list=['power_distribution','BMS_power','em_el_pow','other_pow']
        in_list=[np.array(BMS_pow),np.array(em_el_pow),np.array(other_pow)]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(50),2)

    def BMS(self,workbook,sampling=1/6):
        '''
        sampling自定义采样频率 取值范围[1/60,1]
        '''
        #discharging
        sql="SElECT soc,cocesprotemp1_mean,BMS_pow FROM " +self.tb1_name+ self.tb_join+  \
            " WHERE " + self.con + " AND "+ self.tb1_name + ".charg_s==0 AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=self.client.execute(sql)

        soc,temp_av,pow_bms=[],[],[]
        for value in aus:
            soc.append(value[0])
            temp_av.append(value[1])
            pow_bms.append(value[2])
        
        hist_func_np.hist_cros_2con_show(workbook,['discharging'],np.array(soc),range(0,115,5),np.array(temp_av),range(-30,65,5))

        #charging
        soc,temp_av,pow_bms=[],[],[]
        sql="SElECT soc,cocesprotemp1_mean,BMS_pow FROM " +self.tb1_name+ self.tb_join+  \
            " WHERE " + self.con + " AND "+ self.tb1_name + ".charg_s==1 AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=self.client.execute(sql)
        soc,temp_av,pow_bms=[],[],[]
        for value in aus:
            soc.append(value[0])
            temp_av.append(value[1])
            pow_bms.append(value[2])
        
        hist_func_np.hist_cros_2con_show(workbook,['charging'],np.array(soc),range(0,115,5),np.array(temp_av),range(-30,65,5))
    
    def get_Charge(self):
        '''
        return all_charge=i*[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6 end_mile ]
        '''
        sql1="SELECT deviceid,uploadtime,charg_s_c,soc,soc_c,accmiles FROM " + self.tb1_name + self.tb_join+ \
            " WHERE " + self.con + " AND "+ self.tb1_name +".charg_s_c IN (1,-1) ORDER BY deviceid,uploadtime "
        aus=self.client.execute(sql1)
        #aus=[0 vin  1 time  2充电变化标志位  3 soc   4 d_soc  5 mileage ]
        all_charge=[]        
        #all_charge=[0vin,1time_start,2time_end]
        temp=[]
        #temp=[0soc_start,1soc_end,2mile_start,3end_mile ]
        i=1

        count_1=0#基数多少次充电前数据丢失
        count_2=0#计数充电结束的数据丢失
        count_12=0#充电前，充电后均数据丢失

        while i<len(aus):
            if aus[i][0]==aus[i-1][0] and aus[i-1][2]==1 and aus[i][2]==-1:#i-1时刻是开始充电，i是结束充电时刻
                start_d_soc=aus[i-1][4]
                end_d_soc=aus[i][4]
                if abs(start_d_soc)>5 or abs(end_d_soc)>5:
                    if abs(start_d_soc)>5:
                        count_1+=1
                    if abs(end_d_soc)>5:
                        count_2+=1
                    if abs(start_d_soc)>5 and abs(end_d_soc)>5:
                        count_12+=1
                else:
                    all_charge.append([aus[i][0],aus[i-1][1],aus[i][1]])
                    #all_charge=[0vin,1time_start,2time_end]
                    temp.append([aus[i-1][3],aus[i][3],aus[i-1][5],aus[i][5]])
                    #temp=[0soc_start,1soc_end,2mile_start,3end_mile ]
                i+=2
            else:
                i+=1
        l1=len(all_charge)+count_1+count_2-count_12
        
        i=1
        count_3=0#计数合并充电情况
        count_31=0#计数合并充电情况中充电中断时间过长>30分钟
        while i<len(all_charge):
            if all_charge[i-1][0]==all_charge[i][0] and temp[i-1][3]==all_charge[i][2] and temp[i-1][1]==all_charge[i][0]:
                #如果上一次充电结束的里程与下一次开始充电的里程不变，合并为一次充电。前提是同一辆车。
                count_3+=1
                d=all_charge[i][1]-all_charge[i-1][2]
                if d.seconds/60>30:
                    count_31+=1
                all_charge[i-1][2]=all_charge[i][2]
                temp[i-1][1]=temp[i][1]
                temp[i-1][3]=temp[i][3]
                all_charge.pop(i)
                temp.pop(i)
            else:
                i+=1
        l2=len(all_charge)

        file=open(self.log_filename,'a')
        file.write("---------charge analysis---------\r\n")
        file.write("原始充电次数："+str(l1)+"\r\n")
        file.write("充电前数据丢失次数："+str(count_1)+"占比："+str(round(count_1/l1*100,2))+"%\r\n")
        file.write("充电后数据丢失次数："+str(count_2)+"占比："+str(round(count_2/l1*100,2))+"%\r\n")
        file.write("充电前后数据均丢失次数："+str(count_12)+"占比："+str(round(count_12/l1*100,2))+"%\r\n")
        file.write("充电合并次数："+str(count_3)+"占比："+str(round(count_3/l1*100,2))+"%\r\n")
        file.write("充电合并次数中充电中断时间过长>30分钟："+str(count_31)+"占比："+str(round(count_31/l1*100,2))+"%\r\n")
        file.write("处理后充电次数："+str(l2)+"\r\n")
        file.close()

        return all_charge

    def charge_ana(self):
        '''
        input:  all_charge=i*[0vin,1time_start,2time_end]
        return  [np.array(time_h_s),np.array(time_d),np.array(time_d_c),np.array(mode),charg_soc,charg_temp,charg_pow]
                charg_soc=[np.array(soc_s),np.array(soc_e),np.array(soc_d)]
                charg_temp=[np.array(temp_s),np.array(temp_e),np.array(temp_min),np.array(temp_max),np.array(temp_mean),np.array(temp_range)]
                charg_pow=[np.array(power_max),np.array(power_mean)]
        '''
        all_charge=self.get_Charge()

        sql="SELECT deviceid,uploadtime,-BMS_pow,cocesprotemp1_mean,soc,charg_mode " \
            "FROM " +self.tb1_name + self.tb_join+" WHERE "+ self.con+ " AND "+ self.tb1_name +".charg_s==1 " \
            "ORDER BY deviceid,uploadtime"
        aus=self.client.execute(sql)
        #aus=[i][0vin 1time, 2 BMS_power 3temp 4soc 5charg_mode]

        ss,ee=[],[]#用于存放aus中每段充电开始的index 和每次充电结束的index
        i,j=0,0 #j为all_charge的index      i 为aus的index
        mode=[]#与ss,ee过程变量相同长度的mode

        for j in range(len(all_charge)):#根据all_charge中每次充电开始时间，找到aus中每次充电开始-结束时间
            if ss==[]: 
                i=0
            else:
                i=ee[-1]#每次i从上次充电结束的时候开始搜索
            ff=0 # 找不找得到的flag ff=0开始点找不到，ff=1开始点找到了 结束点找不到，ff=2都找到了
            while aus[i][0]<=all_charge[j][0] and ff==0 and i<len(aus): #如果vin码已经搜索到下一辆车，循环停止#如果找到了，ff=1循环停止
                if all_charge[j][0]==aus[i][0] and all_charge[j][1]==aus[i][1]:
                    #找到aus中vin码和时间与all_charge中开始时间完全相同的数据条，index保存在ss中
                    ff=1
                    ss.append(i)
                else:
                    i+=1
            while aus[i][0]<=all_charge[j][0] and ff==1 and i<len(aus)-1:
                if all_charge[j][0]==aus[i][0] and aus[i][1]<all_charge[j][2] and aus[i+1][1]>all_charge[j][2] and aus[i+1][0]==all_charge[j][0]:
                    #找到aus中vin码和All_charge 相同，时间与all_charge中结束时间最接近的数据条，index保存在ee中
                    ff=2
                    ee.append(i)
                else:
                    i+=1
            if ff==1:#如果只找到开始点，没找到结束点
                ss.pop()
            if ff==2 and aus[ee[-1]][4]<=aus[ss[-1]][4]:#保证结束点位置大于开始点位置，保证充电过程中SOC有增加
                ss.pop()
                ee.pop()

        file=open(self.log_filename,'a')
        file.write("未匹配的充电次数："+str(len(all_charge)-len(ss))+"占比："+str(round((1-len(ss)/len(all_charge))*100,2))+"%\r\n")
        file.write("匹配的充电次数："+str(len(ss))+"\r\n")
        file.close()
       
        temp_s,temp_e,temp_min,temp_max,temp_mean,temp_range=[],[],[],[],[],[]
        power_max,power_mean=[],[]
        temp_a,pow_a=[],[]#中间过程量
        time_h_s,time_d,time_d_c=[],[],[]
        soc_s,soc_e,soc_d=[],[],[]
        
        for i in range(len(aus)):
            pow_a.append(aus[i][2])
            temp_a.append(aus[i][3])

        for i in range(len(ss)):
            mode.append(aus[ss[i]][5])
            power_max.append(max(pow_a[ss[i]:ee[i]]))
            power_mean.append(sum(pow_a[ss[i]:ee[i]])/len(pow_a[ss[i]:ee[i]]))
            temp_s.append(temp_a[ss[i]])
            temp_e.append(temp_a[ss[i]])
            temp_min.append(min(temp_a[ss[i]:ee[i]]))
            temp_max.append(max(temp_a[ss[i]:ee[i]]))
            temp_mean.append(sum(temp_a[ss[i]:ee[i]])/len(temp_a[ss[i]:ee[i]]))
            temp_range.append(max(temp_a[ss[i]:ee[i]])-min(temp_a[ss[i]:ee[i]]))
            soc_s.append(aus[ss[i]][4])
            soc_e.append(aus[ee[i]][4])
            soc_d.append(aus[ee[i]][4]-aus[ss[i]][4])
            d=aus[ee[i]][1]-aus[ss[i]][1]
            time_d.append(d.seconds/60)
            time_d_c.append(d.seconds/60/(aus[ee[i]][4]-aus[ss[i]][4])*100)
            time_h_s.append(aus[ss[i]][1].hour)
        
        charg_temp=[np.array(temp_s),np.array(temp_e),np.array(temp_min),np.array(temp_max),np.array(temp_mean),np.array(temp_range)]
        charg_pow=[np.array(power_max),np.array(power_mean)]
        charg_soc=[np.array(soc_s),np.array(soc_e),np.array(soc_d)]

        return np.array(time_h_s),np.array(time_d),np.array(time_d_c),np.array(mode),charg_soc,charg_temp,charg_pow

    def charg_hist(self,workbook):
        [time_h_s,time_d,time_d_c,mode,charg_soc,charg_pow,charg_temp]=self.charge_ana()

        name_list=['charg_SOC','start_SOC','end_SOC','soc_range']
        hist_func_np.hist_con_show(workbook,name_list,charg_soc,range(0,120,10),2)
        #hist_func_np.hist_cros_2con_show(workbook,['charg_SOC_cros'],charg_soc[0],range(0,120,10),charg_soc[1],range(0,120,10))
        
        name_list=['Charg_Start_Hour','start time']
        hist_func_np.hist_con_show(workbook,name_list,[time_h_s],range(25))

        name_list=['Charging_time','Charging_time','Charging_time(convert SOC0~100)']
        time_interval=[0,30,60,120,180,240,300,360,420,480,540,600,660,720,780,840,900,1500]
        hist_func_np.hist_con_show(workbook,name_list,[time_d,time_d_c],time_interval,2)
        mode_interval=['mode2','mode3_2','mode3_1','DC']
        hist_func_np.hist_cros_con_dis_show(workbook,['charg_mode-time'],time_d,time_interval,mode,mode_interval)
        hist_func_np.hist_cros_con_dis_show(workbook,['charg_mode-time(convert)'],time_d_c,time_interval,mode,mode_interval)
                
        name_list=['charg_temp','start_temp','end_temp','min_temp','max_temp','temp_mean','temp_range']
        hist_func_np.hist_con_show(workbook,name_list,charg_temp,range(-10,60,5),2)
        hist_func_np.hist_cros_con_dis_show(workbook,['charg_temp-mode'],charg_temp[4],range(-10,60,5),mode,mode_interval)

        name_list=['charg_power','pow_max','power_mean']
        hist_func_np.hist_con_show(workbook,name_list,charg_pow,range(50),2)
        hist_func_np.hist_cros_con_dis_show(workbook,['charg_pow-mode'],charg_pow[1],range(50),np.array(mode),mode_interval)

    def Warming_hist():
        sql="SELECT tdfwn,celohwn,vedtovwn,vedtuvwn,lsocwn,celovwn,celuvwn,hsocwn,jpsocwn,cesysumwn,celpoorwn,inswn,dctpwn,bksyswn, " \
            "dcstwn,emctempwn,hvlockwn,emtempwn,vesoc,mxal,count_wn FROM "+self.tb1_name + self.tb_join+" WHERE "+ self.con+ " AND "+ self.tb1_name +".count_wn>0 "
        aus=self.client.execute(sql)
        count_wm=[0]*19
        for val in aus:
            for i in range(19):
                count_wm[i]+=val[i]
        return count_wm

    def summary(self):
        workbook = xlsxwriter.Workbook(self.path+self.proj+".xlsx")
        
        self.daily_mileage(workbook)
        self.percharge_mile(workbook)
        self.v_mode(workbook)
        self.get_drive(workbook)
        self.E_motor(workbook)
        self.BMS(workbook)
        self.power_distribution(workbook)
        self.charg_hist(workbook)

        workbook.close()

def print_in_excel(aus,s1):
    workbook = xlsxwriter.Workbook(s1)
    worksheet = workbook.add_worksheet("sheet1")
    for i in range(len(aus)):
        for j in range(len(aus[0])):
            worksheet.write(i+1,j,aus[i][j])
    workbook.close()


