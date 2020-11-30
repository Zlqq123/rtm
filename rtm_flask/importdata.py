import pandas as pd
import os
import json
#-*- coding:utf-8 -*-  
path="D:/21python/rtm/rtm_flask/"
df1 = pd.read_excel (path + 'data/mile.xlsx', sheet_name = 'warming',index_col=0,header=0)
j_all={}
columns1 = df1.columns.tolist()
j_all['index']=df1.index.tolist()
j_all['col']=df1.columns.tolist()
for column in columns1:
    j_all[column] =df1[column].values.tolist()

dat1=json.dumps(j_all,ensure_ascii=False)
print(dat1)

speed=["-4000~-3500rpm", "-3500~-3000rpm", "-3000~-2500rpm", "-2500~-2000rpm", "-2000~-1500rpm", "-1500~-1000rpm", "-1000~-500rpm", "-500~0rpm", "0~500rpm", "500~1000rpm", "1000~1500rpm", "1500~2000rpm", "2000~2500rpm", "2500~3000rpm", "3000~3500rpm", "3500~4000rpm", "4000~4500rpm", "4500~5000rpm", "5000~5500rpm", "5500~6000rpm", "6000~6500rpm", "6500~7000rpm", "7000~7500rpm", "7500~8000rpm", "8000~8500rpm", "8500~9000rpm", "9000~9500rpm", "9500~10000rpm", "10000~10500rpm", "10500~11000rpm", "11000~11500rpm", "11500~12000rpm", "12000~12500rpm"]
torq=["-300~-250Nm", "-250~-200Nm", "-200~-150Nm", "-150~-100Nm", "-100~-50Nm", "-50~0Nm", "0~50Nm", "50~100Nm", "100~150Nm", "150~200Nm", "200~250Nm", "250~300Nm", "300~350Nm"]
df1=pd.read_excel(path + 'data/e_motor.xlsx', sheet_name = 'lavida-6',index_col=0,header=0)
x=df1.values
re=[]
for i in range(33):
    for j in range(13):
        re.append([torq[j],speed[i],round(x[i,j]*100,3)])
dat1=json.dumps(re,ensure_ascii=False)
print(dat1)


a=''
for i in range(33):
    a+='"'+str(i*500-4000)+"~"+str(i*500-3500)+'rpm", '
print(a)

a=''
for i in range(13):
    a+='"'+str(i*50-300)+"~"+str(i*50-250)+'Nm", '
print(a)

df1 = pd.read_excel (path + 'data/e_motor.xlsx', sheet_name = 'lavida-6',index_col=0,header=0)
j_all={}
columns1 = df1.columns.tolist()
j_all['index']=df1.index.tolist()
j_all['col']=df1.columns.tolist()
for column in columns1:
    j_all[column] =[round(i*100,3) for i in df1[column].values.tolist() ] 

dat1=json.dumps(j_all,ensure_ascii=False)
print(dat1)



df1=pd.read_excel(path+'data/charge.xlsx', sheet_name = 'soc',index_col=0,header=0)
j_all={}
columns1 = df1.columns.tolist()
j_all['index']=df1.index.tolist()
j_all['col']=df1.columns.tolist()
for column in columns1:
    j_all[column] =[round(i*100,3) for i in df1[column].values.tolist() ] 

dat1=json.dumps(j_all,ensure_ascii=False)
print(dat1)

SOC =["0~5%", "5~10%", "10~15%", "15~20%", "20~25%", "25~30%", "30~35%", "35~40%", "40~45%", "45~50%", "50~55%", "55~60%", "60~65%", "65~70%", "70~75%", "75~80%", "80~85%", "85~90%", "90~95%", "95~100%","100%"]
temp = ["-30~-25℃", "-25~-20℃", "-20~-15℃", "-15~-10℃", "-10~-5℃", "-5~0℃", "0~5℃", "5~10℃", "10~15℃", "15~20℃", "20~25℃", "25~30℃", "30~35℃", "35~40℃", "40~45℃", "45~50℃", "50~55℃", "55~60℃"]
df1=pd.read_excel(path+'data/battery.xlsx', sheet_name = 'lavida_6_disc',index_col=0,header=0)
x=df1.values
re=[]
print(re)
for i in range(21):
    for j in range(6,17):
        re.append([temp[j],SOC[i],round(x[i,j]*100,3)])
dat1=json.dumps(re,ensure_ascii=False)
print(dat1)


a=''
for i in range(20):
    a+='"'+str(i*5)+"~"+str(i*5+5)+'%", '
print(a)

a=''
for i in range(18):
    a+='"'+str(i*5-30)+"~"+str(i*5-25)+'℃", '
print(a)

#SOC = ["[0,5)", "[5,10)", "[10,15)", "[15,20)", "[20,25)", "[25,30)", "[30,35)", "[35,40)", "[40,45)", "[45,50)", "[50,55)", "[55,60)", "[60,65)", "[65,70)", "[70,75)", "[75,80)", "[80,85)", "[85,90)", "[90,95)", "[95,100)", "100"]
#temp= ["[-30,-25)", "[-25,-20)", "[-20,-15)", "[-15,-10)", "[-10,-5)", "[-5,0)", "[0,5)", "[5,10)", "[10,15)", "[15,20)", "[20,25)", "[25,30)", "[30,35)", "[35,40)", "[40,45)", "[45,50)", "[50,55)", "[55,60)"] 

df1=pd.read_excel(path+'data/battery.xlsx', sheet_name = 'lavida_6_disc',index_col=0,header=0)
x=df1.values
print(x[20,17])
re=[]
print(re)
for i in range(21):
    
    for j in range(18):

        re.append([j,i,round(x[i,j]*100,3)])
dat1=json.dumps(re,ensure_ascii=False)
print(dat1)





df1=pd.read_excel(path+'data/battery.xlsx', sheet_name = 'lavida_6_char',index_col=0,header=0)
j_all={}
columns1 = df1.columns.tolist()
j_all['index']=df1.index.tolist()
j_all['col']=df1.columns.tolist()
for column in columns1:
    j_all[column] =[round(i*100,3) for i in df1[column].values.tolist() ] 

dat1=json.dumps(j_all,ensure_ascii=False)
print(dat1)


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

