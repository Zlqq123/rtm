import xlsxwriter
import time
import numpy as np
import hist_func_np
import sys
from datetime import datetime
from genarl_func import time_cost1
from genarl_func import time_cost_all
from en_client import en_client
client=en_client()


class RtmAna():
    '''
    用于统计车辆行驶特性，包括里程，速度，驾驶模式，能耗估算，充电行为，电机工作点，电池工作点等。

        V4.0：统计函数采用numpy,统计函数速度提升99.9%
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
        V5.1
        自定义region province usertype mileage_range d_mileage
        V5.2
        自定义处理数据时间选择;    添加call函数;    添加绝缘阻值统计
        v5.3
        client delete
    '''

    def __init__ (self,path,proj,tb1_name,tb2_name):
        '''
        project must be in {'Lavida','Passat','Tiguan','Passat C5','Passat C6','Tiguan C5','Tiguan C6'}
        '''
        self.path=path
        self.tb1_name=tb1_name
        self.tb2_name=tb2_name

        proj=proj.upper()

        if proj=="LAVIDA":
            con_pro= tb2_name + ".project=='Lavida BEV 53Ah' "
            typ_v='BEV'
        else:
            typ_v='PHEV'
            if proj=="TIGUAN":
                con_pro= tb2_name + ".project in {'Tiguan L PHEV C6', 'Tiguan L PHEV C5'} "
            elif proj=="TIGUAN C5":
                con_pro= tb2_name + ".project=='Tiguan L PHEV C5' "
            elif proj=="TIGUAN C6":
                con_pro= tb2_name + ".project=='Tiguan L PHEV C6' "
            elif proj=="PASSAT":
                con_pro= tb2_name + ".project in {'Passat PHEV C6', 'Passat PHEV C5'} "
            elif proj=="PASSAT C5":
                con_pro= tb2_name + ".project=='Passat PHEV C5' "
            elif proj=="PASSAT C6":
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
        self.time_range=[]

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

    def datetime_select(self,start,end):
        '''
        start,end:yyyy-mm-dd        eg: 2020-06-01,2020-06-13
        '''
        self.time_range=[start,end]
        a=start+" 00:00:00"
        b=end+" 23:59:59"
        self.con+=" AND "+self.tb1_name+ ".uploadtime BETWEEN '"+a+"' AND '"+b+"'"

    def reset_select_condution(self):
        self.con=self.con_pro
        self.province="All"
        self.region="All"
        self.user_type="All"
        self.d_mile_condition=0
        self.mile_range=[]
        self.time_range=[]

    def generate_log_file(self):
        sql = "select uniq(deviceid) FROM "+self.tb1_name+ self.tb_join+" Where "+self.con
        print(sql)
        aus=client.execute(sql)
        dt=datetime.now()
        file=open(self.log_filename,'a')
        file.write("\r\n####################################\r\n")
        file.write("##Running Date & Time："+str(dt)+"\r\n")
        file.write("##Project："+self.proj+"\r\n")
        file.write("##Region："+self.region+"  Province:"+self.province+"\r\n")
        file.write("##User Type："+self.user_type+"\r\n")
        file.write("##mile range："+str(self.mile_range)+"  d_mile_condition:>"+str(self.d_mile_condition)+"\r\n")
        file.write("##Vehicle Count："+str(aus[0][0])+"辆\r\n")
        file.write("##Raw data date："+str(self.time_range) +" \r\n")
        file.write("####################################\r\n")
        file.close()
        return aus[0][0]

    def condition_printer(self):
        print("--tb_jion:")
        print(self.tb_join)
        print("--SELECT condition:")
        print(self.con)

    def __call__(self,region=0,user_type=0,province=0,d_mile_condition=0,start_mileage=0,end_mileage=0,start_date=0,end_date=0):
        '''
        region must be in {'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}

        user_type must be in {'Private', 'Fleet', 'Taxi'}

        province must be in {"GuangDong","ShangHai","TianJin","ZheJiang","HeBei","SiChuan","Shan3Xi","HeNan","FuJian","ShanDong","GuangXi","NingXia","XinJinag","JiLin", \
            "Shan1Xi","LiaoNing","ChongQing","JiangSu","HuBei","YunNan","HuNan","GuiZhou","JiangXi","AnHui","HanNan","GanSu","QingHai","NeiMeng","HeiLongJiang","BeiJing","XiZang"}

        start_date,end_date:yyyy-mm-dd        eg: 2020-06-01,2020-06-13
        '''
        file_name=self.proj

        if province!=0:
            self.province_select(province)
            file_name+='_'+province
        
        if region!=0:
            self.region_select(region)
            file_name+='_'+region
        if user_type!=0:
            self.user_type_select(user_type)
            file_name+='_'+user_type
        if d_mile_condition!=0:
            self.d_mile_condition_select(d_mile_condition)
        if start_mileage!=0 and end_mileage!=0:
            self.mileage_select(start_mileage,end_mileage)
            file_name+="_mile("+str(start_mileage)+'~'+str(end_mileage)+")"
        if start_date!=0 and end_date!=0:
            self.datetime_select(start_date,end_date)
            file_name+="_date("+start_date+'~'+end_date+")"
    
        self.condition_printer()

        n=self.generate_log_file()

        if n!=0:            
            workbook = xlsxwriter.Workbook(self.path+file_name+".xlsx")
            self.daily_mileage(workbook)
            self.percharge_mile(workbook)
            self.v_mode(workbook)
            self.get_drive(workbook)
            self.E_motor(workbook)
            self.BMS(workbook)
            self.power_distribution(workbook)
            self.charg_hist(workbook)
            self.Warming_hist(workbook)
            self.insulation_resistance_hist(workbook)
            workbook.close()

    '''
    def __enter__(self):
        return self

    def __exit__(self,exc_type,exc_value,exc_trackback):
        pass
    '''

    @time_cost1()
    def daily_mileage(self,workbook):
        sql="SELECT max(accmiles)-min(accmiles) FROM " +self.tb1_name+ self.tb_join+ \
            " where "+ self.con+" group by deviceid,toDate(uploadtime) "
        aus=client.execute(sql)
        mileage=[]
        for value in aus:
            mileage.append(value[0])
        
        hist_func_np.hist_con_show(workbook,["daily_mile",'mileage per day'],[np.array(mileage)],range(0,500,20),2)

    @time_cost1()
    def percharge_mile(self,workbook):
        sql="SELECT deviceid,uploadtime,charg_s_c,soc,soc_c,accmiles " \
            "FROM " +self.tb1_name+ self.tb_join+ " WHERE " + self.con + " AND "+ self.tb1_name +".charg_s_c IN (1,-1) ORDER BY deviceid,uploadtime "
        aus=client.execute(sql)
        #aus=[0 vin  1 时间  2充电变化标志位  3 soc   4 d_soc  5 mileage ]
        all_drive=[]
        count_1=0#基数多少次行驶前数据丢失
        count_2=0#计数行驶后数据丢失
        count_12=0#行驶前，行驶后均数据丢失
        i=1
        while i<len(aus):
            if aus[i][0]==aus[i-1][0] and aus[i-1][2]==-1 and aus[i][2]==1:#i-1时刻是开始行驶，i是结束行驶时刻
                start_d_soc=abs(aus[i-1][4])
                end_d_soc=abs(aus[i][4])
                if start_d_soc>5 or end_d_soc>5:
                    if start_d_soc>5:
                        count_1+=1
                    if end_d_soc>5:
                        count_2+=1
                    if start_d_soc>5 and end_d_soc>5:
                        count_12+=1
                elif aus[i-1][3]>aus[i][3] and aus[i-1][5]<aus[i][5]:# 行驶过程中SOC减少，里程增加
                    all_drive.append([aus[i][0],aus[i-1][1],aus[i][1],aus[i-1][3],aus[i][3],aus[i-1][5],aus[i][5]])
                    #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
                i+=2
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

    @time_cost1()
    def v_mode(self,workbook,sampling=1/6):
        sql="SELECT vehiclespeed,operationmode FROM " + self.tb1_name + self.tb_join+  \
            " Where "+ self.con+ " AND "+ self.tb1_name +".vehiclespeed>0 and toSecond(uploadtime)<"+str(int(sampling*60))
        aus=client.execute(sql)
        v,mode=[],[]
        for value in aus:
            v.append(value[0])
            mode.append(value[1])
        hist_func_np.hist_con_show(workbook,['v','vehicle speed km/h'],[np.array(v)],[0,10,20,30,40,50,60,70,80,90,100,110,120,200],2)
        if self.pro_typ=="PHEV":
            hist_func_np.hist_cros_con_dis_show(workbook,["driving mode"],np.array(v),[0,10,20,30,40,50,60,70,80,90,100,110,120,200],np.array(mode),['EV','PHEV',"FV"])
    
    @time_cost1()
    def get_drive(self,workbook):
        sql="SELECT deviceid,uploadtime,vehicle_s_c,accmiles,soc,soc_c FROM " +self.tb1_name+ self.tb_join+ \
            " WHERE " + self.con + " AND "+self.tb1_name+".vehicle_s_c in (1,-1) ORDER BY deviceid,uploadtime"
        aus=client.execute(sql)
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
                #如果两次行驶间隔小于300s或者行驶距离小于1km,合并为同一次行驶。前提是同一辆车。
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

    @time_cost1()
    def E_motor(self,workbook,sampling=1/6):
        '''
        sampling自定义采样频率 取值范围[1/60,1]
        '''
        sql="SELECT emspeed,emtq,em_eff,emctltemp,emtemp " \
            " FROM " +self.tb1_name+ self.tb_join+ " WHERE " + self.con + " AND "+ self.tb1_name +".emstat !='CLOSED'" \
            " AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=client.execute(sql)
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

    @time_cost1()
    def power_distribution(self,workbook,sampling=1/6):
        '''
        sampling自定义采样频率 取值范围[1/60,1]
        '''
        sql="SELECT accpedtrav,brakepedstat,BMS_pow,em_me_pow,em_el_pow,other_pow " \
            " FROM " +self.tb1_name+ self.tb_join+ " WHERE " + self.con + " AND "+ self.tb1_name +".vehicle_s ==1" \
            " AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=client.execute(sql)
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

    @time_cost1()
    def BMS(self,workbook,sampling=1/6):
        '''
        sampling自定义采样频率 取值范围[1/60,1]
        '''
        #discharging
        sql="SElECT soc,cocesprotemp1_mean,BMS_pow FROM " +self.tb1_name+ self.tb_join+  \
            " WHERE " + self.con + " AND "+ self.tb1_name + ".charg_s==0 AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=client.execute(sql)

        soc,temp_av,pow_bms=[],[],[]
        for value in aus:
            soc.append(value[0])
            temp_av.append(value[1])
            pow_bms.append(value[2])
        
        hist_func_np.hist_cros_2con_show(workbook,['BMS_workingpoint_discharge'],np.array(soc),range(0,115,5),np.array(temp_av),range(-30,65,5))

        #charging
        soc,temp_av,pow_bms=[],[],[]
        sql="SElECT soc,cocesprotemp1_mean,BMS_pow FROM " +self.tb1_name+ self.tb_join+  \
            " WHERE " + self.con + " AND "+ self.tb1_name + ".charg_s==1 AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=client.execute(sql)
        soc,temp_av,pow_bms=[],[],[]
        for value in aus:
            soc.append(value[0])
            temp_av.append(value[1])
            pow_bms.append(value[2])
        
        hist_func_np.hist_cros_2con_show(workbook,['BMS_workingpoint_charge'],np.array(soc),range(0,115,5),np.array(temp_av),range(-30,65,5))
    
        sql="SELECT arrayReduce('max',cocesprotemp1),arrayReduce('min',cocesprotemp1) " \
            "FROM " +self.tb1_name+ self.tb_join+" WHERE " + self.con + " AND "+ self.tb1_name + ".charg_s==0"
        aus=client.execute(sql)
        max_temp,min_temp,temp_range=[],[],[]
        for val in aus:
            max_temp.append(val[0])
            min_temp.append(val[1])
            temp_range.append(val[0]-val[1])
        name_list=['BMS_temp_discharge','Max','Min','range']
        hist_func_np.hist_con_show(workbook,name_list,[np.array(max_temp),np.array(min_temp),np.array(temp_range)],range(-10,62,2),2)

        sql="SELECT arrayReduce('max',cocesprotemp1),arrayReduce('min',cocesprotemp1) " \
            "FROM " +self.tb1_name+ self.tb_join+" WHERE " + self.con + " AND "+ self.tb1_name + ".charg_s==1"
        aus=client.execute(sql)
        max_temp,min_temp,temp_range=[],[],[]
        for val in aus:
            max_temp.append(val[0])
            min_temp.append(val[1])
            temp_range.append(val[0]-val[1])
        name_list=['BMS_temp_charge','Max','Min','range']
        hist_func_np.hist_con_show(workbook,name_list,[np.array(max_temp),np.array(min_temp),np.array(temp_range)],range(-10,62,2),2)

    def get_Charge(self):
        '''
        return all_charge=i*[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6 end_mile ]
        '''
        sql1="SELECT deviceid,uploadtime,charg_s_c,soc,soc_c,accmiles FROM " + self.tb1_name + self.tb_join+ \
            " WHERE " + self.con + " AND "+ self.tb1_name +".charg_s_c IN (1,-1) ORDER BY deviceid,uploadtime "
        aus=client.execute(sql1)
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
            if all_charge[i-1][0]==all_charge[i][0] and temp[i-1][3]==temp[i][2] and temp[i-1][1]==temp[i][0]:
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

        sql="SELECT deviceid,uploadtime,-BMS_pow,cocesprotemp1_mean,soc,charg_mode,arrayReduce('max',cocesprotemp1),arrayReduce('min',cocesprotemp1) " \
            "FROM " +self.tb1_name + self.tb_join+" WHERE "+ self.con+ " AND "+ self.tb1_name +".charg_s==1 " \
            "ORDER BY deviceid,uploadtime"
        aus=client.execute(sql)
        #aus=[i][0vin 1time, 2 BMS_power 3temp 4soc 5charg_mode 6max_temp 7min_temp]

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
       
        temp_mean,temp_range=[],[]
        temp_min,temp_max=[],[]
        temp_start_max,temp_start_min=[],[]
        power_max,power_mean=[],[]
        temp_a,pow_a,temp_max_a,temp_min_a=[],[],[],[]#中间过程量
        time_h_s,time_d,time_d_c=[],[],[]
        soc_s,soc_e,soc_d=[],[],[]
        
        for i in range(len(aus)):
            pow_a.append(aus[i][2])
            temp_a.append(aus[i][3])
            temp_max_a.append(aus[i][6])
            temp_min_a.append(aus[i][7])

        for i in range(len(ss)):
            mode.append(aus[ss[i]][5])
            power_max.append(max(pow_a[ss[i]:ee[i]]))
            power_mean.append(sum(pow_a[ss[i]:ee[i]])/len(pow_a[ss[i]:ee[i]]))
            #temp_s.append(temp_a[ss[i]])
            #temp_e.append(temp_a[ss[i]])
            #temp_min.append(min(temp_a[ss[i]:ee[i]]))
            #temp_max.append(max(temp_a[ss[i]:ee[i]]))
            temp_mean.append(sum(temp_a[ss[i]:ee[i]])/len(temp_a[ss[i]:ee[i]]))
            temp_range.append(max(temp_a[ss[i]:ee[i]])-min(temp_a[ss[i]:ee[i]]))
            temp_min.append(min(temp_min_a[ss[i]:ee[i]]))
            temp_max.append(max(temp_max_a[ss[i]:ee[i]]))
            temp_start_max.append(aus[ss[i]][6])
            temp_start_min.append(aus[ss[i]][7])
            soc_s.append(aus[ss[i]][4])
            soc_e.append(aus[ee[i]][4])
            soc_d.append(aus[ee[i]][4]-aus[ss[i]][4])
            d=aus[ee[i]][1]-aus[ss[i]][1]
            time_d.append(d.seconds/60)
            time_d_c.append(d.seconds/60/(aus[ee[i]][4]-aus[ss[i]][4])*100)
            time_h_s.append(aus[ss[i]][1].hour)
        
        charg_temp=[np.array(temp_min),np.array(temp_max),np.array(temp_mean),np.array(temp_range),np.array(temp_start_max),np.array(temp_start_min)]
        charg_pow=[np.array(power_max),np.array(power_mean)]
        charg_soc=[np.array(soc_s),np.array(soc_e),np.array(soc_d)]

        return np.array(time_h_s),np.array(time_d),np.array(time_d_c),np.array(mode),charg_soc,charg_temp,charg_pow

    @time_cost1()
    def charg_hist(self,workbook):
        [time_h_s,time_d,time_d_c,mode,charg_soc,charg_temp,charg_pow]=self.charge_ana()

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
                
        name_list=['charg_temp','min_temp','max_temp','temp_mean','temp_range','start_temp_max','start_temp_min']
        hist_func_np.hist_con_show(workbook,name_list,charg_temp,range(-10,60,5),2)
        hist_func_np.hist_cros_con_dis_show(workbook,['charg_temp-mode'],charg_temp[2],range(-10,60,5),mode,mode_interval)

        name_list=['charg_power','pow_max','power_mean']
        hist_func_np.hist_con_show(workbook,name_list,charg_pow,range(50),2)
        hist_func_np.hist_cros_con_dis_show(workbook,['charg_pow-mode'],charg_pow[1],range(50),np.array(mode),mode_interval)

    @time_cost1()
    def Warming_hist(self,workbook):
        sql="SELECT sum(tdfwn),sum(celohwn),sum(vedtovwn),sum(vedtuvwn),sum(lsocwn),sum(celovwn),sum(celuvwn),sum(hsocwn),sum(jpsocwn), " \
            "sum(cesysumwn),sum(celpoorwn),sum(inswn),sum(dctpwn),sum(bksyswn),sum(dcstwn),sum(emctempwn),sum(hvlockwn),sum(emtempwn),sum(vesoc) " \
            "FROM "+self.tb1_name + self.tb_join+" WHERE "+ self.con+ " AND "+ self.tb1_name +".count_wn>0 "
        count_wm=client.execute(sql)

        dic={}
        dic[0]='tdfwn'
        dic[1]='celohwn'
        dic[2]='vedtovwn'
        dic[3]='vedtuvwn'
        dic[4]='lsocwn'
        dic[5]='celovwn'
        dic[6]='celuvwn'
        dic[7]='hsocwn'
        dic[8]='jpsocwn'
        dic[9]='cesysumwn'
        dic[10]='celpoorwn'
        dic[11]='inswn'
        dic[12]='dctpwn'
        dic[13]='bksyswn'
        dic[14]='dcstwn'
        dic[15]='emctempwn'
        dic[16]='hvlockwn'
        dic[17]='emtempwn'
        dic[18]='vesoc'

        count_vehicle_wm=[0]*19
        for i in range(19):
            if count_wm[0][i]!=0:
                wn_name=dic[i]
                sql="SELECT uniq(deviceid) FROM "+self.tb1_name + self.tb_join+" WHERE "+ self.con+ " AND "+ self.tb1_name +"."+ wn_name+ ">0 "
                aus=client.execute(sql)
                count_vehicle_wm[i]=aus[0][0]

        sql="SELECT count(deviceid),uniq(deviceid) FROM "+self.tb1_name + self.tb_join+" WHERE "+ self.con+ " AND "+ self.tb1_name +".count_wn>0 "
        aus=client.execute(sql)

        worksheet = workbook.add_worksheet('Warming')
        worksheet.write(0,0,'Name_warming')
        worksheet.write(0,1,'warming times')
        worksheet.write(0,2,'vehicle involved')
        for i in range(19):
            worksheet.write(i+1,0,dic[i])
            worksheet.write(i+1,1,count_wm[0][i])
            worksheet.write(i+1,2,count_vehicle_wm[i])
        worksheet.write(21,0,'total')
        worksheet.write(21,1,aus[0][0])
        worksheet.write(21,2,aus[0][1])

    def insulation_resistance_hist(self,workbook):
        sql="SELECT avg(ir)/1000 FROM "+self.tb1_name + self.tb_join+" WHERE "+ self.con+ \
            " AND " +self.tb1_name+".ir<10000 AND "+self.tb1_name+".charg_s==0 GROUP BY deviceid,toDate(uploadtime) "
        aus=client.execute(sql)

        ir=[]
        for val in aus:
            ir.append(val[0])

        name_list=['ir','ir(MΩ)']
        hist_func_np.hist_con_show(workbook,name_list,[np.array(ir)],[8,9,9.1,9.2,9.3,9.4,9.5,9.6,9.7,9.8,9.9,10],2)




class feature_extract():
    '''
    用于提取特征
        20200904 v1.0
    '''
    def __init__(self,vin,start_date,end_date,target_date,tb_name):
        '''
        start,end:yyyy-mm-dd        eg: 2020-06-01,2020-06-13
        '''
        self.vin=vin
        a=start_date+" 00:00:00"
        b=end_date+" 23:59:59"
        self.con1=" deviceid='"+self.vin+"' and uploadtime between '"+a+"' AND '"+b+"'"
        a=target_date+" 00:00:00"
        b=target_date+" 23:59:59"
        self.con2=" deviceid='"+self.vin+"' and uploadtime between '"+a+"' AND '"+b+"'"
        self.tb_name=tb_name
    
    def __call__(self):

        y=self.RTM_Warn()
        f1=self.get_static_feature()
        f2=self.mileage_time()
        f3=self.v_mode_acc()
        f4=self.BMS_discharge()
        f5=self.E_motor()
        f6=self.BMS_charge()
        f7=self.get_charge()

        return [y],f1,f2,f3,f4,f5,f6,f7
        

    def RTM_Warn(self):
        sql="SELECT sum(bksyswn) FROM "+self.tb_name+" Where "+self.con2
        aus=client.execute(sql)
        if aus==[]:
            return 'null'
        if aus[0][0]>0:
            y_label=1
        else:
            y_label=0
        return y_label

    def get_static_feature(self):
        '''
        s=[地区，省份，用户类型，行驶里程，绝缘阻值大小]
        '''
        sql="select region,province,user_typ from en.vehicle_vin where deviceid='"+self.vin+"'"
        aus=client.execute(sql)
        s=['null']*5
        if aus!=[]:
            s[0]=aus[0][0]
            s[1]=aus[0][1]
            s[2]=aus[0][2]
        sql="select accmiles from "+self.tb_name+" Where "+self.con1
        aus1=client.execute(sql)
        sql="select avg(accmiles),avg(ir) from "+self.tb_name+" Where "+self.con1
        aus=client.execute(sql)
        if aus1!=[]:
            s[3]=aus[0][0]
            s[4]=aus[0][1]
        
        return s
    
    def mileage_time(self):
        '''
        s=[行驶里程，平均每日行驶里程，行驶时间]
        '''
        s=['null']*3
        sql="SELECT max(accmiles)-min(accmiles) FROM "+self.tb_name+" WHERE "+self.con1
        aus=client.execute(sql)
        if aus!=[]:
            s[0]=aus[0][0]
        
        sql="SELECT max(accmiles)-min(accmiles) FROM "+self.tb_name+" WHERE "+self.con1+" group by toDate(uploadtime) "
        aus=client.execute(sql)
        if aus!=[]:
            a=[]
            for v in aus:
                a.append(v[0])
            s[1]=sum(a)/len(a)
        
        sql="SELECT d_time from "+self.tb_name+" WHERE d_time<31 and charg_s=0 and "+self.con1
        aus=client.execute(sql)
        if aus!=[]:
            a=[]
            aus=client.execute(sql)
            for v in aus:
                a.append(v[0])
            s[2]=sum(a)/3600
        return s
    
    def v_mode_acc(self):
        '''
        s=[车速（平均值，99分位，中位数），EV驾驶模式占比，FV驾驶模式占比，油门踏板开度（平均值，99分位，中位数），制动踏板开度（平均值，99分位，中位数）]
        '''
        s=['null']*11
        sql="SELECT vehiclespeed,operationmode FROM "+self.tb_name+" WHERE vehiclespeed>0 and "+self.con1
        aus=client.execute(sql)
        if aus!=[]:
            v=[]
            mode_ev,mode_fv=0,0
            for value in aus:
                v.append(value[0])
                if value[1]=="EV":
                    mode_ev+=1
                if value[1]=="FV":
                    mode_fv+=1
            vp=np.array(v)
            s[0]=np.mean(vp)
            s[1]=np.percentile(vp,99)
            s[2]=np.percentile(vp,50)
            s[3]=mode_ev/len(aus)
            s[4]=mode_fv/len(aus)
        
        sql="SELECT accpedtrav FROM "+self.tb_name+" WHERE accpedtrav>0 and "+self.con1
        aus=client.execute(sql)
        if aus!=[]:
            a=[]
            for value in aus:
                a.append(value[0])
            ap=np.array(a)
            s[5]=np.mean(ap)
            s[6]=np.percentile(ap,99)
            s[7]=np.percentile(ap,50)
            
        sql="SELECT brakepedstat FROM "+self.tb_name+" WHERE brakepedstat>0 and "+self.con1
        aus=client.execute(sql)
        if aus!=[]:
            a=[]
            for value in aus:
                a.append(value[0])
            ap=np.array(a)
            s[8]=np.mean(ap)
            s[9]=np.percentile(ap,99)
            s[10]=np.percentile(ap,50)
        return s

    def BMS_discharge(self):
        '''
        s=[电池放电温度(最大值，最小值，平均值),电池放电功率(最大值，平均值)，
            放电中电池单体温度（最高温度电芯最大值，最低电芯温度最小值，单体温差最大值，温差平均值），
            #电池单体压差]
        '''
        s=['null']*9
        #discharging
        sql="SElECT cocesprotemp1_mean,BMS_pow FROM " +self.tb_name+ " WHERE charg_s==0 AND " + self.con1
        aus=client.execute(sql)
        if aus!=[]:
            temp=[]
            pow_bms=[]
            for value in aus:
                temp.append(value[0])
                if value[1]>=0:
                    pow_bms.append(value[1])
            
            s[0]=max(temp)
            s[1]=min(temp)
            s[2]=sum(temp)/len(temp)
            if pow_bms!=[]:
                s[3]=max(pow_bms)
                s[4]=sum(pow_bms)/len(pow_bms)
            
        sql="SELECT arrayReduce('max',cocesprotemp1),arrayReduce('min',cocesprotemp1) FROM "+self.tb_name+ " WHERE charg_s==0 AND " + self.con1 
        aus=client.execute(sql)
        if aus!=[]:
            cel_temp_max,cel_temp_min,cel_temp_range=[],[],[]
            for value in aus:
                cel_temp_max.append(value[0])
                cel_temp_min.append(value[1])
                cel_temp_range.append(value[0]-value[1])
            s[5]=max(cel_temp_max)
            s[6]=min(cel_temp_min)
            s[7]=max(cel_temp_range)
            s[8]=sum(cel_temp_range)/len(cel_temp_range)

        return s

    def E_motor(self):
        '''
        s=[电机转速（最大值，平均值），正转矩（最大值，平均值），负转矩（最大值，平均值），负转矩占比，
            电机温度（平均值，99分位，中位数，1分位），LE温度（平均值，99分位，中位数，1分位）]
        '''
        s=['null']*15
        sql="SELECT emspeed,emtq,emctltemp,emtemp FROM " +self.tb_name+" WHERE emstat!='CLOSED' AND "+ self.con1
        aus=client.execute(sql)
        if aus!=[]:
            temp_motor,temp_LE=[],[]
            speed,torq1,torq2=[],[],[]
            for value in aus:
                temp_motor.append(value[3])
                temp_LE.append(value[2])
                if value[0]!=0 and value[1]!=0:
                    speed.append(value[0])
                    if value[1]>0:
                        torq1.append(value[1])
                    else:
                        torq2.append(value[1])
            s[0]=max(speed)
            s[1]=sum(speed)/len(speed)
            if torq1!=[]:
                s[2]=max(torq1)
                s[3]=sum(torq1)/len(torq1)
            if torq2!=[]:
                s[4]=min(torq2)
                s[5]=sum(torq2)/len(torq2)
            s[6]=len(torq2)/len(speed)
            
            tp=np.array(temp_motor)
            s[7]=np.mean(tp)
            s[8]=np.percentile(tp,99)
            s[9]=np.percentile(tp,50)
            s[10]=np.percentile(tp,1)

            tp=np.array(temp_LE)
            s[11]=np.mean(tp)
            s[12]=np.percentile(tp,99)
            s[13]=np.percentile(tp,50)
            s[14]=np.percentile(tp,1)
            
        return s
    
    def BMS_charge(self):
        '''
        s=[电池充电温度(最大值，最小值，平均值),电池充电功率(最大值，平均值)，
            充电中电池单体温度（最高温度电芯最大值，最低电芯温度最小值，单体温差最大值，温差平均值），
            #电池单体压差]
        '''
        s=['null']*9
        #charging
        sql="SElECT cocesprotemp1_mean,BMS_pow FROM " +self.tb_name+ " WHERE charg_s==1 AND " + self.con1
        aus=client.execute(sql)
        if aus!=[]:
            temp=[]
            pow_bms=[]
            for value in aus:
                temp.append(value[0])
                if value[1]<0:
                    pow_bms.append(value[1])
            s[0]=max(temp)
            s[1]=min(temp)
            s[2]=sum(temp)/len(temp)
            if pow_bms!=[]:
                s[3]=max(pow_bms)
                s[4]=sum(pow_bms)/len(pow_bms)

        sql="SELECT arrayReduce('max',cocesprotemp1),arrayReduce('min',cocesprotemp1) FROM "+self.tb_name+ " WHERE charg_s==1 AND " + self.con1
        aus=client.execute(sql)
        if aus!=[]:
            cel_temp_max,cel_temp_min,cel_temp_range=[],[],[]
            for value in aus:
                cel_temp_max.append(value[0])
                cel_temp_min.append(value[1])
                cel_temp_range.append(value[0]-value[1])
            s[5]=max(cel_temp_max)
            s[6]=min(cel_temp_min)
            s[7]=max(cel_temp_range)
            s[8]=sum(cel_temp_range)/len(cel_temp_range)
        
        return s

    def get_charge(self):
        '''
        s=[充电次数，开始充电soc(平均值，中位数)，结束充电SOC(平均值，中位数)，累计冲入电量，平均每次冲入电量，充电模式2占比，模式3占比]
        '''
        s=['null']*9
        sql1="SELECT uploadtime,charg_s_c,soc,soc_c,accmiles,charg_mode FROM " + self.tb_name + " WHERE charg_s_c IN (1,-1) AND "+ self.con1+" ORDER BY uploadtime"
        aus=client.execute(sql1)        #aus=[0 time  1充电变化标志位  2 soc   3 d_soc  4 mileage 5 mode ]
        all_charge=[]        #all_charge=[0time_start, 1time_end, 2 charg_mode]
        temp=[]        #temp=[0soc_start,1soc_end,2mile_start,3end_mile ]

        i=1
        while i<len(aus):
            if aus[i-1][1]==1 and aus[i][1]==-1:#i-1时刻是开始充电，i是结束充电时刻
                all_charge.append([aus[i-1][0],aus[i][0],aus[i-1][5]])                #all_charge=[0time_start,1time_end]
                temp.append([aus[i-1][2],aus[i][2],aus[i-1][4],aus[i][4]])                #temp=[0soc_start,1soc_end,2mile_start,3end_mile ]
                i+=2
            else:
                i+=1

        i=1
        while i<len(all_charge):
            if  temp[i-1][3]==temp[i][2] and temp[i-1][1]==temp[i][0]:#如果上一次充电结束的里程与下一次开始充电的里程不变，合并为一次充电
                all_charge[i-1][1]=all_charge[i][1]
                temp[i-1][1]=temp[i][1]
                temp[i-1][3]=temp[i][3]
                all_charge.pop(i)
                temp.pop(i)
            else:
                i+=1
        
        charge_times=len(all_charge)
        s[0]=len(all_charge)

        if charge_times!=0:
            mode,soc_s,soc_e,soc_d=[],[],[],[]
            for i in range(len(all_charge)):
                mode.append(all_charge[i][2])
                soc_s.append(temp[i][0])
                soc_e.append(temp[i][1])
                soc_d.append(temp[i][1]-temp[i][0])
            
            modep=np.array(mode)
            m1=len(modep[modep=='mode2'])
            m2=len(modep[modep=='mode3_2'])
            s[1]=m1/charge_times
            s[2]=m2/charge_times

            soc_sp=np.array(soc_s)
            soc_ep=np.array(soc_e)

            s[3]=np.mean(soc_sp)
            s[4]=np.percentile(soc_sp,50)
            s[5]=np.mean(soc_ep)
            s[6]=np.percentile(soc_ep,50)
            s[7]=sum(soc_d)/charge_times
            s[8]=sum(soc_d)

        return s

    

    





