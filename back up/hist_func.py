import sys
import numpy as np
import xlsxwriter
import time
'''
given input_input and steps,output hist.
input_data:list,steps:[start,step,end]
output:dictionary, key:start of every block
value: stastics result
'''

def time_cost(fn):
    def _wrapper(*args,**kwargs):
        start=time.time()
        A=fn(*args,**kwargs)
        dt=time.time()-start
        if dt<60:
            print("%s cost %s second"%(fn.__name__,dt))
        elif dt<3600:
            dm=int(dt/60)
            dt=dt-dm*60
            print("%s cost %s min %s second"%(fn.__name__,dm,dt))
        else:
            dh=int(dt/3600)
            dm=int((dt-dh*3600)/60)
            dt=dt-dh*3600-dm*60
            print("%s cost %s hour %s min %s second"%(fn.__name__,dh,dm,dt))
        return A
    return _wrapper

#统计按照顺序排列的连续变量的分布
def hist1(input_data,steps):
    block=[]
    for i in range(len(steps)-1):
        block.append(str(steps[i])+'~'+str(steps[i+1]))
    #data_cut=[]
    result=[]
    s,i,k=0,1,1
    while i<len(input_data)-1 and k<len(input_data):
        if input_data[i-1]<steps[k] and input_data[i]>=steps[k]:
            e=i
            #data_cut.append(input_data[s:e])
            result.append(e-s)
            s=i
            k+=1
        i+=1
    #data_cut.append(input_data[s::])
    result.append(len(input_data)-s)

    return block,result


#input_data is continuous variable
#interval1 is for input_data1
@time_cost
def hist_con(input_data,steps):
    if not input_data:
        print('Input_data is empty')
        sys.exit(1)
    result={}
    for i in range(len(steps)-1):
        block=str(steps[i])+'~'+str(steps[i+1])
        result[block]=0
        for value in input_data:
            if value>=steps[i] and value<steps[i+1]:
                result[block]=result.get(block,0)+1
    keys=[]
    values=[]
    for k in result.keys():
        keys.append(k)
        values.append(result[k])

    return keys,values

#input_data1 is continuous variable
#input_data2 is Discrete variable
#interval1 is for input_data1
def hist_con_dis(input_data1,input_data2,interval1):
    result=[]
    n=len(interval1)-1
    res1=[]
    for i in range(n):
        block=str(interval1[i])+'~'+str(interval1[i+1])
        result.append(block)
        dic={}
        for k in (range(len(input_data1))):
            value1=input_data1[k]
            value2=input_data2[k]
            if value1>=interval1[i] and value1<interval1[i+1]:
                dic[value2]=dic.get(value2,0)+1
        res1.append(dic)

    return result,res1

#input_data1 is continuous variable
#input_data2 is continuous variable
#interval1 is for input_data1
#interval2 is for input_data1
def hist_2con(input_data1,interval1,input_data2,interval2):
    l1=len(interval1)-1
    l2=len(interval2)-1
    res=[]
    interval_list1=[]
    interval_list2=[]
    for j in range(l2):
        interval_list2.append(str(interval2[j])+'~'+str(interval2[j+1]))

    for i in range(l1):
        interval_list1.append(str(interval1[i])+'~'+str(interval1[i+1]))
        res.append([])
        for j in range(l2):
            pp=0
            for k in (range(len(input_data1))):
                value1=input_data1[k]
                value2=input_data2[k]                
                if value1>=interval1[i] and value1<interval1[i+1] and value2>=interval2[j] and value2<interval2[j+1]:
                    pp+=1
            res[i].append(pp)
    return interval_list1,interval_list2,res


#统计输入变量in_list[in1,in2,in3...]在相同的间隔step下的分布，并将结果返回到excel中
#in1和in2长度相同#name_list=[sheet名，in1列名，in2列名,in3列名...]
#need,需要返回的统计值个数，顺序依次为：最大值，最小值，平均值，中位数，众数#need=5,计算所有，need=i，计算前i个统计值
def hist_con_show(workbook,name_list,need,in_list,step):
    
    m=len(in_list)
    worksheet = workbook.add_worksheet(name_list[0])
    for n in range(m):
        [row_con,freq]=hist_con(in_list[n],step)
        c=0
        worksheet.write(c,n+1,name_list[n+1])
        for k in range(len(freq)):
            c+=1
            worksheet.write(c,n+1,freq[k])
        c+=3
        if need>0:
            c+=1
            worksheet.write(c,n+1,max(in_list[n]))
        if need>1:
            c+=1
            worksheet.write(c,n+1,min(in_list[n]))
        if need>2:
            c+=1
            worksheet.write(c,n+1,np.mean(np.array(in_list[n])))
        if need>3:
            c+=1
            worksheet.write(c,n+1,np.median(np.array(in_list[n])))
        if need>4:
            c+=1
            counts=np.bincount(np.array(in_list[n]))
            worksheet.write(c,n+1,np.argmax(counts))
    
    c=0
    for k in range(len(row_con)):
        c+=1
        worksheet.write(c,0,row_con[k])
    c+=3
    if need>0:
        c+=1
        worksheet.write(c,0,"max")
    if need>1:
        c+=1
        worksheet.write(c,0,"min")
    if need>2:
        c+=1
        worksheet.write(c,0,"mean")
    if need>3:
        c+=1
        worksheet.write(c,0,"median")
    if need>4:
        c+=1
        worksheet.write(c,0,"mode")
        

# 统计不同 in2（离散变量）输入变量in1（连续变量）在间隔step下的分布，并将结果返回到excel中。(统计不同充电模式下，充电时长占比)
#in1和in2长度相同#name_list=[sheet名]
#并返回的统计值：最大值，最小值，平均值，中位数
def hist_cros_con_dis_show(workbook,name_list,in1,in2,step):

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
        [row_con,freq]=hist_con(data_cut[i],step)
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
    
# 统计两个连续变量的分布（eg:电机工作点）
#in1和in2长度和step都不要求相同#name_list=[sheet名]
def hist_cros_2con_show(workbook,name_list,in1,step1,in2,step2):
    
    [row_con,col_con,res]=hist_2con(in1,step1,in2,step2)
    con1=name_list[0]
    worksheet = workbook.add_worksheet(con1)
    for c in range(len(col_con)):
        worksheet.write(0,c+1,col_con[c])

    for r in range(len(row_con)):
        worksheet.write(r+1,0,row_con[r])
        for c in range(len(col_con)):
            worksheet.write(r+1,c+1,res[r][c])

