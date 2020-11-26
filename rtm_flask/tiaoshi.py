import pandas as pd
import os
import json
#-*- coding:utf-8 -*-  
path="D:/21python/rtm/data_visualization/f12/"
df1=pd.read_excel(path+'data/mile.xlsx', sheet_name = 'drive_mode',index_col=0,header=0)
j_all={}
columns1 = df1.columns.tolist()
index1 = df1.index.tolist()
j_all['index']=df1.index.tolist()

for column in columns1:
    j_all[column] =[round(i*100,3) for i in df1[column].values.tolist() ] 

dat1=json.dumps(j_all,ensure_ascii=False)
print(dat1)

df1=pd.read_excel(path+'data/mile.xlsx', sheet_name = 'velocity',index_col=0,header=0)
j_all={}
columns1 = df1.columns.tolist()
index1 = df1.index.tolist()
j_all['index']=df1.index.tolist()


for column in columns1:
    j_all[column] =[round(i*100,3) for i in df1[column].values.tolist() ] 

dat1=json.dumps(j_all,ensure_ascii=False)
print(dat1)

df1=pd.read_excel(path+'data/mile.xlsx', sheet_name = 'Sheet3',index_col=0,header=0)
j_all={}
columns1 = df1.columns.tolist()
index1 = df1.index.tolist()
#j_all['index']=df1.index.tolist()


for column in columns1:
    j_all[column] =[round(i*100,3) for i in df1[column].values.tolist() ] 

dat1=json.dumps(j_all,ensure_ascii=False)
print(dat1)

df1=pd.read_excel(path+'data/mile.xlsx', sheet_name = 'consumption',index_col=0,header=0)
j_all={}
columns1 = df1.columns.tolist()
index1 = df1.index.tolist()
j_all['index']=df1.index.tolist()
for column in columns1:
    j_all[column] =df1[column].values.tolist()

dat1=json.dumps(j_all,ensure_ascii=False)
print(dat1)


df3=pd.read_excel(path+'data/vehicle_distribution.xlsx', sheet_name = 'passat')
re=[]

for index, row in df3.iterrows():
    temp = {}
    temp["name"]=row["name"]
    temp["value"]=row["value"]
    re.append(temp)



dat1=json.dumps(re,ensure_ascii=False)
print(dat1)


df3=pd.read_excel(path+'data/vehicle_distribution.xlsx', sheet_name = 'Tiguan')
re=[]

for index, row in df3.iterrows():
    temp = {}
    temp["name"]=row["name"]
    temp["value"]=row["value"]
    re.append(temp)


import json
dat1=json.dumps(re,ensure_ascii=False)
print(dat1)

path="D:/21python/rtm/data_visualization/f12/"
df3=pd.read_excel(path+'data/vehicle_distribution.xlsx', sheet_name = 'lavida')
re=[]

for index, row in df3.iterrows():
    temp = {}
    temp["name"]=row["name"]
    temp["value"]=row["value"]
    re.append(temp)


import json
dat1=json.dumps(re,ensure_ascii=False)
print(dat1)

df1 = pd.read_excel(path+'data/vehicle_distribution.xlsx', sheet_name = 0)
df2 = pd.read_excel(path+'data/vehicle_distribution.xlsx', sheet_name = 1)
#print(df1)
#print(df2)
col1 = df1.columns
print(col1)
df_project=df2.pivot_table(index='车型', values=['车辆数目'], aggfunc=sum)

lavida = df2[ df2['车型'] == 'Lavida BEV 53Ah']
for indexs in df1.index:
    print(df1.loc[indexs].values[0])
    print(df1.loc[indexs].values[1])

c=df2.groupby(['车型','地区'])
print(c)
print(type(c))

'''

df2[ df2['车型'] == 'Passat PHEV']
df2[ df2['车型'] == 'Tiguan L PHEV']

'''

