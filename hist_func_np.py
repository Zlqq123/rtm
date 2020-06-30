import sys
import numpy as np
import xlsxwriter
import time
'''
given input_input and steps,output hist.
input_data:array,interval:array
return [0block: list[str]  1freq: array[int]  2freq_rate: list[float]]
'''
def time_c(fn):
    num=[]
    def _wrapper(*args,**kwargs):
        start=time.time()
        A=fn(*args,**kwargs)
        dt=time.time()-start
        num.append(dt)
        print("%s 第 %s 次执行  耗时 %s  s 总耗时 %s   min"%(fn.__name__,len(num),round(dt,2),round(sum(num)/60,2)))
        return A
    return _wrapper

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


def interval_str(interval):
    '''
    interval list--> interval str list
    eg:
    interval_str([1,2,3,4])
    >>>['1~2','2~3','3~4']
    '''
    block=[]
    for i in range(1,len(interval)):
        block.append(str(interval[i-1])+'~'+str(interval[i]))
    return block


#@time_cost
#@time_c
def hist_con(input_data,interval,show_interval=1):
    BL=65536
    wa = np.zeros(len(interval),dtype=int)
    for i in range(0, len(input_data), BL):
        sa=np.sort(input_data[i:i+BL])
        wa+=np.searchsorted(sa,interval)
    
    re=np.diff(wa)

    if show_interval:
        block=interval_str(interval)
        return block,re
    return re

    

# input_data had sorted in order from largest to smallest
#@time_cost
#@time_c
def hist_sortedcon(input_data,interval,show_interval=1):
    wa = np.searchsorted(input_data,interval)
    re=np.diff(wa)

    if show_interval:
        block=interval_str(interval)
        return block,re
    return re


#@time_cost
#@time_c
def hist_con_dis(input_data1,interval1,input_data2,interval2,show_interval=1,show_hist=0):
    '''
    input_data1 is continuous variable array #interval1 is for input_data1 array
    input_data2 is Discrete variable array #interval2 is for input_data2 list
    len(input_data1)=len(input_data2)
    show_interval是否输出间隔段str
    show_hist是否输出统计值：最小值，4分位置最大值，平均值

    outout:

    '''
    re = np.zeros((len(interval2),len(interval1)-1),dtype=int)
    re2=np.zeros((len(interval2),8),dtype=int)
    
    for i in range(len(interval2)):
        in1=input_data1[input_data2==interval2[i]]
        re[i,:]=hist_con(in1,interval1,0)
        if show_hist and in1!=[]:
            re2[i,0]=np.min(in1)
            re2[i,1]=np.percentile(in1,1)
            re2[i,2]=np.percentile(in1,25)
            re2[i,3]=np.percentile(in1,50)
            re2[i,4]=np.percentile(in1,75)
            re2[i,5]=np.percentile(in1,99)
            re2[i,6]=np.max(in1)
            re2[i,7]=np.mean(in1)

    if show_interval:
        block=interval_str(interval1)
        if show_hist:
            return block,re,re2
        return block,re
    return re


#@time_cost
#@time_c
def hist_cros_2con(input_data1,interval1,input_data2,interval2,show_interval=1):
    '''
    input_data1 is continuous variable array
    input_data2 is continuous variable array
    len(input_data1)=len(input_data2)
    interval1 is for input_data1 lenth l1
    interval2 is for input_data1 lenth l2
    output:in1_list,in2_list: lits[str]
    wa[l2-1][l1-1]
    '''
    BL=65536
    a=len(interval2)-1
    b=len(interval1)-1
    wa = np.zeros((a,b),dtype=int)
    
    for i in range(0, len(input_data2), BL):
        tmp_in2 = input_data2[i:i+BL]
        tmp_in1 = input_data1[i:i+BL]
        sorting_index = np.argsort(tmp_in2)
        sa2 = tmp_in2[sorting_index]
        sa1 = tmp_in1[sorting_index]
        wa1=np.searchsorted(sa2,interval2)
        for j in range(1,len(wa1)):
            sa11=sa1[wa1[j-1]:wa1[j]]
            wa11=hist_con(sa11,interval1,0)
            wa[j-1,:]+=wa11
    
    if show_interval:
        in1_list=interval_str(interval1)
        in2_list=interval_str(interval2)
        return in1_list,in2_list,wa
    return wa


#@time_c
def hist_con_show(workbook,name_list,in_list,step,need=0):
    '''
    统计输入变量in_list[in1,in2,in3...]在相同的间隔step下的分布，并将结果返回到excel中
    in1~in_n: (array)不要求各变量长度相同
    name_list=[sheet名，in1列名，in2列名,in3列名...]
    need: int(0/1/2/3)需要返回的统计值
    0不需要统计值
    1最小值，最大值，平均值
    2最小值，4分位值，最大值，平均值
    3最小值，4分位值，最大值，平均值，众数
    '''
    m=len(in_list)
    worksheet = workbook.add_worksheet(name_list[0])
    for n in range(m):
        inx=in_list[n]
        freq=hist_con(inx,step,0)
        c=0
        worksheet.write(c,n+1,name_list[n+1])
        for k in range(len(freq)):
            c+=1
            worksheet.write(c,n+1,freq[k])
        c+=3
        if need==1:
            worksheet.write(c+1,n+1,np.min(inx))
            worksheet.write(c+2,n+1,np.max(inx))
            worksheet.write(c+3,n+1,np.mean(inx))
        if need==2:
            worksheet.write(c+1,n+1,np.min(inx))
            worksheet.write(c+2,n+1,np.percentile(inx,1))
            worksheet.write(c+3,n+1,np.percentile(inx,25))
            worksheet.write(c+4,n+1,np.percentile(inx,50))
            worksheet.write(c+5,n+1,np.percentile(inx,75))
            worksheet.write(c+6,n+1,np.percentile(inx,99))
            worksheet.write(c+7,n+1,np.max(inx))
            worksheet.write(c+8,n+1,np.mean(inx))
        if need==3:
            worksheet.write(c+1,n+1,np.min(inx))
            worksheet.write(c+2,n+1,np.percentile(inx,1))
            worksheet.write(c+3,n+1,np.percentile(inx,25))
            worksheet.write(c+4,n+1,np.percentile(inx,50))
            worksheet.write(c+5,n+1,np.percentile(inx,75))
            worksheet.write(c+6,n+1,np.percentile(inx,99))
            worksheet.write(c+7,n+1,np.max(inx))
            worksheet.write(c+8,n+1,np.mean(inx))
            counts=np.bincount(inx)
            worksheet.write(c+9,n+1,np.argmax(counts))
    
    row_con=interval_str(step)
    c=0
    for k in range(len(row_con)):
        c+=1
        worksheet.write(c,0,row_con[k])
    c+=3
    if need==1:
        worksheet.write(c+1,0,"min")
        worksheet.write(c+2,0,"max")
        worksheet.write(c+3,0,"mean")
    if need==2:
        worksheet.write(c+1,0,'min')
        worksheet.write(c+2,0,'1%percentile')
        worksheet.write(c+3,0,'25%percentile')
        worksheet.write(c+4,0,'50%percentile')
        worksheet.write(c+5,0,'75%percentile')
        worksheet.write(c+6,0,'99%percentile')
        worksheet.write(c+7,0,'max')
        worksheet.write(c+8,0,'mean')
    if need==3:
        worksheet.write(c+1,0,'min')
        worksheet.write(c+2,0,'1%percentile')
        worksheet.write(c+3,0,'25%percentile')
        worksheet.write(c+4,0,'50%percentile')
        worksheet.write(c+5,0,'75%percentile')
        worksheet.write(c+6,0,'99%percentile')
        worksheet.write(c+7,0,'max')
        worksheet.write(c+8,0,'mean')
        counts=np.bincount(inx)
        worksheet.write(c+7,0,'mode')


#@time_c
def hist_cros_con_dis_show(workbook,name_list,input_data1,interval1,input_data2,interval2):
    '''
    统计不同 in2（离散变量）输入变量in1（连续变量）在间隔step下的分布，并将结果返回到excel中。(统计不同充电模式下，充电时长占比)
    in1和in2长度相同
    name_list=[sheet名]
    并返回的统计值：最小值，4分位值，最大值，平均值
    '''
    worksheet = workbook.add_worksheet(name_list[0])
    [row_con,freq,re2]=hist_con_dis(input_data1,interval1,input_data2,interval2,1,1)

    for c in range(len(interval2)):
        r=0
        worksheet.write(r,c+1,interval2[c])
        for i in range(len(row_con)):
            r+=1
            worksheet.write(r,c+1,freq[c][i])
        r+=3
        for i in range(8):
            worksheet.write(r+i,c+1,re2[c][i])
    
    r=0
    for i in range(len(row_con)):
        r+=1
        worksheet.write(r,0,row_con[i])
    r+=3
    l=['min','1%percentile','25%percentile','50%percentile','75%percentile','99%percentile','max','mean']
    for i in range(8):
        worksheet.write(r+i,0,l[i])

#@time_c
def hist_cros_2con_show(workbook,name_list,in1,step1,in2,step2):
    '''
    统计两个连续变量的分布（eg:电机工作点）
    #name_list=[sheet名]
    '''
    worksheet = workbook.add_worksheet(name_list[0])
    [col_con,row_con,res]=hist_cros_2con(in1,step1,in2,step2)
    
    for c in range(len(col_con)):
        worksheet.write(0,c+1,col_con[c])

    for r in range(len(row_con)):
        worksheet.write(r+1,0,row_con[r])
        for c in range(len(col_con)):
            worksheet.write(r+1,c+1,res[r][c])





