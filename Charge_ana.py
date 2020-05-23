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





class Rtmrunning():
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

    def hist_v(self):
        sql="SELECT cast(vehiclespeed,'float'),CAST(accmiles,'float') from en.rtm_vds " \
            "where cast(vehiclespeed,'float')>=0.1 and deviceid like '"+self.a+"' AND CAST(accmiles,'float')>100 " \
            "order by cast(vehiclespeed,'float')"
        aus=client.execute(sql)
        v,mile=[],[]
        for a in aus:
            v.append(a[0])
            mile.append(a[1])
        [block,v_freq]=hist_func.hist1(v,[0,10,20,30,40,50,60,70,80,90,100,110,120,300])

    def hist_battery(self):
        #battery soc-temp-power
        workbook = xlsxwriter.Workbook(self.path+"battery working point "+self.proj+".xlsx")
        #discharging
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SELECT arrayReduce('sum',temp_list)/length(temp_list),soc,totalcurrent*totalvolt/1000 " \
            "from en.rtm_vds " \
            "where chargingstatus ='NO_CHARGING' and totalcurrent>0 and cast(vehiclespeed,'float')>=0.1 " \
            "and deviceid like '"+self.a+"' AND CAST(accmiles,'float')>100 "
        aus=client.execute(sql)
        SOC,temp,power=[],[],[]
        for value in aus:
            temp.append(value[0])
            SOC.append(value[1])
            power.append(value[2])
        hist_func.hist_cros_2con_show(workbook,['discharging'],SOC,range(0,110,10),temp,range(-10,60,5))
        hist_func.hist_con2_show(workbook,['discharging_pow','power'],3,power,range(0,100,10))

        #recuperatation
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SELECT arrayReduce('sum',temp_list)/length(temp_list),soc, -totalcurrent*totalvolt/1000 " \
            "from en.rtm_vds " \
            "where chargingstatus ='NO_CHARGING' and totalcurrent<0 and cast(vehiclespeed,'float')>=0.1 " \
            "and deviceid like '"+self.a+"' AND CAST(accmiles,'float')>100 "
        aus=client.execute(sql)
        SOC,temp,power=[],[],[]
        for value in aus:
            temp.append(value[0])
            SOC.append(value[1])
            power.append(value[2])
        hist_func.hist_cros_2con_show(workbook,['recuperatation'],SOC,range(0,110,10),temp,range(-10,60,5))
        hist_func.hist_con2_show(workbook,['recuperatation_pow','power'],3,power,range(0,100,10))

        #charging
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list " \
            "SELECT arrayReduce('sum',temp_list)/length(temp_list),soc, -totalcurrent*totalvolt/1000 " \
            "from en.rtm_vds " \
            "where chargingstatus in ('CHARGING_STOPPED','CHARGING_FINISH') and totalcurrent<0 " \
            "and deviceid like '"+self.a+"' AND CAST(accmiles,'float')>100 "
        aus=client.execute(sql)
        SOC,temp,power=[],[],[]
        for value in aus:
            temp.append(value[0])
            SOC.append(value[1])
            power.append(value[2])
        hist_func.hist_cros_2con_show(workbook,['charging'],SOC,range(0,110,10),temp,range(-10,60,5))
        hist_func.hist_con2_show(workbook,['charging_pow','power'],3,power,range(0,100,10))

        workbook.close()


    def hist_e_motor(self):
        # e-motor workingpiont


        #e-motor efficiecy
        sql="SELECT cast(emspeed,'float')*cast(emtq,'float')/9550, cast(emvolt,'float')*cast(emctlcut,'float')/1000 " \
            "from en.rtm_vds " \
            "where cast(emtq,'float')>0 and cast(emctlcut,'float')>0 " \
            "and deviceid like 'LSVA%' AND CAST(accmiles,'float')>100 "
        aus=client.execute(sql)

        # LE temperature
        # E-motor temperature

    #def get_acc(self):



    def get_daily_mile(self):
        sql="SELECT max(CAST(accmiles,'float'))-min(CAST(accmiles,'float')),CAST(accmiles,'float') " \
            "from rtm_vds where deviceid like '"+self.a+"' AND CAST(accmiles,'float')>100 group by deviceid, toDate(uploadtime)"
        aus=client.execute(sql)
        daily_mile=[]
        mile=[]
        for a in aus:
            daily_mile.append(a[0])
            mile.append(a[1])




