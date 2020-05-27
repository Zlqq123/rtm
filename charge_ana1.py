import xlsxwriter
import time
import numpy as np
import hist_func
import sys


class RtmCharging():
    def __init__ (self,name,path,proj,client):
        self.name=name
        self.path=path
        self.client=client
        if proj=="lavida":
            self.a='LSVA%'
            self.proj=proj
        elif proj=="passat":
            self.a='LSVC%'
            self.proj=proj
        elif proj=="tiguan":
            self.a='LSVU%'
            self.proj=proj
        else:
            print("proj error:proj must be in {'lavida','passat','tiguan'}")
            sys.exit(-1)



    #return all_charge=i*[0vin,1time_start,2soc_start,3mile_start,4soc_end,5mile_end,6charging_mode]
    def get_start(self):
        sql1="SELECT deviceid,runningDifference(char_s) AS delta,uploadtime,soc,acc,ch_mode " \
            "from (SELECT deviceid,uploadtime,soc,CAST(accmiles,'float') as acc,if(chargingstatus=='NO_CHARGING',7,8) as char_s, " \
            "multiIf(totalcurrent<=-20,'DC',totalcurrent<=-10 and totalcurrent>-20,'mode3_1',totalcurrent<=-5 and totalcurrent>-10,'mode3_2',totalcurrent<0 and totalcurrent>-5,'mode2','discharging') as ch_mode " \
            "from en.rtm_vds " \
            "where cocesprotemp1!='NULL' and deviceid like '" + self.a + "' AND acc>100 ORDER BY deviceid,uploadtime) " \
            "where delta==1 or delta==-1"
        aus=self.client.execute(sql1)
        #aus=[0 vin  1 充电变化标志位  2 时间  3 soc  4 mileage  5 charging_mode(DC/AC)]
        all_charge=[]
        #all_charge=[0vin,1time_start,2soc_start,3mile_start,4soc_end,5mile_end,6charging_mode]
        i=1
        while i<len(aus):
            if aus[i][0]==aus[i-1][0] and aus[i-1][1]==1 and aus[i][1]==-1:#i-1时刻是开始充电，i是结束充电时刻
                all_charge.append([aus[i][0],aus[i-1][2],aus[i-1][3],aus[i-1][4],aus[i][3],aus[i][4],aus[i-1][5]])
                #all_charge=[0vin, 1time_start,2soc_start,  3mile_start,4soc_end,5mile_end,6charging_mode]
                if len(all_charge)>1:
                    if all_charge[-1][0]==all_charge[-2][0] and all_charge[-1][3]==all_charge[-2][5]:
                        #如果上一次充电结束的里程与下一次开始充电的里程不变，合并为一次充电。前提是同一辆车。
                        all_charge[-2][4:6]=all_charge[-1][4:6]
                        all_charge.pop()
                i+=2
            else:
                i+=1
        return all_charge

    #仅all_charge就可以得到的量：充电起始SOC 结束SOC 开始充电时刻，
    #每次充电间隔行驶里程，每次充电间隔消耗SOC，折算满放SOC的全电行驶里程（for bev）
    #return [time_h_s,soc_s,soc_e,mile,mile_convert]
    def get_soc_time_mode_mile(self):

        all_charge=self.get_start()#all_charge=i*[0vin,1time_start,2soc_start,3mile_start,4soc_end,5mile_end,6charging_mode]

        time_h_s=[]
        soc_s,soc_e=[],[]
        for a in all_charge:
            time_h_s.append(a[1].hour)
            soc_s.append(a[2])
            soc_e.append(a[4])
        
        mile,soc_driving,mile_convert=[],[],[]
        for i in range(len(all_charge)-1):
            if all_charge[i][0]==all_charge[i+1][0] and all_charge[i][4]>all_charge[i+1][2]:
                mile.append(all_charge[i+1][3]-all_charge[i][5])
                soc_driving.append(all_charge[i][4]-all_charge[i+1][2])
                mile_convert.append((all_charge[i+1][3]-all_charge[i][5])/(all_charge[i][4]-all_charge[i+1][2])*100)
        
        return time_h_s,soc_s,soc_e,mile,mile_convert

    #需要充电过程数据才能得到的量
    #每次充电消耗的时间，折算满充的充电时间，充电过程中的温度，起始值，结束值，最大值，最小值，平均值；充电过程中功率，最大电功率，平均功率
    #return [time_d,mode,soc_e,soc_d,time_d_convert,temp_s,temp_e,temp_min,temp_max,temp_mean,power_max,power_mean]
    def get_temp_pow(self):
        all_charge=self.get_start()

        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SELECT deviceid,uploadtime,-totalcurrent*totalvolt/1000,arrayReduce('sum',temp_list)/length(temp_list),soc " \
            "from en.rtm_vds where chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') AND cocesprotemp1!='NULL' " \
            "and deviceid like '" + self.a + "' AND CAST(accmiles,'float')>100 ORDER BY deviceid,uploadtime"
        aus=self.client.execute(sql)
        ss,ee=[],[]#用于存放aus中每段充电开始的index 和每次充电结束的index
        not_find=[]#用于存放在aus中找不到all_charge中的充电次数的index,目的是让mode变量与后面pow和temp相关变量的长度一致，并且一一对应上

        i,j=0,0 #j为all_charge的index      i 为aus的index
        for j in range(len(all_charge)):#根据all_charge中每次充电开始时间，找到aus中每次充电开始-结束时间
            if ss==[]: #每次i从上次充电开始的时候开始搜索
                i=0
            else:
                i=ss[-1]
            ff=0 # 找不找得到的falg
            while aus[i][0]<=all_charge[j][0] and ff==0 and i<len(aus): #如果vin码已经搜索到下一辆车，循环停止#如果找到了，ff=1循环停止
                if all_charge[j][0]==aus[i][0] and all_charge[j][1]==aus[i][1]:
                    #找到aus中vin码和时间与all_charge中完全的数据条，index保存在ss中
                    ff=1                    
                    if len(ss)>0:#前一个时刻保存到上段充电结束时刻ee中
                        ee.append(i-1)
                    ss.append(i)
                i+=1
            if ff==0: #如果找不到
                not_find.append(j)
        ss.pop()#最后一个充电数据找不到结束点，故将开始点也删除。
        j=0
        mode=[]#与后面过程变量由相同长度的mode
        for i in range(len(all_charge)-1):#最后一次充电不要
            if j<len(not_find) and i==not_find[j]:
                j+=1
            else:
                mode.append(all_charge[i][6])
        i=0
        while i<len(ss):#把开头和结束点对应的vin码不一样的删除 把开始点和结束点是一个点的删除
            if aus[ss[i]][0]!=aus[ee[i]][0] or ss[i]==ee[i]:
                ss.pop(i)
                ee.pop(i)
                mode.pop(i)
            else:
                i+=1

        time_d,time_d_convert=[],[]
        soc_e,soc_d=[],[]
        temp_s,temp_e,temp_min,temp_max,temp_mean=[],[],[],[],[]
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
            d=aus[ee[i]][1]-aus[ss[i]][1]
            time_d.append(d.seconds/60)
            soc_e.append(aus[ee[i]][4])
            soc_d.append(aus[ee[i]][4]-aus[ss[i]][4])
            if aus[ee[i]][4]-aus[ss[i]][4]>0:
                sd=aus[ee[i]][4]-aus[ss[i]][4]
            else:
                sd=1
            time_d_convert.append(d.seconds/60/sd*100)
        
        return time_d,mode,soc_e,soc_d,time_d_convert,temp_s,temp_e,temp_min,temp_max,temp_mean,power_max,power_mean

    def Charge_summary(self):
        workbook = xlsxwriter.Workbook(self.path+"charge_"+self.proj+".xlsx")

        [time_h_s,soc_s,soc_e,mile,mile_convert]=self.get_soc_time_mode_mile()
        [time_d,mode,soc_ep,soc_d,time_d_convert,temp_s,temp_e,temp_min,temp_max,temp_mean,power_max,power_mean]=self.get_temp_pow()

        name_list=['SOC','start_SOC','end_SOC','end_SOCp',]
        in_list=[soc_s,soc_e,soc_ep]
        hist_func.hist_con_show(workbook,name_list,5,in_list,range(0,120,10))

        name_list=['Charging_Start_Hour','start time']
        hist_func.hist_con_show(workbook,name_list,0,[time_h_s],range(24))

        name_list=['Charging_time','Charging_time','Charging_time(convert SOC0~100)']
        time_interval=[0,30,60,120,180,240,300,360,420,480,540,600,660,720,780,840,1500]
        hist_func.hist_con_show(workbook,name_list,4,[time_d,time_d_convert],time_interval)
        hist_func.hist_cros_con_dis_show(workbook,['charging mode-time'],time_d,mode,time_interval)
        hist_func.hist_cros_con_dis_show(workbook,['charging mode-time(convert)'],time_d_convert,mode,time_interval)

        temp_r=[temp_max[i]-temp_min[i] for i in range(len(temp_min))]
        name_list=['temperature','start_temp','end_temp','min_temp','max_temp','temp_mean','temp_range']
        in_list=[temp_s,temp_e,temp_min,temp_max,temp_mean,temp_r]
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(-10,60,5))

        name_list=['power','pow_max','power_mean']
        in_list=[power_max,power_mean]
        hist_func.hist_con_show(workbook,name_list,4,in_list,[0,2,4,8,12,40])
        

        name_list=['mile_perCharging','mile_perCharging','mile_convert']
        in_list=[mile,mile_convert]
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(0,500,10))




        workbook.close()




            
               







