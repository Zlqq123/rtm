import sys
sys.path.append('./')
from clickhouse_driver import Client
import xlsxwriter
import time
import csv
import numpy as np
import hist_func
import hist_func_np
from rtm.charge_ana1 import RtmAna

client=Client(host='10.122.17.69',port='9005',user='en' ,password='en1Q',database='en')

l1=RtmAna("D:/03RTM/ALL_RTM_data/0611/","lavida",client)#charging_lavida


sql="SELECT cast(emspeed,'float'),cast(emtq,'float') " \
    "from rtm_vds where deviceid like 'LSVA%' AND cast(vehiclespeed,'float')>0"
aus=client.execute(sql)
workbook = xlsxwriter.Workbook("_drive"+".xlsx")
speed=[]
torq=[]
for value in aus:
    speed.append(value[0])
    torq.append(value[1])



start=time.time()
hist_func_np.hist_cros_2con_show(workbook,['new'],np.array(speed),np.arange(0,5000,1000),np.array(torq),np.arange(0,300,50))
print('new cost',time.time()-start)


start=time.time()
hist_func.hist_cros_2con_show(workbook,['old'],speed,range(0,5000,1000),torq,range(0,300,50))
print('old cost',time.time()-start)
workbook.close()

l1=np.array([1,2,3,1,3,12,2,1,3,4,1,34,5,13,12,3,13,4,6,7,3,7,8,8,9,95,65,45,4,43,23,43,7,68,98,53,23,6,34,64,89])
l2=np.array([53,2,4,15,2,56,7,8,67,9,1,2,1,5,8,5,84,43,5,2,63,7,85,86,42,1,3,4,2,41,26,63,64,74,2,3,4,1,4,5,3])
x=hist_func_np.hist_cros_2con(l1,[0,50,70,100],l2,[0,30,100])
print(np.histogram2d(l1,l2))


l1=[1,2,3,1,3,12,2,1,3,4,1,34,5,13,12,3,13,4,6,7,3,7,8,8,9,95,65,45,4,43,23,43,7,68,98,53,23,6,34,64,89]
steps=np.array([0,5,10,20,40,100])
a=np.arange( 10, 30, 5 )#array([10, 15, 20, 25])
#np.arange( start, end, step )  start default 0   step default 1
input_data=np.array(l1)


c=input_data<40
print(c)
print(sum(c))
c=(input_data<90) & (input_data>40)
print(c)
print(sum(c))


l1=np.array([1,2,3,1,3,12,2,1,3,4,1,34,5,13,12,3,13,4,6,7,3,7,8,8,9,95,65,45,4,43,23,43,7,68,98,53,23,6,34,64,89])
l2=np.array([53,2,4,15,2,56,7,8,67,9,1,2,1,5,8,5,84,43,5,2,63,7,85,86,42,1,3,4,2,41,26,63,64,74,2])
steps=np.array([0,5,10,20,40,100])
BLOCK=5
for i in range(0, len(l1), BLOCK):
     sa = np.sort(a[i:i+BLOCK])
     print(sa)

sa=np.sort(l1)#排序,返回排序后的数组
sorting_index = np.argsort(l1)#排序，返回原数组排序的序号
wa=np.searchsorted(sa,10)#针对从小到大数组，返回第一个>10的值的序号，如果所有数值都小于10，返回数组长度
wa1=np.searchsorted(sa,[3,10,20],side='left')
wa2=np.searchsorted(sa,[3,10,20],side='right')
w=np.concatenate((wa1,wa2))#数组拼接
w1=np.append(w,19)#数组拼接
w1=np.append(wa1,wa2)#数组拼接
a=np.histogram(l1)#统计
a1=np.arange( 10, 30, 5 )#array([10, 15, 20, 25])#np.arange( start, end, step )  start default 0   step default 1
len(l1)
re=np.zeros(len(steps)-1)


a=1