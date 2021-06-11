import sys
sys.path.append("..")#sys.path.append("..")的意思是增加搜索的路径，..代表上一个目录层级

import xlsxwriter
import time
from datetime import datetime
import numpy as np
import pandas as pd

from rtm_hist import hist_func_np
from en_client import en_client
client=en_client()
'''
original table
All data(without warmingsignal)----------------------------- ods.rtm_details  
All data with warmingsignal------------------------ods.rtm_reissue_history
All data with warmingsignal [after 2020-9-25] ------- ods.rtm_details_v2

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

    def __init__ (self,proj,region=0,province=0,user_type=0,date_range=[],mile_range=[]):
        '''
        project must be in {'Lavida','Passat','Tiguan','Passat C5','Passat C6','Tiguan C5','Tiguan C6','ALL BEV','ALL PHEV'}
        region must be in {'MidSouth', 'MidNorth', 'MidEast', 'SouthWest', 'Mid', 'NorthWest', 'NorthEast'}
        province must be in {"GuangDong","ShangHai","TianJin","ZheJiang","HeBei","SiChuan","Shan3Xi","HeNan","FuJian","ShanDong","GuangXi","NingXia","XinJinag","JiLin", \
            "Shan1Xi","LiaoNing","ChongQing","JiangSu","HuBei","YunNan","HuNan","GuiZhou","JiangXi","AnHui","HanNan","GanSu","QingHai","NeiMeng","HeiLongJiang","BeiJing","XiZang"}
        user_type must be in {'Private', 'Fleet', 'Taxi'}
        date_range=[start_date,end_date]:yyyy-mm-dd        eg: ['2020-06-01','2020-06-13']
        mile_range=[start_mileage,end_mileage]
        '''
        tb1='ods.rtm_reissue_history'
        tb2='en.vehicle_vin'
        self.tb1=tb1
        self.tb2=tb2
        con1=" and vehiclestatus!='ERROR' and chargingstatus!='INVALID' and chargingstatus!='ERROR' and cocesprotemp1!='NULL' "

        proj=proj.upper()
        self.proj=proj

        if proj=="LAVIDA" or proj=='All BEV':
            typ_v='BEV'
            con2 = "project=='Lavida BEV 53Ah' "
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
        print(aus[0][0])
        
        return aus[0][0]
        
    def daily_mileage(self,step=range(0,500,20)):
        sql="WITH cast(accmiles,'Float32') AS mile " \
            "SELECT max(mile)-min(mile) FROM " + self.tb1 + self.con+ \
            " GROUP BY deviceid,toDate(uploadtime) "
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
        sql="SELECT deviceid, uploadtime, charg_s_c, socp, d_soc, acc  FROM( " \
            "SELECT deviceid, uploadtime, runningDifference(charg_s) as charg_s_c, socp, runningDifference(socp) as d_soc, cast(accmiles,'Float32') as acc " \
            "FROM (SELECT deviceid, uploadtime, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, accmiles, if(soc<0,0,soc) AS socp " \
            "FROM " + self.tb1 + self.con+ " ORDER BY deviceid, uploadtime ) ORDER BY deviceid,uploadtime ) " \
            "where charg_s_c IN (1,-1)  ORDER BY deviceid,uploadtime "
        aus=client.execute(sql)
        #aus=[0 vin  1 时间  2充电变化标志位  3 soc   4 d_soc  5 mileage ]
        df=pd.DataFrame(aus)
        #df.to_csv('new.csv')
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

        l2=len(mile_r_c)
        print("------mile perCharging analysis---------\r\n")
        print("原始行驶次数："+str(l1)+"\r\n")
        print("充电前数据丢失次数："+str(count_1)+"占比："+str(round(count_1/l1*100,2))+"%\r\n")
        print("充电后数据丢失次数："+str(count_2)+"占比："+str(round(count_2/l1*100,2))+"%\r\n")
        print("充电前后数据均丢失次数："+str(count_12)+"占比："+str(round(count_12/l1*100,2))+"%\r\n")
        print("处理后行驶次数："+str(l2)+"\r\n")

        mile_r=np.array(mile_r)
        

        freq = hist_func_np.hist_con(mile_r,step)
        re1=pd.DataFrame(freq[1])
        re1.index=freq[0]
        re1.columns=['频数']
        re2 =  hist_func_np.box_hist(mile_r,'每次充电间隔里程[km]')
        

        if self.pro_typ=='BEV':
            charging_energy=37 #lavida BEV 实际SOC96~8% 冲入电量37kWh,来源NEDC充电测试平均值
                
            for a in all_drive:
                if (a[6]-a[5])>10 and (a[3]-a[4])>5:
                    Energy_consump.append(charging_energy*(a[3]-a[4])/(a[6]-a[5]))
                    mile_r_c.append((a[6]-a[5])/(a[3]-a[4])*100)

            mile_r_c=np.array(mile_r_c)
            Energy_consump = np.array(Energy_consump)

            freq = hist_func_np.hist_con(mile_r_c,step)
            re3 = pd.DataFrame(freq[1])
            re3.index = freq[0]
            re3.columns = ['频数']
            re4 = hist_func_np.box_hist(mile_r_c,'折算纯电续驶里程[km]')
            
            
            freq = hist_func_np.hist_con(Energy_consump,np.arange(6,30,0.5))
            re5=pd.DataFrame(freq[1])
            re5.index=freq[0]
            re5.columns=['频数']
            re6 = hist_func_np.box_hist(Energy_consump,'折算电耗[kWh/100km]')

            return re1, re2, re3, re4, re5, re6
        else:
            return re1,re2

    def E_motor_temp(self,step=range(-10,120,5),sampling=1/6):
        sql="SELECT cast(emctltemp,'Int32'), cast(emtemp,'Int32') FROM "+self.tb1 + self.con + \
            " AND emstat in ('CONSUMING_POWER','GENERATING_POWER' ) AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=pd.DataFrame(client.execute(sql))
        temp_motor=np.array(aus[1])
        temp_LE=np.array(aus[0])


        freq = hist_func_np.hist_con(temp_motor,step)
        re3=pd.DataFrame(freq[1])
        re3.index=freq[0]
        re3.columns=['频数']
        re4 = hist_func_np.box_hist(temp_motor,'电机温度[℃]')
        

        freq = hist_func_np.hist_con(temp_LE,step)
        re1=pd.DataFrame(freq[1])
        re1.index=freq[0]
        re1.columns=['频数']
        re2 = hist_func_np.box_hist(temp_LE,'LE温度[℃]')

        return re1,re2,re3,re4

    def E_motor_workingPoint(self,sampling=1/6):
        sql="WITH cast(emvolt,'Float32') * cast(emctlcut,'Float32')/1000 as el_pow " \
            "SELECT cast(emspeed, 'Float32') as sp, cast(emtq,'Float32') as tq, " \
            " multiIf(sp*tq*el_pow==0,0,emstat=='CONSUMING_POWER',sp*tq/9550/el_pow,emstat=='GENERATING_POWER',el_pow/sp/tq*9550,100) " \
            " FROM "+self.tb1 + self.con + " AND emstat in ('CONSUMING_POWER','GENERATING_POWER' ) AND toSecond(uploadtime)<"+str(int(sampling*60))
        aus=client.execute(sql)
        speed,torq,eff=[],[],[]
        for value in aus:
            if value[0]!=0 and value[1]!=0:
                speed.append(value[0])
                torq.append(value[1])
                if value[2]>0 and value[2]<1:
                    eff.append(value[2]*100)
        l1=len(aus)
        l2=len(speed)
        l3=len(eff)
        print("-------E-Motor Working Point Analysis---------\r\n")
        print("原始抓取点数："+str(l1)+"\r\n")
        print("去除转矩为零或转速为零之后工作点数："+str(l2)+"   占比："+str(round(l2/l1*100,2))+"%\r\n")
        print("效率值在合理范围数："+str(l3)+"   占比："+str(round(l3/l2*100,2))+"%\r\n")

        speed,torq,eff=np.array(speed),np.array(torq),np.array(eff)

        freq = hist_func_np.hist_con(eff,[0,20,40,50,60,62,64,66,68,70,72,74,76,78,80,82,84,86,88,90,92,94,96,98,100])
        re1=pd.DataFrame(freq[1])
        re1.index=freq[0]
        re1.columns=['频数']
        re2 = hist_func_np.box_hist(eff,'电机工作效率[%]')
        

        [a,b,c] = hist_func_np.hist_cros_2con(speed, range(-4000,13000,500), torq, range(-300,400,50))
        
        re3=pd.DataFrame(c)
        
        re3.index=b
        re3.columns=a
        re3.to_csv('emotor.csv')
        re4 = hist_func_np.box_hist(speed,'电机转速[rpm]')
        re5 = hist_func_np.box_hist(torq,'电机转矩[Nm]')
        return re1, re2, re3, re4, re5

    def get_charge(self):
        '''
        return all_charge=i*[0vin,1time_start,2time_end,3soc_start,4soc_end,5mile_start,6 end_mile ]
        '''
        sql="SELECT deviceid, uploadtime, charg_s_c, socp, d_soc, acc  FROM( " \
            "SELECT deviceid, uploadtime, runningDifference(charg_s) as charg_s_c, socp, runningDifference(socp) as d_soc, cast(accmiles,'Float32') as acc " \
            "FROM (SELECT deviceid, uploadtime, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, accmiles, if(soc<0,0,soc) AS socp " \
            "FROM " + self.tb1 + self.con+ " ORDER BY deviceid, uploadtime ) ORDER BY deviceid,uploadtime ) " \
            "where charg_s_c IN (1,-1)  ORDER BY deviceid,uploadtime "
        aus=client.execute(sql)
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

        print("---------charge analysis---------\r\n")
        print("原始充电次数："+str(l1)+"\r\n")
        print("充电前数据丢失次数："+str(count_1)+"占比："+str(round(count_1/l1*100,2))+"%\r\n")
        print("充电后数据丢失次数："+str(count_2)+"占比："+str(round(count_2/l1*100,2))+"%\r\n")
        print("充电前后数据均丢失次数："+str(count_12)+"占比："+str(round(count_12/l1*100,2))+"%\r\n")
        print("充电合并次数："+str(count_3)+"占比："+str(round(count_3/l1*100,2))+"%\r\n")
        print("充电合并次数中充电中断时间过长>30分钟："+str(count_31)+"占比："+str(round(count_31/l1*100,2))+"%\r\n")
        print("处理后充电次数："+str(l2)+"\r\n")

        return all_charge

    def charge_ana(self):
        '''
        input:  all_charge=i*[0vin,1time_start,2time_end]
        return  [np.array(time_h_s),np.array(time_d),np.array(time_d_c),np.array(mode),charg_soc,charg_temp,charg_pow]
                charg_soc=[np.array(soc_s),np.array(soc_e),np.array(soc_d)]
                charg_temp=[np.array(temp_s),np.array(temp_e),np.array(temp_min),np.array(temp_max),np.array(temp_mean),np.array(temp_range)]
                charg_pow=[np.array(power_max),np.array(power_mean)]
        '''
        all_charge=self.get_charge()
        sql="WITH cast(splitByChar(',',cocesprotemp1),'Array(Int8)') AS temp_list, if(chargingstatus=='NO_CHARGING',0,1) AS charg_s, totalcurrent*totalvolt/1000 AS P " \
            "SELECT deviceid,uploadtime, -P, arrayReduce('avg',temp_list), if(soc<0,0,soc), " \
            "multiIf(P<-7.5,'DC',P>=-7.5 and P<-4,'mode3_1',P>=-4 and P<-2,'mode3_2',P>=-2 and P<0,'mode2','discharging') as charg_mode, " \
            "arrayReduce('max',temp_list), arrayReduce('min',temp_list) " \
            "FROM " + self.tb1 + self.con+ " and charg_s==1 ORDER BY deviceid, uploadtime " 

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

        print("未匹配的充电次数："+str(len(all_charge)-len(ss))+"占比："+str(round((1-len(ss)/len(all_charge))*100,2))+"%\r\n")
        print("匹配的充电次数："+str(len(ss))+"\r\n")
       
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

    def charge_soc(self,step=range(0,120,10)):
        [_, _, _, _,charg_soc, _, _] = self.charge_ana()
        soc_s = charg_soc[0]
        soc_e = charg_soc[1]

        freq = hist_func_np.hist_con(soc_s,step)
        re1=pd.DataFrame(freq[1])
        freq[0][-1]='100'
        re1.index=freq[0]
        re1.columns=['频数']
        re2 =  hist_func_np.box_hist(soc_s,'充电开始SOC[%]')

        freq = hist_func_np.hist_con(soc_e,step)
        re3=pd.DataFrame(freq[1])
        freq[0][-1]='100'
        re3.index=freq[0]
        re3.columns=['频数']
        re4 =  hist_func_np.box_hist(soc_e,'充电结束SOC[%]')

        print(re1, re2, re3, re4)

        return re1, re2, re3, re4
    
    def charge_start_time(self,step = range(25)):
        [time_h_s, _, _, _, _, _, _]=self.charge_ana()
        freq = hist_func_np.hist_con(time_h_s,step)
        re1=pd.DataFrame(freq[1])
        re1.index=["0",'1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21' ,'22', '23']
        re1.columns=['频数']
        print(re1)

        return re1
    
    def charge_time(self, step = [0,30,60,120,180,240,300,360,420,480,540,600,660,720,780,840,900,1500]):
        [_, time_d, time_d_c, mode, _, _, _]=self.charge_ana()

        freq = hist_func_np.hist_con(time_d,step)
        re1=pd.DataFrame(freq[1])
        
        re1.index=freq[0]
        re1.columns=['频数']
        re2 =  hist_func_np.box_hist(time_d,'充电时长[min]')

        freq = hist_func_np.hist_con(time_d_c,step)
        re3=pd.DataFrame(freq[1])
        
        re3.index=freq[0]
        re3.columns=['频数']
        re4 = hist_func_np.box_hist(time_d_c,'折算满充时长[min]')

        [a, b, c] = hist_func_np.hist_con_dis( time_d_c, step, mode,['mode2','mode3_2','mode3_1','DC'],show_hist=1)
        re5=pd.DataFrame(np.array(b).T)
        re5.index=a
        re5.columns=['mode2','mode3_2','mode3_1','DC']
        re6=pd.DataFrame(np.array(c).T)
        re6.index = ['min','1%percentile','25%percentile','50%percentile','75%percentile','99%percentile','max','mean']
        re6.columns = ['mode2','mode3_2','mode3_1','DC']

        print(re1, re2, re3, re4, re5, re6)

        return re1, re2, re3, re4, re5, re6

"""
    调用clickhouse进行查询
    输入：各种查询条件
    返回：查询到的结果，如果没有结果返回0
"""
def f1(pro, date_range, region, userType, mile_range,fuc_name):

    if userType=='all':
        userType=0

    if region=='all':
        region=0

    if mile_range == ['','']:
        l2=RtmHist(pro, date_range=date_range, region=region, user_type=userType )
    else:
        m=[int(mile_range[0]),int(mile_range[0])]
        l2=RtmHist(pro, date_range=date_range, region=region, user_type=userType, mile_range=m)
    n = l2.count_nr()
    a = pd.DataFrame([])
    if n>0 :
        if fuc_name=='fc11':
            [re1, _]= l2.daily_mileage()
            re1['每日行驶里程范围[km]']=re1.index.tolist()
            col_name = re1.columns
            a=re1.reindex(columns=col_name[::-1])            
            
        if fuc_name=='fc12':
            x = l2.percharge_mile()
            re1 = x[0]
            re1['每次充电之间行驶里程范围[km]'] = re1.index.tolist()
            col_name = re1.columns
            a=re1.reindex(columns=col_name[::-1])            
            
        if fuc_name=='fc13':
            x = l2.percharge_mile()
            re1 = x[2]
            re1['折算里程范围[km]'] = re1.index.tolist()
            col_name = re1.columns
            a=re1.reindex(columns=col_name[::-1])            
            
        if fuc_name=='fc14':
            x = l2.percharge_mile()
            re1 = x[4]
            re1['折算电耗范围[kWh/100km]'] = re1.index.tolist()
            col_name = re1.columns
            a=re1.reindex(columns=col_name[::-1])            
            
        if fuc_name=='fc33':
            x = l2.E_motor_workingPoint()
            a = x[2]
            
        '''
        if fuc_name=='fc21':
            x = l2.percharge_mile()
            re1 = x[4]
            re1['折算电耗范围[kWh/100km]'] = re1.index.tolist()
            col_name = re1.columns
            a=re1.reindex(columns=col_name[::-1])            
            
        if fuc_name=='fc22':
            x = l2.percharge_mile()
            re1 = x[4]
            re1['折算电耗范围[kWh/100km]'] = re1.index.tolist()
            col_name = re1.columns
            a=re1.reindex(columns=col_name[::-1])            
            
        '''

    return n,a




#if __name__=="__main__":


