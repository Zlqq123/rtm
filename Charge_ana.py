import xlsxwriter
import time
import numpy as np
import hist_func
import sys

'''
V1.0充电数据的切取逻辑有问题，导致统计出来的tiguanL的充电时间过长。
'''
class RtmCharging():
    def __init__ (self,name,path,proj,client):
        self.name=name
        self.path=path
        self.client=client
        self.s_e=[]
        if proj=="lavida":
            a='LSVA%'
            self.proj=proj
        elif proj=="passat":
            a='LSVC%'
            self.proj=proj
        elif proj=="tiguan":
            a='LSVU%'
            self.proj=proj
        else:
            print("proj error:proj must be in {'lavida','passat','tiguan'}")
            sys.exit(-1)

        self.sql_con="from en.rtm_vds where chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') AND cocesprotemp1!='NULL' " \
            "and deviceid like '" + a + "' AND CAST(accmiles,'float')>100 ORDER BY deviceid,uploadtime"

    def cut_data(self):
        if self.s_e==[]:
            sql="SELECT deviceid,uploadtime,soc,CAST(accmiles,'float')"+self.sql_con
            input_data=self.client.execute(sql)
            ss,ee=[0],[]
            for i in range(len(input_data)-2):
                if input_data[i][0]!=input_data[i+1][0]:
                    ss.append(i+1)
                    ee.append(i)
                elif input_data[i][3]<input_data[i+1][3]:
                #elif input_data[i][2]>input_data[i+1][2] and input_data[i][3]<input_data[i+1][3]:
                    ss.append(i+1)
                    ee.append(i)
        
            ee.append(len(input_data)-1)
            i=0
            while i<len(ss):
                d=input_data[ee[i]][1]-input_data[ss[i]][1]
                if (d.seconds/60)<5:#小于5分钟的充电段去除
                    ss.pop(i)
                    ee.pop(i)
                else:
                    i+=1
            self.s_e=[ss,ee]

    def get_soc(self):
        self.cut_data()
        soc_s,soc_e,soc_d=[],[],[]
        sql="SELECT soc "+self.sql_con
        aus=self.client.execute(sql)
        len_c=len(self.s_e[0])
        for i in range(len_c):
            soc_s.append(aus[self.s_e[0][i]][0])
            soc_e.append(aus[self.s_e[1][i]][0])
            soc_d.append(aus[self.s_e[1][i]][0]-aus[self.s_e[0][i]][0])
        
        return soc_s,soc_e,soc_d

    def get_time(self):
        self.cut_data()
        time_h_s,time_d=[],[]#time_h_e=[]
        sql="SELECT uploadtime "+self.sql_con
        aus=self.client.execute(sql)
        time_a=[]
        for i in aus:
            time_a.append(i[0])
        
        ss=self.s_e[0]
        ee=self.s_e[1]

        for i in range(len(ss)):
            time_h_s.append(time_a[ss[i]].hour)
            d=time_a[ee[i]]-time_a[ss[i]]
            time_d.append(d.seconds/60)
        
        return time_h_s,time_d

    def get_temp(self):
        self.cut_data()
        temp_s,temp_e,temp_min,temp_max,temp_mean=[],[],[],[],[]
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list SELECT arrayReduce('sum',temp_list)/length(temp_list) "+self.sql_con
        aus=self.client.execute(sql)
        temp_a=[]
        for i in aus:
            temp_a.append(i[0])
        
        ss=self.s_e[0]
        ee=self.s_e[1]
        for i in range(len(ss)):
            temp_s.append(temp_a[ss[i]])
            temp_e.append(temp_a[ss[i]])
            temp_min.append(min(temp_a[ss[i]:ee[i]]))
            temp_max.append(max(temp_a[ss[i]:ee[i]]))
            temp_mean.append(sum(temp_a[ss[i]:ee[i]])/len(temp_a[ss[i]:ee[i]]))
        
        return temp_s,temp_e,temp_min,temp_max,temp_mean

    def get_mode(self):
        self.cut_data()
        ss=self.s_e[0]
        sql="SELECT totalcurrent "+self.sql_con
        aus=self.client.execute(sql)
        charge_mode=[]

        for i in range(len(ss)):
            a1=aus[ss[i]+1][0]
            a2=aus[ss[i]+2][0]
            a3=aus[ss[i]+3][0]
            a=min(a1,a2,a3)
            if a<-20:
                charge_mode.append("mode4(DC)")
            elif a<-10:
                charge_mode.append("mode3(AC_7.2kW)")
            elif a<-5:
                charge_mode.append("mode3(AC_3.6kW)")
            elif a<0:
                charge_mode.append("mode2(AC)")
            else:
                charge_mode.append("error")
        
        return charge_mode

    def get_pow(self):
        self.cut_data()
        power_max,power_mean=[],[]
        ss=self.s_e[0]
        ee=self.s_e[1]
        sql="SELECT -totalcurrent*totalvolt/1000 "+self.sql_con
        aus=self.client.execute(sql)
        a_pow=[]
        for i in aus:
            a_pow.append(i[0])
        for i in range(len(ss)):
            power_max.append(max(a_pow[ss[i]:ee[i]]))
            power_mean.append(sum(a_pow[ss[i]:ee[i]])/len(a_pow[ss[i]:ee[i]]))
        return power_max,power_mean

    #return[mileage_per_charging,SOC_Windoews_PerCharging,Convert_full_electric(SOCfrom 0~100%)_mileage]
    def get_mile_soc(self):
        self.cut_data()
        mile,soc_r,mile1=[],[],[]
        ss=self.s_e[0]
        ee=self.s_e[1]
        sql="SELECT deviceid,soc,CAST(accmiles,'float') "+self.sql_con
        aus=self.client.execute(sql)

        for i in range(len(ss)-1):
            s=ee[i]
            e=ss[i+1]
            if aus[s][0]==aus[e][0]:
                mile.append(aus[e][2]-aus[s][2])
                soc_r.append(aus[s][1]-aus[e][1])
                mile1.append((aus[e][2]-aus[s][2])/(aus[s][1]-aus[e][1])*100)
        
        return mile,soc_r,mile1

    def Charge_summary(self):
        workbook = xlsxwriter.Workbook(self.path+"charge_"+self.proj+".xlsx")

        [temp_s,temp_e,temp_min,temp_max,temp_mean]=self.get_temp()
        temp_r=[temp_max[i]-temp_min[i] for i in range(len(temp_min))]
        name_list=['temperature','start_temp','end_temp','min_temp','max_temp','temp_mean','temp_range']
        in_list=[temp_s,temp_e,temp_min,temp_max,temp_mean,temp_r]
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(-10,60,5))

        [soc_s,soc_e,soc_d]=self.get_soc()
        name_list=['SOC','start_SOC','end_SOC','SOC_range']
        in_list=[soc_s,soc_e,soc_d]
        hist_func.hist_con_show(workbook,name_list,5,in_list,range(0,120,10))

        [time_h_s,time_d]=self.get_time()
        name_list=['Charging_Start_Hour','start time']
        hist_func.hist_con_show(workbook,name_list,0,time_h_s,range(24))

        time_d_c=[time_d[i]/soc_d[i]*100 for i in range(len(time_d))]
        name_list=['Charging_time','Charging_time','Charging_time(convert SOC0~100)']
        hist_func.hist_con_show(workbook,name_list,4,[time_d,time_d_c],[0,30,60,120,180,240,300,360,420,480,540,600,660,720,780,840,1500])

        charge_mode=self.get_mode()
        hist_func.hist_cros_con_dis_show(workbook,['charging mode-time'],time_d,charge_mode,[0,30,60,120,180,240,300,360,420,480,540,600,660,720,780,840,1500])
        hist_func.hist_cros_con_dis_show(workbook,['charging mode-time(convert SOC0~100)'],time_d_c,charge_mode,[0,30,60,120,180,240,300,360,420,480,540,600,660,720,780,840,1500])

        [power_max,power_mean]=self.get_pow()


        [mile,soc_r,mile1]=self.get_mile_soc()

        workbook.close()


'''
v2.0
通过chargestatus切换判断，来切取充电数据，
如果上一次充电结束的里程与下一次开始充电的里程不变，合并为一次充电。前提是同一辆车。
'''
class RtmCharging():
    def __init__ (self,path,proj,client):
        #self.name=name
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
            ff=0 # 找不找得到的flag
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
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(0,120,10))

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

'''
V3.0
去除充电中断的噪点，充电前后ΔSOC>0的充电数据不参与统计
添加数据清理log
加入切取行驶数据模块 get_drive
加入统计电机工作点，使用手动采样（取second<10的点，采样位总样本数的1/6）
统计电池工作点模块，使用手动采样（取second<10的点，采样位总样本数的1/6）
'''
class RtmAna():
    def __init__ (self,path,proj,client):
        #self.name=name
        self.path=path
        self.client=client
        if proj=="lavida":
            self.con="deviceid like 'LSVA%' AND "
            self.proj=proj
        elif proj=="passat":
            self.con="deviceid like 'LSVC%' AND "
            self.proj=proj
        elif proj=="tiguan":
            self.con="deviceid like 'LSVU%' AND "
            self.proj=proj
        else:
            print("proj error:proj must be in {'lavida','passat','tiguan'}")
            sys.exit(-1)


    
    #return all_charge=i*[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6charging_mode]
    def get_Charge(self):
        sql1="SELECT deviceid,uploadtime,delta,soc,d_soc,acc,ch_mode " \
            "FROM (SELECT deviceid,uploadtime,runningDifference(char_s) AS delta,soc, runningDifference(soc) AS d_soc,acc, " \
            "multiIf(P>8,'DC',P<=8 and P>5,'mode3_1',P<=5 and P>2.5,'mode3_2',P<=2.5 and P>0,'mode2','discharging') AS ch_mode " \
            "FROM (SELECT deviceid,uploadtime,soc,CAST(accmiles,'float') AS acc, if(chargingstatus=='NO_CHARGING',7,8) AS char_s, -totalcurrent*totalvolt/1000 AS P " \
            "FROM en.rtm_vds " \
            "WHERE " + self.con + " acc>100 ORDER BY deviceid,uploadtime)) " \
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
        dt=datetime.now()
        file.write("\r\n\r\n")
        file.write("##charge analysis##################\r\n")
        file.write("运行日期&时间："+str(dt)+"\r\n")
        file.write("原始充电次数："+str(l1)+"\r\n")
        file.write("充电前数据丢失次数："+str(count_1)+"占比："+str(count_1/l1*100)+"%\r\n")
        file.write("充电后数据丢失次数："+str(count_2)+"占比："+str(count_2/l1*100)+"%\r\n")
        file.write("充电前后数据均丢失次数："+str(count_12)+"占比："+str(count_12/l1*100)+"%\r\n")
        file.write("充电合并次数："+str(count_3)+"占比："+str(count_3/l1*100)+"%\r\n")
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
        
        return time_h_s,time_d,soc_s,soc_e,soc_d,time_d_c,mode
    
    #return [mode,temp_s,temp_e,temp_min,temp_max,temp_mean,temp_range,power_max,power_mean]
    def get_temp_pow(self,all_charge):

        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SELECT deviceid,uploadtime,-totalcurrent*totalvolt/1000,arrayReduce('sum',temp_list)/length(temp_list) " \
            "FROM en.rtm_vds WHERE chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') AND cocesprotemp1!='NULL' " \
            "AND "+ self.con +" CAST(accmiles,'float')>100 ORDER BY deviceid,uploadtime"
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
        file.write("未匹配的充电次数："+str(len(not_find))+"占比："+str(len(not_find)/len(all_charge)*100)+"%\r\n")
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
        
        return mode,temp_s,temp_e,temp_min,temp_max,temp_mean,temp_range,power_max,power_mean

    def Charge_summary(self):
        all_charge=self.get_Charge()
        workbook = xlsxwriter.Workbook(self.path+self.proj+"_charge"+".xlsx")

        [time_h_s,time_d,soc_s,soc_e,soc_d,time_d_c,mode]=self.get_Charge_varible(all_charge)

        name_list=['SOC','start_SOC','end_SOC']
        in_list=[soc_s,soc_e]
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(0,120,10))

        name_list=['Charging_Start_Hour','start time']
        hist_func.hist_con_show(workbook,name_list,0,[time_h_s],range(24))

        name_list=['Charging_time','Charging_time','Charging_time(convert SOC0~100)']
        time_interval=[0,30,60,120,180,240,300,360,420,480,540,600,660,720,780,840,900,1500]
        hist_func.hist_con_show(workbook,name_list,4,[time_d,time_d_c],time_interval)
        hist_func.hist_cros_con_dis_show(workbook,['charging mode-time'],time_d,mode,time_interval)
        hist_func.hist_cros_con_dis_show(workbook,['charging mode-time(convert)'],time_d_c,mode,time_interval)

        [mode,temp_s,temp_e,temp_min,temp_max,temp_mean,temp_range,power_max,power_mean]=self.get_temp_pow(all_charge)
        
        name_list=['temperature','start_temp','end_temp','min_temp','max_temp','temp_mean','temp_range']
        in_list=[temp_s,temp_e,temp_min,temp_max,temp_mean,temp_range]
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(-10,60,5))
        hist_func.hist_cros_con_dis_show(workbook,['charging temp-mode'],temp_mean,mode,range(-10,60,5))

        name_list=['power','pow_max','power_mean']
        in_list=[power_max,power_mean]
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(50))
        hist_func.hist_cros_con_dis_show(workbook,['charging pow-mode'],power_mean,mode,range(50))

        workbook.close()

    def get_drive(self):
        sql="SELECT deviceid,uploadtime,delta,acc,soc,d_soc " \
            "FROM (SELECT deviceid,uploadtime,runningDifference(vh_s) AS delta,acc,soc,runningDifference(soc) AS d_soc " \
            "FROM (SELECT deviceid,uploadtime,if(vehiclestatus=='STARTED',9,8) as vh_s,CAST(accmiles,'float') as acc,soc " \
            "FROM en.rtm_vds " \
            "WHERE " + self.con + " acc>100 ORDER BY deviceid,uploadtime))" \
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
        dt=datetime.now()
        file.write("##driving analysis##################\r\n")
        file.write("运行日期&时间："+str(dt)+"\r\n")
        file.write("原始行驶次数："+str(l1)+"\r\n")
        file.write("行驶前数据丢失次数："+str(count_1)+"占比："+str(count_1/l1*100)+"%\r\n")
        file.write("行驶后数据丢失次数："+str(count_2)+"占比："+str(count_2/l1*100)+"%\r\n")
        file.write("行驶前后数据均丢失次数："+str(count_12)+"占比："+str(count_12/l1*100)+"%\r\n")
        file.write("行驶前后里程不变的次数："+str(count_3)+"占比："+str(count_3/l1*100)+"%\r\n")
        file.write("处理后行驶次数："+str(l2)+"\r\n")
        file.close()

        return all_drive
    
    #return time_h_s,time_d,soc_s,soc_e,soc_d,mile_d,mile_d_c,v_mean
    def get_drive_variable(self):
        all_drive=self.get_drive()#all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
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
            if a[4]-a[3]>0:
                mile_d_c.append((a[6]-a[5])/(a[3]-a[4])*100)
            if d.seconds>0:
                v_mean.append((a[6]-a[5])/d.seconds*3.6)
        
        return time_h_s,time_d,soc_s,soc_e,soc_d,mile_d,mile_d_c,v_mean

    def get_percharge_mile(self,workbook):
        sql1="SELECT deviceid,uploadtime,delta,soc,d_soc,acc " \
            "FROM (SELECT deviceid,uploadtime,runningDifference(char_s) AS delta,soc, runningDifference(soc) AS d_soc,acc " \
            "FROM (SELECT deviceid,uploadtime,soc,CAST(accmiles,'float') AS acc, if(chargingstatus=='NO_CHARGING',7,8) AS char_s " \
            "FROM en.rtm_vds " \
            "WHERE " + self.con + " acc>100 ORDER BY deviceid,uploadtime)) " \
            "WHERE delta IN (1,-1)"
        aus=self.client.execute(sql1)
        #aus=[0 vin  1 时间  2充电变化标志位  3 soc   4 d_soc  5 mileage ]
        all_drive=[]
        i=1
        while i<len(aus):
            if aus[i][0]==aus[i-1][0] and aus[i-1][2]==-1 and aus[i][2]==1:#i-1时刻是开始行驶，i是结束行驶时刻
                all_drive.append([aus[i][0],aus[i-1][1],aus[i][1],aus[i-1][3],aus[i][3],aus[i-1][5],aus[i][5]])
                #all_drive=[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6mile_end]
                i+=2
            else:
                i+=1
        l1=len(all_drive)
        soc_r=[]
        mile_r=[]
        mile_r_c=[]
        for a in all_drive:
            if a[3]>a[4] and a[6]>a[5]:  # 行驶过程中SOC减少，里程增加
                soc_r.append(a[3]-a[4])
                mile_r.append(a[6]-a[5])
                mile_r_c.append((a[6]-a[5])/(a[3]-a[4])*100)
        
        l2=len(mile_r_c)
        file=open(self.path+self.proj+"_log.txt",'a')
        file.write("##mile perCharging analysis##################\r\n")
        file.write("原始行驶次数："+str(l1)+"\r\n")
        file.write("SOC 没有变化的行驶次数："+str(l1-l2)+"   占比："+str((l1-l2)/l1*100)+"%\r\n")
        file.write("处理后行驶次数："+str(l2)+"\r\n")
        file.close()

        name_list=['mile_perCharging','mile_perCharging','mile_convert']
        in_list=[mile_r,mile_r_c]
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(0,500,20))
    
    def E_motor(self,workbook):
        sql="SELECT cast(emspeed,'float') as sp,cast(emtq,'float') as tq,sp*tq/9550,cast(emvolt,'float')*cast(emctlcut,'float')/1000,cast(emtemp,'float'),cast(emctltemp,'float') " \
            "FROM en.rtm_vds " \
            "WHERE cast(vehiclespeed,'float')>0 AND "+ self.con+ " CAST(accmiles,'float')>100 and toSecond(uploadtime)<10 "
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
                if value[2]>0 and value[3]>0:
                    eff.append(value[2]/value[3]*100)
                elif value[2]<0 and value[3]<0:
                    eff.append(value[3]/value[2]*100)
        
        hist_func.hist_cros_2con_show(workbook,['LE_working_point'],speed,range(-4000,13000,500),torq,range(-300,400,50))
        hist_func.hist_con_show(workbook,["LE-eff",'LE_efficiency'],4,[eff],range(0,110,10))
        hist_func.hist_con_show(workbook,["LE-temp",'E_motor temperature','LE temperature'],4,[temp_motor,temp_LE],range(-10,60,5))
        
    def BMS(self,workbook):
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SElECT soc,arrayReduce('sum',temp_list)/length(temp_list),totalcurrent*totalvolt/1000 " \
            "FROM en.rtm_vds " \
            "WHERE chargingstatus='NO_CHARGING' and totalcurrent>0 and cocesprotemp1!='NULL' " \
            "AND "+self.con+" CAST(accmiles,'float')>100 and toSecond(uploadtime)<10"
        aus=self.client.execute(sql)

        soc,temp_av,pow_bms=[],[],[]
        for value in aus:
            soc.append(value[0])
            temp_av.append(value[1])
            pow_bms.append(value[2])

        hist_func.hist_cros_2con_show(workbook,['discharging'],soc,range(0,115,5),temp_av,range(-10,55,5))

        soc,temp_av,pow_bms=[],[],[]
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SElECT soc,arrayReduce('sum',temp_list)/length(temp_list),totalcurrent*totalvolt/1000 " \
            "FROM en.rtm_vds " \
            "where chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') AND totalcurrent<0 AND cocesprotemp1!='NULL' " \
            "AND "+self.con+" CAST(accmiles,'float')>100 and toSecond(uploadtime)<10"
        aus=self.client.execute(sql)
        soc,temp_av,pow_bms=[],[],[]
        for value in aus:
            soc.append(value[0])
            temp_av.append(value[1])
            pow_bms.append(value[2])
        
        hist_func.hist_cros_2con_show(workbook,['charging'],soc,range(0,115,5),temp_av,range(-10,55,5))

    def daily_mileage(self,workbook):
        sql="SELECT deviceid,toDate(uploadtime),max(CAST(accmiles,'float')),min(CAST(accmiles,'float')) " \
            "from rtm_vds where "+ self.con+" CAST(accmiles,'float')>100 group by deviceid,toDate(uploadtime) "
        aus=self.client.execute(sql)
        mileage=[]
        for value in aus:
            mileage.append(value[2]-value[3])
        
        hist_func.hist_con_show(workbook,["daily-mile",'mileage per day'],4,[mileage],range(0,500,20))

    def v_mode(self):
        sql="SELECT cast(vehiclespeed,'float') as v,operationmode,CAST(accmiles,'float') as acc " \
            "from rtm_vds " \
            "Where "+ self.con+" acc>100 AND v>0 and toSecond(uploadtime)<10 GROUP BY v"
        aus=self.client.execute(sql)
        v=[]
        mode=[]
        for value in aus:
            v.append(value(0))
            mode.append(value[1])
        return v,mode

    def drive_summary(self):
        workbook = xlsxwriter.Workbook(self.path+self.proj+"_drive"+".xlsx")
        self.daily_mileage(workbook)
        self.get_percharge_mile(workbook)

        [time_h_s,time_d,soc_s,soc_e,soc_d,mile_d,mile_d_c,v_mean]=self.get_drive_variable()
        
        name_list=['SOC','start_SOC','end_SOC']
        in_list=[soc_s,soc_e]
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(0,120,10))

        name_list=['driving_Start_Hour','start time']
        hist_func.hist_con_show(workbook,name_list,0,[time_h_s],range(24))

        name_list=['driving_time','driving_time']
        hist_func.hist_con_show(workbook,name_list,4,[time_d],[0,30,60,90,120,180,240,300,1500])

        name_list=['mile_perCharging(to delete)','mile_perCharging','mile_convert']
        in_list=[mile_d,mile_d_c]
        hist_func.hist_con_show(workbook,name_list,4,in_list,range(0,500,20))

        name_list=['mean_V','mean_V(Including idle speed)']
        hist_func.hist_con_show(workbook,name_list,4,[v_mean],[0,10,20,30,40,50,60,100,210])

        self.E_motor(workbook)
        self.BMS(workbook)

        workbook.close()

