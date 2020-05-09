from clickhouse_driver import Client
import time
import numpy as np
import hist_func
import xlsxwriter




def charge3(input_data,pro):
    #inputdata
    # [0 str vin,
    # 1 datatime charge_date,
    # 2 int charge_SOC,
    # 3 float charge_mile,
    # 4 float charge_current
    # 5 int mxtemp
    # 6 int mitemp ]
    ss,ee=[],[]
    ss.append(0)
    for i in range(len(input_data)-2):
        if input_data[i][0]!=input_data[i+1][0]:
            ss.append(i+1)
            ee.append(i)
        elif input_data[i][2]>input_data[i+1][2] and input_data[i][3]<input_data[i+1][3]:
            ss.append(i+1)
            ee.append(i)
    
    ee.append(len(input_data)-1)
    i=0
    while i<len(ss):
        d=input_data[ee[i]][1]-input_data[ss[i]][1]
        if (d.seconds/60)<2:
            ss.pop(i)
            ee.pop(i)
        else:
            i+=1

    charge_hour_s,charge_soc_s,charge_soc_e,mile_percharge,charge_mode,charge_time=[],[],[],[],[],[]
    for i in range(len(ss)):
        a=ss[i]
        b=ee[i]
        charge_hour_s.append(input_data[a][1].hour)
        charge_soc_s.append(input_data[a][2])
        charge_soc_e.append(input_data[b][2])
        d=input_data[b][1]-input_data[a][1]
        charge_time.append(d.seconds/60)
        #cha_temp_max.append(max(mxtemp[a:b]))
        #cha_temp_min.append(min(mitemp[a:b]))
        if input_data[a+2][4]<-20:
            charge_mode.append("mode4_DC")
        elif input_data[a+2][4]<-10:
            charge_mode.append("mode3_AC_7.2kW")
        elif input_data[a+2][4]<-5:
            charge_mode.append("mode3_AC_3.6kW")
        elif input_data[a+2][4]<0:
            charge_mode.append("mode2_AC")
        else:
            charge_mode.append("error")
    for i in range(len(ss)-1):
        a=ss[i]
        b=ss[i+1]
        if input_data[a][0] == input_data[b][0]:
            mile_percharge.append(input_data[b][3]-input_data[a][3])
    freq_mode={}
    for x in charge_mode:
        freq_mode[x]=freq_mode.get(x,0)+1

    workbook = xlsxwriter.Workbook("charge_"+pro+".xlsx")

    #temp1=[-10,-5,0,5,10,15,20,25,30,35,40,45,50,55]
    #show_in_excel(workbook,['temp','max temp','min temp'],4,cha_temp_max,temp1,cha_temp_min)
    show_in_excel(workbook,['SOC','start SOC','end SOC'],5,charge_soc_s,range(0,120,10),charge_soc_e)
    show_in_excel(workbook,['time','charging_time'],4,charge_time,[0,30,60,120,180,240,300,360,420,480,1500])
    show_in_excel(workbook,['hour','start time'],0,charge_hour_s,range(24))
    hist_show(workbook,['charging mode'],charge_time,charge_mode,[0,30,60,120,180,240,300,360,420,480,1500])
    hist_2con_show(workbook,['SOC2'],charge_soc_s,range(0,120,10),charge_soc_e,range(0,120,10))
    workbook.close()

    return ss,ee


def hist_2con_show(workbook,name_list,in1,step1,in2,step2):
    
    [row_con,col_con,res]=hist_func.hist_2con(in1,step1,in2,step2)
    con1=name_list[0]
    worksheet = workbook.add_worksheet(con1)
    for c in range(len(col_con)):
        worksheet.write(0,c+1,col_con[c])

    for r in range(len(row_con)):
        worksheet.write(r+1,0,row_con[r])
        for c in range(len(col_con)):
            worksheet.write(r+1,c+1,res[r][c])

    

#统计输入变量in1和in2（可选）在相同的间隔step下的分布，并将结果返回到excel中。
#in1和in2长度相同
#name_list=[sheet名，in1列名，in2列名]
#need,需要返回的统计值个数，顺序依次为：最大值，最小值，平均值，中位数，众数
#need=5,计算所有，need=i，计算前i个统计值

def show_in_excel(workbook,name_list,need,in1,step,in2=[]):

    con=name_list[0]
    name1=name_list[1]
    [row_con,freq1]=hist_func.hist_con(in1,step)
    if in2!=[]:
        [row_con,freq2]=hist_func.hist_con(in2,step)
    worksheet = workbook.add_worksheet(con)
    i=0
    worksheet.write(i,1,name1)
    if in2!=[]:
        name2=name_list[2]
        worksheet.write(i,2,name2)
    for k in range(len(row_con)):
        i+=1
        worksheet.write(i,0,row_con[k])
        worksheet.write(i,1,freq1[k])
        if in2!=[]: worksheet.write(i,2,freq2[k])
    i+=3

    if need>0:
        i+=1
        worksheet.write(i,0,"max")
        worksheet.write(i,1,max(in1))
        if in2!=[]: worksheet.write(i,2,max(in2))
    if need>1:
        i+=1
        worksheet.write(i,0,"min")
        worksheet.write(i,1,min(in1))
        if in2!=[]: worksheet.write(i,2,min(in2))
    if need>2:
        i+=1
        worksheet.write(i,0,"mean")
        worksheet.write(i,1,np.mean(np.array(in1)))
        if in2!=[]: worksheet.write(i,2,np.mean(np.array(in2)))
    if need>3:
        i+=1
        worksheet.write(i,0,"median")
        worksheet.write(i,1,np.median(np.array(in1)))
        if in2!=[]: worksheet.write(i,2,np.median(np.array(in2)))
    if need>4:
        i+=1
        worksheet.write(i,0,"mode")
        counts=np.bincount(np.array(in1))
        worksheet.write(i,1,np.argmax(counts))
        if in2!=[]:
            counts = np.bincount(np.array(in2))
            worksheet.write(i,2,np.argmax(counts))
    

# 统计不同充电模式下，充电时长占比

# 统计不同 in2（离散变量）输入变量in1（连续变量）在间隔step下的分布，并将结果返回到excel中。
#in1和in2长度相同
#name_list=[sheet名]
#并返回的统计值：最大值，最小值，平均值，中位数
def hist_show(workbook,name_list,in1,in2,step):

    all_mode=list(set(in2))
    data_cut=[]
    for k in range(len(all_mode)):
        data_cut.append([])
        for i in range(len(in1)):
            if in2[i]==all_mode[k]:
                data_cut[k].append(in1[i])

    con1=name_list[0]
    worksheet = workbook.add_worksheet(con1)

    for i in range(len(all_mode)):
        [row_con,freq]=hist_func.hist_con(data_cut[i],step)
        r=0
        worksheet.write(r,i+1,all_mode[i])
        for c in range(len(row_con)):
            r+=1
            worksheet.write(r,i+1,freq[c])
        r+=2
        worksheet.write(r,i+1,max(data_cut[i]))
        worksheet.write(r+1,i+1,min(data_cut[i]))
        worksheet.write(r+2,i+1,np.mean(np.array(data_cut[i])))
        worksheet.write(r+3,i+1,np.median(np.array(data_cut[i])))
    
    worksheet.write(r,0,"max")
    worksheet.write(r+1,0,"min")
    worksheet.write(r+2,0,"mean")
    worksheet.write(r+3,0,"median")

    for i in range(len(row_con)):
        worksheet.write(i+1,0,row_con[i])
    

#统计了充电过程中的温度，由于占用内存过大，passat的数据无法计算，此段作废
def charge2(input_data,pro):
    #inputdata
    # [0 str vin,
    # 1 datatime charge_date,
    # 2 int charge_hour,
    # 3 int charge_SOC,
    # 4 str charge_mile,
    # 5 str chargingstatus
    # 6 float charge_current
    # 7 str mxtemp
    # 8 str mitemp ]
    vin,charge_SOC,charge_mile=[],[],[]
    mxtemp,mitemp=[],[]
    for value in input_data:
        vin.append(value[0])
        charge_SOC.append(value[3])
        charge_mile.append(float(value[4]))
        mxtemp.append(float(value[7]))
        mitemp.append(float(value[8]))
    ss,ee=[],[]
    ss.append(0)
    for i in range(len(input_data)-2):
        if vin[i]!=vin[i+1]:
            ss.append(i+1)
            ee.append(i)
        elif charge_SOC[i]>charge_SOC[i+1] and charge_mile[i]<charge_mile[i+1]:
            ss.append(i+1)
            ee.append(i)
    
    ee.append(len(input_data)-1)
    i=0
    while i<len(ss):
        if (ee[i]-ss[i])<2:
            ee.pop(i)
            ss.pop(i)
        else:
            i+=1

    charge_hour_s,charge_soc_s,charge_soc_e,mile_percharge,charge_mode,charge_time=[],[],[],[],[],[]
    cha_temp_max,cha_temp_min=[],[]
    for i in range(len(ss)):
        a=ss[i]
        b=ee[i]
        charge_hour_s.append(input_data[a][2])
        charge_soc_s.append(charge_SOC[a])
        charge_soc_e.append(charge_SOC[b])
        d=input_data[b][1]-input_data[a][1]
        charge_time.append(d.seconds/60)
        cha_temp_max.append(max(mxtemp[a:b]))
        cha_temp_min.append(min(mitemp[a:b]))
        if input_data[a+2][6]<-20:
            charge_mode.append("mode4_DC")
        elif input_data[a+2][6]<-10:
            charge_mode.append("mode3_AC_7.2kW")
        elif input_data[a+2][6]<-5:
            charge_mode.append("mode3_AC_3.6kW")
        elif input_data[a+2][6]<0:
            charge_mode.append("mode2_AC")
        else:
            charge_mode.append("error")
    for i in range(len(ss)-1):
        a=ss[i]
        b=ss[i+1]
        if input_data[a][0] == input_data[b][0]:
            mile_percharge.append(charge_mile[b]-charge_mile[a])
    freq_mode={}
    for x in charge_mode:
        freq_mode[x]=freq_mode.get(x,0)+1

    workbook = xlsxwriter.Workbook("charge_"+pro+".xlsx")

    temp1=[-10,-5,0,5,10,15,20,25,30,35,40,45,50,55]
    show_in_excel(workbook,['temp','max temp','min temp'],4,cha_temp_max,temp1,cha_temp_min)
    show_in_excel(workbook,['SOC','start SOC','end SOC'],5,charge_soc_s,range(0,110,10),charge_soc_e)
    show_in_excel(workbook,['time','charging_time'],4,charge_time,[0,30,60,120,180,240,300,360,420,480,1500])
    show_in_excel(workbook,['hour','start time'],0,charge_hour_s,range(24))
    hist_show(workbook,['charging mode'],charge_time,charge_mode,[0,30,60,120,180,240,300,360,420,480,1500])
    workbook.close()
    #return charge_time,freq_mode,cha_temp_max,cha_temp_min
    return freq_mode



