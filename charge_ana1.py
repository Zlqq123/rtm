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
添加能耗计算模块
添加每个小时的行驶时间和行驶距离统计
'''

class RtmAna():
    def __init__ (self,path,proj,client):
        self.path=path
        self.client=client
        if proj=="lavida":
            con="deviceid like 'LSVA%' AND CAST(accmiles,'float')>100"
        elif proj=="passat":
            con="deviceid like 'LSVC%' AND CAST(accmiles,'float')>100"
        elif proj=="tiguan":
            con="deviceid like 'LSVU%' AND CAST(accmiles,'float')>100"
        else:
            print("proj error:proj must be in {'lavida','passat','tiguan'}")
            sys.exit(-1)
        self.con=con
        self.proj=proj
        sql = "select uniq(deviceid) from en.rtm_vds Where "+con
        aus=client.execute(sql)
        dt=datetime.now()
        file=open(path+proj+"_log.txt",'a')
        file.write("\r\n####################################\r\n")
        file.write("##运行日期&时间："+str(dt)+"\r\n")
        file.write("##参与统计车辆总数："+str(aus[0][0])+"辆\r\n")
        file.write("##参与统计天数：2020/03/01~2020/03/19 \r\n")
        file.write("####################################\r\n")
        file.close()

    #return all_charge=i*[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6charging_mode]
    def get_Charge(self):
        sql1="SELECT deviceid,uploadtime,delta,soc,d_soc,acc,ch_mode " \
            "FROM (SELECT deviceid,uploadtime,runningDifference(char_s) AS delta,soc, runningDifference(soc) AS d_soc,acc, " \
            "multiIf(P>7.5,'DC',P<=7.5 and P>4,'mode3_1',P<=4 and P>2,'mode3_2',P<=2 and P>0,'mode2','discharging') AS ch_mode " \
            "FROM (SELECT deviceid,uploadtime,soc,CAST(accmiles,'float') AS acc, if(chargingstatus=='NO_CHARGING',7,8) AS char_s, -totalcurrent*totalvolt/1000 AS P " \
            "FROM en.rtm_vds " \
            "WHERE " + self.con + " ORDER BY deviceid,uploadtime)) " \
            "WHERE delta IN (1,-1)"
        aus=self.client.execute(sql1)
        #aus=[0 vin  1 时间  2充电变化标志位  3 soc   4 d_soc  5 mileage  6 charging_mode(DC/AC)]
        all_charge=[]        
        #all_charge=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6charging_mode]
        tmp=[]
        # tmp=[0start_d_soc, 1 end_d_soc, 2 end_mile]
        i=1
        while i<len(aus):
            if aus[i][0]==aus[i-1][0] and aus[i-1][2]==1 and aus[i][2]==-1:#i-1时刻是开始充电，i是结束充电时刻
                all_charge.append([aus[i][0],aus[i-1][1],aus[i][1],aus[i-1][3],aus[i][3],aus[i-1][5],aus[i-1][6]])
                #all_charge=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6charging_mode]
                tmp.append([aus[i-1][4],aus[i][4],aus[i][5]])
                # tmp=[0start_d_soc, 1 end_d_soc, 2 end_mile]
                i+=2
            else:
                i+=1
        l1=len(all_charge)
        count_1=0#基数多少次充电前数据丢失
        count_2=0#计数充电结束的数据丢失
        count_12=0#充电前，充电后均数据丢失
        i=0
        while i<len(tmp):
            if abs(tmp[i][0])>5 or abs(tmp[i][1])>5:
                if abs(tmp[i][0])>5:
                    count_1+=1
                if abs(tmp[i][1])>5:
                    count_2+=1
                if abs(tmp[i][0])>5 and abs(tmp[i][1])>5:
                    count_12+=1
                tmp.pop(i)
                all_charge.pop(i)
            else:
                i+=1
        i=1
        count_3=0#计数合并充电情况
        while i<len(all_charge):
            if all_charge[i-1][0]==all_charge[i][0] and tmp[i-1][2]==all_charge[i][5] and all_charge[i-1][4]==all_charge[i][3]:
                #如果上一次充电结束的里程与下一次开始充电的里程不变，合并为一次充电。前提是同一辆车。
                all_charge[i-1][2]=all_charge[i][2]
                all_charge[i-1][4]=all_charge[i][4]
                tmp[i-1][1]=tmp[i][1]
                tmp[i-1][2]=tmp[i][2]
                tmp.pop(i)
                all_charge.pop(i)
                count_3+=1
            else:
                i+=1
        l2=len(all_charge)

        file=open(self.path+self.proj+"_log.txt",'a')
        file.write("---------charge analysis---------\r\n")
        file.write("原始充电次数："+str(l1)+"\r\n")
        file.write("充电前数据丢失次数："+str(count_1)+"占比："+str(round(count_1/l1*100,2))+"%\r\n")
        file.write("充电后数据丢失次数："+str(count_2)+"占比："+str(round(count_2/l1*100,2))+"%\r\n")
        file.write("充电前后数据均丢失次数："+str(count_12)+"占比："+str(round(count_12/l1*100,2))+"%\r\n")
        file.write("充电合并次数："+str(count_3)+"占比："+str(round(count_3/l1*100,2))+"%\r\n")
        file.write("处理后充电次数："+str(l2)+"\r\n")
        file.close()

        return all_charge
    
    #return [time_h_s,time_d,soc_s,soc_e,soc_d,time_d_c,mode]
    def get_Charge_varible(self,all_charge):
        #all_charge=i*[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6charging_mode]
        time_h_s,time_d,time_d_c=[],[],[]
        soc_s,soc_e,soc_d=[],[],[]
        mode=[]
        
        for a in all_charge:
            time_h_s.append(a[1].hour)
            soc_s.append(a[3])
            soc_e.append(a[4])
            soc_d.append(a[4]-a[3])
            if a[4]-a[3]>0:
                d=a[2]-a[1]
                time_d.append(d.seconds/60)
                time_d_c.append(d.seconds/60/(a[4]-a[3])*100)
                mode.append(a[6])
        
        return np.array(time_h_s),np.array(time_d),np.array(soc_s),np.array(soc_e),np.array(soc_d),np.array(time_d_c),np.array(mode)
    
    #return [mode,temp_s,temp_e,temp_min,temp_max,temp_mean,temp_range,power_max,power_mean]
    def get_temp_pow(self,all_charge):
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SELECT deviceid,uploadtime,-totalcurrent*totalvolt/1000,arrayReduce('sum',temp_list)/length(temp_list) " \
            "FROM en.rtm_vds WHERE chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') AND cocesprotemp1!='NULL' " \
            "AND "+ self.con +" ORDER BY deviceid,uploadtime"
        aus=self.client.execute(sql)
        #aus=[i][0vin 1time 2power 3temp]
        ss,ee=[],[]#用于存放aus中每段充电开始的index 和每次充电结束的index
        not_find=[]#用于存放在aus中找不到all_charge中的充电次数的index,目的是让mode变量与后面pow和temp相关变量的长度一致，并且一一对应上
        i,j=0,0 #j为all_charge的index      i 为aus的index
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
            if ff==2 and ee[-1]==ss[-1]:
                ff=0
                ss.pop()
                ee.pop()
            if ff<2: #如果找不到
                not_find.append(j)

        file=open(self.path+self.proj+"_log.txt",'a')        
        file.write("未匹配的充电次数："+str(len(not_find))+"占比："+str(round(len(not_find)/len(all_charge)*100,2))+"%\r\n")
        file.write("匹配的充电次数："+str(len(ss))+"\r\n")
        file.close()

        mode=[]#与后面过程变量由相同长度的mode
        j=0
        for i in range(len(all_charge)):#最后一次充电不要
            if j<len(not_find) and i==not_find[j]:
                j+=1
            else:
                mode.append(all_charge[i][6])
       
        temp_s,temp_e,temp_min,temp_max,temp_mean,temp_range=[],[],[],[],[],[]
        power_max,power_mean=[],[]
        temp_a,pow_a=[],[]#中间过程量
        for i in range(len(aus)):
            pow_a.append(aus[i][2])
            temp_a.append(aus[i][3])

        for i in range(len(ss)):
            power_max.append(max(pow_a[ss[i]:ee[i]]))
            power_mean.append(sum(pow_a[ss[i]:ee[i]])/len(pow_a[ss[i]:ee[i]]))
            temp_s.append(temp_a[ss[i]])
            temp_e.append(temp_a[ss[i]])
            temp_min.append(min(temp_a[ss[i]:ee[i]]))
            temp_max.append(max(temp_a[ss[i]:ee[i]]))
            temp_mean.append(sum(temp_a[ss[i]:ee[i]])/len(temp_a[ss[i]:ee[i]]))
            temp_range.append(max(temp_a[ss[i]:ee[i]])-min(temp_a[ss[i]:ee[i]]))
        
        return np.array(mode),np.array(temp_s),np.array(temp_e),np.array(temp_min),np.array(temp_max),np.array(temp_mean),np.array(temp_range),np.array(power_max),np.array(power_mean)


    def percharge_mile(self,workbook):
        sql1="SELECT deviceid,uploadtime,delta,soc,d_soc,acc " \
            "FROM (SELECT deviceid,uploadtime,runningDifference(char_s) AS delta,soc, runningDifference(soc) AS d_soc,acc " \
            "FROM (SELECT deviceid,uploadtime,soc,CAST(accmiles,'float') AS acc, if(chargingstatus=='NO_CHARGING',7,8) AS char_s " \
            "FROM en.rtm_vds " \
            "WHERE " + self.con + " ORDER BY deviceid,uploadtime)) " \
            "WHERE delta IN (1,-1)"
        aus=self.client.execute(sql1)
        #aus=[0 vin  1 时间  2充电变化标志位  3 soc   4 d_soc  5 mileage ]
        all_drive=[]
        tmp=[]
        i=1
        while i<len(aus):
            if aus[i][0]==aus[i-1][0] and aus[i-1][2]==-1 and aus[i][2]==1:#i-1时刻是开始行驶，i是结束行驶时刻
                all_drive.append([aus[i][0],aus[i-1][1],aus[i][1],aus[i-1][3],aus[i][3],aus[i-1][5],aus[i][5]])
                #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
                tmp.append([aus[i-1][4],aus[i][4]])
                i+=2
            else:
                i+=1
        l1=len(all_drive)
        count_1=0#基数多少次行驶前数据丢失
        count_2=0#计数行驶后数据丢失
        count_12=0#行驶前，行驶后均数据丢失
        soc_r=[]
        mile_r=[]
        mile_r_c=[]
        Energy_consump=[]

        for i,a in enumerate(all_drive):
            if abs(tmp[i][0])>5 or abs(tmp[i][1])>5:
                if abs(tmp[i][0])>5:
                    count_1+=1
                if abs(tmp[i][1])>5:
                    count_2+=1
                if abs(tmp[i][0])>5 and abs(tmp[i][1])>5:
                    count_12+=1
            else:
                if a[3]>a[4] and a[6]>a[5]:  # 行驶过程中SOC减少，里程增加
                    soc_r.append(a[3]-a[4])
                    mile_r.append(a[6]-a[5])
                    mile_r_c.append((a[6]-a[5])/(a[3]-a[4])*100)
        
        l2=len(mile_r_c)
        file=open(self.path+self.proj+"_log.txt",'a')
        file.write("------mile perCharging analysis---------\r\n")
        file.write("原始行驶次数："+str(l1)+"\r\n")
        file.write("充电前数据丢失次数："+str(count_1)+"占比："+str(round(count_1/l1*100,2))+"%\r\n")
        file.write("充电后数据丢失次数："+str(count_2)+"占比："+str(round(count_2/l1*100,2))+"%\r\n")
        file.write("充电前后数据均丢失次数："+str(count_12)+"占比："+str(round(count_12/l1*100,2))+"%\r\n")
        file.write("SOC 没有变化的行驶次数："+str(l1-l2-count_1-count_2+count_12)+"   占比："+str(round((l1-l2-count_1-count_2+count_12)/l1*100,2))+"%\r\n")
        file.write("处理后行驶次数："+str(l2)+"\r\n")
        file.close()

        name_list=['mile_perCharging','mile_perCharging','mile_convert']
        in_list=[np.array(mile_r),np.array(mile_r_c)]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(0,500,20),2)

        if self.proj=='lavida':
            charging_energy=37 #lavida BEV 实际SOC96~8% 冲入电量37kWh,来源NEDC充电测试平均值
            for a in all_drive:
                if a[3]>a[4] and a[6]>a[5]:
                    Energy_consump.append(charging_energy*(a[3]-a[4])/(a[6]-a[5]))
            hist_func_np.hist_con_show(workbook,['Energy consumption','Energy consumption'],[Energy_consump],np.arange(9,21,0.5),2)



    def E_motor(self,workbook):
        sql="SELECT cast(emspeed,'float') as sp,cast(emtq,'float') as tq,sp*tq/9550,cast(emvolt,'float')*cast(emctlcut,'float')/1000,cast(emtemp,'float'),cast(emctltemp,'float') " \
            "FROM en.rtm_vds " \
            "WHERE cast(vehiclespeed,'float')>0 AND "+ self.con+ " and toSecond(uploadtime)<10 "
        aus=self.client.execute(sql)
        speed=[]
        torq=[]
        eff=[]
        temp_motor,temp_LE=[],[]
        for value in aus:
            temp_motor.append(value[4])
            temp_LE.append(value[5])
            if value[2]!=0 and value[3]!=0:
                speed.append(value[0])
                torq.append(value[1])
                if value[2]>0 and value[3]>value[2]:
                    eff.append(value[2]/value[3]*100)
                elif value[2]<value[3] and value[3]<0:
                    eff.append(value[3]/value[2]*100)
        l1=len(temp_LE)
        l2=len(speed)
        l3=len(eff)
        file=open(self.path+self.proj+"_log.txt",'a')
        file.write("-------E-Motor Working Point Analysis---------\r\n")
        file.write("原始抓取点数："+str(l1)+"\r\n")
        file.write("去除转矩为零或转速为零之后工作点数："+str(l2)+"   占比："+str(round(l2/l1*100,2))+"%\r\n")
        file.write("效率值在合理范围数："+str(l3)+"   占比："+str(round(l3/l2*100,2))+"%\r\n")
        file.close()


        hist_func_np.hist_cros_2con_show(workbook,['LE_working_point'],np.array(speed),range(-4000,13000,500),np.array(torq),range(-300,400,50))
        hist_func_np.hist_con_show(workbook,["LE-eff",'LE_efficiency'],[np.array(eff)],[0,50,70,80,82,84,86,88,90,92,94,96,98,100],2)
        hist_func_np.hist_con_show(workbook,["LE-temp",'E_motor temperature','LE temperature'],[np.array(temp_motor),np.array(temp_LE)],range(-10,120,5),2)
        
    def BMS(self,workbook):
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SElECT soc,arrayReduce('sum',temp_list)/length(temp_list),totalcurrent*totalvolt/1000 " \
            "FROM en.rtm_vds " \
            "WHERE chargingstatus='NO_CHARGING' and totalcurrent>0 and cocesprotemp1!='NULL' " \
            "AND "+self.con+" and toSecond(uploadtime)<10"
        aus=self.client.execute(sql)

        soc,temp_av,pow_bms=[],[],[]
        for value in aus:
            soc.append(value[0])
            temp_av.append(value[1])
            pow_bms.append(value[2])
        
        hist_func_np.hist_cros_2con_show(workbook,['discharging'],np.array(soc),range(0,115,5),np.array(temp_av),range(-30,65,5))

        soc,temp_av,pow_bms=[],[],[]
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SElECT soc,arrayReduce('sum',temp_list)/length(temp_list),totalcurrent*totalvolt/1000 " \
            "FROM en.rtm_vds " \
            "where chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') AND totalcurrent<0 AND cocesprotemp1!='NULL' " \
            "AND "+self.con+" and toSecond(uploadtime)<10"
        aus=self.client.execute(sql)
        soc,temp_av,pow_bms=[],[],[]
        for value in aus:
            soc.append(value[0])
            temp_av.append(value[1])
            pow_bms.append(value[2])
        
        hist_func_np.hist_cros_2con_show(workbook,['charging'],np.array(soc),range(0,115,5),np.array(temp_av),range(-30,65,5))

    def daily_mileage(self,workbook):
        sql="SELECT deviceid,toDate(uploadtime),max(CAST(accmiles,'float')),min(CAST(accmiles,'float')) " \
            "from rtm_vds where "+ self.con+" group by deviceid,toDate(uploadtime) "
        aus=self.client.execute(sql)
        mileage=[]
        for value in aus:
            mileage.append(value[2]-value[3])
        
        hist_func_np.hist_con_show(workbook,["daily-mile",'mileage per day'],[np.array(mileage)],range(0,500,20),2)

    def hourly_mileage(self,workbook):
        sql="SELECT deviceid,toDate(uploadtime),toHour(uploadtime),max(CAST(accmiles,'float')),min(CAST(accmiles,'float')),COUNT(deviceid) " \
            "from rtm_vds where vehiclestatus=='STARTED' AND "+ self.con+" group by deviceid,toDate(uploadtime),toHour(uploadtime) "
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
        
        hist_func_np.hist_cros_con_dis_show(workbook,["hourly_mileage"],np.array(mileage_h),range(0,150,10),np.array(hour),range(24))
        hist_func_np.hist_cros_con_dis_show(workbook,["hourly_driving_time"],np.array(durate),range(0,65,5),np.array(hour),range(24))


    def v_mode(self,workbook):
        sql="SELECT cast(vehiclespeed,'float') as v,operationmode,CAST(accmiles,'float') as acc " \
            "from rtm_vds " \
            "Where "+ self.con+" AND v>0 and toSecond(uploadtime)<10 "
        aus=self.client.execute(sql)
        v,mode=[],[]
        for value in aus:
            v.append(value[0])
            mode.append(value[1])
        hist_func_np.hist_con_show(workbook,['v','vehicle speed km/h'],[np.array(v)],range(0,180,10),2)
        if self.proj in {'passat','tiguan'}:
            hist_func_np.hist_cros_con_dis_show(workbook,["driving mode"],np.array(v),range(0,180,10),np.array(mode),['EV','PHEV',"FV"])

    def Charge_summary(self):
        all_charge=self.get_Charge()
        workbook = xlsxwriter.Workbook(self.path+self.proj+"_charge"+".xlsx")

        [time_h_s,time_d,soc_s,soc_e,soc_d,time_d_c,mode]=self.get_Charge_varible(all_charge)

        name_list=['SOC','start_SOC','end_SOC']
        in_list=[soc_s,soc_e]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(0,120,10),2)
        hist_func_np.hist_cros_2con_show(workbook,['SOC_cros'],soc_s,range(0,120,10),soc_e,range(0,120,10))

        name_list=['Charging_Start_Hour','start time']
        hist_func_np.hist_con_show(workbook,name_list,[time_h_s],range(25))

        name_list=['Charging_time','Charging_time','Charging_time(convert SOC0~100)']
        time_interval=[0,30,60,120,180,240,300,360,420,480,540,600,660,720,780,840,900,1500]
        hist_func_np.hist_con_show(workbook,name_list,[time_d,time_d_c],time_interval,2)
        mode_interval=['mode2','mode3_2','mode3_1','DC']
        hist_func_np.hist_cros_con_dis_show(workbook,['charging mode-time'],time_d,time_interval,mode,mode_interval)
        hist_func_np.hist_cros_con_dis_show(workbook,['charging mode-time(convert)'],time_d_c,time_interval,mode,mode_interval)

        [mode,temp_s,temp_e,temp_min,temp_max,temp_mean,temp_range,power_max,power_mean]=self.get_temp_pow(all_charge)
        
        name_list=['temperature','start_temp','end_temp','min_temp','max_temp','temp_mean','temp_range']
        in_list=[temp_s,temp_e,temp_min,temp_max,temp_mean,temp_range]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(-10,60,5),2)
        hist_func_np.hist_cros_con_dis_show(workbook,['charging temp-mode'],temp_mean,range(-10,60,5),mode,mode_interval)

        name_list=['power','pow_max','power_mean']
        in_list=[power_max,power_mean]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(50),2)
        hist_func_np.hist_cros_con_dis_show(workbook,['charging pow-mode'],power_mean,range(50),mode,mode_interval)

        workbook.close()

    def get_drive(self):
        sql="SELECT deviceid,uploadtime,delta,acc,soc,d_soc " \
            "FROM (SELECT deviceid,uploadtime,runningDifference(vh_s) AS delta,acc,soc,runningDifference(soc) AS d_soc " \
            "FROM (SELECT deviceid,uploadtime,if(vehiclestatus=='STARTED',9,8) as vh_s,CAST(accmiles,'float') as acc,soc " \
            "FROM en.rtm_vds " \
            "WHERE " + self.con + " ORDER BY deviceid,uploadtime))" \
            "WHERE delta IN (1,-1)"
        aus=self.client.execute(sql)
        #aus=[0 vin  1 time  2车辆状态变化标志位（-1start->stop 1stop->start）  3 mileage   4 soc   5 d_soc]
        all_drive=[]        
        #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
        tmp=[]
        #tmp=[0start_d_soc, 1end_d_soc]
        i=1
        while i<len(aus):
            if aus[i][0]==aus[i-1][0] and aus[i-1][2]==1 and aus[i][2]==-1:
                #i-1时刻是开始行驶，i是结束行驶时刻
                all_drive.append([aus[i][0],aus[i-1][1],aus[i][1],aus[i-1][4],aus[i][4],aus[i-1][3],aus[i][3]])
                #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
                tmp.append([aus[i-1][5],aus[i][5]])
                # tmp=[0start_d_soc, 1 end_d_soc]
                i+=2
            else:
                i+=1
        
        l1=len(all_drive)
        count_1=0#行驶前数据丢失计数
        count_2=0#行驶后的数据丢失计数
        count_12=0#行驶前，行驶后均数据丢失
        count_3=0#行驶前后里程不变的次数
        i=0
        while i<len(tmp):
            if abs(tmp[i][0])>5 or abs(tmp[i][1])>5:
                if abs(tmp[i][0])>5:
                    count_1+=1
                if abs(tmp[i][1])>5:
                    count_2+=1
                if abs(tmp[i][0])>5 and abs(tmp[i][1])>5:
                    count_12+=1
                tmp.pop(i)
                all_drive.pop(i)
            elif all_drive[i][6]==all_drive[i][5]:
                count_3+=1
                tmp.pop(i)
                all_drive.pop(i)
            else:
                i+=1

        l2=len(all_drive)

        file=open(self.path+self.proj+"_log.txt",'a')
        file.write("---------driving analysis--------------\r\n")
        file.write("原始行驶次数："+str(l1)+"\r\n")
        file.write("行驶前数据丢失次数："+str(count_1)+"占比："+str(round(count_1/l1*100,2))+"%\r\n")
        file.write("行驶后数据丢失次数："+str(count_2)+"占比："+str(round(count_2/l1*100,2))+"%\r\n")
        file.write("行驶前后数据均丢失次数："+str(count_12)+"占比："+str(round(count_12/l1*100,2))+"%\r\n")
        file.write("行驶前后里程不变的次数："+str(count_3)+"占比："+str(round(count_3/l1*100,2))+"%\r\n")
        file.write("处理后行驶次数："+str(l2)+"\r\n")
        file.close()

        return all_drive
    
    #return time_h_s,time_d,soc_s,soc_e,soc_d,mile_d,mile_d_c,v_mean
    def get_drive_variable(self):
        all_drive=self.get_drive()
        #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
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

        return np.array(time_h_s),np.array(time_d),np.array(soc_s),np.array(soc_e),np.array(soc_d),np.array(mile_d),np.array(mile_d_c),np.array(v_mean)

    def drive_summary(self):
        workbook = xlsxwriter.Workbook(self.path+self.proj+"_drive"+".xlsx")
        self.daily_mileage(workbook)
        self.hourly_mileage(workbook)
        self.percharge_mile(workbook)
        self.v_mode(workbook)

        [time_h_s,time_d,soc_s,soc_e,soc_d,mile_d,mile_d_c,v_mean]=self.get_drive_variable()

        name_list=['SOC','start_SOC','end_SOC']
        in_list=[soc_s,soc_e]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(0,120,10),2)

        name_list=['driving_Start_Hour','start time']
        hist_func_np.hist_con_show(workbook,name_list,[time_h_s],range(25))

        name_list=['driving_time','driving_time']
        hist_func_np.hist_con_show(workbook,name_list,[time_d],[0,30,60,90,120,180,240,300,1500],2)

        '''
        name_list=['mile_perCharging(to delete)','mile_perCharging','mile_convert']
        in_list=[mile_d,mile_d_c]
        hist_func_np.hist_con_show(workbook,name_list,in_list,range(0,500,20),2)
        '''

        name_list=['mean_V','mean_V(Including idle speed)']
        hist_func_np.hist_con_show(workbook,name_list,[v_mean],[0,10,20,30,40,50,60,100,210],2)

        self.E_motor(workbook)
        self.BMS(workbook)

        workbook.close()
