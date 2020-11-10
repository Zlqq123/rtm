import pandas as pd
import os
path="D:/21python/rtm/data_visualization/f12/"

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

